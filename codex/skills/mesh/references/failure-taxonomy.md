# Mesh Failure Taxonomy

Use exactly one primary code when a unit is not accepted.

- `safety_regression_risk`: candidate introduces likely behavioral regression or invariant break.
- `proof_missing`: required validation signal was not executed and no explicit waiver exists.
- `invalid_output_schema`: worker output cannot be parsed into required contract fields.
- `scope_overlap_conflict`: unit conflicts with another active write scope.
- `timeout_retry_exhausted`: unit timed out after one retry and one replacement.
- `delivery_blocked`: integrator could not safely produce commit/patch artifact.
- `requires_clarification`: blocking requirement ambiguity remains.
- `tooling_unavailable`: required tool/runtime unavailable for this unit.

When reporting a non-accepted outcome, pair the code with one concrete evidence anchor.
