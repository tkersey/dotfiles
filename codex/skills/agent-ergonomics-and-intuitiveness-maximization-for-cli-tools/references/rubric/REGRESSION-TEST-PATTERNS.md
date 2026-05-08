# REGRESSION-TEST-PATTERNS — How to pin agent-ergonomic contracts

Each applied recommendation gets a regression test in `audit/regression_tests/R-NNN__<short>.test.{sh,rs,py,ts}`. This file shows the canonical patterns by dimension.

The test must:
1. Exit 0 on success, ≥1 on failure with a clear message naming the broken contract.
2. Be deterministic (no wall-clock, no network, no random).
3. Be runnable in CI without setup beyond the repo + a built binary.

---

## Pattern 1 — Pin `--help` text

For dimensions: agent_intuitiveness, ease_of_use, self_documentation.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-007__list_help_mentions_robot.test.sh
# Pins: <tool> list --help mentions --robot-list
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

if ! "$TOOL" list --help | grep -q -- '--robot-list'; then
  echo "REGRESSION: '<tool> list --help' no longer mentions --robot-list" >&2
  echo "Recommendation R-007 added --robot-list; --help must surface it." >&2
  exit 1
fi
echo "OK"
```

Rust equivalent (insta snapshot):
```rust
// tests/r007_list_help_robot.rs
use assert_cmd::Command;
use insta::assert_snapshot;

#[test]
fn list_help_mentions_robot() {
    let output = Command::cargo_bin("mytool").unwrap()
        .args(["list", "--help"])
        .output().unwrap();
    let stdout = String::from_utf8(output.stdout).unwrap();
    assert!(stdout.contains("--robot-list"),
        "list --help no longer mentions --robot-list (R-007)");
    assert_snapshot!(stdout);
}
```

---

## Pattern 2 — Pin exit-code dictionary

For dimensions: output_parseability, regression_resistance.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-014__exit_code_dictionary.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

# capabilities --json must include exit_codes for 0,1,2
got=$("$TOOL" capabilities --json | jq -r '.exit_codes | keys | sort | join(",")')
expected="0,1,2"
if [ "$got" != "$expected" ]; then
  echo "REGRESSION: exit_codes dictionary changed; got '$got', expected '$expected'" >&2
  echo "Recommendation R-014 pinned the exit-code dictionary; bump rubric_version if intentional." >&2
  exit 1
fi
echo "OK"
```

---

## Pattern 3 — Pin JSON schema for a verb's output

For dimensions: output_parseability, determinism, regression_resistance.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-022__list_json_schema.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

# list --json output must have keys: items[], total, ok
output=$("$TOOL" list --json)
echo "$output" | jq -e '.items | type == "array"' > /dev/null || {
  echo "REGRESSION: list --json '.items' is not an array" >&2; exit 1; }
echo "$output" | jq -e '.total | type == "number"' > /dev/null || {
  echo "REGRESSION: list --json '.total' is not a number" >&2; exit 1; }
echo "$output" | jq -e '.ok | type == "boolean"' > /dev/null || {
  echo "REGRESSION: list --json '.ok' is not a boolean" >&2; exit 1; }
echo "OK"
```

For Python (pytest):
```python
# tests/test_r022_list_json.py
import subprocess, json
def test_list_json_schema():
    out = subprocess.check_output(["mytool", "list", "--json"])
    data = json.loads(out)
    assert isinstance(data["items"], list), "list.items must be array"
    assert isinstance(data["total"], int), "list.total must be int"
    assert data["ok"] is True or data["ok"] is False, "list.ok must be bool"
```

---

## Pattern 4 — Pin error-message hints (intent inference)

For dimensions: error_pedagogy, intent_inference.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-007__levenshtein_typo_hint.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

# Typo --jsno should produce "did you mean --json?" hint on stderr
stderr=$("$TOOL" list --jsno 2>&1 >/dev/null) || true
if ! echo "$stderr" | grep -qE 'did you mean.*--json'; then
  echo "REGRESSION: --jsno typo no longer produces 'did you mean --json' hint" >&2
  echo "Recommendation R-007 added levenshtein-1 hint; restore it." >&2
  exit 1
fi
echo "OK"
```

---

## Pattern 5 — Pin stdout-data / stderr-diag separation

For dimensions: output_parseability, composability.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-031__stdout_data_only.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

# list --json --verbose: stdout must be valid JSON; stderr may have logs
stdout=$("$TOOL" list --json --verbose 2>/dev/null)
if ! echo "$stdout" | jq . > /dev/null 2>&1; then
  echo "REGRESSION: list --json --verbose produced invalid JSON on stdout" >&2
  echo "Verbose log lines must go to stderr, not stdout." >&2
  exit 1
fi
echo "OK"
```

---

## Pattern 6 — Pin determinism (byte-identical re-runs)

For dimensions: determinism, regression_resistance.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-040__list_deterministic.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

# Re-run produces same output (modulo known volatile fields)
out1=$("$TOOL" list --json)
out2=$("$TOOL" list --json)

# Strip known volatile fields if any (request_id, ts)
norm() { jq 'del(.meta.request_id, .meta.ts)' <<< "$1"; }
n1=$(norm "$out1"); n2=$(norm "$out2")

if [ "$n1" != "$n2" ]; then
  echo "REGRESSION: list --json output not deterministic across re-runs" >&2
  diff <(echo "$n1") <(echo "$n2") >&2
  exit 1
fi
echo "OK"
```

---

## Pattern 7 — Pin NO_COLOR / non-TTY behavior

For dimensions: composability.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-051__no_color.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

# NO_COLOR=1 must suppress ANSI escapes on stdout
out=$(NO_COLOR=1 "$TOOL" list)
if echo "$out" | grep -qE $'\x1b\['; then
  echo "REGRESSION: NO_COLOR=1 ignored; ANSI escapes still in stdout" >&2
  exit 1
fi

# Piped stdout must also suppress (TTY-detect)
out=$("$TOOL" list | cat)
if echo "$out" | grep -qE $'\x1b\['; then
  echo "REGRESSION: piped stdout still has ANSI escapes" >&2
  exit 1
fi
echo "OK"
```

---

## Pattern 8 — Pin dangerous-op gate

For dimensions: safety_with_recovery.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-060__delete_requires_yes.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"
TMPSTORE=$(mktemp -d)

# Without --yes: must refuse (non-zero exit; preserves state)
"$TOOL" --store "$TMPSTORE" delete item1 2>/dev/null
if [ $? -eq 0 ]; then
  echo "REGRESSION: 'delete' ran without --yes; safety gate broken" >&2
  exit 1
fi

# With --dry-run: should print plan; not mutate
"$TOOL" --store "$TMPSTORE" delete item1 --dry-run > /tmp/plan
[ -s /tmp/plan ] || { echo "REGRESSION: --dry-run produced no plan" >&2; exit 1; }

# State should be unchanged after --dry-run
[ ! -e "$TMPSTORE/item1.deleted" ] || { echo "REGRESSION: --dry-run actually deleted" >&2; exit 1; }

rm -rf "$TMPSTORE"
echo "OK"
```

---

## Pattern 9 — Pin capabilities contract

For dimensions: self_documentation, regression_resistance.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-070__capabilities_contract.test.sh
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"

caps=$("$TOOL" capabilities --json)
required_keys=(version contract_version features commands exit_codes env_vars)
for key in "${required_keys[@]}"; do
  echo "$caps" | jq -e ".$key" > /dev/null || {
    echo "REGRESSION: capabilities --json missing required key '$key'" >&2
    exit 1
  }
done
echo "OK"
```

---

## Pattern 10 — Pin agent-canonical-task transcript

For overall agent-ergonomic regression coverage. This is the most valuable pattern: it tests the actual end-to-end agent flow.

```bash
#!/usr/bin/env bash
# audit/regression_tests/R-080__canonical_task_init_then_add.test.sh
# Simulates an agent doing the canonical task: init → add → list
set -euo pipefail
TOOL="${TOOL_BIN:-./target/release/mytool}"
TMPSTORE=$(mktemp -d)

# Step 1: init
"$TOOL" --store "$TMPSTORE" init --json > /tmp/init.json
jq -e '.ok == true' /tmp/init.json > /dev/null || { echo "init failed" >&2; exit 1; }

# Step 2: add
"$TOOL" --store "$TMPSTORE" add foo --json > /tmp/add.json
jq -e '.ok == true and .id != null' /tmp/add.json > /dev/null || { echo "add failed" >&2; exit 1; }

# Step 3: list
list_count=$("$TOOL" --store "$TMPSTORE" list --json | jq '.items | length')
[ "$list_count" -eq 1 ] || { echo "list returned wrong count: $list_count" >&2; exit 1; }

rm -rf "$TMPSTORE"
echo "OK"
```

---

## Pattern selection matrix

For each rec, pick the pattern that matches the failing dimension(s):

| Failing dim | Default pattern | Optional add-on |
|-------------|-----------------|------------------|
| agent_intuitiveness | Pattern 1 (--help text) | Pattern 10 (canonical task) |
| agent_ergonomics | Pattern 10 (canonical task) | Pattern 1 |
| agent_ease_of_use | Pattern 1 + Pattern 9 | |
| output_parseability | Pattern 3 (JSON schema) | Pattern 5 (stdout/stderr) |
| error_pedagogy | Pattern 4 (error hint) | |
| intent_inference | Pattern 4 (typo hint) | |
| safety_with_recovery | Pattern 8 (dangerous-op gate) | |
| determinism | Pattern 6 (byte-identical) | |
| self_documentation | Pattern 9 (capabilities) | Pattern 1 |
| composability | Pattern 5 + Pattern 7 (NO_COLOR) | |
| regression_resistance | meta — every pattern contributes | |

---

## Test naming convention

`audit/regression_tests/R-<NNN>__<short_description>.test.{sh,rs,py,ts}`

- `R-NNN`: matches the recommendation_id.
- `<short_description>`: snake_case, lowercase, ≤ 30 chars.
- Extension matches the project's idiom (default `.sh`).

Example: `R-007__levenshtein_typo_hint.test.sh`.

---

## CI integration

Add to the project's CI:

```yaml
# .github/workflows/agent-ergonomics-regression.yml
- name: Build the binary
  run: cargo build --release  # or go build, npm run build, etc.

- name: Run agent-ergonomics regression tests
  run: |
    export TOOL_BIN="$(pwd)/target/release/mytool"
    for t in audit/regression_tests/R-*.test.sh; do
      echo "Running $t"
      bash "$t" || { echo "FAIL: $t"; exit 1; }
    done
    # For Rust:
    cargo test --tests
```

This is the *drift-guard*. Every PR runs these tests; any regression is caught at PR time.
