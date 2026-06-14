# Falsification Rules

## Universalist not-needed falsification

A previous `universalist_check.decision: not-needed` is falsified when the same cluster produces a new CAS/review/validation/PR counterexample after the repair.

When falsified:

```yaml
falsification:
  prior_decision_invalidated: yes
  next_required_action: universal-boundary-packet | block
```

The next packet may not say `decision: not-needed` unless a full `$universalist` output or root-equivalent `universal_boundary_packet` explains why the boundary artifact is still unnecessary despite the recurrence.

## Normal form falsification

A selected normal form is falsified when the same counterexample family reappears on a current artifact state after implementation.

Do not patch locally again. Reopen compiler, run universalist if needed, or block.
