# Review loop pattern

## Default

```text
$cas review
-> $review-fold
-> resolution fold
-> $goal-grind accepted liabilities only
-> $evidence-fold
-> 3 clean CAS review evidence units
-> $proof-patch
-> $ship only when PR update/publication is requested
```

## Modes

| Mode | Purpose | Code changes |
|---|---|---|
| review-only | Find and classify review findings. | No |
| resolution-plan-only | Produce the resolution plan. | No |
| resolve | Default review remediation. Classify, fix accepted liabilities, prove closure. | Yes |

## Clean CAS review evidence unit

A clean CAS review evidence unit is either a `CAS-RER-v1` record or, on dispatchers without the ledger surface, a normalized tuple-bound `reviewVerdict` compatibility projection. It must carry current-tuple clean evidence with strong usable principal and must show no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker after review-fold and the resolution fold.

The run is still clean when findings are duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already addressed by the current implementation.

Reset the clean-run counter when code changes, review scope changes, base/head/diff changes, proof bar changes, or the workflow cannot prove CAS review evidence units are current, strong, and distinct.
