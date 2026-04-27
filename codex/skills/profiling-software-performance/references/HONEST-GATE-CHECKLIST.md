# Honest-Gate Checklist — Pre / During / Post Benchmark

> Operationalized from the FrankenSQLite `overlay_honesty_gate` and `fairness.rs` harness. Fourteen questions with pass/fail criteria. Walk the list *before* you publish a number, not after a reviewer asks.

Pair this file with `scripts/honest_gate.sh` — it prompts for each question and emits an attestation JSON beside the bench result. Bench artifacts without an attestation are unfit to cite.

## Contents

- [Pre-run gate (before the harness starts)](#pre-run-gate-before-the-harness-starts)
- [During-run gate (while samples collect)](#during-run-gate-while-samples-collect)
- [Post-run gate (before the number leaves the host)](#post-run-gate-before-the-number-leaves-the-host)
- [The attestation artifact](#the-attestation-artifact)
- [When a question cannot be answered "pass"](#when-a-question-cannot-be-answered-pass)

---

## Pre-run gate (before the harness starts)

### 1. Is there a written scenario?

> PASS: a file names the scenario, inputs, expected output, success metric (p95/throughput/RSS), and the claim you intend to make ("A is 2× B at p95 on workload X").
>
> FAIL if you cannot name the metric, or the scenario is "run the benchmark."

### 2. Are both sides on the same build profile?

> PASS: both implementations built with symmetric optimization flags (release-perf or release with LTO on both; debug on neither). From FrankenSQLite `methodology.rs:155`: LTO=true, codegen_units=1, debug=false, strip=true.
>
> FAIL: "A used release, B used default." Kills credibility instantly.

### 3. Are the API surfaces matched?

> PASS: prepared-vs-prepared, batched-vs-batched, async-vs-async. Cite the exact API entrypoints on both sides in the scenario doc.
>
> FAIL: the FrankenSQLite audit — prepared rusqlite vs ad-hoc `format!()` strings — revised six months of "10× faster" numbers to noise-level.

### 4. Are the PRAGMAs / tuning knobs identical?

> PASS: for databases, identical page_size, journal_mode, synchronous, temp_store, mmap_size, auto_vacuum, cache_size. Enforcement gate present (the bench refuses to run on divergence).
>
> FAIL: "defaults on both sides" — defaults differ between implementations.

### 5. Is the workload the project's actual use case?

> PASS: the workload is a realistic slice of what users actually do, or a clearly-labeled microbenchmark that isolates one mechanism.
>
> FAIL: synthetic workload tuned to one side's sweet spot without a matched workload tuned to the other's.

### 6. Is the fixture the same on both sides?

> PASS: same rows, same schema, same seed, same indexes, same DB file (or reset from the same golden copy per iteration).
>
> FAIL: "we copied the data" — silent schema or index drift is common.

---

## During-run gate (while samples collect)

### 7. Is warmup symmetric?

> PASS: both sides warm up for the same number of iterations against the same workload. FrankenSQLite default: **3 warmup iterations, discarded**.
>
> FAIL: "we warmed up A with 1000 queries to populate its cache; B got none" — you just measured B's cold cache.

### 8. Is N high enough?

> PASS: **≥ 20 samples after warmup** *and* **≥ 10 seconds of measurement wall clock** per bench. Criterion's default is good here.
>
> FAIL: 3 samples, "looks consistent." p95 of N=3 is the max; that's not a measurement.

### 9. Is the host quiet?

> PASS: no other heavy process during the run; governor=performance; no_turbo=1; SMT off for microbenches; taskset on isolated cores. Fingerprint captured (`env_fingerprint.sh`).
>
> FAIL: parallel `cargo build` mid-bench, browser open, VM host under load.

### 10. Does the p95 variance envelope hold?

> PASS: three same-host repeat runs have p95 drift ≤ 10% (`variance_envelope.py`). If > 10%, investigate before trusting the number.
>
> FAIL: "the bench is just noisy" — fix noise or widen N, don't paper over it.

---

## Post-run gate (before the number leaves the host)

### 11. Is the reporting three-tier (not binary)?

> PASS: classify each scenario as `BelowParity` (> 1.25× slower), `ParityToMargin` (within 1.25×), or `HealthyMargin` (≥ 1.10× faster). From FrankenSQLite `overlay_honesty_gate.rs:26`.
>
> FAIL: one winner, one loser, no gradient.

### 12. Are losses published alongside wins?

> PASS: the results table shows every workload × concurrency cell, including where A loses. The `BelowParity` classification is visible.
>
> FAIL: "we only report the wins." Reviewers will find the omissions.

### 13. Is apples-to-oranges flagged in-source?

> PASS: if A's architectural advantage (e.g., MVCC concurrent writers) is the comparison point, the bench file has an in-code comment that says *exactly what you can and cannot cite from this run*. See FrankenSQLite `concurrent_write_bench.rs:7-14` for the template.
>
> FAIL: the comparison sneaks into a marketing table without the asterisk.

### 14. Is the result reproducible from the spec?

> PASS: a `HarnessSettings` record or equivalent (git SHA, host, toolchain, workload, pragma list, seed, N, warmup) travels with the numbers. Another engineer can re-run and land within the variance envelope.
>
> FAIL: "we did some runs." History cannot audit "some."

---

## The attestation artifact

`scripts/honest_gate.sh` asks each question, requires a tagged answer (`pass` / `fail` / `waive:<reason>`), and emits:

```json
{
  "scenario": "frankensqlite_vs_rusqlite_commutative_inserts",
  "timestamp": "2026-04-20T19:00:00Z",
  "git_sha": "<hash>",
  "host_fingerprint_sha256": "<hash of fingerprint.json>",
  "questions": {
    "1_written_scenario": "pass",
    "2_same_build_profile": "pass",
    "3_api_matched": "pass",
    "4_pragmas_identical": "pass",
    "5_realistic_workload": "pass",
    "6_same_fixture": "pass",
    "7_warmup_symmetric": "pass",
    "8_N_sufficient": "pass",
    "9_host_quiet": "pass",
    "10_variance_envelope": "pass",
    "11_three_tier_reporting": "pass",
    "12_losses_published": "pass",
    "13_apples_flagged": "waive:microbench isolates one axis; workload matrix covers cross-axis",
    "14_reproducible": "pass"
  },
  "attested_by": "<user or CI run-id>"
}
```

Store the attestation in the same directory as the bench result. A stale or missing attestation should fail CI as loudly as a broken test.

## When a question cannot be answered "pass"

Two valid moves:
1. **Fix the cause**, re-run, attest.
2. **Waive with reason**, in writing, in the attestation. Reviewers can then argue with the waiver rather than with the number.

The move you must NOT make: publish the number without the attestation and hope nobody asks. Future-you will read the result six months later and be unable to judge whether to trust it.

---

**Cross-references:** [UNBIASED-BENCHMARKING.md](UNBIASED-BENCHMARKING.md) for the 5-level fairness ladder. [APPLES-TO-APPLES-MATRIX.md](APPLES-TO-APPLES-MATRIX.md) for which dimensions must match vs which are the comparison's *point*. [STATISTICAL-RIGOR.md](STATISTICAL-RIGOR.md) for N-sizing and p-value sanity.
