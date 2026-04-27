# Unbiased Benchmarking — Fair Head-to-Head Comparison

> How to compare implementations (v1 vs v2, system A vs system B, C SQLite vs FrankenSQLite, library X vs library Y) without fooling yourself or the audience. The frankensqlite "honest-gate" pattern made concrete.

## Contents

1. [Why this matters (and the FrankenSQLite audit)](#why-this-matters-and-the-frankensqlite-audit)
2. [FrankenSQLite methodology — the ground truth](#frankensqlite-methodology--the-ground-truth)
3. [The five levels of fairness](#the-five-levels-of-fairness)
4. [API normalization — prepared vs ad-hoc](#api-normalization--prepared-vs-ad-hoc)
5. [Cache poisoning and how to avoid it](#cache-poisoning-and-how-to-avoid-it)
6. [Warmup policy — the same way on both sides](#warmup-policy--the-same-way-on-both-sides)
7. [When apples-to-oranges IS the right comparison](#when-apples-to-oranges-is-the-right-comparison)
8. [Multi-dimensional reporting](#multi-dimensional-reporting)
9. [The honest-gate audit](#the-honest-gate-audit)
10. [Workload fixture discipline](#workload-fixture-discipline)
11. [Dual-direction reporting (don't hide losses)](#dual-direction-reporting-dont-hide-losses)
12. [Checklist](#checklist)
13. [Anti-patterns encyclopedia](#anti-patterns-encyclopedia)

---

## Why this matters (and the FrankenSQLite audit)

FrankenSQLite's "Benchmark Truthfulness Audit" found three separate hidden biases:

1. **Prepared vs ad-hoc mismatch**: "FrankenSQLite benchmarks were unfairly comparing prepared rusqlite paths against ad hoc FrankenSQLite SQL strings"
2. **Concurrent-write sequential sham**: "concurrent-write bench measured sequential control, not real persistent concurrent path"
3. **Cache-poisoning via `format!()`**: "Ad hoc `format!()` SQL in mixed-path benches prevents cache hits on FrankenSQLite side"

Six months of "10× faster" numbers were revised after the audit. The lesson is general: **the benchmarks you don't audit are the ones that lie to you**.

Unbiased benchmarking is a skill. It's not the default behavior. Every adversarial reviewer you don't invite, your bench will still eventually meet — in the form of a user who actually tried it and noticed it's slower than advertised.

---

## FrankenSQLite methodology — the ground truth

This section is the canonical template distilled from the FrankenSQLite benchmarking harness. Cite equivalent files when building your own harness — they are the worked solution to "how do I run a fair head-to-head between architecturally-different systems?"

### Files in the FrankenSQLite repo

```
crates/fsqlite-e2e/
├── METHODOLOGY.md                          ← the charter
├── benches/
│   ├── mixed_oltp_bench.rs                 ← 80/15/3/2 mix, deterministic seed
│   ├── concurrent_write_bench.rs           ← multi-writer contention
│   ├── read_heavy_bench.rs
│   ├── large_txn_bench.rs
│   ├── write_throughput_bench.rs
│   └── operation_baseline_bench.rs         ← per-op latency isolation
└── src/
    ├── methodology.rs                      ← constants (warmup, N, env capture)
    ├── benchmark.rs                        ← BenchmarkRunner::run() loop
    ├── fairness.rs                         ← BENCHMARK_PRAGMAS + verify fns
    ├── overlay_honesty_gate.rs             ← BelowParity / ParityToMargin / HealthyMargin
    └── bin/realdb_e2e.rs                   ← CLI harness
```

Result artifacts live under `sample_sqlite_db_files/working/<fixture>/<run_id>/results/` as markdown tables per scenario — self-auditable forever.

### The BENCHMARK_PRAGMAS contract (verbatim)

From FrankenSQLite's `fairness.rs` — both engines must configure these identically before any timed measurement. A divergence halts the run with a diagnostic.

```rust
// canonical fairness contract
("page_size",     "4096"),   // Default SQLite page size
("journal_mode",  "wal"),    // Both engines' fastest concurrent mode
("synchronous",   "1"),      // NORMAL: production-realistic durability/speed balance
("temp_store",    "2"),      // MEMORY: avoid disk I/O variance
("mmap_size",     "0"),      // Test page cache, not OS mmap
("auto_vacuum",   "0"),      // No non-deterministic background vacuuming
("cache_size",    "-64000"), // 64 MB (negative = KiB notation)
```

Pragma enforcement isn't advisory — it's a gate (`verify_rusqlite_pragmas()` / `verify_fsqlite_pragmas()` in `fairness.rs:80-214`). When pragmas disagree, the bench refuses to run rather than producing numbers that are quietly incomparable.

### The methodology constants (verbatim)

From `fsqlite-e2e/src/methodology.rs:39-101`:

| Constant | Value | Why |
|---|---|---|
| Warmup iterations | **3** (discarded) | Eliminates cold-cache, JIT, first-allocation effects |
| Min measurement iterations | **20** (after warmup) | Fixed floor prevents wall-clock bias on slower hardware |
| Measurement time floor | **10 seconds** | Criterion keeps sampling until ≥ 10s *and* ≥ 20 samples |
| Fresh DB per iteration | **Yes** | Each iter starts from golden copy — no state leakage |
| Identical pragmas | **Enforced** | Both engines run `HarnessSettings` converted per-engine |
| Primary statistic | **Median** | Robust to GC pauses, OS jitter, background I/O |
| Tail statistic | **p95** | Captures tail without p99's single-outlier sensitivity |
| Per-iter record | latency, retry_count, abort_count | `IterationRecord` in `benchmark.rs:126` |
| Environment capture | `EnvironmentMeta` struct | OS, arch, CPU, RAM, rustc, cargo profile (`methodology.rs:196-221`) |
| Build-level contract | `release-perf` profile | LTO=true, codegen_units=1, debug=false, strip=true (`methodology.rs:155`) |

### The three-tier classification (verbatim)

From `fsqlite-e2e/src/overlay_honesty_gate.rs:26-276`. Instead of a binary pass/fail, classify the result:

| Tier | Criterion | What it means |
|---|---|---|
| `BelowParity` | fsqlite p95 > 1.25× sqlite3 | Clearly slower — call it out, do not hide |
| `ParityToMargin` | within 1.25× ratio | Within noise — report, don't claim a win |
| `HealthyMargin` | fsqlite ≥ 1.10× baseline | Clear win, backed by p95 (not just mean) |

**Why three tiers and not one p-value:** percentiles are noisy in absolute terms but ratios are more stable. 1.25× is the `DEFAULT_MAX_P95_RATIO` (`fairness.rs`). Tighter projects can raise the bar to 1.10×.

### The workload list (real names from the repo)

From `fsqlite-e2e/src/workload.rs` and bench files:

| Workload | What it exercises | File |
|---|---|---|
| `commutative_inserts_disjoint_keys` | Pure write-lock serialization (non-overlapping keys, no PK contention) | `benches/concurrent_write_bench.rs` |
| `hot_page_contention` | Concurrent writers target same pages repeatedly | `benches/concurrent_write_bench.rs` |
| `mixed_read_write` | 80% SELECT / 15% INSERT / 3% UPDATE / 2% DELETE, seed-deterministic | `benches/mixed_oltp_bench.rs` |
| `read_heavy` | Mostly-read, cache-behavior-sensitive | `benches/read_heavy_bench.rs` |
| `large_txn` | Throughput with big transactions | `benches/large_txn_bench.rs` |
| `operation_baseline` | Per-operation latency isolation | `benches/operation_baseline_bench.rs` |

Concurrency levels tested in every workload: **c1, c4, c8**. Pair the concurrency with the workload — `commutative_inserts @ c1` is a very different benchmark from `hot_page_contention @ c8`.

### Concrete measured numbers (with file:line)

From `sample_sqlite_db_files/working/beads_bench_20260310/results/mvcc_vs_sqlite3.md`:

**commutative_inserts_disjoint_keys @ c1** (single-threaded, no contention)
```
sqlite3:        median  29.0 ms,  p95  29.0 ms,  6,945 ops/sec
fsqlite (mvcc): median 480.0 ms,  p95 495.8 ms,    298 ops/sec
ratio           16.6× slower (fsqlite MVCC)
```

**hot_page_contention @ c4** (contended writes, the actual differentiator)
```
sqlite3:        median   89.0 ms,  p95  188.2 ms,  5,467 ops/sec
fsqlite (mvcc): median 1166.0 ms,  p95 1178.4 ms,    169 ops/sec
ratio           13.1× slower
```

And from `post_snapshot_skip_c1_single.md` — the **same fixture, same workload**, measured across an optimization:

```
before snapshot-skip (c1): median 445.0 ms,   321 ops/sec
after snapshot-skip  (c1): median 113.0 ms, 1,282 ops/sec
speedup                     3.94× (332 ms saved)
```

This is what "hand-off to extreme-software-optimization" looks like after we did our job: a before/after pair with p95 + median + ops/sec on the exact same fixture, reproducible from the `HarnessSettings` spec.

### The canonical harness command (verbatim)

From `fsqlite-e2e/METHODOLOGY.md:119-133`:

```bash
# Single workload, single concurrency
cargo run -p fsqlite-e2e --bin realdb-e2e -- run \
  --db chinook --workload commutative_inserts --engine sqlite3

# Scaling sweep with repeats
cargo run -p fsqlite-e2e --bin realdb-e2e -- run \
  --db chinook --workload commutative_inserts --engine sqlite3 \
  --concurrency 1,2,4,8 --repeat 5

# Criterion benchmarks (uses methodology constants)
cargo bench -p fsqlite-e2e
```

Our `scripts/bench_baseline.sh` is modeled on this command shape: one workload per invocation, concurrency as an explicit arg, repeat count as an explicit arg, fingerprint emitted next to the result.

### Why MVCC-vs-single-writer IS the right comparison

From `concurrent_write_bench.rs:7-14`:

> Measures aggregate INSERT throughput when multiple threads write concurrently. C SQLite uses WAL mode with `busy_timeout` for write serialisation; FrankenSQLite runs the equivalent operations sequentially (MVCC concurrent writer path is not yet wired to persistence). Do not cite the FrankenSQLite control in this file as concurrent-writer evidence; it is only a fairness-normalized same-total-work control.

That's the apples-to-oranges principle made honest: **the comparison IS the point** (MVCC is the reason FrankenSQLite exists), but the harness explicitly flags what each run does and does NOT prove. The file comment *inside the bench* tells future readers what they're allowed to cite.

See `APPLES-TO-APPLES-MATRIX.md` for the general decision framework.

---

## The five levels of fairness

Each level is a stronger guarantee. Stop when the guarantee matches the claim you want to make.

### Level 0 — "Both sides run"

Weakest. Both implementations complete the workload without error. You have numbers. You have almost nothing else.

### Level 1 — "Same workload"

Both sides process the same input. Same record count, same queries, same payloads. No cherry-picking per side.

### Level 2 — "Same API class"

If side A uses prepared statements, side B also uses prepared statements. If A batches, B batches. If A is async, B is async (or both sync). No "A got the fast path, B got the slow path."

### Level 3 — "Same cache state"

Both sides start with the same cache state (usually both cold or both warm). Both sides see the same fraction of warm cache hits. If warmup differs (e.g., side A has a larger cache so caches more after a warmup round), document it.

### Level 4 — "Same physical constraints"

Same host, same CPU, same governor, same kernel, same storage, same filesystem. Same measurement window (interleaved, not sequential). Same noise profile.

### Level 5 — "Same data shape and access pattern"

Same key distribution (Zipfian α, record size distribution, session lengths). Same arrival pattern. Same error/retry injection.

**What you can claim** at each level:

- L0: "Both implementations are functional"
- L1: "Numbers are in this range"
- L2: "API-level difference on this workload class"
- L3: "Real performance difference on this workload"
- L4: "Real performance difference, reproducible on this host"
- L5: "Real performance difference for production-like traffic"

Papers, blog posts, and marketing-ready claims should be L5 where possible. Internal engineering decisions can usually ride at L3-L4.

---

## API normalization — prepared vs ad-hoc

The biggest foot-gun. Concrete examples:

### Wrong (favors rusqlite unfairly)

```rust
// Side A: rusqlite with prepared statement (cached)
let mut stmt_c = conn_c.prepare("INSERT INTO t (k, v) VALUES (?1, ?2)")?;
for (k, v) in rows {
    stmt_c.execute([&k, &v])?;
}

// Side B: FrankenSQLite with ad-hoc, format!-ed SQL (no cache hit)
for (k, v) in rows {
    let sql = format!("INSERT INTO t (k, v) VALUES ('{}', '{}')", k, v);
    conn_f.execute(&sql)?;
}
```

Side B pays: parse + compile + plan per row. Side A pays: bind + execute per row. Numbers are not comparable.

### Right (both prepared)

```rust
let mut stmt_c = conn_c.prepare("INSERT INTO t (k, v) VALUES (?1, ?2)")?;
let mut stmt_f = conn_f.prepare("INSERT INTO t (k, v) VALUES (?1, ?2)")?;
for (k, v) in rows {
    stmt_c.execute([&k, &v])?;
    stmt_f.execute([&k, &v])?;
}
```

### Right (both ad-hoc, but parameterized)

```rust
for (k, v) in rows {
    conn_c.execute("INSERT INTO t (k, v) VALUES (?1, ?2)", [&k, &v])?;
    conn_f.execute("INSERT INTO t (k, v) VALUES (?1, ?2)", [&k, &v])?;
}
```

Each driver may cache internally; as long as both drivers get the same SQL-string sequence, comparable.

### Rule

One driver should never see a different SQL-string sequence than another. The `?1`, `?2` binding is what keeps cache lookups consistent — `format!`-ing values into the SQL breaks the cache per call.

### For non-SQL APIs

Same principle: "both sides use the batch API" or "both sides use the item API." Never mix. If one system has a batch API the other lacks, document the benchmark as a one-API test, not a head-to-head.

---

## Cache poisoning and how to avoid it

Caches (parse, plan, prepared-statement, buffer pool, dentry, page) make benchmarks touchy. Concrete rules:

1. **Same SQL/key shape across runs per side.** `f"SELECT * FROM t WHERE k = '{key}'"` invalidates the parse cache each iteration; `"SELECT * FROM t WHERE k = ?"` hits.
2. **Don't warm one side's cache while cold-starting the other.** If you run side A then side B without interleaving, A's pages may be in the OS page cache by the time B runs, giving B a free boost (or vice-versa).
3. **Document cache expectations per scenario.** "Warm cache steady-state" vs "cold-start first-request" are different regimes; benchmarking both separately is fine — mixing them is not.
4. **Interleave rather than sequentially run.** Instead of `AAAA…BBBB…`, run `ABABAB…` or random `A|B` order with fixed seed.
5. **For fsync-heavy workloads**, rotate the backing file per run if durability state carries over.

---

## Warmup policy — the same way on both sides

```
wrong: Side A warms up for 30 sec, Side B for 5 sec (because it "looked stable faster")
right: Both sides warm up until p95 is within ±3% over 3 consecutive windows

wrong: Side A measured once, Side B measured 20 times (averaging out Side B's outliers)
right: Both measured the same N times, report the same percentiles
```

Criterion does this correctly by default. If you write custom benches, codify the warmup/measurement policy and apply identically.

---

## When apples-to-oranges IS the right comparison

Sometimes the comparison you need IS NOT L5-fair, and that's the right answer. Example from frankensqlite:

> "Concurrent writers is one of THE main reasons for the existence of the frankensqlite project in the first place"

FrankenSQLite's MVCC concurrent-writer path vs C SQLite's serialized-writer path is NOT an apples-to-apples API comparison — they use fundamentally different APIs and semantic models. Forcing "fairness" (e.g., running FrankenSQLite in single-writer mode for the comparison) would hide the entire point of the project.

The right approach: **label the comparison explicitly** and report on BOTH the fair axes AND the designed-to-differ axes.

```markdown
## Multi-writer throughput (different architectures, same workload goal)

| Writers | C SQLite (serialized) | FrankenSQLite (MVCC) | Δ     | Interpretation          |
|--------:|----------------------:|---------------------:|------:|-------------------------|
|      2  |               21.8ms |                5.0ms | 4.35× | F's MVCC allows disjoint writers without serializing |
|      4  |               32.3ms |               17.5ms | 1.85× | Both systems partially saturate (F less so)          |
|      8  |              119.0ms |               38.4ms | 3.10× | F scales better past C's global writer lock          |

Note: C SQLite is architecturally a single-writer system. This comparison
measures whether FrankenSQLite's MVCC delivers on the promise of concurrent
writers — NOT whether FrankenSQLite is a drop-in faster replacement.

## Single-writer throughput (fair comparison, same architecture)

| Operation           | C SQLite | FrankenSQLite | ratio | Interpretation       |
|---------------------|---------:|--------------:|------:|----------------------|
| tiny_1col_100       |  73.7µs  |     535.3µs   | 7.3×  | F slower (expected)  |
| autocommit_10K      |  8.40ms  |    296.16ms   | 35.3× | F slower (expected)  |
| update_10K          |  3.91ms  |     53.94ms   | 13.8× | F slower (expected)  |

F's MVCC adds overhead per operation; the concurrent-writer table is the
workload where that overhead pays off.
```

This is the honest version. Both tables appear. The interpretation text says WHAT the comparison is actually showing.

### Rule

An apples-to-oranges comparison is honest **only if**:
- The semantic mismatch is the point
- The mismatch is stated explicitly
- A fair comparison ALSO appears (or an explanation why one isn't meaningful)

### Examples of valid apples-to-oranges

- **Concurrent model**: MVCC vs serialized (as above)
- **Consistency**: strict serializable vs eventual
- **Durability**: sync commit vs async WAL
- **Query language expressiveness**: full SQL vs restricted KV
- **Memory model**: tracing GC vs ref-count vs arena
- **Compilation model**: AOT vs JIT
- **Concurrency runtime**: stackful vs stackless (Go vs Tokio)

### Examples of invalid apples-to-oranges

- "Our new HTTP server is 10× faster than Apache!" — but new server doesn't handle HTTPS, WebSockets, CGI, or module loading like Apache does.
- "Our database beats Postgres on reads!" — but with ACID off.
- "Our language is faster than Python!" — but the benchmarks avoid dynamic dispatch / duck typing.

If the claim implies general superiority, the comparison must be fair. If the claim is scoped to a specific axis, the scope must be in the headline.

---

## Multi-dimensional reporting

One number = one claim. Real systems have tradeoffs across axes. Report in a **matrix**, not a point.

Recommended minimum dimensions:

```
                          Throughput          p95 latency       Peak memory       Cold-start
                          --------------------------------------------------------------------
single-thread             ...                 ...               ...               ...
2 writers                 ...                 ...               ...               ...
8 writers                 ...                 ...               ...               ...
read-heavy (95% R, 5% W)  ...                 ...               ...               ...
write-heavy (5% R, 95% W) ...                 ...               ...               ...
small records (1 KB)      ...                 ...               ...               ...
large records (1 MB)      ...                 ...               ...               ...
```

Per cell: `(A_value / B_value ratio)` where the ratio direction is explicit (>1 = A faster or <1 = A faster, state it).

### Hyperbolic honesty pattern

If your system wins on 5 cells and loses on 3, **show all 8**. Systems that hide losses attract credibility complaints; systems that publish losses attract trust.

FrankenSQLite's Section 1 (INSERT throughput, 7-35× slower than C SQLite single-thread) appears in the baseline. That's the losses side. Section 4 (concurrent writer 1.8-4.35× faster) appears alongside. That's the wins. Both visible. Readers trust the reporting.

---

## The honest-gate audit

Encode benchmark-fairness checks as an automated artifact, like frankensqlite's `build_benchmark_honest_gate_report()`.

Checks to automate:

1. **API parity**: both sides use the same call shape per scenario
2. **Cache-hit parity**: if one side's cache hits, so does the other (or the mismatch is intentional and labeled)
3. **Identical input**: same records, same order, same seeds
4. **Identical output**: same result set (byte-identical or semantically equivalent)
5. **Interleaved execution**: warmup/measurement order not biased
6. **Environment parity**: same fingerprint
7. **Variance parity**: CV within 2× of each other (if one side is 3% CV and the other is 30%, the measurement of the noisier side is untrustworthy)

Output: a report like
```markdown
## Honest Gate — archive_batch_100 — 2026-04-18

| Check                       | A (ext4)   | B (xfs)    | Pass? |
|-----------------------------|-----------:|-----------:|-------|
| Identical input rows        |     100    |     100    | ✓     |
| Same API (batch_write)      |        ✓   |        ✓   | ✓     |
| Same commit policy          |  fdatasync |  fdatasync | ✓     |
| Variance (CV)               |      2.1%  |      3.4%  | ✓     |
| Output bytes identical      |     8192   |     8192   | ✓     |
| Interleaved run order       |        ✓   |        ✓   | ✓     |

Verdict: FULLY_COMPARABLE. Claim ratio is trustworthy.
```

Every bench output should carry a gate verdict. Non-comparable runs are advisory-only.

---

## Workload fixture discipline

From `WORKLOAD-GENERATORS.md`: realistic workloads are Zipfian, log-normal-sized, bursty. But they also need to be **reproducible**.

### Seeded, deterministic, versioned

```rust
let seed = 0xCAFEBABE_u64;
let mut rng = StdRng::seed_from_u64(seed);
let keys: Vec<u64> = (0..N).map(|_| zipf_sample(&mut rng, KEY_COUNT, 1.0)).collect();
```

Record the seed in the bench output. Same seed → same input across runs and across sides.

### Corpus-based fixtures (recommended for database benches)

FrankenSQLite uses "golden database corpora" — versioned, checksum-pinned, realistic datasets. Same corpus on both sides:

```
sample_sqlite_db_files/
├── golden/                    # read-only source of truth
│   ├── small.sqlite    sha256=...
│   ├── medium.sqlite   sha256=...
│   └── large.sqlite    sha256=...
└── working/                   # per-run copies; one per side
```

Before each run, rsync from `golden/` to a fresh `working/` dir. Both sides open identical working copies.

### Synthetic variance across runs

For multi-run benches, vary the seed between runs to cover the distribution; keep seed constant across A vs B for a single run.

---

## Dual-direction reporting (don't hide losses)

A common bias: report "X is 2× faster" but hide that "X is 5× slower on workload Y."

Mandatory sections in any perf report:

1. **Workload matrix** (the multi-dim table above)
2. **Where we win** (short list of cells > 1.0 ratio)
3. **Where we lose** (short list of cells < 1.0 ratio with honest explanation)
4. **Draw conditions** (cells where ratio is within ±10%)
5. **Design rationale** (why wins and losses align with the architecture's goals)

Leaving out section 3 is the single most common form of benchmark dishonesty — whether accidental or intentional.

### Front-load the hardest case

If your system is positioned as X but loses on a case that X-users care about, lead with that case in the report and explain it. Trying to hide it is the quickest way to lose reader trust.

---

## Checklist

Before publishing any comparative benchmark:

- [ ] Both sides' API calls documented side-by-side
- [ ] Same input on both sides (seeded, same corpus)
- [ ] Interleaved execution order (ABAB not AAAA BBBB)
- [ ] Same warmup policy per side
- [ ] Cache-state documented (cold / warm / hot) — same on both sides
- [ ] Variance envelope passed on both sides (CV < 10%; ratio of CVs < 2×)
- [ ] Fingerprint identical on both sides (same host, same kernel, etc.)
- [ ] Output equivalence verified (byte-identical OR semantically equivalent AND documented why)
- [ ] Multi-dimensional table, not a single number
- [ ] Wins AND losses published; draw conditions noted
- [ ] Designed-to-differ axes labeled as such
- [ ] Honest-gate verdict attached (FULLY_COMPARABLE | ADVISORY | NOT_COMPARABLE)
- [ ] Report uses ratios, not absolute ms (or reports both with fingerprint attached)

If ANY checkbox is unchecked, the report is **provisional** and must be labeled "internal review only."

---

## Anti-patterns encyclopedia

| Anti-pattern | How it lies | How to avoid |
|--------------|-------------|--------------|
| Prepared vs ad-hoc mismatch | Cache hit on one side, miss on the other | Normalize API on both sides |
| `format!`-ed SQL | Parse cache misses each call | Parameterized bind, always |
| Mean instead of percentile | Tail hidden | Report p50/p95/p99/p99.9 |
| Warmup-then-measure only one side | Other side is cold | Identical warmup schedule |
| Best-of-N without median-of-N | Lucky runs dominate | Report median with CI |
| Different workloads per side | Side A easier input | Same corpus, same seed |
| Closed-loop load on "throughput" claim | Backpressure lies | Open-loop (wrk2, vegeta, k6 at fixed rate) |
| Sequential run order AAA…BBB… | Thermal drift across transitions | Interleave ABAB |
| Side A's errors hidden as retries | A looks faster while failing silently | Report error rates per side |
| Side A's errors counted in latency | A looks slower while succeeding | Same error-handling policy |
| Bench on CI runner, claim on prod | Hardware mismatch | Match hardware OR relax claim |
| Benchmark that doesn't include realistic concurrency | Single-thread numbers lie | Multi-concurrency matrix |
| "X is N× faster" without budget | No threshold; reader can't judge | Attach budget from BUDGETS.md |
| Hiding a failed honest-gate | Wink-wink claim | Mark ADVISORY explicitly |
| Running against DB in development mode | No sync, no WAL, no durability | Production-config on both sides |
| Cherry-picked scenario list | Only favorable cases | Matrix with everything |
| Claim "10× faster" on workload reviewers won't run | Unfalsifiable | Include repro fixtures + corpus hashes |
| "X uses less memory" without budget | Meaningless without scale | Tie memory to workload size |

---

## Meta-lesson

Fair benchmarks are **work to build, not work to avoid.** The honest-gate audit takes real engineering time. Budget for it. The alternative is eventually a user saying "your claim is wrong" — a much more expensive conversation.

And where a fair comparison hides the core point of your system (e.g., concurrent writers in FrankenSQLite vs serialized writers in C SQLite), **do the unfair comparison AND a fair one**, publish both, and explain.

The goal isn't fairness for fairness's sake. The goal is **numbers a reader can trust to make decisions**.
