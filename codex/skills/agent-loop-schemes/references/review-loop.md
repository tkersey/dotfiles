# Review loop pattern

## Default

```text
$cas review
-> $review-fold
-> resolve pass
-> $goal-grind accepted liabilities only
-> $evidence-fold
-> 3 clean normalized $cas review runs
-> $proof-patch
-> $ship only when PR update/publication is requested
```

## Modes

| Mode | Purpose | Code changes |
|---|---|---|
| review-only | Find and classify review findings. | No |
| resolve-only | Produce the closure agenda. | No |
| resolve-and-fix | Default review remediation. Resolve, fix accepted liabilities, prove closure. | Yes |

## Clean normalized CAS run

A clean normalized CAS run means no new in-scope accepted liability, unresolved proof gap, unresolved refactor-kernel candidate, or human-owned blocker remains after review-fold and resolve.

The run is still clean when findings are duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already resolved by the current implementation.

Reset the clean-run counter when code changes, review scope changes, base/head/diff changes, proof bar changes, or CAS lane/session continuity is lost.
