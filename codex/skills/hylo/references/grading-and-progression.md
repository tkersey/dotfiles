# Grading and progression

## Grade the world, trace, and answer

Prefer outcome and trace evidence over final-text resemblance. Separate:

```text
world outcome       repository or external state reached
trace behavior      tools, permissions, ordering, budgets, side effects
answer quality      correctness, completeness, clarity, calibration
operational cost    tokens, latency, retries, human intervention
```

The original response is evidence, not a golden answer. It may contain both
good behavior and the defect the campaign is meant to improve.

Grade that original response first as the historical diagnostic baseline.
Then create a separate blind replay baseline for comparisons. Never claim a
target-version delta by comparing a controlled candidate run directly against
an unreconstructed historical response.

## Grader authority

Use the strongest available authority:

1. deterministic state/test/schema assertion;
2. deterministic trace invariant;
3. model grader calibrated against human anchors;
4. human judgment.

Record disagreement instead of averaging it away. A model grader cannot be
the sole authority for a safety-critical pass.

Campaign and scenario syntax freeze declared grader identities before replay;
Ledger compares grades against them but does not execute or authenticate those
graders. Treat deterministic and trace grades as credible only when their refs
resolve to independently inspectable receipts, and treat human grades as
authoritative only after human confirmation.

For pass/fail events, submit every frozen rubric dimension with its frozen
weight. Native Ledger recomputes the weighted aggregate and rejects mismatches;
the caller cannot improve a result by changing weights or supplying a different
scalar. Record at most one comparison-eligible grade per attempt.

## Blindness

A progress-eligible attempt must not receive:

- the source response;
- later source-session messages or outcome;
- hidden oracle values;
- grades or feedback for the same holdout scenario;
- target-specific repair hints derived from the hidden reference.

Practice scenarios may become non-blind after feedback, but their later grades
must be marked `comparison_eligible=false` unless a fresh blind variant is
used.

## Comparability

Two grades are directly comparable only when all of these match:

```text
scenario_id
rubric_fingerprint
environment_fingerprint
replay_policy_fingerprint
required observation surface
judge kind, identity, version, and configuration fingerprint
per-dimension and per-oracle grader fingerprints
```

The target fingerprint may differ; that difference is the candidate
intervention. If any comparison field changes, create a new baseline or mark
the grade incomparable.

A candidate grade also requires a like-for-like controlled `replay_baseline`
whose attempt predates the candidate attempt for that scenario. The baseline
may be graded after the target change is frozen, which lets holdout results
remain quarantined while preventing post-candidate baseline selection.
Historical diagnostics never supply the comparison denominator.

## Progress views

Report at least:

- sample count and repeat count;
- pass/fail counts by split;
- critical invariant violations;
- per-dimension means or distributions;
- target fingerprints compared;
- unresolved scenarios;
- environment and grader limitations.

Do not let a weighted aggregate conceal a critical regression. Do not combine
practice and holdout denominators. Report target-by-split summaries and compute
the frontier only for the current target and configured repeat count. A repeat
gate is the latest consecutive cohort; a newer failure reopens the frontier
even when older passes exist.

## Improvement vocabulary

Use:

```text
improved               comparable holdout evidence supports the stated delta
practice_gain          comparable practice evidence improved; holdout unproved
regression             comparable evidence worsened materially
incomparable           the comparison contract changed
insufficient_evidence  the sample/repeat/uncertainty gate is unmet
invalid                replay, trace, grader, or chain integrity failed
```

State the dimension and denominator: “correctness improved on 8/10 holdout
scenarios across 3 blind repeats” is meaningful; “score improved” is not.

## Frontier selection

Choose the next scenario by this order:

1. critical invariant violation;
2. environment or grader invalidity;
3. reproducible holdout failure, routed to rejection or rebaseline;
4. reproducible practice failure, eligible to motivate repair;
5. high-uncertainty or flaky scenario;
6. mutation that tests whether the repair transfers.

One failure may produce one repair hypothesis. A target change is not
validated until a fresh blind replay observes the expected delta without a new
critical regression.

Only practice evidence may shape a target repair. Once a holdout or challenge
case influences a repair hypothesis, it is no longer independent promotion
evidence; start a new campaign with untouched cases instead. Native Ledger
therefore seals a target against further applied changes as soon as an eligible
holdout or challenge grade for that target is recorded.

## Promotion and commit

Treat a candidate change as three distinct states:

```text
applied       the owner changed the target and validation ran
promoted      fresh comparison-eligible grades passed the campaign gate
committed     explicit publication authority produced a commit
```

Do not collapse these states. A commit without a promotion grade is not a
Hylo-validated improvement; a promotion grade without commit authority remains
a validated local candidate. Record the exact committed paths and never stage
unrelated worktree changes.

Before each candidate replay, require the staged diff to retain the recorded
fingerprint, require all target roots to be free of tracked and untracked
contamination, and let Ledger recompute the staged target snapshot. Drift
invalidates the change record.

For publication, cite exactly the latest configured repeat cohort for every
frozen scenario; every member must pass. Native Ledger verifies the local
commit object, tree, exact changed paths, and equality between the committed
target projection and every promotion attempt's target snapshot. That proves
publication scope and target identity, not remote push or generalized
improvement.

## Stop rule

Treat the stop condition as reopenable campaign evidence, not proof of general
intelligence. Close only against the configured scenario distribution,
rubric, environment fidelity, repeat count, and budget. A new failure,
distribution, rubric, or target version may reopen work through a new campaign.
