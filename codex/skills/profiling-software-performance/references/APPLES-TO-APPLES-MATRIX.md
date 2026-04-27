# Apples-to-Apples Matrix — What Must Match, What IS the Point

> Most "apples to oranges" warnings are lazy. The right question is NOT "are these identical?" but "which axes must match for the claim I want to make, and which axis is the design difference I am trying to measure?" This file gives you the decision framework, with a worked example from FrankenSQLite.

## Contents

- [The core insight](#the-core-insight)
- [The matrix](#the-matrix)
- [Worked example: MVCC vs single-writer](#worked-example-mvcc-vs-single-writer)
- [Claim types and the minimum matching set](#claim-types-and-the-minimum-matching-set)
- [Rule of thumb: state your loss-of-generality up front](#rule-of-thumb-state-your-loss-of-generality-up-front)
- [Common mistakes](#common-mistakes)

---

## The core insight

Every head-to-head comparison has **N axes of variation**. For each axis, exactly one of:

| Status | Meaning | Action |
|---|---|---|
| **MATCH** | Axis must be identical across sides | Enforce identity; fail the bench if not |
| **STATE** | Axis differs but the difference is the point | Name it explicitly; publish both |
| **RANDOMIZE** | Axis is irrelevant; vary it to show insensitivity | Sample across values; report median + spread |

The mistake is binary thinking: "fair" vs "biased." The right shape is a matrix where each axis is classified, justified, and documented with the result.

---

## The matrix

Build this table *before you run the bench*:

| Axis | Status | Chosen value(s) | Rationale |
|------|--------|-----------------|-----------|
| Workload identity | MATCH | `commutative_inserts_disjoint_keys @ c4` | Cannot compare A and B on different scripts |
| Data fixture | MATCH | `chinook.sqlite` golden copy | Same schema, same rows, same indexes |
| Build profile | MATCH | release-perf (LTO=true, debug=false) | Both sides optimized the same way |
| PRAGMA settings | MATCH | WAL, synchronous=NORMAL, page_size=4096 | Both engines use identical knobs |
| API surface | MATCH | prepared statements, single session | Apples-to-apples API class |
| Warmup count | MATCH | 3 iterations, discarded | Symmetric cache warming |
| Host / kernel | MATCH | Ryzen 5995WX reference host, Linux 6.17.0-19-generic | Same machine class, same run |
| Write concurrency | **STATE** | MVCC (A) vs BEGIN-IMMEDIATE lock (B) | **The axis being measured** |
| Storage engine | **STATE** | A: own B-tree + WAL; B: SQLite B-tree + WAL | Different, by design of the comparison |
| RNG seed | RANDOMIZE | seed ∈ {1, 42, 1337, 9999} | Insensitivity check |
| Measurement order | RANDOMIZE | interleave A/B/A/B rather than A×100 then B×100 | Kills time-of-day, thermal ordering |

The example above is the FrankenSQLite template. The **two STATE axes are why the comparison exists**. If both sides were identical on those, there would be no reason to run it.

---

## Worked example: MVCC vs single-writer

The question: does FrankenSQLite's MVCC give us something C SQLite cannot?

**Wrong framing**: "FrankenSQLite is 16× slower, case closed." (True on `c1`, wrong question.)

**Right framing**: for the STATE axis "concurrency model," we expect:

- On **`c1`** (single writer): MVCC pays overhead for a feature it cannot use. **C SQLite should win.** A result where C loses here is a bug in our implementation.
- On **`c4`** / **`c8`** (multi-writer contention): MVCC writes can proceed in parallel; C SQLite serializes via `BEGIN IMMEDIATE`. **FrankenSQLite should eventually win** as contention scales.

Results matrix:

| Workload × Concurrency | C SQLite | FrankenSQLite MVCC | Ratio | Expected? |
|---|---|---|---|---|
| `commutative_inserts @ c1` | 29 ms | 480 ms | 16.6× slower | ✓ (C wins; MVCC has no parallelism to exploit) |
| `commutative_inserts @ c4` | ??? | ??? | ??? | ← the question |
| `hot_page_contention @ c4` | 89 ms p50 | 1166 ms p50 | 13.1× slower | ✗ unexpected; MVCC should shine here — investigate |
| `hot_page_contention @ c8` | ??? | ??? | ??? | ← the question |

The honest-gate conclusion from FrankenSQLite at this writing: **we have not yet realized the MVCC advantage in practice** — the write path is still sequential even though the concurrency model allows parallel writes. The bench explicitly annotates this in `concurrent_write_bench.rs:7-14`:

> Measures aggregate INSERT throughput when multiple threads write concurrently. C SQLite uses WAL mode with `busy_timeout` for write serialisation; FrankenSQLite runs the equivalent operations sequentially (MVCC concurrent writer path is not yet wired to persistence). Do not cite the FrankenSQLite control in this file as concurrent-writer evidence; it is only a fairness-normalized same-total-work control.

**That in-code warning is the artifact of apples-to-apples discipline.** Future readers cannot mistake what the bench proves.

---

## Claim types and the minimum matching set

Different claims need different MATCH sets. Match more than you need and you waste effort; match less and your claim is indefensible.

| Claim | Minimum MATCH axes |
|---|---|
| "A is faster for this workload on this host" | workload, fixture, build, PRAGMA/tuning, API, warmup, host, kernel |
| "A is faster for this workload, generally" | above + N hosts + N kernels + N RNG seeds |
| "A is faster across workloads" | above + workload matrix (≥ 5 workloads, published, not cherry-picked) |
| "A is the right architecture for this use case" | above + realistic workload blend + production-like data size + production-like concurrency |
| "A will beat B in production" | above + shadow traffic replay + matched error rates + matched retry discipline |

The honest path: pick the claim you *actually* want to make, figure out its minimum MATCH set, run that. Do not publish stronger claims than your MATCH set supports.

---

## Rule of thumb: state your loss-of-generality up front

Every bench result should include one sentence that reads:

> This result supports claim X. It does *not* support claim Y (because axis Z was STATE / was not matched / was not tested).

If you cannot write this sentence, you do not understand your own bench. Do not publish until you can.

Examples:
- "This result supports 'MVCC pays overhead at c1 as expected.' It does *not* support 'MVCC beats single-writer at c8' — we have not yet wired the concurrent write path to persistence."
- "This result supports 'A is 20% faster for small reads on the reference host.' It does *not* support 'A is faster on ARM' — we only tested x86."

---

## Common mistakes

1. **Making every axis MATCH**: Then you have no comparison, just two runs of effectively the same code. The STATE axis IS the point.
2. **Making the comparison axis implicit**: "Well everyone knows MVCC is different from locks." No. Write it down in the bench file so the six-month-later reviewer can verify.
3. **Letting MATCH axes drift silently**: "We used default PRAGMAs on both." Defaults differ. Enforce identity explicitly.
4. **Skipping RANDOMIZE**: One seed, one measurement order, one run. You just captured a point, not a distribution.
5. **Cherry-picking winners**: Running 10 workloads, publishing the 3 wins. Publish the full matrix or publish nothing.
6. **Citing the wrong axis**: The bench proved X, the marketing cites Y. The in-code comment exists to prevent exactly this.

---

**See also**: [UNBIASED-BENCHMARKING.md](UNBIASED-BENCHMARKING.md), [HONEST-GATE-CHECKLIST.md](HONEST-GATE-CHECKLIST.md), [CASE-STUDIES.md](CASE-STUDIES.md) §Case 7 for the 2026-03-19 audit that produced these rules.
