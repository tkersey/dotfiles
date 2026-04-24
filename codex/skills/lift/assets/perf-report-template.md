# Performance Report: <title>

Date: <yyyy-mm-dd>
Owner: <name/team>
System: <component>
Mode: <measured|unmeasured|audit>

## Performance Contract

- Metric:
- Target / goal:
- Percentile:
- Workload command:
- Dataset:
- Environment:
- Constraints:

## Correctness Oracle

- Oracle type: <tests|golden|differential|property|invariant|canary>
- Command(s):
- Baseline result:

## Baseline

- Measurement method:
- Warmup:
- Sample size:
- Results (min/p50/p95/p99/max or throughput/RSS):
- Secondary metrics:
- Noise floor / variance notes:

## Bottleneck Evidence

- Tool(s):
- Artifact path(s):
- Top hot paths / waits:
- Bound classification:

## Opportunity Matrix

| Rank | Candidate | Evidence | Impact | Confidence | Effort | Score | Decision |
|---:|---|---|---:|---:|---:|---:|---|
| 1 |  |  |  |  |  |  |  |

## Behavior Proof

- Change:
- Inputs covered:
- Ordering preserved:
- Tie-breaking unchanged:
- Floating-point semantics:
- RNG/time/concurrency determinism:
- Error handling and edge cases:
- Golden/differential/property check:

## Experiments

| Experiment | Hypothesis | Change | Result | Delta | Confidence | Decision |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Result

- Variant measurements:
- Delta vs baseline:
- Confidence:
- Trade-offs:
- Regressions checked:

## Regression Guard

- Benchmark / budget / monitor:
- Threshold:
- CI or rollout status:

## Validation

- Correctness command(s) -> pass/fail:
- Performance command(s) -> numbers:
- Profile/trace/counter command(s) -> evidence:
- Lift CLI proof if applicable:

## Residual Risks / Next Steps

-

## Lift Compliance

`lift_compliance: mode=<measured|unmeasured|audit>; workload=<cmd>; baseline=<yes/no>; after=<yes/no>; correctness=<yes/no>; bottleneck_evidence=<yes/no>; behavior_proof=<yes/no>; score_gate=<yes/no>`
