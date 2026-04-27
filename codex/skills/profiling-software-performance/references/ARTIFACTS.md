# Artifact Templates — fingerprint, BUDGETS, hotspot table, scaling law, hypothesis ledger

> Copy these directly. Every profiling run must produce these files under `tests/artifacts/perf/<run-id>/`.

## Contents

1. [Directory layout](#directory-layout)
2. [DEFINE.md — scenario, metric, budget](#definemd--scenario-metric-budget)
3. [fingerprint.json — host + build](#fingerprintjson--host--build)
4. [BUDGETS.md — the performance contract](#budgetsmd--the-performance-contract)
5. [BASELINE.md — measurement card](#baselinemd--measurement-card)
6. [hotspot_table.md](#hotspot_tablemd)
7. [scaling_law.md](#scaling_lawmd)
8. [hypothesis.md](#hypothesismd)
9. [History table (appended across rounds)](#history-table-appended-across-rounds)
10. [Hand-off summary](#hand-off-summary)
11. [Wrapper script skeleton](#wrapper-script-skeleton)

---

## Directory layout

```
tests/artifacts/perf/<run-id>/
├── DEFINE.md
├── fingerprint.json
├── tuning.json                # from OS-TUNING.md verification block
├── BASELINE.md
├── flame.svg                  # or cpu.json for samply
├── off-cpu.svg                # if wait time is a factor
├── span_summary.json          # Chrome traceEvents + span roll-ups
├── <scenario>_spans.json      # raw spans (see INSTRUMENTATION.md)
├── dhat-heap.json             # or memray / heaptrack equivalent
├── fio.json                   # if I/O was evaluated
├── hotspot_table.md
├── scaling_law.md
├── hypothesis.md
└── golden_checksums.txt       # sha256 of outputs the next skill must preserve
```

Naming: `<run-id>` = `<unix-seconds>_<microseconds>` or the timestamped ID emitted by `scripts/bench_baseline.sh`. Never overwrite a prior run — iteration across rounds needs the history.

---

## DEFINE.md — scenario, metric, budget

```markdown
# DEFINE — <scenario-name>

## Scenario
<one-paragraph description of the exact workload being measured>

## Metric
<what we're measuring — p95 wall-time, throughput, peak RSS, IOPS, etc.>

## Budget
<the number "fast enough" must beat — e.g. `batch-100 p95 ≤ 250ms on reference host`>

## Golden output
<how behavior equivalence is verified — sha256 file, property tests, diff of outputs>

## Scope boundary
Out of scope: <things this run will NOT measure>

## Variance envelope
- ≤10% drift vs prior same-host run → noise
- >10% → investigate
- >20%, or 3 consecutive >10% → escalate

## Stakeholder / requester
<who asked for this profile, and what decision hinges on it>
```

---

## fingerprint.json — host + build

```json
{
  "run_id": "20260418T103015Z-abcdef",
  "captured_at_utc": "2026-04-18T10:30:15Z",
  "git_sha": "abcdef123456",
  "hardware": {
    "cpu_model": "AMD Ryzen Threadripper PRO 5995WX",
    "cpu_cores": 64,
    "cpu_threads": 128,
    "cpu_mhz_reported": "413-4575",
    "ram_total": "499 GiB",
    "swap_total": "63 GiB"
  },
  "storage": {
    "device": "/dev/nvme0n1",
    "model": "Samsung SSD 9100 PRO 4TB NVMe",
    "mount_point": "/data",
    "filesystem": "btrfs",
    "mount_options": "rw,noatime,compress=zstd:1,ssd,discard=async,space_cache=v2,subvolid=5,subvol=/"
  },
  "os": {
    "distribution": "Ubuntu 25.10",
    "kernel": "6.17.0-19-generic"
  },
  "toolchain": {
    "rustc": "rustc 1.97.0-nightly (e9e32aca5 2026-04-17)",
    "go": null,
    "node": null,
    "python": null
  },
  "build_profile": {
    "name": "release-perf",
    "opt_level": 3,
    "lto": "thin",
    "codegen_units": 1,
    "debug": "line-tables-only",
    "panic": "abort",
    "strip": false
  },
  "workload_isolation": {
    "taskset": null,
    "cgroup": null,
    "rch": true,
    "bare": false
  },
  "tuning_applied": {
    "perf_event_paranoid": -1,
    "kptr_restrict": 0,
    "nmi_watchdog": 0,
    "governor": "performance",
    "no_turbo": 1,
    "smt_active": "off"
  },
  "cache_state": "warm",
  "notes": "MCP_AGENT_MAIL_ARCHIVE_PROFILE=1 enabled for warm-path side-artifacts"
}
```

A diff over `fingerprint.json` between runs instantly shows whether a comparison is valid.

---

## BUDGETS.md — the performance contract

Commit once, update with ceremony. This is the long-lived document per project; individual runs check against it.

```markdown
# Performance Budgets

Baseline performance targets. Updated when a measured improvement earns a tighter budget — never relaxed without a written reason.

## Optimization workflow
1. Profile — measure before changing anything
2. Change — apply one optimization
3. Prove — behavior unchanged (golden) AND performance improved

## Hardware + Environment Baseline
<fill in from fingerprint.json>

- CPU: ...
- RAM: ...
- Storage: ...
- OS: ...
- Toolchain: ...
- Build profile: ...

## Variance envelope
- ≤10% p95 drift on the same host → noise
- >10% → investigate; >20% or 3 consecutive >10% → escalate

## Budgets by surface

| Surface                          | Baseline   | Budget     | Notes                       |
|----------------------------------|-----------:|-----------:|-----------------------------|
| Format resolution (explicit)     |   ~39 ns   |  < 100 ns  | Pure string matching        |
| Stats parsing (full)             |  ~243 ns   |  < 500 ns  | 2-line scan                 |
| Archive batch-100 p95            | 3491 ms    |  < 250 ms  | reference host (btrfs)      |
| ...                              |            |            |                             |

## Cross-filesystem matrix (if relevant)

| FS                    | Single p95 | Batch-100 p95 | Notes                         |
|-----------------------|-----------:|--------------:|-------------------------------|
| ext4 (data=ordered)   | < 25 ms    | < 250 ms      | Linux recommendation          |
| xfs                   | < 25 ms    | < 250 ms      | Low-variance server writes    |
| btrfs                 | < 50 ms    | < 500 ms      | Slower under CoW pressure     |
| APFS (macOS)          | < 35 ms    | < 300 ms      | Barrier semantics differ      |
| tmpfs                 | < 15 ms    | < 150 ms      | Canary; not durable           |

## Emergency rollback
If a same-host rerun breaches the envelope after a change: <link to runbook>.
```

---

## BASELINE.md — measurement card

```markdown
# Baseline — <scenario> — <YYYY-MM-DD> — <git-sha>

| Metric          | Value        | Notes                                     |
|-----------------|-------------:|-------------------------------------------|
| p50             |    X ms      |                                           |
| p95             |    X ms      |                                           |
| p99             |    X ms      |                                           |
| p99.9           |    X ms      | *conservative* if samples < 1000          |
| p99.99          |    X ms      | *conservative* if samples < 1000          |
| max             |    X ms      |                                           |
| samples         |    N         |                                           |
| throughput      |    X ops/sec |                                           |
| peak RSS        |    X MiB     | /usr/bin/time -v                          |
| heap high-water |    X MiB     | dhat / heaptrack / massif                 |
| process CPU avg |    X %       | pidstat -u                                |
| tests           | PASS / FAIL  |                                           |

## Run command
```
<exact command line>
```

## Variance snapshot (5 reruns on the same host)
p95 values: A ms, B ms, C ms, D ms, E ms — max drift Y% → noise / investigate / escalate
```

---

## hotspot_table.md

```markdown
# Hotspot table — <run-id>

| Rank | Location                             | Metric       | Value       | Category   | Evidence                                      |
|-----:|--------------------------------------|--------------|------------:|------------|-----------------------------------------------|
|  1   | record_decode                        | cumulative   |    841 ms   | CPU        | flame.svg width 0.23; span_summary.json       |
|  2   | parser_ast_churn                     | cumulative   |    627 ms   | CPU+alloc  | dhat-heap.json#L412; AST clone path           |
|  3   | archive.flush_async_commits          | p95          |     82 ms   | I/O        | span_summary.json; biolatency bimodal 3ms/80ms|
|  4   | btree_seek                           | count × avg  | 3063 × 250ns| CPU        | perf.data; _profile_btree_seek sentinel bar   |
|  5   | page_buffer_pool (misses)            | miss rate    |    100 %    | cache      | cache_stats.json (zero hits, pool unsupported)|

## Notes
- Rank 1–2 are attack surfaces for next round (CPU-bound; algorithmic candidates)
- Rank 3 supports "file layout" hypothesis (I/O dominates the p95 tail)
- Rank 5 is a ram-for-speed tradeoff candidate — see IO-AND-TRADEOFFS.md table

## Baseline Reuse Ledger
| Cache                     | supported | hits | misses | hit_rate_bps | target notes |
|---------------------------|-----------|-----:|-------:|-------------:|--------------|
| page_buffer_pool_reuse    | false     |    0 |      0 |          n/a | opaque; needs evidence surface |
| compiled_plan_cache       | true      |    0 |     52 |            0 | direct evidence for plan cache |
| statement_parse_cache     | true      |  100 |     62 |         6173 | still avoidable prepare churn  |
| cursor_frame_reuse        | true      |  100 |      1 |         9901 | drive reuse rate up            |
```

Each row MUST cite an artifact. An unsourced rank is a guess and won't pass hand-off review.

---

## scaling_law.md

```markdown
# Scaling law — <run-id> — <scenario>

Axis: batch size
Samples per point: 12-40 (see note)

| Size  | p50 µs     | p95 µs     | p99 µs     | Throughput ops/s | p95 multiple vs baseline | Amortized p95/msg |
|------:|-----------:|-----------:|-----------:|-----------------:|-------------------------:|------------------:|
|     1 |    23 307  |    27 101  |    28 650  |           43.71  |                  1.00×   |            1.00×  |
|    10 |   142 453  |   154 429  |   159 740  |           69.99  |                  5.70×   |            0.570× |
|    50 |   682 683  | 1 490 815  | 1 925 691  |           60.88  |                 55.01×   |            1.100× |
|   100 | 1 327 095  | 3 491 133  | 7 640 550  |           45.72  |                128.82×   |            1.288× |
|   500 | 6 438 268  | 7 088 480  | 7 088 480  |           75.96  |                261.56×   |            0.523× |
|  1000 | 13 091 095 |14 461 498  |14 461 498  |           74.67  |                533.61×   |            0.534× |

**Verdict:** Overall scaling remains sublinear through batch-1000 (amortized p95/msg drops at large N).

**Implication:**
- No lock-driven blow-up
- Amortization favors batch ≥ 500 for throughput
- 10 ≤ batch ≤ 100 sees worst amortization (coalescer win threshold likely here)

**Note on samples:** batch-100 warm-path sample counts are below 1 000 per scenario; p99.9 and p99.99 are labeled *conservative worst-observed*.
```

---

## hypothesis.md

```markdown
# Hypothesis ledger — <run-id>

Every candidate explanation for the hotspots is written down and marked `supports` / `rejects` with evidence.

| Hypothesis                   | Verdict   | Evidence                                                                                  |
|------------------------------|-----------|-------------------------------------------------------------------------------------------|
| coalescer batching           | rejects   | write_message_batch cumulative 25.4s vs flush_async_commits 0.87s                         |
| fsync per msg                | rejects   | wbq_flush cumulative 0 µs vs flush_async_commits 873 ms                                   |
| file layout                  | supports  | per-message archive burst dominates at 25.4s cumulative                                   |
| SQLite per-msg txn           | rejects   | no sqlite spans in top 10 of span_summary.json                                            |
| hashing                      | rejects   | no hash-oriented spans in top 10                                                          |
| lock thrash                  | rejects   | scaling is sublinear through batch-1000 (see scaling_law.md); no superlinear blow-up      |

## New candidates raised this round
- mmap fault-in during first-pass scan? → needs test next round (capture `perf stat -e page-faults` baseline)
- btrfs CoW fragmentation of archive file? → run `filefrag -v` before/after a run and compare

## Hypotheses to revisit next round
- coalescer batching: re-test with larger target batch (batch-500) — amortized p95/msg improves there
```

---

## History table (appended across rounds)

Living file at `tests/artifacts/perf/HISTORY.md`:

```markdown
# Performance History — <scenario>

| Round | Date       | Change                          | p95 Before | p95 After | Δ     | run-id              |
|------:|------------|---------------------------------|-----------:|----------:|------:|---------------------|
|    1  | 2026-03-13 | baseline                        |       n/a  | 3491 ms   |   —   | 20260313_canonical  |
|    2  | 2026-03-22 | arc-cached statements           | 3491 ms    | 2104 ms   | -40%  | 190118022           |
|    3  | 2026-04-03 | batch coalescer                 | 2104 ms    |  980 ms   | -53%  | 20260418T103015Z   |
|    4  | pending    | —                               |       —    |     —     |   —   | —                   |
```

---

## Hand-off summary

Before declaring done and calling `extreme-software-optimization`, verify:

- [ ] `DEFINE.md` exists and has all four questions answered
- [ ] `fingerprint.json` captured and matches prior run (or is noted as new-host)
- [ ] `tuning.json` captured (if kernel was tuned)
- [ ] `BASELINE.md` filled with p50/p95/p99/p99.9 + samples count
- [ ] `hotspot_table.md` has ≥ 3 rows, each with an artifact citation
- [ ] `scaling_law.md` filled when the scenario has a natural scale axis
- [ ] `hypothesis.md` has every candidate marked supports / rejects
- [ ] Golden outputs captured, `golden_checksums.txt` written
- [ ] Variance envelope check done (rerun p95 across same-host runs ≤ 10%)

Then output this summary to the user verbatim:

```
Profile complete: <scenario> — run-id <id>
Baseline: <p95-value> — budget <budget> — gap <N×>
Top 3 hotspots (rank, location, category):
  1. <loc> — <metric-value> — <category>
  2. <loc> — <metric-value> — <category>
  3. <loc> — <metric-value> — <category>
Supported hypothesis: <name>
Rejected hypotheses: <list>
Ready for extreme-software-optimization to score (Impact × Confidence / Effort ≥ 2.0).
Artifacts: tests/artifacts/perf/<run-id>/
```

---

## Wrapper script skeleton

Same shape as the bundled `scripts/bench_baseline.sh` — adapt per project.

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_ID="$(date -u '+%s_%6N')"
OUTDIR="${PROJECT_ROOT}/tests/artifacts/perf/${RUN_ID}"
mkdir -p "${OUTDIR}"

# 1. Fingerprint
{
  echo "run_id: ${RUN_ID}"
  echo "git: $(git rev-parse HEAD)"
  lscpu | grep -E 'Model name|Socket|Core|Thread'
  free -h | head -2
  findmnt -T "${PROJECT_ROOT}" -o SOURCE,FSTYPE,OPTIONS
  uname -r
  rustc --version --verbose 2>/dev/null || true
  cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null
  cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || true
} > "${OUTDIR}/fingerprint.txt"
# JSON version via jq -R ... or a dedicated dumper — see fingerprint.json template above

# 2. OS tuning verification (read-only)
{
  sudo sysctl kernel.perf_event_paranoid kernel.kptr_restrict kernel.yama.ptrace_scope kernel.nmi_watchdog
  cat /sys/kernel/mm/transparent_hugepage/enabled
} > "${OUTDIR}/tuning.txt" 2>&1 || true

# 3. Baseline
hyperfine --warmup 3 --runs 20 --export-json "${OUTDIR}/hyperfine.json" \
    "${PROJECT_ROOT}/target/release-perf/myapp <args>"

# 4. Profile (CPU)
samply record --save-only -o "${OUTDIR}/cpu.json" -- \
    "${PROJECT_ROOT}/target/release-perf/myapp" <args>

# 5. Profile (alloc) — comment out if not needed
# heaptrack -o "${OUTDIR}/heaptrack.bin.gz" "${PROJECT_ROOT}/target/release-perf/myapp" <args>

# 6. Span summaries & Chrome trace
MYAPP_PROFILE=1 TRACE_FILE="${OUTDIR}/spans.json" \
  "${PROJECT_ROOT}/target/release-perf/myapp" <args>

# 7. Golden output capture
"${PROJECT_ROOT}/target/release-perf/myapp" <args> > "${OUTDIR}/golden.out"
sha256sum "${OUTDIR}/golden.out" > "${OUTDIR}/golden_checksums.txt"

echo "Artifacts written to ${OUTDIR}"
```

Make the script executable, commit it, and treat `tests/artifacts/perf/<run-id>/` as the only canonical place to argue about performance.
