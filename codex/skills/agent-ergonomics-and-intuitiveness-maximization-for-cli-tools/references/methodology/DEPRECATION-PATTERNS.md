# DEPRECATION-PATTERNS — Safe breaking changes

The audit will frequently find recommendations that change a user-visible contract: rename a flag, change an exit code, restructure JSON output. These changes are valuable BUT must be applied with a deprecation path; a "rip the bandaid" approach silently breaks downstream agents.

This file gives the canonical deprecation patterns.

Applies whenever a recommendation's `risk` field says "would break existing usage" — instead of dropping the rec, refactor it through one of the patterns below.

---

## Stage model

A breaking change goes through stages:

```
[stage 0: introduce]   → both old + new work; old emits no warning yet
[stage 1: warn]        → both old + new work; old emits deprecation warning
[stage 2: error]       → old fails with migration recipe; new is canonical
[stage 3: remove]      → old gone from source; only new remains
```

Each stage corresponds to a release or a pass:

| Stage | When to enter |
|-------|---------------|
| 0 | The new form is added; old form is still primary. Pass introduces both. |
| 1 | The new form is canonical. Old form emits a warning when used. Wait ≥ 1 release for users to migrate. |
| 2 | Old form errors with a migration recipe. Wait ≥ 1 more release. |
| 3 | Old form removed entirely. |

Skipping stages is **never** safe for a public CLI. For internal tools with no external users, the audit can compress stages 1-3 within one pass — but document explicitly in `applied_changes.jsonl.risk`.

---

## Pattern D-1: Rename a flag

**Old.** `--colour`. **New.** `--color`.

### Stage 0 (introduce)

```rust
// Both --color and --colour work; both set the same internal field.
#[derive(Args)]
pub struct StyleArgs {
    /// Use color output.
    #[arg(long, alias = "colour")]
    pub color: ColorMode,
}
```

### Stage 1 (warn)

```rust
// Detect that the alias was the actual token used (clap doesn't expose this directly;
// scan std::env::args() for "--colour" and emit a warning if present).
fn warn_deprecated() {
    if std::env::args().any(|a| a == "--colour") {
        eprintln!("warning: '--colour' is deprecated since v0.4.0; use '--color'.");
        eprintln!("  to suppress: set MYTOOL_NO_DEPRECATION_WARNINGS=1");
        eprintln!("  see: <project>/CHANGELOG.md § v0.4.0");
    }
}
```

### Stage 2 (error)

```rust
// Remove the alias; install a custom error.
if std::env::args().any(|a| a == "--colour") {
    eprintln!("error: '--colour' was removed in v0.5.0");
    eprintln!("  use '--color' instead (canonical since v0.4.0)");
    eprintln!("  to migrate: sed -i 's/--colour/--color/g' your-script.sh");
    std::process::exit(1);
}
```

### Stage 3 (remove)

Just delete the detection. No mention of `--colour` anywhere.

### Capabilities updates

In `capabilities --json`:

```jsonc
// Stage 0/1
"flags": [
  {"name": "--color", "type": "string"},
  {"name": "--colour", "deprecated": true, "alias_for": "--color", "removed_in": "v0.6.0"}
]

// Stage 2
"flags": [
  {"name": "--color", "type": "string"},
  {"name": "--colour", "removed": true, "removed_in": "v0.5.0"}
]
```

Agents reading capabilities can avoid deprecated flags proactively.

---

## Pattern D-2: Rename a verb

**Old.** `list-all`. **New.** `list`.

### Stage 0

Both verbs exist. Internally both call the same handler. Capabilities documents both:

```jsonc
"commands": {
  "list":     {"description": "List items", "mutates": false, ...},
  "list-all": {"description": "List items (deprecated alias)", "deprecated": true, "alias_for": "list"}
}
```

### Stage 1

`<tool> list-all` works AND emits a warning to stderr.

### Stage 2

`<tool> list-all` errors with: "use 'mytool list' instead." Migration script suggested.

### Stage 3

`list-all` gone. No reference except in CHANGELOG.

---

## Pattern D-3: Change an exit code

**Old.** `exit 1` for "no results" AND "user-input-error" (ambiguous). **New.** `exit 1` = user-input-error only; "no results" is `exit 0` with `{"items": [], "total": 0}`.

This is delicate because changing exit codes can break shell pipelines depending on `$?`.

### Stage 0

Add a new env var to opt into the new behavior:

```rust
let strict_exit = std::env::var("MYTOOL_STRICT_EXIT").is_ok();

if results.is_empty() {
    if strict_exit {
        // New: exit 0 with empty result
        emit_json(&Output { items: vec![], total: 0, ok: true });
        return Ok(());
    } else {
        // Old: exit 1 (preserved for compat)
        eprintln!("no results");
        eprintln!("note: this exit code is changing in v0.5.0; opt-in early via MYTOOL_STRICT_EXIT=1");
        std::process::exit(1);
    }
}
```

### Stage 1

Flip the default. Add deprecation warning to old behavior:

```rust
let legacy_exit = std::env::var("MYTOOL_LEGACY_EXIT").is_ok();

if results.is_empty() {
    if legacy_exit {
        eprintln!("warning: MYTOOL_LEGACY_EXIT will be removed in v0.6.0");
        std::process::exit(1);
    }
    emit_json(&Output { items: vec![], total: 0, ok: true });
    return Ok(());
}
```

### Stage 2

Remove the legacy env var.

### Capabilities updates

Document the migration in `capabilities.exit_codes`:

```jsonc
"exit_codes": {
  "0": {"meaning": "success (or no results, since v0.5.0)", "retryable": false},
  "1": {"meaning": "user-input-error (since v0.5.0; was 'error or no results' in <0.5)"}
}
```

---

## Pattern D-4: Change JSON output schema

**Old.** `{"results": [...]}` (per-verb-named root). **New.** `{"items": [...]}` (consistent envelope).

### Stage 0

Output **both** keys, with the new one canonical:

```jsonc
{
  "ok": true,
  "items": [...],     // new canonical
  "results": [...],   // deprecated alias, identical content
  "meta": {"data_hash": "..."}
}
```

Document in capabilities:

```jsonc
"commands": {
  "list": {
    "json": true,
    "output_schema": {
      "items": {"type": "array", "canonical": true},
      "results": {"type": "array", "deprecated": true, "alias_for": "items", "removed_in": "v0.6.0"}
    }
  }
}
```

### Stage 1

Add a header at top of JSON output indicating deprecation:

```jsonc
{
  "ok": true,
  "items": [...],
  "results": [...],
  "_deprecation": [
    {"path": "$.results", "use_instead": "$.items", "removed_in": "v0.6.0"}
  ]
}
```

### Stage 2

Remove `results` field. Old consumers break with a clear message.

---

## Pattern D-5: Change default behavior

**Old.** Default = case-sensitive search. **New.** Default = case-insensitive search.

This is harder than renaming because behavior changes silently.

### Stage 0

Introduce a flag for the new behavior, default off:

```bash
mytool search "FOO" --case-insensitive   # opt-in to new behavior
```

Document the planned default change in `--help`:

```
SEARCH BEHAVIOR:
  Default: case-sensitive (will change to case-insensitive in v1.0; use --case-sensitive to keep current)
```

### Stage 1

Flip the default. Add `--case-sensitive` to preserve old behavior:

```bash
mytool search "FOO"                # case-insensitive (new default)
mytool search "FOO" --case-sensitive   # opt-out to old behavior
```

Emit a warning at startup if running on a script that doesn't pass either flag (best-effort detection):

```
note: search default changed in v1.0 from case-sensitive to case-insensitive.
to opt-out: pass --case-sensitive
```

### Stage 2

Remove the warning. The new default is settled.

---

## Pattern D-6: Remove a feature entirely

**Old.** `mytool legacy-import`. **New.** Feature removed; users should use `mytool import`.

### Stage 0

Mark `legacy-import` as deprecated in `capabilities` AND emit warning when invoked.

### Stage 1

`legacy-import` errors with the migration recipe.

### Stage 2

`legacy-import` removed. Capabilities reflects this.

---

## Tooling migrations: `mytool migrate-from-X` subcommand

For non-trivial migrations, add a `mytool migrate-from-<old-version> --to=<new-version>` subcommand that automates the rewrite:

```bash
$ mytool migrate-from-v04 --to=v05 --dry-run /my/scripts/
plan:
  /my/scripts/foo.sh:
    line 12: --colour → --color
    line 18: list-all → list
  /my/scripts/bar.sh:
    line 5:  exit 1 (no results) handling — review manually
2 files, 3 automatic + 1 manual change. Run without --dry-run to apply.
```

This pattern transforms the deprecation message from a passive warning into an active migration tool. Hugely valuable for downstream agents.

---

## Multi-pass deprecation

A single audit pass typically introduces stage 0 of any breaking change. Stages 1–3 land in subsequent passes:

| Pass | Stage |
|------|-------|
| Pass N | Stage 0: new form added; old form unchanged |
| Pass N+1 (3-6 months later) | Stage 1: old form warns |
| Pass N+2 (6-12 months later) | Stage 2: old form errors |
| Pass N+3 (12+ months later) | Stage 3: old form removed |

The `HANDOFF.md` queues the next stage for the next pass. Don't compress unless the user explicitly approves.

For internal-only tools (no external users), the audit can compress stages 0+1+2+3 into one pass — document in `applied_changes.jsonl.risk` and confirm with user.

---

## Capabilities-driven deprecation discovery

Agents can proactively avoid deprecated surfaces by reading `capabilities --json`:

```bash
# List deprecated flags
mytool capabilities --json | jq '.commands | to_entries[] | .value.flags // [] | .[] | select(.deprecated == true) | .name'

# List flags that will be removed in next version
mytool capabilities --json | jq '.commands | to_entries[] | .value.flags // [] | .[] | select(.removed_in)'
```

This is why every flag, verb, env var should have:
- `deprecated: bool`
- `removed_in: <version>` (when applicable)
- `alias_for: <canonical>` (when applicable)
- `since: <version>` (introduction)

In capabilities. Agents reading the schema can build forward-compatible code.

---

## Anti-patterns

- **Don't** ship a breaking change without a deprecation path. Even "this is broken; we're fixing it" deserves a stage 0+1.
- **Don't** silently drop deprecated input (silent_fail). Always warn or error.
- **Don't** auto-correct destructive flags (e.g. `--force-delete-all` → `--force-recursive-delete`). Destructive ops require explicit canonical form; auto-correct only on non-destructive surfaces.
- **Don't** break capabilities schema without bumping `contract_version`. The whole agent ecosystem depends on the schema being stable.
- **Don't** remove a flag in the same release where you added the replacement. Users haven't had time to migrate.

---

## Test pinning the deprecation path

Add regression tests for each stage:

```bash
# audit/regression_tests/D-001__colour_to_color_stage_0.test.sh
# Stage 0: both --colour and --color produce the same output
out_old=$("$TOOL_BIN" list --colour 2>/dev/null)
out_new=$("$TOOL_BIN" list --color 2>/dev/null)
[ "$out_old" = "$out_new" ] || { echo "FAIL: stages must be identical in output" >&2; exit 1; }
```

```bash
# audit/regression_tests/D-001__colour_to_color_stage_1.test.sh
# Stage 1: --colour works AND emits warning
stderr=$("$TOOL_BIN" list --colour 2>&1 >/dev/null)
echo "$stderr" | grep -q "deprecated" || { echo "FAIL: stage 1 should emit deprecation warning" >&2; exit 1; }
```

The deprecation tests stay in `audit/regression_tests/` across stages; only the assertion changes.

---

## Communication

Whenever a deprecation lands:

1. Update CHANGELOG.md with the migration recipe
2. Update README.md if the flag/verb is documented there
3. Update `robot-docs guide` if the surface is mentioned
4. File a follow-up bead for the next stage's pass

Without these, the deprecation isn't really a deprecation — it's just a warning nobody sees.
