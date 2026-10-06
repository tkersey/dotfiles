# Performance report: <target>

## Result

<Measured result, explicit unmeasured/inconclusive conclusion, or audit finding.>

- Objective and protected acceptance criteria:
- Original baseline -> final candidate; revisions and configuration:
- Status: <accepted | rejected | inconclusive | unmeasured | audit>
- Material tradeoffs and remaining uncertainty:

## Workload and measurement

- Workload/task distribution, dataset, and exact reproduction commands:
- Hardware/OS, toolchain/runtime/model, concurrency and offered load:
- Cold/warm state, warmup, run order, sample count and unit sampled:
- Raw evidence locations; variability/intervals and coverage limits:

| Relevant metric / unit | Original baseline | Final candidate | Absolute / relative delta | Uncertainty / guardrail |
|---|---|---|---|---|
| <metric> | <observation> | <observation or unmeasured> | <supported comparison or unavailable> | <result and limits> |

## Limiting mechanism and intervention

- Profile/trace/counter or scaling evidence:
- Mechanism and expected end-to-end benefit:
- Selected intervention and why it addresses the mechanism:
- Alternatives rejected and their discriminators:

## Protected behavior and evidence

- Required observations, assumptions, and preservation argument:
- Correctness/quality commands and actually observed results:
- Independent oracle and fresh baseline/candidate comparison, when applicable:
- Inputs, schedules, numerical cases, effects, or environments not covered:

## Agent outcomes, when applicable

- Matched tasks and holdout/regression coverage:
- Successes / total attempts, failures, retries, timeouts, and quality guards:
- Total cost across attempts and cost per successful task, or undefined at zero successes:
- End-to-end latency, model/reasoning configuration, and cache-state conditions:
- Missing usage/trace coverage and attribution limits:

## Experiments, when needed

| Intervention | Evidence / expected delta | Observed outcome | Retained / rejected / inconclusive |
|---|---|---|---|
| <one attributable lever> | <mechanism> | <objective and guardrails> | <disposition> |

## Regression guard and closeout

- Existing benchmark/evaluation case and workload-specific threshold:
- Cumulative original/final comparison and second-order regressions checked:
- Rollback/state-compatibility considerations; rollout only when authorized:
- Stopping reason, remaining bottleneck, and exact blocked reproduction steps:
