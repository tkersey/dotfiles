# Metrics Dashboard — what to measure, what to show

> "More readable" is not a metric. This file defines the exact numbers to track per refactor pass, how to compute them, and how to present them to the user and to reviewers.

## Contents

1. [The seven metrics](#the-seven-metrics)
2. [Per-metric: how to compute](#per-metric-how-to-compute)
3. [The dashboard template](#the-dashboard-template)
4. [CI integration](#ci-integration)
5. [Historical series](#historical-series)
6. [When metrics disagree](#when-metrics-disagree)

---

## The seven metrics

Any refactor pass reports these, before → after → Δ.

| # | Metric | Unit | Direction | Tool |
|---|--------|------|-----------|------|
| 1 | **LOC** (code only) | lines | ↓ good | tokei / scc |
| 2 | **Duplication index** | % cloned / kloc | ↓ good | jscpd, similarity-*, dupl |
| 3 | **Cyclomatic complexity** | mean, max | ↓ good | radon / gocyclo / lizard / clippy |
| 4 | **Coupling** | imports-in/out per module | ↓ good | `rg` counts / dep-cruiser / madge |
| 5 | **Test pass count** | integer | = required | native test runner |
| 6 | **Typecheck warnings** | integer | = required (not >) | clippy / tsc / mypy / vet |
| 7 | **Bundle size** (frontend) | gzipped KB | ↓ good or = | next build / webpack analyzer |

### Supplementary (when relevant)

| Metric | When | Tool |
|--------|------|------|
| **Property-test count** | refactors with prop tests | test framework |
| **Mutation score** | risk-critical code | Stryker / mutmut / cargo-mutants |
| **Perf smoke** | hot paths | hyperfine |
| **Benchmark** | perf-sensitive | criterion / benchstat |

---

## Per-metric: how to compute

### 1. LOC

```bash
tokei --output json . > loc_before.json
# after refactor
tokei --output json . > loc_after.json

# Delta
python3 - <<'EOF'
import json
b = json.load(open('loc_before.json'))['Total']['code']
a = json.load(open('loc_after.json'))['Total']['code']
print(f'LOC: {b} → {a}  (Δ {a-b}; {(a-b)/b*100:.2f}%)')
EOF
```

**What NOT to count:**
- Blank lines (tokei excludes by default)
- Comments (tokei excludes by default)
- Generated code (`target/`, `node_modules/`, etc. — exclude via `.tokeignore`)
- Test code counts separately; some refactors trade test LOC for invariant-expressed-as-type LOC. Both are fine.

### 2. Duplication index

`jscpd` reports a percentage; `similarity-*` reports pairs.

```bash
# jscpd — run for JS/TS
jscpd --min-tokens 50 --reporters json --output reports/jscpd src/
# parse: duplication % = total clone lines / total lines
jq '.statistics.total.percentage' reports/jscpd/jscpd-report.json

# similarity-ts — pair count
similarity-ts -p 80 src/ | grep -c '^\[Similarity'
```

The metric is: "what fraction of LOC exists as a near-duplicate elsewhere." 0% = no cloning; >15% is typically problematic.

### 3. Cyclomatic complexity

```bash
# Python
radon cc -a -s src/ | tail -1   # "Average complexity: B (4.2)"
radon cc -a -s src/ -j > cc_before.json

# Go
gocyclo -avg -over 10 . | head

# Rust — clippy has cognitive_complexity; proxy for cyclomatic
cargo clippy -- -W clippy::cognitive_complexity 2>&1 | grep -c warning

# TypeScript — via ESLint rule
npx eslint --rule 'complexity:[error,10]' --format json src/ \
  | jq '[.[] | .messages[]] | length'

# C/C++
lizard -X src/ > lizard.xml
grep -c '<function' lizard.xml    # function count as denominator
```

**Report:** mean complexity + p95 complexity. Max is an outlier; mean hides drift.

### 4. Coupling

Heuristic: count imports.

```bash
# Imports-out per file (Rust)
for f in $(find src -name '*.rs'); do
  n=$(rg '^use ' "$f" | wc -l)
  echo "$n $f"
done | sort -rn | head

# TypeScript
for f in $(find src -name '*.ts'); do
  n=$(rg '^import ' "$f" | wc -l)
  echo "$n $f"
done | sort -rn | head

# Better — dep-cruiser for TypeScript
npx depcruise --output-type json src > deps.json
jq '.summary.violations' deps.json
```

Better still: compute module-level fan-in / fan-out and track. High-fan-in utility modules are coupling magnets; this skill's pass should aim to break them up.

### 5. Test pass count

```bash
# Rust
cargo test 2>&1 | rg '^test result' | awk '{ok+=$4; fail+=$6; skip+=$8} END{printf "%d %d %d\n", ok, fail, skip}'

# Go
go test -json ./... 2>&1 | jq -rs '[.[] | select(.Action=="pass") | .Test] | length'

# Pytest
pytest --tb=no -q 2>&1 | tail -1     # e.g., "42 passed, 2 skipped"

# Vitest / Jest
pnpm test --reporter=json 2>/dev/null | jq '.numPassedTests'
```

**Compare** before and after. Exactness matters: "347 passed, 2 skipped" → "346 passed, 3 skipped" is a **fail** (a test silently started skipping).

### 6. Typecheck warnings

```bash
# Rust
cargo clippy --all-targets -- -D warnings 2>&1 | tee clippy.txt
# count warnings (not errors — those are gated)
grep -c '^warning:' clippy.txt

# TypeScript
tsc --noEmit 2>&1 | grep -c 'error TS'

# Python (mypy strict)
mypy --strict src/ 2>&1 | grep -c ': error:'

# Go
go vet ./... 2>&1 | wc -l
```

**Delta requirement:** `after ≤ before`. Never introduce new warnings in a refactor. Don't silence with `#[allow]` / `// eslint-disable` / `# noqa` / `# type: ignore` — that's a regression.

### 7. Bundle size

```bash
# Next.js
pnpm build
# parse .next/server/app-paths-manifest.json or use next/bundle-analyzer
npx next build --profile | grep 'First Load JS' | awk '{print $NF}'

# Vite / Rollup
pnpm build
find dist -name '*.js' -exec wc -c {} \; | awk '{s+=$1} END{print s/1024" KB"}'

# Better — gzipped
find dist -name '*.js' -exec gzip -c {} \; | wc -c | awk '{print $1/1024" KB gz"}'
```

A refactor that grows the bundle by > 5% is suspect — usually means imports pulled in more surface than expected.

---

## The dashboard template

Write to `refactor/artifacts/<run>/DASHBOARD.md`:

```markdown
# Refactor pass <run-id> — metrics dashboard

> Generated 2026-04-23T20:00Z after candidates D1–D5 landed.

## Summary

| Metric                 | Before    | After     | Δ           | Direction |
|------------------------|-----------|-----------|-------------|-----------|
| LOC (code only)        | 28,413    | 28,062    | **−351**    | ↓ ✅      |
| Duplication index      | 6.2%      | 3.8%      | −2.4 pp     | ↓ ✅      |
| Cyclomatic mean        | 4.2       | 3.9       | −0.3        | ↓ ✅      |
| Cyclomatic p95         | 18.0      | 16.0      | −2.0        | ↓ ✅      |
| Coupling (mean imp-out)| 9.7       | 8.4       | −1.3        | ↓ ✅      |
| Test pass count        | 342       | 342       | 0           | = ✅      |
| Typecheck warnings     | 0         | 0         | 0           | = ✅      |
| Bundle (gz, frontend)  | 142 KB    | 138 KB    | −4 KB       | ↓ ✅      |
| Property-test count    | 14        | 22        | +8          | ↑ (bonus) |
| Goldens identical      | —         | ✓         | —           | ✅        |

## Per-candidate contribution

| ID  | Title                              | LOC Δ | Complexity Δ | Bundle Δ  |
|-----|------------------------------------|-------|--------------|-----------|
| D1  | collapse 3× send_* → send(kind, …) | −79   | −0.8         | —         |
| D2  | <Button variant=…>                 | −121  | −0.3         | −4 KB     |
| D3  | #[derive(PartialEq)] × 3           | −16   | 0            | —         |
| D4  | CSV/TSV parser unify               | −85   | −0.5         | —         |
| D5  | useResource hook                   | −50   | 0            | —         |

## Risk & verification

| Gate                        | Result |
|-----------------------------|--------|
| All tests still pass        | ✅     |
| Goldens bit-identical       | ✅     |
| No new clippy warnings      | ✅     |
| LOC delta within predicted ±10% | ✅ (predicted −326; actual −351; +7.7%) |
| Perf smoke (hyperfine)      | p95 −1.2% (noise) |

## Remaining candidates (rejected, for future consideration)

| ID  | Reason rejected                      | Revisit when      |
|-----|--------------------------------------|-------------------|
| D6  | error-semantic divergence (Type IV)  | after error-type unification |
| D7  | accidental rhyme (bytes_to_kib)      | never (documented) |
| D11 | perf-sensitive; needs profiling first| after hot-path profile run |
```

---

## CI integration

Wire the dashboard into CI for every refactor PR:

```yaml
# .github/workflows/refactor-metrics.yml
name: Refactor metrics
on: [pull_request]
jobs:
  metrics:
    if: contains(github.head_ref, 'refactor/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Run metrics on base
        run: |
          git checkout ${{ github.base_ref }}
          ./scripts/metrics_snapshot.sh > base.json
      - name: Run metrics on HEAD
        run: |
          git checkout ${{ github.head_ref }}
          ./scripts/metrics_snapshot.sh > head.json
      - name: Compute delta + post PR comment
        uses: ./scripts/metrics_delta.py
        with:
          base: base.json
          head: head.json
          post_to_pr: true
```

The delta script posts a table comment on the PR. Reviewers see "LOC −351, complexity −0.3, no new warnings, bundle −4 KB" at a glance.

---

## Historical series

Keep a time-series JSON per project:
```
refactor/history/series.jsonl
```
Each line:
```json
{"ts":"2026-04-23T20:00Z","run_id":"2026-04-23-pass-1","loc":28062,"dup_pct":3.8,"cc_mean":3.9,"warnings":0,"bundle_kb":138}
```

Plot it with [interactive-visualization-creator](../../interactive-visualization-creator/SKILL.md) or even a simple gnuplot script. A project with a monotone-decreasing LOC + duplication trend is being tended to well.

---

## When metrics disagree

Occasionally:

- **LOC down, complexity up** — you removed helpers and inlined their bodies into a conditional. The resulting big function is worse to read. Reconsider.
- **LOC up, duplication down** — you added a properly-abstracted helper, but it's bigger than the sum of its replacements. Usually fine if complexity is also down.
- **LOC down, test count up** — you added property tests. Excellent; this is the virtuous ratio.
- **Bundle size up despite LOC down** — you switched to a library that inflates the bundle (e.g., replaced hand-rolled regex with a heavy dep). Audit.
- **Everything improved, perf regressed** — a Cow became an owned String somewhere; or an iterator got materialized. Profile.

No single metric is the target. The goal is **most metrics improve, others stay flat, none regress**.
