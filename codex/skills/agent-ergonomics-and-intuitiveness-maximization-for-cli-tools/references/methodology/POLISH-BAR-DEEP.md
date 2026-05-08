# POLISH-BAR-DEEP — Deep verification queries for the 12 Polish Bar rows

POLISH-BAR.md gives the 12 non-negotiables. This file gives the DEEP verification queries — the exact bash invocations + JSON jq paths + expected outcomes for each row.

Use during Phase 6 / Phase 8 to verify Polish Bar compliance with mechanical precision.

---

## Row 1 — First-try success (DEEP)

### Verification

```bash
TOOL_BIN="${TOOL_BIN}"
violations=()

# Subtest 1.1: bare invocation produces useful output (or exits cleanly with help pointer)
out=$(timeout 2 "$TOOL_BIN" </dev/null 2>&1) || ec=$?
if [ "${ec:-0}" -eq 124 ]; then
  violations+=("bare invocation timed out (likely TUI launch in non-TTY)")
fi
if [ -z "$out" ] && [ "${ec:-0}" -eq 0 ]; then
  violations+=("bare invocation silent_fail: exit 0, no output")
fi

# Subtest 1.2: --help in 2s
timeout 2 "$TOOL_BIN" --help > /dev/null 2>&1 || violations+=("--help slow or crashed")

# Subtest 1.3: -h works
timeout 2 "$TOOL_BIN" -h > /dev/null 2>&1 || violations+=("-h slow or crashed")

# Subtest 1.4: help (subcommand) works
timeout 2 "$TOOL_BIN" help > /dev/null 2>&1 || violations+=("'help' subcommand slow or crashed")

# Subtest 1.5: --version works
timeout 2 "$TOOL_BIN" --version > /dev/null 2>&1 || violations+=("--version slow or crashed")

if [ ${#violations[@]} -gt 0 ]; then
  echo "Row 1 FAIL:"
  printf '  %s\n' "${violations[@]}"
  exit 1
fi
echo "Row 1 PASS"
```

### Pass criteria

- All 5 subtests succeed within 2 seconds
- Bare invocation produces stdout OR informative stderr
- No subtest launches a TUI in non-TTY context

### Fix-pointer if FAIL

- If TUI launches: detect non-TTY, emit guidance ("use --json"), exit non-zero
- If silent_fail on bare: print first line of `--help` to stderr; exit 0
- If slow: profile; quick-reject filter

---

## Row 2 — JSON everywhere (DEEP)

### Verification

```bash
caps=$("$TOOL_BIN" capabilities --json 2>/dev/null) || { echo "Row 2 FAIL: no capabilities"; exit 1; }

# Get list of read-side verbs (mutates: false)
read_verbs=$(echo "$caps" | jq -r '.commands | to_entries[] | select(.value.mutates == false) | .key')

# For each read-side verb, verify --json works
violations=()
for v in $read_verbs; do
  out=$("$TOOL_BIN" $v --json 2>/dev/null)
  if ! echo "$out" | jq . > /dev/null 2>&1; then
    violations+=("$v --json doesn't produce valid JSON")
  fi
done

[ ${#violations[@]} -gt 0 ] && { printf '  %s\n' "${violations[@]}"; exit 1; }
echo "Row 2 PASS"
```

### Pass criteria

Every read-side verb's `--json` mode produces valid JSON.

---

## Row 3 — Capabilities endpoint (DEEP)

### Verification

```bash
caps=$("$TOOL_BIN" capabilities --json 2>/dev/null) || { echo "Row 3 FAIL: no capabilities --json"; exit 1; }

# Required keys
for k in version contract_version features commands exit_codes env_vars; do
  if ! echo "$caps" | jq -e ".$k" > /dev/null 2>&1; then
    echo "Row 3 FAIL: capabilities missing required key '.$k'"
    exit 1
  fi
done

# Type checks
echo "$caps" | jq -e '.version | type == "string"' > /dev/null      || { echo "FAIL: .version not string"; exit 1; }
echo "$caps" | jq -e '.contract_version | type == "string"' > /dev/null || { echo "FAIL: .contract_version not string"; exit 1; }
echo "$caps" | jq -e '.features | type == "array"' > /dev/null      || { echo "FAIL: .features not array"; exit 1; }
echo "$caps" | jq -e '.commands | type == "object"' > /dev/null     || { echo "FAIL: .commands not object"; exit 1; }
echo "$caps" | jq -e '.exit_codes | type == "object"' > /dev/null   || { echo "FAIL: .exit_codes not object"; exit 1; }
echo "$caps" | jq -e '.env_vars | type == "object"' > /dev/null     || { echo "FAIL: .env_vars not object"; exit 1; }

echo "Row 3 PASS"
```

---

## Row 4 — Robot-docs endpoint (DEEP)

### Verification

```bash
out=$("$TOOL_BIN" robot-docs guide 2>&1) || \
out=$("$TOOL_BIN" --robot-help 2>&1) || \
{ echo "Row 4 FAIL: no robot-docs guide / --robot-help"; exit 1; }

lines=$(echo "$out" | wc -l)
[ "$lines" -gt 80 ] && echo "Row 4 WARN: handbook is $lines lines (>80; consider trimming)"

# Required mentions
for required in '--json' 'capabilities' 'exit'; do
  echo "$out" | grep -qi "$required" || echo "Row 4 WARN: handbook doesn't mention '$required'"
done

echo "Row 4 PASS"
```

---

## Row 5 — Mega-command (DEEP)

### Verification

```bash
# Try common mega-command patterns
mega_outputs=()
"$TOOL_BIN" --robot-triage 2>/dev/null | jq . >/dev/null 2>&1 && mega_outputs+=("--robot-triage")
"$TOOL_BIN" --robot-overview 2>/dev/null | jq . >/dev/null 2>&1 && mega_outputs+=("--robot-overview")
"$TOOL_BIN" status --json 2>/dev/null    | jq . >/dev/null 2>&1 && mega_outputs+=("status --json")
"$TOOL_BIN" doctor --json 2>/dev/null    | jq . >/dev/null 2>&1 && mega_outputs+=("doctor --json")

if [ ${#mega_outputs[@]} -eq 0 ]; then
  echo "Row 5 FAIL: no mega-command found"
  exit 1
fi

# For the first mega-command found, verify it returns multiple slices + commands field
mega="${mega_outputs[0]}"
out=$("$TOOL_BIN" $mega 2>/dev/null)

# Check has ≥ 3 top-level keys
top_level=$(echo "$out" | jq 'keys | length')
[ "$top_level" -lt 3 ] && echo "Row 5 WARN: mega-command returns only $top_level top-level keys (expected ≥ 3)"

# Check has commands field
echo "$out" | jq -e '.commands or .data.commands' > /dev/null || \
  echo "Row 5 WARN: mega-command lacks 'commands' field with paste-ready follow-ups"

echo "Row 5 PASS (using $mega)"
```

---

## Row 6 — Exit-code contract (DEEP)

### Verification

```bash
caps=$("$TOOL_BIN" capabilities --json)
exit_codes=$(echo "$caps" | jq -r '.exit_codes | keys | join(" ")')

# Verify each documented code is reachable in source (best-effort)
violations=()
for ec in $exit_codes; do
  if ! grep -rqE "exit\\(\\s*$ec|ExitCode::$ec|process\\.exit\\($ec|os\\.Exit\\($ec" "$TARGET" 2>/dev/null; then
    violations+=("documented exit $ec not found in source")
  fi
done

# Verify exit 0 only used for success
src_exit_0=$(grep -rE 'exit\(0\)|ExitCode::Success|process\.exit\(0\)' "$TARGET" 2>/dev/null | wc -l)
[ "$src_exit_0" -lt 1 ] && violations+=("no exit(0) found; suspicious")

if [ ${#violations[@]} -gt 0 ]; then
  printf '  %s\n' "${violations[@]}"
  exit 1
fi
echo "Row 6 PASS"
```

---

## Row 7 — Error pedagogy (DEEP)

### Verification

```bash
# Sample 5 random useless_error entries from intent corpus
violations=()
sample=$(jq -c 'select(.classification == "useless_error")' audit/intent_inference_corpus.jsonl | shuf -n 5)

while IFS= read -r row; do
  inv=$(echo "$row" | jq -r '.invocation')
  stderr=$($inv 2>&1 >/dev/null)

  # Should now be useful_hint after Phase 5 fixes
  if ! echo "$stderr" | grep -qiE 'did you mean|use [`'"'"']?-{1,2}|alternative|see:|try '; then
    violations+=("$inv still useless_error: '$stderr'")
  fi
done <<< "$sample"

[ ${#violations[@]} -gt 0 ] && { printf '  %s\n' "${violations[@]}"; exit 1; }
echo "Row 7 PASS"
```

---

## Row 8 — Intent inference (DEEP)

### Verification

```bash
# For each known flag, try a 1-edit-distance typo
violations=()

for flag in $(echo "$caps" | jq -r '.commands | to_entries[] | .value.flags // [] | .[] | .name'); do
  flag_clean="${flag#--}"
  [ "${#flag_clean}" -lt 3 ] && continue   # skip short flags (typos too-common)
  
  # Insert a typo: drop the second-to-last char
  typo="${flag_clean:0:-2}${flag_clean: -1}"
  out=$("$TOOL_BIN" --$typo 2>&1) || true
  
  if echo "$out" | grep -qiE 'did you mean|--'$flag_clean; then
    : # OK — useful hint
  else
    violations+=("typo '--$typo' didn't suggest '--$flag_clean'")
  fi
done

[ ${#violations[@]} -gt 5 ] && { printf '  %s\n' "${violations[@]:0:5}" "..."; exit 1; }
echo "Row 8 PASS (or partial)"
```

---

## Row 9 — Dangerous-op gating (DEEP)

### Verification

```bash
violations=()

mutating_verbs=$(echo "$caps" | jq -r '.commands | to_entries[] | select(.value.mutates == true) | .key')

for v in $mutating_verbs; do
  vh=$("$TOOL_BIN" $v --help 2>&1)
  
  # Must support --yes (or --force or --confirm)
  if ! echo "$vh" | grep -qE -- '--yes|--force|--confirm'; then
    violations+=("$v lacks --yes/--force/--confirm")
  fi
  
  # Must support --dry-run
  if ! echo "$vh" | grep -qE -- '--dry-run|--plan'; then
    violations+=("$v lacks --dry-run/--plan")
  fi
done

[ ${#violations[@]} -gt 0 ] && { printf '  %s\n' "${violations[@]}"; exit 1; }
echo "Row 9 PASS"
```

---

## Row 10 — Determinism (DEEP)

### Verification

```bash
export SOURCE_DATE_EPOCH=1234567890

run1=$("$TOOL_BIN" list --json 2>/dev/null)
run2=$("$TOOL_BIN" list --json 2>/dev/null)

# Strip volatile fields
norm() {
  jq 'walk(if type=="object" then del(.meta.request_id, .meta.ts_iso, .meta.elapsed_ms, .request_id, .timestamp) else . end)' <<< "$1"
}

n1=$(norm "$run1"); n2=$(norm "$run2")
if [ "$n1" != "$n2" ]; then
  echo "Row 10 FAIL: output differs across re-runs"
  diff <(echo "$n1") <(echo "$n2") | head -20
  exit 1
fi

echo "Row 10 PASS"
```

---

## Row 11 — NO_COLOR / CI / non-TTY (DEEP)

### Verification

```bash
violations=()

# Pipe must strip ANSI
out=$("$TOOL_BIN" list 2>/dev/null | cat)
if echo "$out" | grep -qE $'\x1b\['; then
  violations+=("ANSI in piped stdout")
fi

# NO_COLOR=1
out=$(NO_COLOR=1 "$TOOL_BIN" list 2>/dev/null)
if echo "$out" | grep -qE $'\x1b\['; then
  violations+=("NO_COLOR=1 ignored")
fi

# CI=true
out=$(CI=true "$TOOL_BIN" list 2>/dev/null)
if echo "$out" | grep -qE $'\x1b\['; then
  violations+=("CI=true ignored")
fi

# TERM=dumb
out=$(TERM=dumb "$TOOL_BIN" list 2>/dev/null)
if echo "$out" | grep -qE $'\x1b\['; then
  violations+=("TERM=dumb ignored")
fi

[ ${#violations[@]} -gt 0 ] && { printf '  %s\n' "${violations[@]}"; exit 1; }
echo "Row 11 PASS"
```

---

## Row 12 — Regression test (DEEP)

### Verification

```bash
violations=()

# Every applied:true rec has a regression test
applied_rids=$(jq -r 'select(.applied == true) | .recommendation_id' audit/recommendations.jsonl 2>/dev/null)

for rid in $applied_rids; do
  if ! ls "audit/regression_tests/${rid}__"*.test.* >/dev/null 2>&1; then
    violations+=("$rid: no regression test")
  fi
done

# Every regression test passes
for t in audit/regression_tests/R-*.test.sh; do
  bash "$t" >/dev/null 2>&1 || violations+=("$t fails")
done

[ ${#violations[@]} -gt 0 ] && { printf '  %s\n' "${violations[@]}"; exit 1; }
echo "Row 12 PASS"
```

---

## Aggregate Polish Bar verifier

```bash
#!/usr/bin/env bash
# audit/scripts/verify-polish-bar.sh — verify all 12 rows
set -euo pipefail

violations=()
for row in 1 2 3 4 5 6 7 8 9 10 11 12; do
  if ! bash "audit/scripts/verify-polish-bar-row-$row.sh" 2>&1 | tail -1 | grep -q "PASS"; then
    violations+=("Row $row")
  fi
done

if [ ${#violations[@]} -gt 0 ]; then
  echo "Polish Bar FAIL on rows: ${violations[*]}"
  exit 1
fi
echo "Polish Bar PASS (all 12 rows)"
```

---

## Row weighting

Some rows are more critical than others:

| Row | Weight | Critical |
|-----|--------|----------|
| 1 First-try | × 2 | Critical |
| 2 JSON everywhere | × 1.5 | High |
| 3 Capabilities | × 1.5 | High |
| 4 Robot-docs | × 1.0 | Medium |
| 5 Mega-command | × 1.5 | High |
| 6 Exit-code contract | × 2 | Critical |
| 7 Error pedagogy | × 2 | Critical |
| 8 Intent inference | × 1.0 | Medium |
| 9 Dangerous-op gating | × 2 | Critical |
| 10 Determinism | × 1.5 | High |
| 11 NO_COLOR | × 1.5 | High |
| 12 Regression test | × 1.0 | Medium (per-rec) |

Failing a "Critical" row blocks the audit's release recommendation. Failing "High" rows generates P1 recs. Failing "Medium" generates P2 recs.

---

## When the bar can be relaxed

For:
- Tools that target only humans (no agent use case at all) — but this is rare
- Internal one-off scripts — relax rows 4, 5, 8 (no capabilities, no robot-docs needed)
- Strict legacy compatibility - some rows may have phase 0 → 1 → 2 deprecation paths

Always document relaxations in `phase0_scope_decision.md` so they're auditable.

---

## Cross-references

- `methodology/POLISH-BAR.md` — the 12 rows summary (top-level)
- `methodology/JSON-SCHEMA-PATTERNS.md` — for Row 2 + 3 + 10 details
- `methodology/ERROR-REWRITING-COOKBOOK.md` — for Row 7 detail
- `methodology/CRASH-RECOVERY-AND-RESUMABILITY.md` — for Row 9 detail
- `methodology/OBSERVABILITY-AND-TELEMETRY-SURFACES.md` — for Row 11 detail
- `references/rubric/REGRESSION-TEST-PATTERNS.md` — for Row 12 detail
