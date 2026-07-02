# Review loop pattern

## Default

```text
$cas review
-> $review-fold
-> closure-agenda pass
-> $goal-grind accepted liabilities only
-> $evidence-fold
-> 3 clean CAS-RER review records
-> $proof-patch
-> $ship only when PR update/publication is requested
```

## Modes

| Mode | Purpose | Code changes |
|---|---|---|
| review-only | Find and classify review findings. | No |
| agenda-only | Produce the closure agenda. | No |
| review-fix | Default review remediation. Classify, fix accepted liabilities, prove closure. | Yes |

## Clean CAS-RER review record

A clean CAS-RER review record means current-tuple `verdict.status=clean` evidence with strong usable principal and no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker remains after review-fold and the closure-agenda pass.

The run is still clean when findings are duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already addressed by the current implementation.

Reset the clean-run counter when code changes, review scope changes, base/head/diff changes, proof bar changes, or the workflow cannot prove CAS-RER records are current, strong, and distinct.
