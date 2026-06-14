# Shipping Gate

`$ship` is permitted only after proof is current for the intended branch head.

## Required checks before `$ship`

- all in-scope `$st` tasks are complete, blocked, deferred, or removed from scope with evidence
- build proof is current or absent with evidence
- lint/static proof is current or absent with evidence
- tests/proofs are current or absent with evidence
- language-specific proof lanes have run when relevant
- no unresolved material fixed-point, ablation, soundness, or verification gate remains
- PR creation/update is in scope

## Missing commands

If a repo lacks a build/lint/test command, record:

- where you looked
- what command category was missing
- what substitute proof was run
- whether this weakens shipping confidence

Do not say “all checks pass” for categories that were not found or not run.
