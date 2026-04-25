# Hooks — cc-hooks integration for safe refactor sessions

> Claude Code hooks are shell commands the harness executes around tool calls.
> During a refactor session they add automatic guardrails that even a distracted
> agent can't bypass. Install them per-project via `.claude/settings.json`.
>
> See the sibling [cc-hooks](../../cc-hooks/SKILL.md) skill for schema details
> and troubleshooting.

## Contents

1. [Why hooks matter for refactors](#why-hooks-matter-for-refactors)
2. [PreToolUse — block dangerous patterns](#pretooluse--block-dangerous-patterns)
3. [PostToolUse — auto-verify after Edit](#posttooluse--auto-verify-after-edit)
4. [Stop — pass-closeout checks](#stop--pass-closeout-checks)
5. [Copy-paste: `.claude/settings.json`](#copy-paste-claudesettingsjson)
6. [Interaction with the Rule #1 no-deletion policy](#interaction-with-the-rule-1-no-deletion-policy)
7. [Installing / uninstalling](#installing--uninstalling)

---

## Why hooks matter for refactors

The failure modes this skill is designed to prevent — two-pathway drift,
`_v2` orphans, codemod runs, unauthorized deletions, warning creep — are
mechanically easy to catch at the tool boundary. A PreToolUse hook on `Bash`
rejecting `sed -i` is worth more than any amount of "don't use sed" in the
SKILL.md. The text might be skimmed; the hook fires every time.

## PreToolUse — block dangerous patterns

Block the following before execution:

- `Bash` with `sed -i`, `perl -i`, `jq -i`, or any in-place codemod → refactors
  must go through `Edit`.
- `Bash` with `rm ` on anything under `src/` → file deletion needs an isomorphism
  card citing explicit user approval (AGENTS.md Rule #1).
- `Write` when the target path matches `*_v2.*`, `*_new.*`, or `tmp_*` → the
  skill forbids these filename shapes entirely.
- `Bash` with `git reset --hard` or `git push --force` on `main` → dcg-style
  pre-check before a destructive git op.

Behavior: emit a one-line rationale and a pointer to the relevant section of
the skill. Do NOT silently eat the command.

## PostToolUse — auto-verify after Edit

After any `Edit` or `Write` under `src/`, run a cheap check that the warning
ceiling hasn't grown:

```bash
./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/lint_ceiling.sh check \
  || echo 'WARNING CEILING EXCEEDED — fix before next Edit'
```

Keep it non-blocking — the first run after introducing a new warning may be
fine if the agent is about to fix it; the message is a reminder, not a brake.

After a `Bash` that ran the test suite, snapshot the result so Phase-G's
`ledger_row.sh` has the fresh counts to use. Cheaply:

```bash
case "$TOOL_INPUT_COMMAND" in
  *cargo\ test*|*pytest*|*npm\ test*|*go\ test*)
    mkdir -p refactor/artifacts/latest
    echo "$TOOL_INPUT_COMMAND" > refactor/artifacts/latest/test_cmd
    ;;
esac
```

## Stop — pass-closeout checks

When the session ends (Stop hook), fire these as a final guard:

1. Any `_v2` / `_new` / `tmp_` files in the diff → loud warning.
2. Any new `any`/`unwrap`/bare `except:` in the diff compared to the baseline → loud warning.
3. `git status` clean or fully staged — no half-committed refactor state.
4. Ledger row exists for each commit touching `src/` this pass.

These are informational; the user may intentionally end the session mid-pass.
The point is to surface state, not to block `Stop`.

## Copy-paste: `.claude/settings.json`

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'cmd=\"$CLAUDE_TOOL_INPUT_COMMAND\"; case \"$cmd\" in *sed*-i*|*perl*-i*|*jq*-i*) echo \"{\\\"decision\\\":\\\"block\\\",\\\"reason\\\":\\\"refactor skill forbids codemods — use Edit\\\"}\" ;; esac'"
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'p=\"$CLAUDE_TOOL_INPUT_FILE_PATH\"; case \"$p\" in *_v2.*|*_new.*|*/tmp_*) echo \"{\\\"decision\\\":\\\"block\\\",\\\"reason\\\":\\\"refactor skill forbids _v2/_new/tmp_ filenames — edit the canonical file\\\"}\" ;; esac'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "./.claude/skills/simplify-and-refactor-code-isomorphically/scripts/lint_ceiling.sh check 2>&1 | head -5"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "git diff --name-only | grep -E '_v2|_new|tmp_' && echo 'WARN: orphan-style filenames in working tree' || true"
          }
        ]
      }
    ]
  }
}
```

Adjust `CLAUDE_TOOL_INPUT_*` variable names to the actual cc-hooks env-var
schema for your Claude Code version; consult [cc-hooks/SKILL.md](../../cc-hooks/SKILL.md).

## Interaction with the Rule #1 no-deletion policy

AGENTS.md Rule #1 forbids file deletion without explicit user approval. The
`rm` PreToolUse hook above is intentionally conservative — it allows `rm` on
paths outside `src/` (like `refactor/artifacts/*/tmp`). If your project has
AGENTS.md placing the same rule on `tests/`, `migrations/`, etc., widen the
pattern.

## Installing / uninstalling

```bash
# after editing .claude/settings.json, confirm the harness sees it
cat .claude/settings.json | jq .hooks

# test a single hook by simulating the invocation
CLAUDE_TOOL_INPUT_COMMAND='sed -i s/x/y/ file' \
  bash -c 'source .claude/settings.json-simulation && run_hook PreToolUse Bash'
```

To uninstall, remove the block from `.claude/settings.json`. Project-scoped
hooks don't leak outside the repo.
