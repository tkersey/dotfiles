# SCHEMA-EVOLUTION — Versioning capabilities + tool contracts safely

A tool's `capabilities --json` and `--robot-*` schemas are the agent contract. Once shipped, agents depend on them. This file gives the patterns for evolving those schemas without breaking the ecosystem.

---

## Three classes of change

### Additive (always safe)

- Adding a new optional field to capabilities
- Adding a new verb (with backwards-compat for old capabilities readers)
- Adding a new optional flag
- Adding a new exit code (only for new conditions; existing exit codes unchanged)
- Adding a new env var
- Adding a new feature to the `features` array

**No deprecation needed.** Agents reading old capabilities ignore new fields.

### Renaming (deprecation needed)

- Renaming a verb
- Renaming a flag
- Renaming an env var
- Renaming a JSON output key
- Renaming an exit code's semantic meaning

**Use DEPRECATION-PATTERNS.md.** Both names work for ≥ 1 release; old emits warning; eventually removed.

### Breaking (major version bump)

- Removing a verb
- Removing a flag
- Reusing an exit code for a different meaning
- Changing a default behavior
- Changing the output schema's structure (e.g. moving fields around)

**Bump `contract_version` from "1" → "2".** Agents reading `meta.contract_version` know to use compat path.

---

## `contract_version` semantics

Always present in `capabilities` AND `meta.contract_version` per `--json` response:

| Change type | Increment |
|-------------|-----------|
| Additive | "1" → "1.1" (minor; optional) |
| Renaming, with deprecation | "1.1" → "1.2" (minor) |
| Breaking | "1" → "2" (major) |

Agents check `contract_version` major-version compatibility:

```python
caps = json.loads(subprocess.check_output(["mytool", "capabilities", "--json"]))
major = int(caps["contract_version"].split(".")[0])
if major != 1:
    raise NotImplementedError(f"agent supports contract v1; tool ships v{major}")
```

---

## Capabilities pinning across versions

`audit/regression_tests/capabilities-golden.json` pins the schema. The golden file lives in the repo:

```bash
audit/regression_tests/
├── capabilities-golden.json           # pinned at contract_version "1"
└── R-001__capabilities_contract.test.sh
```

The test:

```bash
got=$("$TOOL" capabilities --json | jq -S .)
want=$(cat audit/regression_tests/capabilities-golden.json | jq -S .)
diff <(echo "$got") <(echo "$want") || {
  echo "REGRESSION: capabilities drifted; bump contract_version OR re-pin golden" >&2
  exit 1
}
```

When you intentionally bump `contract_version`:

1. Update the schema in source
2. Bump `contract_version`
3. Re-pin: `<tool> capabilities --json | jq -S . > audit/regression_tests/capabilities-golden.json`
4. Document the change in `CHANGELOG.md`
5. The test re-passes

---

## Versioning per verb

Each verb's output schema can have its own contract version:

```jsonc
{
  "commands": {
    "list": {
      "description": "...",
      "json": true,
      "schema_version": "2",          // verb-level; allows independent evolution
      "output_schema": { ... }
    }
  }
}
```

`meta.schema_version` per response:

```jsonc
{
  "ok": true,
  "data": { "items": [...] },
  "meta": {
    "tool_version":     "0.4.1",
    "contract_version": "1",                  // tool-level
    "schema_version":   "2"                   // verb-level
  }
}
```

Agents can branch on either.

---

## Backward-compatible additions to existing JSON output

Adding fields:

```jsonc
// Before (schema_version: "1")
{"data": {"items": [{"id": "X-001", "title": "..."}]}}

// After (schema_version: "1" — still backward-compat; just additive)
{"data": {"items": [{"id": "X-001", "title": "...", "tags": ["foo"]}]}}
```

Old agents ignore `tags`. New agents use it. No version bump needed.

Removing or renaming fields requires schema_version bump.

---

## Old-version client support

For wide-deployed CLIs, support old contract versions for ≥ 6 months:

```bash
# Default behavior (current contract_version)
$ mytool list --json
{"meta": {"contract_version": "2"}, ...}

# Force old contract version (compat mode)
$ mytool list --json --contract-version=1
{"meta": {"contract_version": "1"}, ...}
```

The `--contract-version=N` flag forces the tool to emit the old envelope. After 6 months, ship a deprecation warning when this flag is used. After 12 months, remove the compat path.

For `capabilities --json`:

```bash
$ mytool capabilities --json --contract-version=1
# returns the v1 schema
```

This is the pattern that lets the ecosystem migrate gradually.

---

## Schema migration tools

For non-trivial schema changes, ship a migration script:

```bash
$ mytool migrate-output --from=1 --to=2 < old-output.json > new-output.json
```

Old downstream pipelines:

```bash
# Old: mytool list --json | downstream-tool
# Migrated:
mytool list --json | mytool migrate-output --from=1 --to=2 | downstream-tool
```

Eventually the downstream tool will be updated to consume the new schema directly.

---

## Pre-1.0 schema discipline

Before v1.0, schema changes are expected. Conventions:

- Document in CHANGELOG that `contract_version` MAY change at any pre-1.0 release.
- Use `contract_version: "0.x"` semver to signal pre-stability.
- Don't promise backward-compat across minor versions.
- Once v1.0 ships, lock the contract.

This is honest about pre-1.0 churn while still giving agents *a* contract to depend on.

---

## CHANGELOG entries for schema changes

Every schema change needs a CHANGELOG entry:

```markdown
## v0.5.0

### Breaking changes (contract_version 1 → 2)

- The `list --json` output schema changed:
  - `data.items[].labels` (array) is now `data.items[].tags` (array)
  - `data.results` (deprecated alias for `data.items`) removed
- Migration: `sed -i 's/\.labels/.tags/g; s/\.results/.items/g' your-script.sh`
- Compat mode: `mytool list --json --contract-version=1` emits old schema (deprecated; removed in v0.7.0)

### Additive (contract_version 2 → 2.1)

- New `data.items[].priority` field (integer 0-9)
- New env var: `MYTOOL_DEFAULT_PRIORITY` (default: 5)
```

The CHANGELOG IS the migration documentation. Without it, agents can't follow the bumps.

---

## Detecting schema regressions in CI

`CI-INTEGRATION.md` includes the capabilities schema-pin check. Add per-verb schema pins:

```bash
# audit/regression_tests/SCHEMA-list.test.sh
got=$("$TOOL" list --json --limit=1 | jq 'del(.meta.request_id, .meta.ts_iso, .meta.elapsed_ms, .data.items[]._hash)')
want=$(cat audit/regression_tests/list-golden.json | jq 'del(.meta.request_id, .meta.ts_iso, .meta.elapsed_ms, .data.items[]._hash)')
diff <(echo "$got" | jq -S .) <(echo "$want" | jq -S .)
```

Strip volatile fields (request_id, ts_iso, etc.) before comparing.

---

## Old version detection / fallback

Agents can detect tool version + adapt:

```python
import json, subprocess

def get_capabilities():
    out = subprocess.check_output(["mytool", "capabilities", "--json"])
    return json.loads(out)

caps = get_capabilities()
contract = caps["contract_version"].split(".")[0]
verbs = caps["commands"]

# Branch on contract version
if contract == "1":
    # use v1 logic
    pass
elif contract == "2":
    # use v2 logic; check for new features
    if "new_feature" in caps["features"]:
        # use it
        pass
else:
    # contract version we don't know
    raise NotImplementedError(f"unsupported contract {contract}")
```

This is what the agent-facing schema is FOR — letting agents detect + adapt.

---

## Anti-patterns

- **Silent schema changes.** Adding a new required field without documenting → breaks agents.
- **Reusing exit codes.** "Exit 1 used to mean X; now means Y" → unknowable from outside without docs.
- **Renaming without deprecation.** "Old name silently dropped" → agents using old name silent_fail.
- **Bumping contract_version on additive changes only.** Major bumps should be reserved for actual breakage; over-bumping causes alert fatigue.
- **Removing the compat-mode flag too soon.** 6+ months of `--contract-version=N` is the minimum.
- **Keeping multiple compat versions forever.** After 12 months, remove the old path. Don't accumulate dead code.

---

## Related

- `methodology/DEPRECATION-PATTERNS.md` — the four-stage rollout
- `methodology/JSON-SCHEMA-PATTERNS.md` — universal envelope + per-verb schemas
- `methodology/CI-INTEGRATION.md` — drift-guard tests
- `methodology/HOOKS-INTEGRATION.md` — pre-commit drift-guard
