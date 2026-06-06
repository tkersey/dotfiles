# Ablation Activation

Every `$fixed-point-driver` run must decide whether ablation is active. The point
is to make deletion/collapse pressure observable instead of letting it remain a
concept in the skill body.

## Activation states

- `required`: additive mutation, duplicate truth surface, questionable kept surface, local-fix pileup, or PR/review closure could change by deleting/collapsing/canonicalizing instead.
- `not-required`: the run is proof-only, validation-only, or has no mutation-capable / keep-surface decision.
- `blocked`: artifact state is too stale or incomplete to judge ablation safely.

## Valid receipts

- `ablation_auditor` packet;
- root-equivalent Ablation Packet;
- Ablation Ledger rows;
- explicit no-candidate receipt with surfaces checked and proof that no candidate exists.

A fixed-point run with ablation triggers may not proceed to closure on an implicit
or omitted ablation decision.
