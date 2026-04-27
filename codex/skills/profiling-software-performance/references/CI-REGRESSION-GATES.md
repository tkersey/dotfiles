# CI Performance-Regression Gates

> How to turn `BUDGETS.md` into a pull-request gate that blocks regressions. Covers runner selection, baseline maintenance, comparison tooling, and the nightly cross-filesystem matrix.

## Contents

1. [Why CI perf gates](#why-ci-perf-gates)
2. [Runner match — the #1 false-regression cause](#runner-match--the-1-false-regression-cause)
3. [Architecture of a gate](#architecture-of-a-gate)
4. [Per-language wiring](#per-language-wiring)
5. [Baseline management strategy](#baseline-management-strategy)
6. [Budget comparison](#budget-comparison)
7. [PR comments and artifacts](#pr-comments-and-artifacts)
8. [Nightly matrix (cross-FS, cross-OS)](#nightly-matrix-cross-fs-cross-os)
9. [Hosted services](#hosted-services)
10. [Self-hosted runners for expensive benches](#self-hosted-runners-for-expensive-benches)
11. [False-positive triage](#false-positive-triage)
12. [Sample workflow files](#sample-workflow-files)

---

## Why CI perf gates

Without a gate:
- Regressions accrue silently, one 1% at a time
- The campaign ledger (see CASE-STUDIES.md §Case 6) has no immune system
- Reverts require forensic analysis (which commit regressed?) instead of automatic detection

With a gate:
- PR author sees the regression during review, not after merge
- Cumulative budgets are enforced — you can't give back what previous rounds earned
- Artifact trail (flamegraph, span_summary, fingerprint) captured on every perf-touching PR

The gate is NOT a substitute for local profiling. It's the safety net.

---

## Runner match — the #1 false-regression cause

**Before any gate talks about thresholds**, answer: does the CI runner match the reference host in `fingerprint.json`?

Axes that matter:
- CPU model (GitHub default is Intel/AMD shared; may differ across runs)
- CPU count (2-core GitHub free vs 64-core self-hosted)
- RAM (7 GB vs 256 GB)
- Kernel major version (Ubuntu 22 vs 25)
- Filesystem (ext4 vs overlayfs on Docker)
- CPU governor (governor=powersave on GitHub, governor=performance on a tuned self-hosted)
- Turbo / SMT / thermals (GitHub may throttle; self-hosted may be pinned)

**If the CI runner doesn't match the reference host, the gate is comparing apples to oranges.**

Options:
1. **Match the runner to the reference host** (self-hosted). Expensive, reliable.
2. **Have a CI-class reference host** and a prod-class reference host, each with its own BUDGETS.md row. Cheap, requires discipline.
3. **Use a hosted perf service** (codspeed, bencher.dev) that runs their own matched hardware.

### Document the runner in BUDGETS.md

```markdown
## Hardware + Environment Baseline

### Production reference host
- CPU: AMD Ryzen Threadripper PRO 5995WX, 64 cores / 128 threads, governor=performance
- Storage: /data -> btrfs on Samsung SSD 9100 PRO 4TB NVMe
- Kernel: Linux 6.17.0-19-generic
- [full fingerprint.json link]

### CI runner (GitHub Actions, `ubuntu-latest` x64)
- CPU: varies (Intel Xeon or AMD EPYC, 4 vCPU)
- Storage: /tmp on overlayfs over ext4 over cloud disk
- Kernel: 5.15+
- Governor: cannot be set on shared runners (powersave typical)
- **Budgets must be looser here** — typical 1.5-3× the reference host for same workload

### CI runner (self-hosted, matches reference host)
- same as production reference host
- full budgets apply unmodified
```

---

## Architecture of a gate

```
┌───────────────────────────────────────────────────────────────┐
│ PR trigger                                                     │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. Check out PR branch                                         │
│ 2. Capture fingerprint.json                                    │
│ 3. Run bench_baseline.sh (or equivalent)                       │
│ 4. Output: pr.json (hyperfine / criterion / benchstat format)  │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. Download main branch baseline artifact (main.json)          │
│ 2. Verify fingerprints match → else skip or annotate advisory  │
│ 3. Compare pr.json vs main.json per bench                      │
│ 4. Each bench: pass / warn / fail                              │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. Upload artifacts (pr.json, flamegraph.svg, span_summary)   │
│ 2. Post PR comment with table, deltas, artifact URLs           │
│ 3. Set status: green/yellow/red                                │
│ 4. Fail the check if any bench exceeds threshold               │
└───────────────────────────────────────────────────────────────┘
```

Thresholds (from CASE-STUDIES.md §Case 10 and BUDGETS.md convention):
- `|Δ| ≤ 3%` → pass (within criterion `noise_threshold`)
- `3% < |Δ| ≤ 10%` → warn (annotate PR; don't block)
- `|Δ| > 10%` → fail for regressions; celebrate for improvements

Use statistical test (non-overlapping CI at p < 0.05) in addition to raw Δ.

---

## Per-language wiring

### Rust + Criterion

```yaml
- name: Bench main
  run: |
    git checkout main
    cargo bench -p mycrate --bench my_bench -- --save-baseline main
    git checkout -

- name: Bench PR
  run: cargo bench -p mycrate --bench my_bench -- --baseline main

- name: Check regression
  run: |
    # Criterion prints "Performance has regressed" on stderr for >noise changes
    if grep -q "Performance has regressed" bench.log; then exit 1; fi
```

Alternative with `cargo criterion` (Canonical CI runner):
```bash
cargo install cargo-criterion
cargo criterion --message-format=json > pr.json
# Compare with main.json (previously saved)
cargo-criterion compare --threshold 10% main.json pr.json
```

### Rust + iai-callgrind

Deterministic instruction counts — no statistical noise. Perfect for CI.

```yaml
- name: Bench
  run: cargo bench --bench iai_bench

- name: Check instruction count regression
  run: |
    diff target/iai/main.out target/iai/pr.out || exit 1
```

Tradeoff: measures instructions, not time. Catches algorithmic regressions, not microarchitectural ones (branch prediction, cache).

### Go

```yaml
- name: Bench main
  run: |
    git checkout main
    go test -bench=. -count=10 -benchmem ./... > main.txt
    git checkout -

- name: Bench PR
  run: go test -bench=. -count=10 -benchmem ./... > pr.txt

- name: benchstat
  run: |
    go install golang.org/x/perf/cmd/benchstat@latest
    benchstat main.txt pr.txt | tee diff.txt
    # Fail if any bench > 10% slower at p<0.05
    if grep -qE '\+[0-9]+\.[0-9]+%.*p=0\.0[0-4]' diff.txt; then exit 1; fi
```

### Node / TypeScript

Using `mitata`:
```yaml
- run: npm run bench > pr.json

- run: node scripts/compare_mitata.mjs main.json pr.json
```

Or with `tinybench`:
```yaml
- run: npx tinybench bench.js --json > pr.json
- run: node scripts/compare_tinybench.mjs main.json pr.json
```

### Python

```yaml
- run: pytest --benchmark-only --benchmark-json=pr.json

- run: |
    # compare with pytest-benchmark's compare feature
    py.test-benchmark compare main.json pr.json --histogram=diff
    # Hard gate: adapt/export to the summary.json shape and use the bundled comparator.
    ./scripts/ci_compare.sh main-summary.json pr-summary.json --max-pct 10 --metrics p95_ms
```

### CLI wall-clock (language-agnostic)

```yaml
- name: Bench PR
  run: |
    hyperfine --warmup 3 --runs 20 --export-json pr.json \
      './target/release/mycli input1' \
      './target/release/mycli input2'

- name: Compare
  run: |
    jq -s '.[0].results[0].mean as $m1 | .[1].results[0].mean as $m2 |
           ($m2 - $m1) / $m1 * 100' main.json pr.json | \
    awk '{ if ($1 > 10) exit 1 }'
```

---

## Baseline management strategy

### Option A: Baseline from main on every run (expensive, stable)

Every PR run:
1. Checkout main, run bench → main.json
2. Checkout PR, run bench → pr.json
3. Compare

Pros: always comparing against the actual current main
Cons: 2× the compute per PR

### Option B: Scheduled baseline (cheap, can drift)

Nightly job:
1. Run bench on main → upload artifact `main-baseline.json`

Per-PR job:
1. Download yesterday's main-baseline.json
2. Run bench on PR → pr.json
3. Compare

Pros: 1× compute per PR
Cons: baseline can drift between nightly and merge; main can have advanced

### Option C: Per-commit baseline (best tradeoff)

On push to main:
1. Run bench → upload `baseline-<SHA>.json`
2. Update "latest-main" pointer

On PR:
1. Download `baseline-<PR's-merge-base-SHA>.json`
2. Run bench on PR → pr.json
3. Compare

Pros: always comparing against the exact merge base, no drift
Cons: requires a small artifact-storage service (GitHub Releases, S3, or `gh-actions-cache`)

### Skipping the gate

Conditions under which skipping is reasonable:
- PR doesn't touch perf-sensitive code paths (e.g., docs-only, README changes)
- PR is explicitly marked `skip-perf` (with a comment explaining why)
- Baseline is missing (first run after a bench change); warn but don't block

Use path filters to avoid running perf on every doc commit:
```yaml
on:
  pull_request:
    paths:
      - 'src/**'
      - 'Cargo.toml'
      - 'Cargo.lock'
      - 'benches/**'
```

---

## Budget comparison

Beyond "no regression," compare against the written BUDGETS.md target:

```python
import json, sys

budgets = {
    "archive_batch_100_p95_ms": 250,  # from BUDGETS.md
    "format_resolution_explicit_ns": 100,
}

pr = json.load(open("pr.json"))
violations = []
for bench, budget in budgets.items():
    measured = pr[bench]["p95"]
    if measured > budget:
        violations.append(f"{bench}: measured={measured} > budget={budget}")

if violations:
    print("\n".join(violations))
    sys.exit(1)
```

Dual gate:
1. **vs main** — no regression
2. **vs BUDGETS.md** — absolute ceiling not crossed

Either failing blocks the PR.

---

## PR comments and artifacts

Post the comparison table as a PR comment. Link to artifacts.

```bash
# GitHub Actions: use `gh pr comment` or `actions/github-script`
gh pr comment $PR --body "$(cat <<EOF
## Perf comparison

| Bench | Main | PR | Δ | Verdict |
|-------|-----:|---:|--:|---------|
| archive_batch_100 p95 | 238ms | 251ms | +5.5% | ⚠️ WARN |
| format_resolution_explicit | 39ns | 39ns | 0% | ✅ |
| btree_insert_10K | 3.53ms | 3.48ms | -1.4% | ✅ |

[flamegraph main](./runs/main/flame.svg) ・ [flamegraph PR](./runs/pr/flame.svg)
[span_summary main](./runs/main/span_summary.json) ・ [span_summary PR](./runs/pr/span_summary.json)
[fingerprint diff](./runs/fingerprint-diff.txt)

EOF
)"
```

Include:
- Numeric delta per bench
- Verdict emoji (✅ / ⚠️ / ❌)
- Links to flamegraph, span_summary, fingerprint (uploaded as artifacts)
- Variance caveat if CV > 10%

---

## Nightly matrix (cross-FS, cross-OS)

Reusable cross-filesystem workflow shape:

```yaml
name: Cross-filesystem fsync matrix
on:
  schedule:
    - cron: '17 3 * * *'  # daily 03:17 UTC
  workflow_dispatch:

jobs:
  matrix:
    strategy:
      fail-fast: false
      matrix:
        fs: [ext4-ordered, ext4-journal, xfs, btrfs, tmpfs]
        runner: [ubuntu-latest]
        include:
          - fs: apfs
            runner: macos-latest
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup loopback FS (${{ matrix.fs }})
        if: matrix.runner == 'ubuntu-latest' && matrix.fs != 'tmpfs'
        run: ./scripts/setup_loopback_fs.sh ${{ matrix.fs }}

      - name: Run matrix bench
        run: ./scripts/bench_archive_fsync_matrix.sh --fs ${{ matrix.fs }}

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: fsync-${{ matrix.fs }}
          path: tests/artifacts/bench/fsync-matrix/${{ matrix.fs }}/

      - name: Verify per-FS budget
        run: python scripts/verify_fs_budget.py --fs ${{ matrix.fs }}
```

Per-FS budget rows (from BUDGETS.md) are the truth source — each run checks its FS row, not a single global number.

---

## Hosted services

### codspeed.io

- Continuous benchmarking for Rust / Node / Python / Go
- Runs benches on their hardware (matches across runs)
- Statistical significance testing built in
- GitHub PR integration with visual comparisons

```toml
# Cargo.toml — codspeed-criterion-compat
[dev-dependencies]
codspeed-criterion-compat = "2"
```

```yaml
# .github/workflows/codspeed.yml
- uses: CodSpeedHQ/action@v3
  with:
    token: ${{ secrets.CODSPEED_TOKEN }}
    run: cargo codspeed run
```

### bencher.dev

- Stack-agnostic (accepts any bench output via adapters)
- Self-hostable
- Alert thresholds + PR gating

### Grafana Cloud k6 / Datadog Synthetic Perf / BuildPulse

More ops-oriented; less "per PR gate", more "watch trends over time."

### When to reach for hosted

- Team doesn't want to run self-hosted runners
- Multi-language stack where one service works across languages
- Visual dashboards are valuable

When NOT:
- Custom bench format (might not have an adapter)
- Sensitive workload / data — hosted services run your code

---

## Self-hosted runners for expensive benches

When the bench takes > 5 minutes or needs > 8 GB RAM, shared CI runners are too noisy / too small.

### Setup

```
# On the bench host
sudo apt install -y jq curl
cd /opt/actions-runner
./config.sh --url https://github.com/YOUR_ORG/YOUR_REPO --token <TOKEN>
./svc.sh install
./svc.sh start

# Tag it
labels: self-hosted, bench, linux, x64, btrfs
```

### Workflow pin

```yaml
jobs:
  bench:
    runs-on: [self-hosted, bench, linux, x64, btrfs]
```

### Isolation

Runner host must be:
- Dedicated (no other workloads during bench)
- Pinned CPU governor (performance)
- SMT off if measuring per-core
- `taskset` to isolated cores during the bench
- `drop_caches` before cold-cache runs

Capture this state in tuning.json alongside the bench artifact. CI should FAIL if tuning.json doesn't match the expected state.

### Cost ceiling

Self-hosted = you pay for electricity, hardware, maintenance. Typically worth it only if:
- Bench runs > N times per day (where N ≥ 20)
- Workload requires specific hardware (GPU, large RAM, NVMe)
- Security / compliance forbids hosted

---

## False-positive triage

When the gate fails:

1. **Check fingerprint diff first.** Runner changed? Kernel upgrade? That's not a code regression.
2. **Rerun the PR.** Single run may have been noisy. Require 2/3 or 3/5 failing to declare regression.
3. **Check variance.** If CV > 10% on either side, the comparison is too noisy to conclude.
4. **Interleave.** Did the workflow run PR-bench first, main-bench second? Thermal drift. Use A-B-A-B ordering.
5. **Look at the flamegraph diff.** Is the red bar in a file this PR touched? If no, it's environmental.
6. **Bisect.** If main has drifted since the baseline, the regression may be someone else's. Run the baseline on current main to check.

Rules of thumb for "override":
- 1 false positive → mark as noise, rerun
- 2 false positives in a row → fix the runner (not the gate)
- Real regression → block, diagnose with the artifacts, fix or revert

---

## Sample workflow files

### `.github/workflows/perf-gate.yml` (Rust example)

```yaml
name: Perf Gate
on:
  pull_request:
    paths:
      - 'src/**'
      - 'Cargo.toml'
      - 'Cargo.lock'
      - 'benches/**'

jobs:
  bench:
    runs-on: [self-hosted, bench, linux, x64]
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Capture fingerprint
        run: ./scripts/env_fingerprint.sh > fingerprint.json

      - name: Verify host state
        run: |
          if [ "$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)" != "performance" ]; then
            echo "ERROR: governor is not 'performance'; aborting bench"; exit 1
          fi

      - name: Download latest main baseline
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          run_id=$(gh run list --workflow perf-baseline.yml --branch main --status success \
            --limit 1 --json databaseId --jq '.[0].databaseId')
          test -n "$run_id"
          gh run download "$run_id" --name main-baseline --dir baseline

      - name: Bench PR
        run: |
          export RUSTFLAGS="-C force-frame-pointers=yes"
          ./scripts/bench_baseline.sh --name rust-bench \
            --cmd 'cargo bench --profile release-perf -- --output-format=bencher' \
            --runs 20 --warmup 3
          run_dir=$(readlink -f tests/artifacts/perf/rust-bench/latest)
          cp "$run_dir/summary.json" pr-summary.json
          cp "$run_dir/fingerprint.json" fingerprint.json

      - name: Compare
        run: |
          ./scripts/ci_compare.sh baseline/summary.json pr-summary.json \
            --max-pct 10 \
            --metrics p50_ms,p95_ms,p99_ms \
            --baseline-fingerprint baseline/fingerprint.json \
            --candidate-fingerprint fingerprint.json | tee diff.txt

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: bench-pr-${{ github.event.pull_request.number }}
          path: |
            pr-summary.json
            diff.txt
            fingerprint.json
            tests/artifacts/perf/rust-bench/**
            target/criterion/**/*.svg

      - name: Post PR comment
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = `## Perf gate\n\n\`\`\`\n${fs.readFileSync('diff.txt', 'utf8')}\n\`\`\`\n\n` +
                         `[Artifacts](${context.payload.pull_request.html_url}/checks)`;
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body,
            });
```

### `.github/workflows/perf-baseline-main.yml`

```yaml
name: Update main perf baseline
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Cargo.toml'
      - 'Cargo.lock'
      - 'benches/**'

jobs:
  baseline:
    runs-on: [self-hosted, bench, linux, x64]
    steps:
      - uses: actions/checkout@v4

      - name: Capture fingerprint
        run: ./scripts/env_fingerprint.sh > fingerprint.json

      - name: Bench main
        run: |
          export RUSTFLAGS="-C force-frame-pointers=yes"
          cargo bench --profile release-perf -- --save-baseline main

      - name: Upload main baseline
        uses: actions/upload-artifact@v4
        with:
          name: main-baseline
          path: |
            target/criterion/
            fingerprint.json
          retention-days: 30
```

### Custom comparison script

See `scripts/ci_compare.sh` in this skill's scripts folder for a cross-language, CI-friendly comparator driven from `hyperfine --export-json`.
