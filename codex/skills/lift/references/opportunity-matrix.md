# Opportunity Matrix

## Purpose

The matrix prevents hunch-driven tuning. Each optimization candidate must connect
to observed bottleneck evidence and pass an ROI threshold before implementation.

## Score Formula

```text
Score = (Impact x Confidence) / Effort
```

Only implement candidates with `Score >= 2.0`, unless the user explicitly asks for
exploration.

## Scale

### Impact

| Value | Expected impact |
|---:|---|
| 5 | >50% improvement or removes dominant bound |
| 4 | 25-50% improvement |
| 3 | 10-25% improvement |
| 2 | 5-10% improvement |
| 1 | <5% or only local/marginal |

### Confidence

| Value | Evidence |
|---:|---|
| 5 | profiler/trace/counter directly confirms hotspot and lever |
| 4 | strong benchmark and code inspection support |
| 3 | plausible from workload and common pattern |
| 2 | weak signal or indirect evidence |
| 1 | speculative |

### Effort

| Value | Cost/risk |
|---:|---|
| 1 | minutes, tiny diff, low risk |
| 2 | small patch, clear proof |
| 3 | hours, moderate refactor or test work |
| 4 | multi-file change, nontrivial proof/risk |
| 5 | >1 day, high complexity, risky rollout |

## Matrix Template

| Rank | Opportunity | Evidence | Impact | Confidence | Effort | Score | Proof burden | Decision |
|---:|---|---|---:|---:|---:|---:|---|---|
| 1 |  |  |  |  |  |  |  |  |

## Decision Rules

- Prefer the highest score that targets the dominant bottleneck.
- Reject candidates that cannot be behavior-proven.
- Defer micro-optimizations until algorithmic/data-layout wins are exhausted.
- If two candidates conflict, run the less invasive one first.
- After each accepted change, re-profile and recompute scores.

## Example Candidate Mapping

| Evidence | Candidate |
|---|---|
| repeated DB calls in trace | batch or prefetch |
| O(n^2) nested loop in hot path | index, sort+two-pointer, or better algorithm |
| allocation frame dominates | preallocate, reuse buffer, arena, reduce temporaries |
| mutex wait dominates | shard, reduce scope, RCU, lock-free queue |
| JSON parse dominates | cache parse, stream parser, schema/binary format |
| p99 spikes near saturation | admission control, bounded queues, smaller batches |
