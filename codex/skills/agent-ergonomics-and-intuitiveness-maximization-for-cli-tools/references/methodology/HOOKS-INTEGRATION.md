# HOOKS-INTEGRATION — Pre-commit drift guards for agent contracts

> **Status: aspirational design document.** The check scripts referenced
> below at `scripts/aerg-hooks/*.sh` are NOT yet implemented. Use this
> document as a specification — the code samples + invocation patterns are
> the authoritative description. When implementing, place the scripts at
> `scripts/aerg-hooks/<name>.sh` with the names this doc uses so existing
> recipes work as-is.

The agent-facing contracts (`capabilities --json`, `--help` footer, exit-code dict, `robot-docs guide`) must NOT drift silently. Hooks catch drift at commit-time, before it hits agents.

This file gives copy-pasteable hook configs for the most common setups: Claude Code's `cc-hooks`, the `pre-commit` framework, husky / lefthook (TypeScript), and plain git hooks.

For CI-side (PR-time) drift guards, see `CI-INTEGRATION.md`.

---

## What to hook

### High-value hooks (always add)

1. **`capabilities --json` schema-pin** — if the schema changes, fail unless `contract_version` was bumped
2. **Exit-code dict drift** — if `capabilities.exit_codes` changes, fail unless `--help` was updated to match
3. **`--help` footer drift** — every subcommand's `--help` ends with the AGENT/AUTOMATION footer; fail if missing
4. **`robot-docs guide` length** — < 80 lines AND mentions all 6 required topics

### Mid-value hooks (add for high-stakes tools)

5. **Levenshtein-1 typo coverage** — `KNOWN_FLAGS` array covers every clap/cobra/argparse-defined flag
6. **Mutating-verb gate audit** — every verb with `mutates: true` requires `--yes` AND offers `--dry-run`
7. **Stdout/stderr split** — emit-statements scanning to verify error paths don't print to stdout
8. **No `rm -rf` / `git reset --hard` in tool source** — meta-AGENTS.md compliance

### Low-value (skip unless paranoid)

9. **Performance budget** — `<tool> --help` returns < 200ms (only if hot-path is critical)

---

## Claude Code `cc-hooks` (PreToolUse / PostToolUse)

For projects developed with Claude Code, use `cc-hooks` to enforce the above at edit-time.

**`.claude/settings.json`:**

```jsonc
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          { "type": "command", "command": "scripts/aerg-hooks/check-capabilities-pin.sh" },
          { "type": "command", "command": "scripts/aerg-hooks/check-help-footer.sh" }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          { "type": "command", "command": "scripts/aerg-hooks/check-capabilities-pin.sh" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "dcg" }
        ]
      }
    ]
  }
}
```

The hooks themselves live under `scripts/aerg-hooks/`. Templates below.

### `scripts/aerg-hooks/check-capabilities-pin.sh`

```bash
#!/usr/bin/env bash
# Block commits that change capabilities --json without bumping contract_version.
set -euo pipefail

# Only run if capabilities source changed
changed=$(git diff --cached --name-only | grep -E '(capabilities|src/cli|src/cmd)' || true)
[ -z "$changed" ] && exit 0

# Build the post-edit binary (or use cached build)
TOOL_BIN="${TOOL_BIN:-./target/release/mytool}"
[ ! -x "$TOOL_BIN" ] && cargo build --release >/dev/null

new=$("$TOOL_BIN" capabilities --json | jq -S .)
golden_path="audit/regression_tests/capabilities-golden.json"

if [ ! -f "$golden_path" ]; then
  echo "warn: no golden capabilities at $golden_path; treating as first run" >&2
  echo "$new" > "$golden_path"
  exit 0
fi

old=$(cat "$golden_path" | jq -S .)
if [ "$new" != "$old" ]; then
  # Schema changed — require contract_version bump
  old_v=$(echo "$old" | jq -r '.contract_version')
  new_v=$(echo "$new" | jq -r '.contract_version')
  if [ "$old_v" = "$new_v" ]; then
    echo "BLOCK: capabilities --json changed but contract_version is still '$old_v'." >&2
    echo "Bump contract_version OR revert the schema change." >&2
    diff <(echo "$old") <(echo "$new") | head -30 >&2
    exit 1
  fi
  echo "note: capabilities changed and contract_version bumped to '$new_v'; updating golden" >&2
  echo "$new" > "$golden_path"
fi
exit 0
```

### `scripts/aerg-hooks/check-help-footer.sh`

```bash
#!/usr/bin/env bash
# Verify every subcommand's --help ends with the AGENT/AUTOMATION footer.
set -euo pipefail
TOOL_BIN="${TOOL_BIN:-./target/release/mytool}"
[ ! -x "$TOOL_BIN" ] && exit 0

# Required footer keywords
required=("--json" "capabilities" "robot-docs" "EXIT CODES")

# Top-level
help=$("$TOOL_BIN" --help 2>&1)
for k in "${required[@]}"; do
  if ! echo "$help" | grep -qE "$k"; then
    echo "BLOCK: top-level --help missing '$k'. Add an AGENT/AUTOMATION footer." >&2
    exit 1
  fi
done

# Per-subcommand
verbs=$("$TOOL_BIN" capabilities --json | jq -r '.commands | keys[]' 2>/dev/null || echo "")
for v in $verbs; do
  help=$("$TOOL_BIN" "$v" --help 2>&1 || true)
  if ! echo "$help" | grep -qE 'AGENT/AUTOMATION|--json|robot'; then
    echo "BLOCK: '$v --help' lacks AGENT/AUTOMATION footer or --json mention." >&2
    exit 1
  fi
done
exit 0
```

---

## `pre-commit` framework

For projects using the pre-commit framework, add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: aerg-capabilities-pin
        name: agent-ergo capabilities --json schema pin
        entry: scripts/aerg-hooks/check-capabilities-pin.sh
        language: script
        files: '(capabilities|src/cli|src/cmd)\.(rs|go|py|ts)$'
        pass_filenames: false

      - id: aerg-help-footer
        name: agent-ergo --help footer check
        entry: scripts/aerg-hooks/check-help-footer.sh
        language: script
        pass_filenames: false
        stages: [pre-push]   # build the binary; expensive; run on push not commit

      - id: aerg-mutating-verb-gates
        name: agent-ergo mutating verbs require --yes/--dry-run
        entry: scripts/aerg-hooks/check-mutating-verb-gates.sh
        language: script
        pass_filenames: false

      - id: aerg-stdout-stderr-split
        name: agent-ergo stdout/stderr split
        entry: scripts/aerg-hooks/check-stdout-stderr-split.sh
        language: script
        pass_filenames: false
```

### `scripts/aerg-hooks/check-mutating-verb-gates.sh`

```bash
#!/usr/bin/env bash
# Verify every verb with mutates:true in capabilities also has --yes and --dry-run flags.
set -euo pipefail
TOOL_BIN="${TOOL_BIN:-./target/release/mytool}"
[ ! -x "$TOOL_BIN" ] && exit 0

mutating=$("$TOOL_BIN" capabilities --json | jq -r '
  .commands | to_entries[] | select(.value.mutates == true) | .key' 2>/dev/null || echo "")

failed=0
for v in $mutating; do
  flags=$("$TOOL_BIN" "$v" --help 2>&1)
  for required in '--yes' '--dry-run'; do
    if ! echo "$flags" | grep -qE -- "$required"; then
      echo "BLOCK: mutating verb '$v' missing $required flag" >&2
      failed=$((failed + 1))
    fi
  done
done
[ "$failed" -gt 0 ] && exit 1
exit 0
```

### `scripts/aerg-hooks/check-stdout-stderr-split.sh`

```bash
#!/usr/bin/env bash
# Best-effort scan for error paths that print to stdout instead of stderr.
# Patterns vary by language; this catches the obvious Rust + Python ones.
set -euo pipefail

violations=0

# Rust: println! inside an Err / .map_err pattern is suspicious
while IFS= read -r line; do
  if echo "$line" | grep -qE 'println!.*[Ee]rror|println!.*[Ff]ail'; then
    echo "WARN: $line (use eprintln! for errors)" >&2
    violations=$((violations + 1))
  fi
done < <(grep -rn -E 'println!' --include='*.rs' src/ 2>/dev/null || true)

# Python: print() inside except / raise paths
while IFS= read -r line; do
  if echo "$line" | grep -qE 'print\(.*[Ee]rror|print\(.*[Ff]ail'; then
    echo "WARN: $line (use sys.stderr.write or print(file=sys.stderr))" >&2
    violations=$((violations + 1))
  fi
done < <(grep -rn -E 'print\(' --include='*.py' src/ 2>/dev/null || true)

# This is a warning-only hook by default (false positives common); set strict=1 to fail
strict="${AERG_STRICT_STDOUT_STDERR:-0}"
[ "$strict" = "1" ] && [ "$violations" -gt 0 ] && exit 1
exit 0
```

---

## Husky (TypeScript / npm projects)

```json
// package.json
{
  "scripts": {
    "aerg:check-capabilities": "scripts/aerg-hooks/check-capabilities-pin.sh",
    "aerg:check-help": "scripts/aerg-hooks/check-help-footer.sh",
    "aerg:check-all": "npm run aerg:check-capabilities && npm run aerg:check-help"
  },
  "husky": {
    "hooks": {
      "pre-commit": "npm run aerg:check-capabilities",
      "pre-push": "npm run aerg:check-help"
    }
  }
}
```

For modern husky v8+:

```bash
# .husky/pre-commit
#!/usr/bin/env bash
. "$(dirname "$0")/_/husky.sh"
npm run aerg:check-capabilities

# .husky/pre-push
#!/usr/bin/env bash
. "$(dirname "$0")/_/husky.sh"
npm run aerg:check-help
```

---

## Lefthook (Go / mixed projects)

`lefthook.yml`:

```yaml
pre-commit:
  parallel: true
  commands:
    aerg-capabilities:
      glob: '{capabilities,cmd,internal/cmd}/**/*.go'
      run: scripts/aerg-hooks/check-capabilities-pin.sh
    aerg-stdout-stderr:
      run: scripts/aerg-hooks/check-stdout-stderr-split.sh

pre-push:
  commands:
    aerg-help-footer:
      run: scripts/aerg-hooks/check-help-footer.sh
    aerg-mutating-verb-gates:
      run: scripts/aerg-hooks/check-mutating-verb-gates.sh
```

---

## Plain git hooks

If no hook framework is in use, drop scripts into `.git/hooks/`:

`.git/hooks/pre-commit`:

```bash
#!/usr/bin/env bash
set -e
SKILL_HOOKS=scripts/aerg-hooks
[ -x "$SKILL_HOOKS/check-capabilities-pin.sh" ] && "$SKILL_HOOKS/check-capabilities-pin.sh"
[ -x "$SKILL_HOOKS/check-stdout-stderr-split.sh" ] && "$SKILL_HOOKS/check-stdout-stderr-split.sh"
```

`.git/hooks/pre-push`:

```bash
#!/usr/bin/env bash
set -e
SKILL_HOOKS=scripts/aerg-hooks
[ -x "$SKILL_HOOKS/check-help-footer.sh" ] && "$SKILL_HOOKS/check-help-footer.sh"
[ -x "$SKILL_HOOKS/check-mutating-verb-gates.sh" ] && "$SKILL_HOOKS/check-mutating-verb-gates.sh"
```

Note: `.git/hooks/` is local-only; check the scripts into the repo's `scripts/aerg-hooks/` AND have a `setup.sh` that symlinks into `.git/hooks/` for new clones.

---

## Drift-guard hook for the `audit/regression_tests/` directory itself

Worth adding for the audit workspace itself:

```bash
#!/usr/bin/env bash
# audit/.git-hooks/check-regression-tests-runnable.sh
# All audit/regression_tests/*.test.sh must be executable + pass on the current binary.
set -euo pipefail
TOOL_BIN="${TOOL_BIN:-./target/release/mytool}"

failed=0
for t in audit/regression_tests/*.test.sh; do
  [ ! -x "$t" ] && { echo "BLOCK: $t not executable" >&2; failed=$((failed + 1)); continue; }
  bash "$t" >/dev/null 2>&1 || { echo "BLOCK: $t failed" >&2; failed=$((failed + 1)); }
done

[ "$failed" -gt 0 ] && exit 1
exit 0
```

---

## Hook-friendly `dcg` integration

If the project uses `/dcg` for shell-command safety, the destructive-command-guard hook is also a great place to enforce agent-ergonomic block messages: every block message must name the safe alternative.

`scripts/aerg-hooks/check-dcg-block-messages.sh`:

```bash
#!/usr/bin/env bash
# Verify dcg pack messages contain alternatives.
set -euo pipefail
[ ! -d packs/ ] && exit 0

failed=0
for pack in packs/*.toml; do
  # Find every "reason" field; verify it contains an alternative
  while IFS= read -r reason; do
    if ! echo "$reason" | grep -qiE 'use|try|alt|instead|safe'; then
      echo "WARN: dcg pack '$pack' has block message without alternative: $reason" >&2
      failed=$((failed + 1))
    fi
  done < <(grep -E '^reason\s*=' "$pack" | sed -E 's/^reason\s*=\s*//')
done

[ "$failed" -gt 5 ] && exit 1
exit 0
```

---

## Hook performance budget

Hooks run on every commit. Keep them fast:

| Hook | Target latency |
|------|----------------|
| Capabilities pin | < 500ms (with cached build) |
| Help footer | < 1s (full build + N help invocations) |
| Stdout/stderr split scan | < 200ms (regex over source) |
| Mutating-verb gates | < 1s (capabilities + per-verb help) |
| dcg block messages | < 100ms |

If a hook is slower:
- Move it from `pre-commit` to `pre-push`
- Cache the build artifact (only rebuild when source changes)
- Sample N% of files instead of all

---

## Bypass discipline

Per AGENTS.md, **never use `--no-verify`** to bypass hooks. If a hook is failing:

1. Diagnose: read the hook's stderr; understand what's being protected.
2. Fix the underlying issue.
3. If the hook itself is buggy, fix the hook (don't bypass).
4. If the hook is too strict, document the exception via `<HOOK_NAME>_EXCEPTIONS=<reason>` env var or in `.aerg-hooks-config.toml`.

The whole point of these hooks is to catch agent-contract drift. Bypassing them puts agents at risk.

---

## Distribute the hooks across the team

Add to project README:

```markdown
## For contributors

We use agent-ergonomic drift guards (see `scripts/aerg-hooks/`). Install once:

    bash scripts/aerg-hooks/install.sh

This symlinks the hooks into `.git/hooks/` (or registers them with `pre-commit` if installed).

To run the hooks manually:

    bash scripts/aerg-hooks/check-all.sh
```

`scripts/aerg-hooks/install.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
HOOK_DIR=$(git rev-parse --git-dir)/hooks

for hook in pre-commit pre-push; do
  cat > "$HOOK_DIR/$hook" <<EOF
#!/usr/bin/env bash
exec scripts/aerg-hooks/run-stage.sh $hook "\$@"
EOF
  chmod +x "$HOOK_DIR/$hook"
done

echo "agent-ergo hooks installed in $HOOK_DIR"
```

---

## Related

- `CI-INTEGRATION.md` — PR-time guards (run in CI, not at commit-time)
- `references/rubric/REGRESSION-TEST-PATTERNS.md` — what each hook is enforcing
- `/cc-hooks` skill — Claude Code hook framework details
- `/dcg` skill — destructive-command guard hook (already canonical for command safety)
