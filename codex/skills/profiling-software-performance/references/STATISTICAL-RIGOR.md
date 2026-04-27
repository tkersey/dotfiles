# Statistical Rigor — How Not To Lie With Numbers

> Before you publish "X is Y% faster," apply these rules. Most perf claims that turn out wrong are not false on purpose — they are statistically naive.

## Contents

1. [Why means lie, medians mislead, and tails matter](#why-means-lie-medians-mislead-and-tails-matter)
2. [Which percentiles to report, when](#which-percentiles-to-report-when)
3. [Sample size and the p99.9 honesty rule](#sample-size-and-the-p999-honesty-rule)
4. [Variance, coefficient of variation, and MAD](#variance-coefficient-of-variation-and-mad)
5. [Outlier policy — quarantine, don't delete](#outlier-policy--quarantine-dont-delete)
6. [A/B testing the numbers](#ab-testing-the-numbers)
7. [Confidence intervals — parametric vs bootstrap](#confidence-intervals--parametric-vs-bootstrap)
8. [t-test vs Mann-Whitney U — when each applies](#t-test-vs-mann-whitney-u--when-each-applies)
9. [`benchstat` reading guide](#benchstat-reading-guide)
10. [Criterion's analysis in plain words](#criterions-analysis-in-plain-words)
11. [Open-loop vs closed-loop load](#open-loop-vs-closed-loop-load)
12. [Compounding wins correctly](#compounding-wins-correctly)
13. [Checklist before publishing a number](#checklist-before-publishing-a-number)

---

## Why means lie, medians mislead, and tails matter

You have three candidates for "the" latency number:

- **Mean (average)**: sum ÷ count. Skewed heavily by tails. If 1 in 1000 requests takes 1 second and the rest take 1 ms, mean ≈ 2 ms — but 99.9% of users see 1 ms, and 0.1% see 1 second. The mean communicates neither.
- **Median (p50)**: middle-valued sample. Insensitive to tails. Users don't experience the median — they experience their own request, which may be far from the median.
- **p99, p99.9, p99.99**: the worst-experience number. For user-facing systems, what 1-in-100 (or 1-in-10k) users see drives churn. For batch/throughput systems, less important.

**Rule**: publish at least `p50 / p95 / p99` together. Never a single number.

A single-number communicator problem: if you *must* pick one, the best is **p95** for user-facing systems (captures the tail without being dominated by the one-in-a-million artifact) and **median throughput** for batch systems (tail throughput matters less).

---

## Which percentiles to report, when

```
| Scenario                              | Primary      | Secondary       | Skip            |
|---------------------------------------|--------------|-----------------|-----------------|
| User-facing request (HTTP, RPC)       | p95          | p50, p99, p99.9 | mean            |
| Internal batch (ETL, cron)            | total time   | p95             | mean, p99.99    |
| Data ingestion, streaming             | throughput   | p99 backlog     | mean            |
| Cold-start / init                     | p95 cold     | p95 warm        | combined stat   |
| Real-time / deadline system           | p99.99       | p99.9           | median          |
| Background maintenance                | mean         | total time      | p95             |
```

Reporting only the mean is the most common perf-communication failure. Reporting only the median is second. Publishing the triple `(p50, p95, p99)` handles 95% of cases.

---

## Sample size and the p99.9 honesty rule

To estimate a percentile `p` with ε relative error at 95% confidence, you need roughly:

```
N ≥ (1.96)² × (1 - p) / (p × ε²)
```

Concretely:

- **p50**: ~400 samples for ±5% error
- **p95**: ~1500 samples for ±5% error
- **p99**: ~15,000 samples for ±5% error
- **p99.9**: ~150,000 samples for ±5% error
- **p99.99**: ~1,500,000 samples for ±5% error

With < 1000 samples, p99.9 and p99.99 are **worst-observed**, not true percentile estimates. Label them *conservative* in the report.

A good profile report follows exactly this rule:

> "note: current warm-path sample counts are below 1,000 per scenario, so p99.9/p99.99 act as a conservative worst-observed tail sentinel."

### Practical minimums

- For a sanity check: 20 samples (captures p95 only as "worst-few-of-20")
- For a tight p95 claim: 200+ samples
- For a p99 claim: 2000+ samples
- For a p99.9 claim: 20000+ samples

When samples are expensive (each run is seconds or minutes), you **cannot** get a reliable p99.9. Report what you have and label it.

---

## Variance, coefficient of variation, and MAD

Raw standard deviation is hard to compare across workloads with different scales. Use:

### Coefficient of Variation (CV)

```
CV = stddev / mean
```

- CV < 3% — negligible noise (publish the number)
- CV < 10% — acceptable for relative A/B claims
- CV > 10% — too noisy; fix environmental noise before publishing
- CV > 30% — something is wrong (background workload, thermal throttling, data-dependent cost)

**CV is workload-independent**. 1ms ± 0.03ms has the same CV as 100ms ± 3ms. Use it for cross-workload variance comparison.

### Median Absolute Deviation (MAD)

MAD is robust to outliers (unlike stddev). It's the median of `|x_i - median|`.

- For a roughly-normal distribution: `stddev ≈ 1.4826 × MAD`
- MAD doesn't explode when one sample is 100× larger

When outliers are present (most real-world perf distributions), prefer **median + MAD** over **mean + stddev**.

### Interquartile Range (IQR)

```
IQR = p75 - p25
```

Insensitive to outliers in both tails. Useful as an "effective spread" metric.

---

## Outlier policy — quarantine, don't delete

Real perf distributions are heavy-tailed. The p99.9 sample that's 10× the p50 is often:

- a GC pause
- an I/O stall from writeback
- a lock contention event
- a context switch to a high-priority task
- a thermal throttle kick-in

**Deleting it hides the bug the user cares about most.** Averaging it in hides the median.

The right policy (from OPERATOR-CARDS.md `ΔE Anomaly-Quarantine`):

1. Record every raw sample — `hist.record()` per event, not aggregated.
2. Log samples > 3σ from median to `anomaly_register.md` with classification.
3. Publish two numbers:
   - **Steady-state**: median or p95 with outliers removed (`trimmed`)
   - **Outlier-inclusive**: p99.9 / max including everything
4. Investigate outlier classification (GC? I/O? lock?) and put the finding in hypothesis.md.

---

## A/B testing the numbers

When comparing "before" (baseline) and "after" (change), you need:

1. **Paired comparisons** — same input, same host, same time window. Never "baseline was yesterday, change is today" — thermal drift alone can exceed your effect size.
2. **Interleaved runs** — `A B A B A B …` so both sides see the same thermal / neighbor variation.
3. **≥ 20 runs per side** — typical minimum for a 10% claim at reasonable confidence.
4. **A non-parametric test OR a paired t-test** depending on distribution (see below).

Tooling:

- **`hyperfine`**: gives you `mean ± stddev`, `min`, `max`, and a "X.XX ± X.XX times faster than Y" claim. Uses t-test-flavored stats internally.
- **`benchstat`** (Go): paired Wilcoxon signed-rank test by default; outputs a delta and a p-value.
- **`criterion.rs --baseline before`**: bootstrap confidence intervals + "No change / Improved / Regressed" verdict at 95% CI.
- **`iai-callgrind`**: instruction-count based, deterministic — no statistics needed beyond count equality. Best for CI-stable claims.

---

## Confidence intervals — parametric vs bootstrap

### Parametric (t-distribution)

Assumes the mean of your samples is approximately normally distributed (Central Limit Theorem kicks in for N > 30 usually).

```
95% CI for mean = mean ± 1.96 × (stddev / √N)
```

Works well for:
- mean-of-many-samples when underlying distribution is roughly symmetric
- throughput (ops/sec) where sample-to-sample is close to normal

Breaks down when:
- distribution is heavy-tailed (typical for latency)
- N is small
- samples are correlated (repeated measurements on same host within seconds)

### Bootstrap (resampling)

No distributional assumption — resample the data with replacement many times and compute the statistic each time.

```python
# rough sketch — real tools (criterion) do this better
import numpy as np
samples = [...]  # your latency samples
bootstrap_means = [np.mean(np.random.choice(samples, len(samples), replace=True)) for _ in range(10000)]
ci_low, ci_high = np.percentile(bootstrap_means, [2.5, 97.5])
```

Works for:
- any statistic (median, p95, p99, MAD)
- heavy-tailed distributions
- small N (but still biased if N < 20)

`criterion.rs` uses bootstrap by default — when it reports `[p95_low, p95_high]`, those are bootstrap CI bounds.

---

## t-test vs Mann-Whitney U — when each applies

### Paired t-test

Use when:
- Data is roughly normal (or N is large enough for CLT)
- Samples are paired (interleaved A B A B runs)
- You're comparing means

Not robust to outliers or heavy tails — common with latency.

### Wilcoxon signed-rank (paired non-parametric)

`benchstat` default. Use when:
- Samples are paired
- Distribution is skewed or heavy-tailed
- You care about median shift rather than mean shift

More robust than t-test for real perf data.

### Mann-Whitney U

Use when samples are **not paired** (independent groups). Less common for benchmarking because you almost always can pair.

### Permutation test

For small N where you want an exact p-value without distributional assumptions. Tools: `scipy.stats.permutation_test`.

### Practical rule

- Using `benchstat` or `criterion --baseline`? You're already using the right test. Don't second-guess.
- Eyeballing `hyperfine` output? Non-overlapping CI bars → claim OK. Overlapping bars → not clearly a win.
- Comparing two means manually? Use bootstrap CI, not t-test, unless you know the distribution is normal.

---

## `benchstat` reading guide

```
name                           old time/op    new time/op    delta
ArchiveWriteBatch100-128       3.49s ± 6%     2.10s ± 4%     -39.83%  (p=0.002 n=10+10)
FormatResolutionExplicit-128   39.1ns ± 2%    38.9ns ± 3%       ~     (p=0.423 n=10+10)
```

Columns:
- `old time/op` — baseline, mean ± variance (± relative CV)
- `new time/op` — after change
- `delta` — mean shift; `~` means no statistically significant change
- `p` — Wilcoxon p-value; `p < 0.05` conventionally "significant"
- `n` — sample counts on each side

Interpretation rules:
- **p > 0.05 and delta ≈ 0**: no change. Don't claim anything.
- **p < 0.05 and delta < -5%**: real improvement. Claim it.
- **p > 0.05 and delta ≠ 0**: noisy data. More samples, or accept it's inconclusive.
- **p < 0.05 and delta > +5%**: real regression. Block the change.
- **Variance (± X%) > 10%**: unreliable baseline. Fix the host first (pinning, governor, isolation).

---

## Criterion's analysis in plain words

When you run `cargo bench --baseline before`, Criterion prints one of:

- **"Performance has not regressed."** — no statistically significant difference at 95% CI
- **"Performance has improved."** — bootstrap 95% CI shows a negative delta
- **"Performance has regressed."** — positive delta at 95% CI
- **"Change within noise threshold."** — tied to `.noise_threshold()` setting in the bench (default 3% in the Criterion template)

Default Criterion config:
```rust
Criterion::default()
    .sample_size(50)
    .measurement_time(Duration::from_secs(3))
    .warm_up_time(Duration::from_secs(1))
    .noise_threshold(0.03)
    .confidence_level(0.95)
    .without_plots()
```

Tuning:
- `.sample_size(50)` → 50 distinct measurements; more gives tighter CIs but slower bench
- `.measurement_time(3s)` → duration for Criterion to gather samples
- `.warm_up_time(1s)` → discard initial runs (JIT warmup, cache fill)
- `.noise_threshold(0.03)` → smaller changes are "within noise"
- `.confidence_level(0.95)` → CI width

For CI gating, raise `sample_size` to ~200 and `measurement_time` to 10s+ for stability.

---

## Open-loop vs closed-loop load

Closed-loop: virtual users each wait for their own response before sending next. Classic `wrk`.
Open-loop: fixed arrival rate, irrespective of server response time. `wrk2`, `k6`, `vegeta`.

**Closed-loop hides tail latency when the server saturates.** Under overload, virtual users back up on the client side rather than the server side. The server appears "still responding in N ms" because slow requests prevent new ones from ever being issued.

**Open-loop exposes the real server queue.** Arrivals proceed at the target rate; slow responses pile up on the server, and tail latency blows up correctly.

For realistic user-facing tail measurements: always open-loop.

```bash
# closed-loop (wrk) — DON'T use for tail latency
wrk -t4 -c100 -d30s http://x
# open-loop (wrk2) — DO use for tail latency
wrk2 -t4 -c100 -d30s -R 5000 http://x     # 5000 req/s constant

# open-loop alternatives
k6 run --vus 50 --duration 30s --rps 5000 script.js
echo "GET http://x" | vegeta attack -rate=5000/s -duration=30s | vegeta report
```

---

## Compounding wins correctly

### The rule

Multiplicative. 1.05× × 1.08× = 1.134× (≈ 13.4%), **NOT** 1.13× (13% sum).

Equivalently: if you report in "% faster," you must convert to speedup ratios before combining:

- 5% faster = `1 / 0.95` = 1.0526× speedup
- 8% faster = `1 / 0.92` = 1.0870× speedup
- Combined: 1.0526 × 1.0870 = 1.144× = 14.4% faster than original

Naive sum (5 + 8 = 13%) underestimates. Naive product in the wrong direction overestimates.

### How to compute

For absolute times (ms per op):

```
speedup = before_time / after_time
combined_speedup = product of individual speedups
combined_pct_faster = (combined_speedup - 1) × 100
```

For throughput (ops/sec):

```
ratio = after_throughput / before_throughput
combined_ratio = product of individual ratios
```

### Common error

Tracking "% faster" across N rounds and summing. 5 rounds × 10% each reported as "50% faster." Actual: 1.1^5 = 1.61 = 61% faster. The error grows with N.

### Reporting format

```
| Round | Individual | Cumulative (multiplicative) | Pct faster |
|-------|-----------:|----------------------------:|-----------:|
|   1   | 1.05×      | 1.05×                       | 5%         |
|   2   | 1.08×      | 1.13×                       | 13%        |
|   3   | 1.12×      | 1.27×                       | 27%        |
|   4   | 1.06×      | 1.35×                       | 35%        |
|   5   | 1.09×      | 1.47×                       | 47%        |
```

See Case Study 6 for a real campaign ledger.

---

## Checklist before publishing a number

- [ ] Samples ≥ 20 (minimum for any claim)
- [ ] Samples ≥ 200 for p95 at ±5%; ≥ 2000 for p99; ≥ 20000 for p99.9
- [ ] Reported as `(p50, p95, p99, [p99.9 if eligible])`, NOT as mean alone
- [ ] CV < 10% or explicit explanation of noise sources
- [ ] Fingerprint captured; comparison within same fingerprint
- [ ] A/B runs were interleaved (or paired test used)
- [ ] Statistical test applied (`benchstat`, `criterion --baseline`, or bootstrap CI manually)
- [ ] p-value ≤ 0.05 or non-overlapping CI
- [ ] Outliers quarantined, not silently dropped
- [ ] Compounding computed multiplicatively, not summed
- [ ] Open-loop load if reporting tail latency on a server
- [ ] Reported as a ratio (`1.35×` or `-27%`) for portability; absolute ms only with fingerprint attached
- [ ] Variance snapshot: 5 same-host reruns, max drift ≤ 10%

If any unchecked, the number is provisional, mark it as such.

---

## Fuel for the ledger — "this many samples for this claim"

Post this near your benchmarking harness:

```
claim = f"archive_batch_100 p95 {p95:.0f}ms ± {ci:.0f}%"
if samples < 200:
    claim += "  [INSUFFICIENT N for p95 ±5% — treat as advisory]"
if samples < 2000 and "p99" in claim:
    claim += "  [p99 is worst-observed of {samples}]"
if cv > 0.1:
    claim += f"  [HIGH VARIANCE cv={cv:.1%} — fix host noise]"
print(claim)
```

Force yourself to label what you don't have. Builds trust with future-you.
