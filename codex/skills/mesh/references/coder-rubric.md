# Coder Rubric

Score each dimension `1` (poor) to `5` (strong):

- `contract_clarity`: change objective, scope, and invariants are explicit and testable.
- `invariant_strength`: impossible states and boundary constraints are preserved.
- `minimal_incision`: smallest change that solves the problem without drift.
- `proof_credibility`: proof command and result line directly support the claim.
- `legibility_trace`: reasoning, diff, and handoff are easy to audit.

Pass rule:

- PASS only when average `>= 4.0` and no dimension `< 3`.
- Otherwise FAIL.
