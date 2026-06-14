# Falsification Rules

## Route falsification

A selected route is falsified when the same cluster produces a new current-state counterexample after the route claimed to close it.

Examples:

- `mutate-existing-owner` chosen, same cluster reappears.
- `universalist not-needed` chosen, boundary-shaped counterexample reappears.
- proof matrix chosen, CAS finds untested same-family counterexample.
- public bypass introduced, CAS flags it as invalid.

Falsification creates a negative route exclusion card.

## Universalist not-needed falsification

A prior `universalist_check.decision: not-needed` is falsified when the same cluster produces a new CAS/review/validation/PR counterexample after the repair.

The next packet may not say `decision: not-needed` unless a full `$universalist` output or root-equivalent `universal_boundary_packet` explains why the boundary artifact remains unnecessary.
