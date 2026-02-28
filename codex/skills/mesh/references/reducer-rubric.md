# Reducer Rubric

Score each dimension `1` (poor) to `5` (strong):

- `abstraction_targeting`: identifies a real high-cost abstraction instead of cosmetic style edits.
- `primitive_replacement`: replacement primitive is explicit, lower-level, and operationally simpler.
- `invariant_preservation`: contract and invariants remain intact with no semantic drift.
- `incision_size`: patch is minimal, reversible, and scoped to the unit boundary.
- `rollback_clarity`: rollback path is one step and evidence-backed.

Pass rule:

- PASS only when average `>= 4.0` and no dimension `< 3`.
- Otherwise FAIL.
