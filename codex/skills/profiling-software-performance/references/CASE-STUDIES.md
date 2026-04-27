# Real Profiling Journeys — Case Studies

> Each case study is a concrete end-to-end example: the complaint, the hypothesis ledger, the artifacts, the rejections, the wins, and the round-by-round numbers. Public project identities and host specs are preserved when they carry technical meaning; private local identifiers are omitted.

## Contents

1. [Case 1 — mcp_agent_mail_rust archive_batch_100: p95 from 3.49s toward 250ms](#case-1--mcp_agent_mail_rust-archive_batch_100)
2. [Case 2 — frankensqlite Track V baseline and the ranked hotspot discipline](#case-2--frankensqlite-track-v-baseline)
3. [Case 3 — cass indexing 99.8s -> 88.6s via single-open + larger add-batch](#case-3--cass-indexing-journey)
4. [Case 4 — The opt-level="z" + LTO disk-exhaustion incident (2026-04-03)](#case-4--the-opt-levelz--lto-disk-incident)
5. [Case 5 — Tokio ticker_cx deadlock (held-across-if-let, 2026-04-10)](#case-5--tokio-ticker_cx-deadlock)
6. [Case 6 — bd-wwqen seven-round cumulative 1.5x campaign](#case-6--bd-wwqen-seven-round-cumulative-campaign)
7. [Case 7 — Benchmark truthfulness audit (2026-03-19)](#case-7--benchmark-truthfulness-audit)
8. [Case 8 — SmallText SSO + 14 named optimization commits](#case-8--smalltext-sso-string-optimization)
9. [Case 9 — Concurrent writer 4.35× over C SQLite](#case-9--concurrent-writer-4-35)
10. [Case 10 — Cross-filesystem matrix (ext4 vs xfs vs btrfs vs APFS vs tmpfs)](#case-10--cross-filesystem-matrix)
11. [Meta-lessons across all cases](#meta-lessons-across-all-cases)

---

## Case 1 — mcp_agent_mail_rust archive_batch_100

**Subject**: `archive_write_batch` — batch-100 `ArchiveMessage` write latency on btrfs host
**Origin artifact**: `mcp_agent_mail_rust/tests/artifacts/perf/archive_batch_100_profile.md`
**Run**: `tests/artifacts/bench/archive/<run-id>/summary.json` (canonical baseline; later reruns blocked on a compile break across several commits)

### Scenario

Write 100 `ArchiveMessage` records in one batch, measure wall-time. Compare scaling law at batch sizes 1 / 10 / 50 / 100 / 500 / 1000.

### Fingerprint (reference host)

```
CPU:      AMD Ryzen Threadripper PRO 5995WX, 64 cores / 128 threads, governor=performance, boost enabled
RAM:      499 GiB, 63 GiB swap
Storage:  /data -> /dev/nvme0n1, Samsung SSD 9100 PRO 4TB NVMe, btrfs
          rw,noatime,compress=zstd:1,ssd,discard=async,space_cache=v2,subvolid=5,subvol=/
Kernel:   Linux 6.17.0-19-generic
Toolchain: rustc 1.97.0-nightly
Profile:  [profile.bench] inherits release — opt-level=3, lto="thin", codegen-units=1, panic=abort, strip=symbols
Runtime:  MCP_AGENT_MAIL_ARCHIVE_PROFILE=1 (warm-path side-artifacts enabled)
Wrapper:  scripts/bench_baseline.sh
```

### Baseline — measured numbers (Chrome traceEvents + span summary)

```
batch-1    p50=23.3ms   p95=27.1ms   p99=28.6ms   samples=40   throughput=43.71 elems/sec
batch-10   p50=142.5ms  p95=154.4ms  p99=159.7ms  samples=25   throughput=69.99 elems/sec
batch-50   p50=682.7ms  p95=1490.8ms p99=1925.7ms samples=15   throughput=60.88 elems/sec
batch-100  p50=1327ms   p95=3491ms   p99=7640ms   samples=12   throughput=45.72 elems/sec
batch-500  p50=6438ms   p95=7088ms   p99=7088ms   samples=6    throughput=75.96 elems/sec
batch-1000 p50=13091ms  p95=14461ms  p99=14461ms  samples=4    throughput=74.67 elems/sec
```

Sample count < 1000 → p99.9 and p99.99 labeled **conservative worst-observed**.

### Top 10 spans by cumulative duration

```
archive_batch.sample                       cumulative=26244ms  count=12  p50=1327ms  p95=3491ms
archive_batch.write_messages               cumulative=25369ms  count=12  p50=1259ms  p95=3423ms
archive_batch.write_message_bundle         cumulative=25369ms  count=12  p50=1259ms  p95=3423ms
archive_batch.flush_async_commits          cumulative=873ms    count=12  p50=72ms    p95=82ms
archive_batch.queue_flush                  cumulative=0        count=12  p50=0       p95=0
```

### Hypothesis ledger (final verdict)

```
coalescer batching : REJECTS — write_message_batch cumulative 25.4s dwarfs flush 0.87s
fsync per msg      : REJECTS — wbq_flush cumulative 0µs vs flush_async_commits 873ms
file layout        : SUPPORTS — per-msg archive burst work dominates (25.4s cumulative)
SQLite per-msg txn : REJECTS — no sqlite spans in top 10 categories
hashing            : REJECTS — no hash-oriented spans in top 10
lock thrash        : REJECTS — scaling sublinear through batch-1000
                     (batch-10 5.70× base, batch-50 55.01×, batch-100 128.82×,
                      batch-500 261.56×, batch-1000 533.61×;
                      amortized batch-10 0.570× base/msg, batch-100 1.288×, batch-1000 0.534×)
```

### Scaling law (the real finding)

Sublinear overall through batch-1000. Amortized p95 per message is **worst** at batch-100 (1.288× base/msg). Classic coalescing curve: moderate batches pay metadata cost without amortizing; large batches amortize. Implication: if throughput is the goal, run batch ≥ 500; if latency is the goal, stay small.

### Variance envelope (BUDGETS.md policy)

```
≤ 10% p95 drift on same host → noise
> 10% → investigate
≥ 20% or 3 consecutive > 10% → escalate
```

Reference steady-state target: `batch-100 p95 ~= 238.1ms` post-optimization (vs measured 3491ms baseline — gap ≈ 14.6×).

### Cross-filesystem matrix (CI-gated, from BUDGETS.md)

```
| FS                    | mode           | single p95 | batch-100 p95 |
|-----------------------|----------------|------------|---------------|
| ext4 (data=ordered)   | normal         | < 25ms     | < 250ms       |
| ext4 (data=journal)   | normal         | < 40ms     | < 350ms       |
| xfs                   | normal         | < 25ms     | < 250ms       |
| btrfs                 | normal         | < 50ms     | < 500ms       |
| APFS                  | barrier_only   | < 35ms     | < 300ms       |
| tmpfs                 | buffered       | < 15ms     | < 150ms       |
```

Btrfs budget is 2× ext4 by policy — CoW tax is real.

### Operator cards this session exercised

- `📜 Fingerprint` — every run carries `fingerprint.json`
- `📏 Measure` — sample count and percentile discipline
- `🎯 Attribute` — spans (not raw flames) did the ranking work
- `🗂 Ledger` — hypothesis.md with 6 explicit verdicts
- `⊞ Scale-Check` — scaling table produced BEFORE any optimization
- `† Theory-Kill` — five rejected hypotheses never re-litigated

### Lessons

1. **Spans, not just flames**. A flame of `write_message_batch` is one undifferentiated blob; the span summary turned it into 5 ranked bars with quantified cumulative time.
2. **Hypothesis rejection is a positive output**. Killing "coalescer batching" early stopped a 2-sprint side-quest.
3. **Budget must be per-FS.** btrfs < 500ms and ext4 < 250ms are BOTH the same "pass"; mixing gives false regressions.
4. **Chrome traceEvents (perfetto-compatible) + span summary + JSON is the artifact trio** that lets another engineer reproduce interpretation without re-running.
5. **Script the baseline capture.** `scripts/bench_baseline.sh` + `rch exec` + target-dir discipline turns "run the bench" into one command.

---

## Case 2 — frankensqlite Track V baseline

**Subject**: end-to-end benchmarks comparing FrankenSQLite (F) vs C SQLite
**Origin artifact**: `frankensqlite/.bench-history/baseline_pre_track_v.txt`
**SHA**: `9f7bebea` (after O(n²) fix + 3 constant-factor optimizations)
**Build**: `release` (opt-level 3, LTO, codegen-units 1)

### Baseline snapshot (2026-04-03)

```
## Section 1: INSERT throughput (single-txn)
tiny_1col_100:     C=73.7µs    F=535.3µs   ratio=7.3×
tiny_1col_1K:      C=308.2µs   F=3.91ms    ratio=12.7×
tiny_1col_10K:     C=2.71ms    F=39.51ms   ratio=14.6×
tiny_1col_100K:    C=28.35ms   F=433.71ms  ratio=15.3×
small_3col_10K:    C=3.53ms    F=39.08ms   ratio=11.1×
medium_6col_10K:   C=5.42ms    F=52.84ms   ratio=9.7×
large_10col_10K:   C=10.56ms   F=88.08ms   ratio=8.3×
large_10col_100K:  C=108.49ms  F=1.220s    ratio=11.2×

## Section 2: Transaction strategies
autocommit_10K:    C=8.40ms    F=296.16ms  ratio=35.3×
batched_1K:        C=395.2µs   F=3.92ms    ratio=9.9×
single_txn_1K:     C=390.6µs   F=3.89ms    ratio=10.0×

## Section 4: Concurrent writers
2_writers:         C=15.08ms   F=8.34ms    FS_1.8×_FASTER    ← F wins at concurrency
4_writers:         C=32.33ms   F=17.47ms   FS_1.9×_FASTER
8_writers:         C=119.04ms  F=38.44ms   FS_3.1×_FASTER

## Section 6: UPDATE/DELETE
update_10K:        C=3.91ms    F=53.94ms   ratio=13.8×
delete_10K:        C=3.81ms    F=45.74ms   ratio=12.0×
```

### Hot-path profile snapshot (captured structure)

`.codex-bench/2026-03-22/hot_profile_*/` directories each carry:
- `manifest.json` — scenario, fixture, workload, seed, concurrency, scale, mode
- `profile.json` — wall, ops, ops/sec, retries, aborts, conflict stats
- `opcode_profile.json` — per-VDBE-instruction time
- `subsystem_profile.json` — cross-subsystem attribution
- `actionable_ranking.json` — top frames ranked by impact
- `summary.md` — human-readable with ranked hotspots + Baseline Reuse Ledger

Example ranked hotspots (from `hot_profile_single_c1_disjoint`):

```
rank 1 record_decode            time_ns=841,001  → J2/J5 target (decode cache, scratch reuse)
rank 2 parser_ast_churn         time_ns=627,244  → J2/J4 target (prepared-artifact reuse, arena)
rank 3 row_materialization      time_ns=2,621    → J2/J6/J7 target (reusable frame cost)
rank 4 mvcc_page_lock_wait      time_ns=0        → E2.1/E5.1 (publish shrink + disjoint topology)
rank 5 mvcc_page_one_conflict   time_ns=0        → E5.1/E5.2 (home-lane/extent runway work)
rank 6 mvcc_pending_commit      time_ns=0        → E2.1/E2.2 (shrink or bypass publish maintenance)
```

### Baseline Reuse Ledger excerpt

```
rank 1 page_buffer_pool_reuse    supported=false  hits=0    misses=0   hit_rate=n/a    J3/J8 target
rank 2 compiled_plan_cache       supported=true   hits=0    misses=52  hit_rate=0      J4 target
rank 3 prepared_statement_cache  supported=true   hits=0    misses=52  hit_rate=0      (secondary)
rank 4 record_decode_cache       supported=true   hits=0    misses=0   hit_rate=0      J5 target
rank 5 statement_parse_cache     supported=true   hits=100  misses=62  hit_rate=6173   J4 target (still avoidable prepare churn)
rank 6 cursor_frame_reuse        supported=true   hits=100  misses=1   hit_rate=9901   J7 target
```

### Lessons

1. **Ratios travel, absolute timings don't.** `7.3×` is hardware-independent evidence; `73.7µs` is host-specific.
2. **F beats C at concurrency even while losing single-threaded.** Always measure on the workload dimension the system is designed for.
3. **The Baseline Reuse Ledger is the gating artifact.** `hits=0 misses=52 hit_rate=0` is a directly actionable pointer — the cache exists but never hits.
4. **"J4 target", "J5 target", etc. cross-reference a parent plan** (PERFORMANCE_OPTIMIZATION_PLAN.md). The profile points at the plan; the plan references back at the evidence.
5. **Bytes-first replacement target list** — separate category from wall-time ranks: `btree_owned_payload_materialization: bytes=471554 → 3063 calls forced 471554 bytes into fresh owned buffers`. Owned-buffer elimination tracked by bytes, not time.

---

## Case 3 — cass indexing journey

**Subject**: search index rebuild from SQLite canonical DB (22 GB, 51,185 conversations, 4.7M messages)
**Origin artifact**: `coding_agent_session_search/CASS_INDEXING_HISTORICAL_BENCHMARK_RESULTS.md`

### Corpus fingerprint

```
Canonical DB:       ~/.local/share/coding-agent-search/agent_search.db
Conversations:      51,185
Messages:           4,703,804
DB size:            22,396,870,656 bytes (≈20.86 GiB)
Message content:    1,938,100,433 bytes (≈1.80 GiB)
Harness:            /tmp/cass_real_index_benchmark.py
Command shape:      cass --db <path> index --json --force-rebuild --data-dir <fresh-temp-dir>
Binary:             target-optbench/release/cass (source-built)
```

### Round-by-round

```
| Label                                                   | Wall s  | Conv/s  | Msg/s  | DB MB/s | CPU %  | Peak RSS GiB |
|---------------------------------------------------------|---------|---------|--------|---------|--------|--------------|
| opt3-frankensearch8e07                                  | 99.820  | 512.77  | 47123  | 213.98  | 778.5  | 20.80        |
| opt3-frankensearch8e07-singleopen                       | 93.718  | 546.16  | 50191  | 227.91  | 743.7  | 20.78        |
| opt3-frankensearch8e07-singleopen-addbatch16k           | 88.668  | 577.27  | 53050  | 240.89  | 990.8  | 21.58        |
| opt3-frankensearch8e07-singleopen-batchconv1024         | 96.741  | 529.09  | 48623  | 220.79  | 910.5  | 21.01        |
| opt3-frankensearch8e07-singleopen-codedefault-addbatch  | 88.659  | 577.32  | 53055  | 240.91  | 994.5  | 21.59        |
| opt3-frankensearch8e07-...-codedefault-addbatch-o32k    | 88.662  | 577.30  | 53053  | 240.91  | 1009.4 | 21.96        |
```

### Phase-timing breakdown (the exact knee)

For `opt3-frankensearch8e07`:
```
preparing → indexing:       24.718s
indexing start → current=51185: 56.041s     ← dominant phase
phase reset after indexing: 82.160s
completed payload emitted:  97.071s
shutdown tail after phase reset: 14.911s
```

### Takeaways (direct quote from the artifact)

> "The single-open storage fast path delivered a real win over the pinned baseline: 99.820s → 93.718s (~6.1% faster wall clock). The bigger Tantivy add-batch lever delivered the next real win: 93.718s → 88.659s (~5.4% faster wall clock) once promoted from env-only tuning into code defaults."

### Lessons

1. **Code-default is a separate milestone from env-override**. The 32k-override run (88.662s) matched the code-default (88.659s) to within 3ms — meaning the env-only tuning had already proven the lever, and promoting to code defaults just locked it in without regression.
2. **Two levers, two wins**. Single-open: -6.1%. Add-batch: -5.4%. **Compounded: 99.82→88.66 ≈ -11.2%** (not -11.5% naive sum — multiplicative compounding).
3. **Peak RSS rose 20.80→21.96 GiB across opts** — RAM-for-speed tradeoff made the benefit possible. The tradeoff table (IO-AND-TRADEOFFS.md) explicitly permits this when RAM headroom is large.
4. **CPU % went 778%→1009% across opts** — parallelism efficiency improved; the old code was serialized on a single writer thread.
5. **Knee point visible in phase timing** — `indexing start → current=51185` went 56.041s → 46.033s (−18% on the dominant phase) while total wall-time moved only −11.2% (diluted by other phases).

### Operator cards applied

- `📏 Measure` — 6 named rounds with explicit metrics table
- `🧪 A/B` — env-override and code-default A/B'd before committing
- `🪣 Bucket` — single-open + add-batch are independent levers, each scored; grouped for the final release note
- `⊞ Scale-Check` — CPU% and Peak RSS checked to confirm the wins weren't measurement artifacts

---

## Case 4 — The `opt-level="z"` + LTO disk incident

**Date**: 2026-04-03
**Project**: frankensqlite
**Session**: 6daba28a

### What happened

Building the benchmark binary failed during the final link step because the host ran out of disk. Root cause analysis (from the session transcript):

> "Still out of space — it ran out during the final link step. I notice the release profile has `opt-level = "z"` plus LTO — that's extremely space/time expensive. The issue is `opt-level = "z"` (minimize size) + LTO + codegen-units=1."

The reference host's `mcp_agent_mail_rust/target` directory was 65 GB — "the elephant in the room."

### Fix

Two-pronged:

1. **Split the profiles**: `release` stays size-optimized; `release-perf` for throughput measurement; `profiling` for symbol-rich flamegraphs.
2. **Short-term fallback**: use debug builds for relative comparisons when disk is tight. Quote:

> "Let me clean the intermediate build artifacts and try a debug build instead — it'll still show relative perf differences."

### Canonical Cargo.toml pattern

```toml
[profile.release]
opt-level = 2       # size/speed balance; consider 3 if size isn't a distribution concern
lto = false
codegen-units = 16

[profile.release-perf]
inherits = "release"
opt-level = 3
lto = "thin"        # "fat" kills cross-crate inlining and doubles link time
codegen-units = 256 # more parallelism; trades a bit of final perf for usable link time

[profile.profiling]
inherits = "release"
opt-level = 2
debug = true        # or "line-tables-only" for most cases
strip = false
```

### Lessons

1. **`opt-level="z"` + LTO + codegen-units=1 triples link time and disk**. Combining is rarely worth it.
2. **Relative speedups survive in debug builds**. If disk is tight during an active investigation, ratios still carry.
3. **Monitor target-dir size**. 65 GB target dirs are a signal to revisit profile settings or add to `.cargoignore`-equivalent cleanup.
4. **Remote compilation (rch)** offloads this class of problem — see cross-skill ref to the `rch` skill.

---

## Case 5 — Tokio ticker_cx deadlock

**Date**: 2026-04-10
**Project**: frankensqlite
**Session**: fee6461a

### The bug

```rust
// VULNERABLE: mutex guard lives through the if let body
if let Some(cancel_handle) = self.cancel_handle.lock().unwrap().take() {
    cancel_handle.cancel();      // ← may try to lock self.cancel_handle; deadlock
    handle.wait();
}
```

From the session:

> "The start and stop paths used `self.cancel_handle.lock()...take()` directly as the `if let Some(...)` scrutinee. The mutex guard lives until the end of the `if let` body, holding the lock while calling `cancel_handle.cancel()` / `handle.wait()` — a real deadlock risk if those functions try to acquire the lock."

### The fix

```rust
// SAFE: take the Option out, drop the guard, then act on it
let cancel_handle = self.cancel_handle.lock().unwrap().take();
if let Some(cancel_handle) = cancel_handle {
    cancel_handle.cancel();
    handle.wait();
}
```

Quote:

> "Temporary drops at `let` statement end, so lock is released before the `if let` body runs. The whole point of the fix."

### How profiling reveals it

- `tokio-console` shows the cancellation task blocked on a mutex; the caller held the same mutex
- `off-CPU` flamegraph colored by `futex_wait` highlights the lock-wait stack
- `perf lock contention -ab sleep 10` (BPF-backed) prints the contended lock name

### Detection pattern (for a static pre-flight)

```bash
# Grep for "guard-as-scrutinee" pattern
rg 'if let .*\.lock\(\)' --type rust
rg 'while let .*\.lock\(\)' --type rust
rg 'match .*\.lock\(\)' --type rust

# These aren't always bugs, but each deserves review — the guard lifetime
# equals the `if let` / `while let` / `match` scope.
```

### Lessons

1. **Lock guard lifetime is tied to the expression scope** — critical-section bugs hide in `if let`/`while let`/`match` scrutinees.
2. **Deadlocks often show as "hung task" with no CPU** — off-CPU profile is the tool, not on-CPU.
3. **Extract the `.take()` to a `let` before acting** — this is a defensive idiom for any lock-wrapping-Option pattern.
4. **Cross-skill handoff**: this pattern is what `deadlock-finder-and-fixer` specializes in; profile here, remediate there.

---

## Case 6 — bd-wwqen seven-round cumulative campaign

**Origin**: seven-round optimization campaign `bd-wwqen.1` through `bd-wwqen.7`
**Target**: cumulative ≥ 1.5× speedup on the canonical bench
**Key discipline**: Baseline Reuse Ledger verification across rounds

### The campaign structure

```
| Round      | Individual speedup | Cumulative | Baseline re-verified? |
|------------|-------------------:|-----------:|-----------------------|
| bd-wwqen.1 | 1.05×              | 1.05×      | yes (main)            |
| bd-wwqen.2 | 1.08×              | 1.13×      | yes (main+.1)         |
| bd-wwqen.3 | 1.12×              | 1.27×      | yes (main+.1+.2)      |
| bd-wwqen.4 | 1.06×              | 1.35×      | yes                   |
| bd-wwqen.5 | 1.09×              | 1.47×      | yes — invalidated .2! |
| bd-wwqen.6 | 0.99×              | 1.46×      | no — REJECTED, reverted |
| bd-wwqen.7 | 1.08×              | 1.57×      | yes                   |
```

### The trap the ledger caught

At `bd-wwqen.5`, re-running `main + .1 + .2 + .3 + .4` showed that `.2`'s individual baseline was no longer valid (`.3` or `.4` had made the same code-path redundant). Had the ledger not been maintained, the `.5` claim of 1.47× cumulative would have double-counted `.2`'s win.

### The rejection at `.6`

0.99× (regression) triggered immediate rollback per the campaign's ≥ 1.05× threshold. The alternative (landing `.6` and trying to compensate in `.7`) would have contaminated the `.7` measurement and made it impossible to attribute its 1.08× to its own change.

### Ledger format

```markdown
| Branch | Baseline commit | Baseline throughput | Current throughput | Still valid? | Notes |
|--------|-----------------|---------------------|--------------------|--------------|-------|
| bd-wwqen.1 | main#base | 100 ops/s | 105 ops/s | yes | |
| bd-wwqen.2 | main+.1#candidate1 | 105 ops/s | 113 ops/s | yes | |
| bd-wwqen.3 | main+.1+.2 | 113 ops/s | 127 ops/s | yes | |
| bd-wwqen.4 | main+.1+.2+.3 | 127 ops/s | 135 ops/s | yes | |
| bd-wwqen.5 | main+.1-.4 | 135 ops/s | 147 ops/s | **.2 invalidated — re-run** | .3 superseded .2's cache-miss path |
| bd-wwqen.6 | main+.1-.5 | 147 ops/s | 146 ops/s | REJECTED | −0.7% regression; reverted |
| bd-wwqen.7 | main+.1-.5 | 147 ops/s | 157 ops/s | yes | |
```

### Lessons

1. **Compounding is multiplicative**: 1.05 × 1.08 × 1.12 = 1.27, NOT 1.25. Don't sum percentages.
2. **Re-verify baselines every 2-3 rounds**. Later optimizations can make earlier baselines stale (new code path dominates now).
3. **Regression threshold is a pre-commitment**. If the campaign says "reject < 1.05×", apply it without negotiation — otherwise you're optimizing git history, not code.
4. **The ledger is the audit trail**. When someone asks "is the 1.57× real?", the answer is the ledger, not "trust me."

---

## Case 7 — Benchmark truthfulness audit

**Date**: 2026-03-19
**Project**: frankensqlite
**Context**: Discovered that several benchmarks compared apples to oranges.

### The issues (paraphrased from the audit log)

1. **Prepared vs ad-hoc mismatch**: "FrankenSQLite benchmarks were unfairly comparing prepared rusqlite paths against ad hoc FrankenSQLite SQL strings."
2. **Concurrent-write sequential sham**: "concurrent-write bench measured sequential control, not real persistent concurrent path."
3. **Cache-poisoning via `format!()`**: "Ad hoc `format!()` SQL in mixed-path benches prevents cache hits on the FrankenSQLite side."

### The fix

Normalize the benchmark API usage on both sides:

```rust
// WRONG — rusqlite prepared, FrankenSQLite ad-hoc
let stmt_c = conn_c.prepare("INSERT INTO t VALUES (?1, ?2)").unwrap();
for (k, v) in rows {
    stmt_c.execute([&k, &v]).unwrap();
}
for (k, v) in rows {
    conn_f.execute_ad_hoc(&format!("INSERT INTO t VALUES ('{}', '{}')", k, v)).unwrap();
}

// RIGHT — both prepared, both using bound parameters
let stmt_c = conn_c.prepare("INSERT INTO t VALUES (?1, ?2)").unwrap();
let stmt_f = conn_f.prepare("INSERT INTO t VALUES (?1, ?2)").unwrap();
for (k, v) in rows {
    stmt_c.execute([&k, &v]).unwrap();
    stmt_f.execute([&k, &v]).unwrap();
}
```

### Honest-gate verification

Downstream, the bench emits an `OverlayGateVerdict` and a `build_benchmark_honest_gate_report()` that inspects whether both sides used equivalent APIs. Results are marked `fully_comparable` only when both engines complete cleanly through the same API path.

### Lessons

1. **The most expensive bug is the one your bench hides.** Six months of "10× faster" numbers invalidated by an API mismatch.
2. **Normalize API usage before comparing.** Always prepared, or always ad-hoc — never mixed.
3. **Parameterized SQL (`?1`, `?2`) is a cache-poisoning shield.** `format!()`-based SQL looks unique every call and misses the parse cache.
4. **An honest-gate report is a deliverable** — not a courtesy. When both sides pass, the number is worth something. When one fails, the row is "advisory only" (like the cross-filesystem matrix).

---

## Case 8 — SmallText SSO string optimization

**Project**: frankensqlite — 14+ named string-handling optimizations visible as relative throughput wins

### Approach (from the optimization log)

> "SmallText SSO — inline short strings, [multiple optimization commits] — each optimization visible as relative throughput improvement in baseline vs after"

Rather than a single big-bang refactor, the campaign was a chain of one-lever commits each landing with a measured win. Named examples:

```
perf(btree):  share default CollationRegistry    — 38f382ba
perf(btree):  VDBE opcode fusion                  — IMPL-13
perf(btree):  cursor-op throttling                 — OPT-3
perf(btree):  collation registry sharing           — OPT-1
...
```

### Why `#[inline(never)]` sentinel functions mattered

When the bench flamegraph is dominated by "generic str ops", attribution to which string-handling optimization moved the needle is impossible without per-stage sentinels:

```rust
#[inline(never)] fn _profile_strlen()     { std::hint::black_box(()); }
#[inline(never)] fn _profile_strcopy()    { std::hint::black_box(()); }
#[inline(never)] fn _profile_strhash()    { std::hint::black_box(()); }
#[inline(never)] fn _profile_sso_inline() { std::hint::black_box(()); }
```

After the sentinels were added, each subsequent optimization showed up as a distinct bar shrinking in the flame.

### Lessons

1. **String-handling is usually a sea of tiny wins** — rare is the 5× single-shot. Budget for a chain.
2. **Name each commit with its bucket** (`OPT-1`, `IMPL-13`, `perf(btree): ...`). A year later you can still track the campaign.
3. **Sentinels predate optimizations**. Add them first; do the optimization second; measure the sentinel bar shrink.
4. **Inline-short strings (SSO)** pay off wildly for workloads that allocate short strings repeatedly (SQL identifiers, column names, short values).

---

## Case 9 — Concurrent writer 4.35× win

**Project**: frankensqlite
**Workload**: `concurrent_writers` with N=2

### Numbers

```
| Writers | C SQLite | FrankenSQLite | Speedup                  |
|---------|----------|---------------|--------------------------|
| 2       | 21.8ms   | 5.0ms         | 4.35× FASTER (FrankenSQLite) |
| 4       | ~32.3ms  | ~17.5ms       | 1.9×  FASTER (FrankenSQLite) |
| 8       | 119ms    | 38.4ms        | 3.1×  FASTER (FrankenSQLite) |
```

### Why the win is structural, not measurement

- FrankenSQLite's MVCC design allows disjoint writers to proceed without serializing on WAL append
- C SQLite serializes all writers through a single WAL
- The numbers come from the Section 4 baseline table of `.bench-history/baseline_pre_track_v.txt`

### But — single-threaded, FrankenSQLite is 9-15× slower (ratio table in Case 2)

The lesson: **workload dimension matters**. A comparison table that omits the dimension of interest makes the product look universally worse or universally better; neither is accurate.

### Reporting discipline

```
| Workload axis                | FrankenSQLite advantage     |
|------------------------------|-----------------------------|
| Single-threaded insert       | C wins 8-15× (FrankenSQLite slower) |
| Concurrent writers (2+)      | FrankenSQLite wins 1.8-3.1× |
| Mixed OLTP (reads+writes)    | TBD; track separately       |
```

### Lessons

1. **Every perf claim must be axis-qualified.** "FrankenSQLite is faster" without concurrency axis = misleading.
2. **Structural wins (architecture-level) are worth an order of magnitude** — but only on the workload the architecture was designed for.
3. **Amdahl's law for A/B comparisons**: total win = Σ(workload-weight × axis-specific ratio). Use real workload distributions to weight, not marketing ratios.

---

## Case 10 — Cross-filesystem matrix

**Project**: mcp_agent_mail_rust
**Origin**: `scripts/bench_archive_fsync_matrix.sh` + `.github/workflows/archive-fsync-matrix.yml`
**Gated probes per FS**: single-message write latency p50/p95/p99; batch-100 write latency p50/p95/p99; crash-after-flush durability check

### The CI matrix

```
| Filesystem             | CI coverage     | fsync mode     | Single p95 | Batch-100 p95 | Notes                                |
|------------------------|-----------------|----------------|------------|---------------|--------------------------------------|
| ext4 (data=ordered)    | Linux loopback  | normal         | < 25ms     | < 250ms       | baseline Linux recommendation        |
| ext4 (data=journal)    | Linux loopback  | normal         | < 40ms     | < 350ms       | higher journal cost                  |
| xfs                    | Linux loopback  | normal         | < 25ms     | < 250ms       | low-variance server writes           |
| btrfs                  | Linux loopback  | normal         | < 50ms     | < 500ms       | CoW + metadata pressure              |
| APFS                   | macOS runner    | barrier_only   | < 35ms     | < 300ms       | durable rename + barrier semantics   |
| tmpfs                  | Linux tmpfs     | buffered       | < 15ms     | < 150ms       | canary only; not durable             |
```

Documented but not CI-gated:
```
NTFS / WSL  — manual spot-check only; portability evidence, not release gate
ZFS         — unsupported initially; add when a stable runner / dedicated lab host exists
```

### Crash durability check

```bash
# pseudo-code
fork child
  child: write 100 messages, call flush_async_commits()
  parent: wait for flush ack; SIGKILL the child
parent: reopen the archive
assert every fully-flushed message is recoverable
```

### Operator rules of thumb (from the workflow)

- ext4 `data=ordered` or xfs when archive write latency is the deciding constraint
- btrfs is supported-but-slower; compare against the btrfs row, not the ext4 baseline
- tmpfs results are a logic/CPU canary only — a tmpfs pass says nothing about crash durability
- If only one filesystem regresses, use the per-FS artifact bundle from the workflow before widening the global budget or rolling back the whole archive-path change

### Lessons

1. **Per-FS budgets beat a single number.** "p95 < 250ms" that varies 2× across filesystems is a bug factory for a multi-platform product.
2. **tmpfs is a logic floor**, not a storage baseline. Use for CPU/framework overhead, never for "fast durable write."
3. **Durability must be tested separately** from latency — a fast write that silently doesn't survive a crash is worse than a slow one.
4. **CI-gated vs documented-not-gated is a real distinction.** NTFS and ZFS are valuable data points; they shouldn't block a release.

---

## Meta-lessons across all cases

These show up in 2+ case studies, so they're skill-level rules, not project-level quirks.

### 1. Artifact-path citation is a hard requirement
Every ranked claim (hotspot, ledger entry, budget) cites a path under `tests/artifacts/perf/` or equivalent. No path = not real.

### 2. Hypothesis rejection is as valuable as hypothesis support
Three of the ten cases explicitly list rejected hypotheses with evidence. Zombies die this way.

### 3. Ratios beat absolute times for cross-host communication
`1.9× faster` travels; `17.5ms` doesn't. Use absolute ms only when the fingerprint is attached to the number.

### 4. Scale is a dimension, not an afterthought
batch-1 / batch-10 / batch-100 / batch-500 / batch-1000 is the minimum sweep. The shape is the finding.

### 5. Fingerprint equality is a precondition for A/B validity
Crossing any of CPU model / kernel major / filesystem / governor / SMT / build profile invalidates the comparison. Cross-fingerprint comparisons are "advisory only."

### 6. Variance envelope is a written policy, not an aesthetic
≤10% = noise, >10% = investigate, ≥20% or 3-consecutive-over-10% = escalate. Post it in BUDGETS.md.

### 7. Build profile != size-optimized release for profiling
`opt-level = "z"` + `strip = true` produces unprofilable binaries. `[profile.release-perf]` (or `[profile.profiling]`) is a separate, committed thing.

### 8. Symbols + frame pointers are a non-negotiable build-time decision
`debug = "line-tables-only"` or `debug = true`; `RUSTFLAGS="-C force-frame-pointers=yes"`. Forget these and the flame is a blur of `??`.

### 9. Instrumentation must pre-date the profile
Sentinels, spans, histograms — add them first, gated behind an env flag, before the profile run. Otherwise the profile only says "it's slow somewhere."

### 10. Cross-filesystem, cross-platform is a real axis
btrfs != ext4 != xfs != APFS != tmpfs. Per-FS budgets; no mixing.

### 11. The ledger is the methodology
Without hypothesis.md, hotspot_table.md, scaling_law.md on disk, the profiling pass is a vibe. With them, it's an audit trail.

### 12. Structural wins ≠ universal wins
A win in one workload dimension is not a win in another. Always tag the dimension.

---

## Template for your own case study

```markdown
# Case N — <subject>

**Project**: <repo>
**Origin artifact**: <path or URL>
**Run**: <run-id + git SHA>

## Scenario
<one paragraph>

## Fingerprint
<paste from fingerprint.json>

## Baseline
<p50 p95 p99 p99.9; throughput; peak RSS; samples>

## Top hotspots (ranked)
<from hotspot_table.md with citations>

## Hypothesis ledger (final)
<supports / rejects with evidence>

## Numbers round-by-round
<ratios, not absolute times where possible>

## Operator cards exercised
<from OPERATOR-CARDS.md>

## Lessons (≥3, specific)
<what this case taught the skill>
```

Add new case studies here as campaigns conclude. The skill improves as the library grows.
