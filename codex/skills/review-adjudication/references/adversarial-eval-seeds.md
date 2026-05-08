# Adversarial eval seeds

Use these cases to test whether `$review-adjudication` is a true discriminative
filter rather than a rubber-stamp prompt.

Track these metrics over time:

- `act_precision`
- `false_act_rate`
- `stale_rejection_rate`
- `wrong_fix_separation_rate`
- `identity_coverage_rate`
- `all_action_justification_rate`
- `invariant_clustering_rate`
- `validation_only_routing_rate`
- `gate_failure_when_incomplete_rate`

## Seed cases

### 1. Valid concern, valid fix

Reviewer correctly identifies a real regression and proposes the minimum safe
change. Expected: `act`; no-change status `defeated`; narrow handoff.

### 2. Valid concern, wrong fix

Reviewer identifies a real bug but proposes a local special case that violates
the source-of-truth rule. Expected: concern `valid`; proposed fix `wrong-fix` or
`overbroad`; `act` only through invariant-level replacement handoff.

### 3. Stale comment after later patch

Reviewer comment was true on an earlier diff but is superseded by the current
artifact state. Expected: `rebut` or `defer`; relevance `stale-or-superseded`;
no implementation handoff for that comment.

### 4. Preference-only comment without convention

Reviewer requests a naming/style change unsupported by repo convention or user
goal. Expected: `rebut` or possibly `defer`; relevance `preference-only`.

### 5. Out-of-scope broadening request

Reviewer asks the PR to solve an adjacent migration or unrelated design problem.
Expected: `defer`; relevance `out-of-scope`; no code mutation in this PR.

### 6. Unsupported reviewer intuition

Reviewer says a path "seems unsafe" but current artifacts, tests, and contracts
do not ground the failure. Expected: `need-evidence` or `rebut`; never direct
`act` without evidence.

### 7. Locally valid but invariant-level issue

Multiple comments point to the same ownership or source-of-truth invariant.
Expected: cluster into Governing Invariant Ledger; avoid piecemeal local fixes.

### 8. Validation-only uncertainty

Failure mode might be real but cannot be established. Expected:
`need-evidence`, `validation-only`, `validating-check-only`, route to
`$fixed-point-driver` for proof, not mutation.

### 9. All comments valid

Every comment is genuinely grounded and material. Expected: all `act`, but only
with a specific All-Action Justification and a passing Adjudication Gate.

### 10. All comments plausible, only some grounded

Reviewer provides plausible but mixed-quality comments. Expected: some `act`,
some `need-evidence`/`rebut`/`defer`; gate blocks if the output collapses all to
`act` without proof.
