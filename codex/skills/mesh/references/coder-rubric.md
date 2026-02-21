# Coder Doctrine-Fit Rubric

Use this rubric to evaluate whether coder output matches the expected TK style.

## Dimensions (1-5 each)

1. `contract_clarity`
   - 1: objective unclear
   - 3: objective mostly clear but incomplete
   - 5: objective and success criteria are explicit and testable
2. `invariant_strength`
   - 1: invariants missing or vague
   - 3: invariants present but weakly enforced
   - 5: invariants explicit, scoped, and enforced by structure or checks
3. `minimal_incision`
   - 1: broad or noisy diff
   - 3: mostly targeted with minor spread
   - 5: smallest credible change at stable boundary
4. `proof_credibility`
   - 1: no executed signal
   - 3: weak or indirect signal
   - 5: direct executed proof with clear pass/fail evidence
5. `legibility_trace`
   - 1: hard to reason about decisions
   - 3: understandable with effort
   - 5: decision path and tradeoffs are immediately legible

## Pass rule

- Average score must be >= 4.0.
- No individual dimension may be below 3.

## Output expectations

Feedback should return:

1. per-dimension numeric scores
2. one-line rationale per dimension
3. final pass/fail
4. prioritized corrective actions for any failing dimension
