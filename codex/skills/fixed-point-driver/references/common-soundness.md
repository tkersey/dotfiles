# Common soundness

Use soundness rows when the implementation makes or preserves a guarantee that
could be unwitnessed, illegally inhabited, stale, or contradicted by a review or
adversarial counterexample.

Minimum row fields:

- `claim_id`
- `claim_or_obligation`
- `witness_required`
- `witness_status`
- `preservation`
- `progress`
- `inhabitance`
- `minimum_acceptable_fix`

No closure while a material soundness row remains open without accepted risk.
