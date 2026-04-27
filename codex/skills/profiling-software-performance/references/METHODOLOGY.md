# Profiling Methodology — Phase by Phase

> This is the rigorous path from "it feels slow" to a ranked hotspot table that `extreme-software-optimization` can act on. Every phase produces a file on disk; no file → not done.

## Contents

1. [Phase 1 — Define](#phase-1--define)
2. [Phase 2 — Environment Fingerprint](#phase-2--environment-fingerprint)
3. [Phase 3 — Baseline](#phase-3--baseline)
4. [Phase 4 — Instrument](#phase-4--instrument)
5. [Phase 5 — Profile](#phase-5--profile)
6. [Phase 6 — Interpret](#phase-6--interpret)
7. [Phase 7 — Hand Off](#phase-7--hand-off)
8. [Iteration Protocol](#iteration-protocol)

---

## Phase 1 — Define

Before any measurement, the user (or you) must answer these four questions in writing. If any is missing, go ask — do not start profiling.

```
Q1. Scenario       — what exact workload will we measure?
Q2. Metric         — latency (which percentile), throughput, memory, or a combo?
Q3. Budget         — what number makes this "fast enough"?
Q4. Golden output  — how will we confirm optimizations didn't change behavior?
```

Template (commit under `tests/artifacts/perf/<scenario>/DEFINE.md`):

```markdown
## Scenario
archive_batch_100 — 100 ArchiveMessage inserts in a single batch

## Metric
p95 wall-time per batch; peak RSS during the run

## Budget
batch-100 p95 ≤ 250ms on the declared reference host (Ryzen 5995WX, btrfs, Linux 6.17.0-19-generic)

## Golden output
tests/artifacts/perf/golden/archive_batch_100.sha256 — sha256 of the output file after run

## Scope boundary
Out of scope: batch-1000, cross-filesystem, cold-cache runs
```

**Rule:** Budget must be a number, not "faster" or "better". If the user won't commit to a number, pick the current p95 × 0.5 and ask them to accept or override.

---

## Phase 2 — Environment Fingerprint

Every perf number is tied to a host. Changing filesystem, kernel, governor, or CPU model invalidates prior numbers. Capture the fingerprint once per run and store it next to results.

Required fields (captured by `scripts/bench_baseline.sh`):

```bash
lscpu | awk -F: '/Model name|Socket|Core|Thread|CPU MHz/{print $0}'
cat /proc/meminfo | head -3
findmnt -T $(pwd) -o SOURCE,FSTYPE,OPTIONS
uname -r
rustc --version --verbose      # or: go version, node -v, python -V
git rev-parse HEAD
date -u '+%Y-%m-%dT%H:%M:%SZ'
cpupower frequency-info | grep 'current policy'     # governor
cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null
cat /sys/devices/system/cpu/smt/active 2>/dev/null
```

Store to `fingerprint.json` so diffs are machine-readable. Include build profile (opt-level, lto, codegen-units, debug, panic, strip) for whichever language.

**Rule:** A run is "noise" until its `fingerprint.json` matches a prior run's fields on: CPU model, kernel major, filesystem, governor, no_turbo, SMT, build profile. Reject any A/B comparison that crosses a fingerprint boundary.

---

## Phase 3 — Baseline

Capture a baseline *before* any instrumentation changes. Otherwise instrumentation overhead contaminates all future diffs.

### CLI workloads — `hyperfine`

```bash
hyperfine --warmup 3 --runs 20 --export-json baseline.json \
    --command-name before 'cmd args' \
    --prepare 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches'   # only for cold-cache scenarios
jq '.results[0].times | sort |
    {p50: .[length/2], p95: .[length*0.95|floor], p99: .[length*0.99|floor]}' baseline.json
```

### Rust — `criterion`

```rust
// benches/bench_utils.rs — criterion configuration template
pub fn configure_criterion() -> Criterion {
    Criterion::default()
        .sample_size(50)
        .measurement_time(Duration::from_secs(3))
        .warm_up_time(Duration::from_secs(1))
        .noise_threshold(0.03)
        .confidence_level(0.95)
        .without_plots()   // CI
}
```
```bash
cargo bench --bench <name> -- --save-baseline before
# ... make change ...
cargo bench --bench <name> -- --baseline before
```

### Go — `go test -bench` + `benchstat`

```bash
go test -bench=. -benchmem -count=10 ./... | tee before.txt
# ... make change ...
go test -bench=. -benchmem -count=10 ./... | tee after.txt
benchstat before.txt after.txt     # delta + t-test, use its verdict not eyeballs
```

### Latency for servers — `wrk2` / `k6` / `vegeta`

Closed-loop `wrk` underreports tail latency; prefer open-loop tools (`wrk2`, `vegeta`) with a fixed rate for real p99/p99.9.

### Memory baseline

```bash
/usr/bin/time -v ./bin                 # Maximum resident set size (KiB)
cat /proc/$PID/smaps_rollup | head     # live Rss/Pss/Uss
valgrind --tool=massif --pages-as-heap=yes ./bin
ms_print massif.out.*                  # true peak heap
```

### Report card (commit under `BASELINE.md`)

```markdown
## Baseline — <scenario> — <date> — <git-sha>
| Metric | Value |
|--------|-------|
| p50    | X ms |
| p95    | X ms |
| p99    | X ms |
| p99.9  | X ms (flag as conservative if samples < 1000) |
| max    | X ms |
| samples| N    |
| throughput | X ops/s |
| peak RSS | X MiB |
| heap high-water | X MiB |
| tests  | PASS |
```

**Rule:** Samples < 1000 → label p99.9 and p99.99 as *conservative worst-observed* in the write-up. Don't pretend to have stats you don't have.

---

## Phase 4 — Instrument

Add measurement plumbing *before* running the sampler. Sampler-only profiling answers "what function is hot" but can't answer "which of my two logical phases is hot" — instrumentation does.

Three layers, in this order:

### 4a. Sentinel frames (flamegraph attribution)

When a pipeline has logical stages (parse → compile → plan → execute → commit), wrap each with a `#[inline(never)]` no-op sentinel function. They show up in flames as distinct bars.

```rust
#[inline(never)] fn _profile_parse()    { std::hint::black_box(()); }
#[inline(never)] fn _profile_compile()  { std::hint::black_box(()); }
#[inline(never)] fn _profile_execute()  { std::hint::black_box(()); }

fn run() {
    _profile_parse();    parse();
    _profile_compile();  compile();
    _profile_execute();  execute();
}
```
This sentinel-frame pattern makes the flamegraph show, at a glance, which stage owns the bar.

### 4b. Spans / structured timing

```rust
#[tracing::instrument(skip_all, fields(batch_size))]
fn write_message_batch(batch: &[Message]) -> Result<()> { ... }
```

For non-Rust stacks: `trace.StartRegion` (Go), `performance.timerify` (Node), `@viztracer.log_sparse` (Python), `ZoneScoped` (C++ Tracy).

Emit `span_summary.json` (schema: `span_name, count, p50, p95, cumulative_us, max`) alongside the flamegraph — this is what a human reads, not the SVG.

### 4c. Histograms + structured logging

Even if the profiler runs only in dev, keep latency histograms in production.

```rust
use hdrhistogram::Histogram;
let mut h = Histogram::<u64>::new_with_bounds(1, 60_000_000, 3).unwrap();
h.record(elapsed.as_micros() as u64).unwrap();
tracing::info!(target: "perf.profile.span_summary",
    span_name = "archive_batch.write_messages",
    p50 = h.value_at_quantile(0.5),
    p95 = h.value_at_quantile(0.95),
    p99 = h.value_at_quantile(0.99),
    cumulative_us = h.mean() * h.len() as f64);
```

Structured log contract (see `INSTRUMENTATION.md` for the full field set):
```
perf.profile.run_start         { scenario, version, hardware }
perf.profile.sample_collected  { sample_count, duration_sec }
perf.profile.span_summary      { span_name, cumulative_us, count, p50, p95 }
perf.profile.hypothesis_evaluated { name, verdict, evidence }
perf.profile.run_complete      { duration_sec, artifacts_written }
```

Gate instrumentation behind an env flag such as `MCP_AGENT_MAIL_ARCHIVE_PROFILE=1` so production pays nothing.

---

## Phase 5 — Profile

Pick samplers from `LANGUAGE-GUIDES.md`. The minimum per scenario:

| Axis | Answer it gives |
|------|------------------|
| CPU flamegraph | "where is on-CPU time?" |
| Allocation | "what's churning memory and causing GC / malloc overhead?" |
| Off-CPU flamegraph | "where are we *waiting* (I/O, locks, futex, park)?" |
| Contention | "which locks / channels block us?" |
| Syscall / I/O | "are we reading the same file 10,000 times?" |

Skip allocation profiling only if the alloc rate is < 1% of CPU time (check via `perf stat -e page-faults,context-switches` and DHAT's alloc count).

### Collection checklist

- [ ] Host matches fingerprint (Phase 2)
- [ ] Kernel / governor tuned as negotiated (Phase 2 / OS-TUNING)
- [ ] Instrumentation build (Phase 4) not stripped / inlined away
- [ ] 3+ warmups, ≥ 20 measurement runs
- [ ] Cold vs warm cache: pick one, document it
- [ ] One sampler at a time (avoid stacking overhead)
- [ ] Emit raw data (not just renders) so someone else can re-interpret

### Anti-patterns observed

- Profiling the size-optimized `[profile.release]` build: frames are stripped, `unwrap()` inlined, inner loops merged. Use `[profile.release-perf]` or the equivalent.
- Running two samplers simultaneously (e.g. `perf record` + `heaptrack`): blows timing apart.
- Benchmarking the prepared API for one engine and ad-hoc for the other. Normalize API usage or you're measuring your own mistake.
- Using format-string SQL in a prepared-statement benchmark — every call misses the cache.

---

## Phase 6 — Interpret

Rendering the output into something actionable. This phase produces three files:

1. `hotspot_table.md` — ranked, evidence-cited
2. `scaling_law.md` — p95 at 1/10/50/100/500/1000 × base workload
3. `hypothesis.md` — supports/rejects ledger

### Hotspot table

```markdown
| Rank | Location              | Metric       | Value    | Category | Evidence                     |
|------|-----------------------|--------------|----------|----------|------------------------------|
| 1    | record_decode         | cumulative   | 841 ms   | CPU      | flame.svg (0.23 width)       |
| 2    | parser_ast_churn      | cumulative   | 627 ms   | CPU+alloc| dhat-heap.json#L412          |
| 3    | archive_batch.write_messages | p95   | 3491 ms  | I/O      | span_summary.json            |
| 4    | btree_seek            | count × avg  | 3063×250ns | CPU    | perf.data + _profile_seek    |
```

Interpret like this:

- Widest bar on the flame = highest rank, unless evidence from spans says otherwise.
- Convert cumulative_us × count into a single "total time share" figure; rank by that.
- Tag each row CPU / alloc / I/O / lock / GC — it determines which technique catalog applies later.
- Cite an artifact. An unsourced row is a guess.

### Scaling law

Example scaling law:
```
batch-10  p95 is  5.70× batch-1  (amortized 0.570× per msg)
batch-50  p95 is 55.01× batch-1  (amortized 1.100× per msg)
batch-100 p95 is 128.82× batch-1 (amortized 1.288× per msg)
batch-500 p95 is 261.56× batch-1 (amortized 0.523× per msg)
batch-1000 p95 is 533.61× batch-1 (amortized 0.534× per msg)
=> sublinear overall; no lock-driven blow-up
```

The *shape* is the finding. Linear + small constant = no leverage. Sublinear at large N but superlinear at moderate N = batch coalescing pays off only past a threshold. Super-linear = lock thrash or alloc cliff.

### Hypothesis ledger

Name every "maybe this is the cause", pick evidence, stamp verdict:
```
coalescer batching : rejects — write_message_batch dominates 25.4s cum vs flush 0.87s
fsync per msg      : rejects — wbq_flush cum 0 vs flush_async_commits 873ms
file layout        : supports — per-msg archive burst dominates profile at 25.4s
sqlite per-msg txn : rejects — no sqlite spans in top 10
hashing            : rejects — no hash spans in top 10
lock thrash        : rejects — scaling is sublinear through batch-1000
```

Rejecting hypotheses with evidence is how you stop relitigating them next week.

---

## Phase 7 — Hand Off

The hand-off artifact for `extreme-software-optimization`:

```
tests/artifacts/perf/<run-id>/
├── DEFINE.md                 # scenario, metric, budget, golden
├── fingerprint.json          # host + toolchain + build
├── BASELINE.md               # p50/p95/p99/p99.9, throughput, RSS
├── flame.svg                 # or cpu.json (samply)
├── span_summary.json
├── dhat-heap.json            # or memray / heaptrack equivalent
├── off-cpu.svg               # if relevant
├── hotspot_table.md          # ranked, evidence-cited
├── scaling_law.md            # when scenario has a natural scale axis
├── hypothesis.md             # supports/rejects
└── golden_checksums.txt      # sha256 of golden outputs
```

Tell the user in plain English:
> Baseline: archive_batch_100 p95 = 3.49s, budget = 250ms. Top hotspot: `archive_batch.write_messages` 25.4s cumulative (supports "file layout" hypothesis). Secondary: `flush_async_commits` 873ms. Artifacts under `tests/artifacts/perf/<run-id>/`. Ready to hand off to `extreme-software-optimization` for scoring.

**Stop here.** Do not implement optimizations in this skill. The next skill handles scoring (Impact × Confidence / Effort ≥ 2.0), one lever per commit, isomorphism proofs, and golden verification.

---

## Iteration Protocol

After `extreme-software-optimization` ships a change:

1. **Re-baseline** — new numbers under a new run-id directory (never overwrite).
2. **Re-profile** — bottlenecks *shift*. The #2 from round 1 is often the #1 for round 2.
3. **Re-rank** — fresh hotspot table. Score drops across rounds — stop when no row has Score ≥ 2.0 in the optimization skill.
4. **Append to history**:
```markdown
| Round | Change | p95 Before | p95 After | Δ | run-id |
|-------|--------|-----------|-----------|---|--------|
| 1 | cached statements | 3491 ms | 2104 ms | -40% | 20260418T103015Z |
| 2 | batch coalescer | 2104 ms |  980 ms | -53% | 1776601234 |
```

A round where Δ < 5% means either (a) remaining hotspots need a different technique class (algorithmic vs constant-factor — switch to ADVANCED.md in the next skill) or (b) you've hit the irreducible floor. Declare it and stop.
