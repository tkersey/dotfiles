# Common ledgers

Use ledger fields consistently across skills, specialist outputs, and closure
handoffs.

## Canonical identifiers

- Keep stable IDs for findings, invariants, hazards, checks, passes, ablation rows,
  and negative-evidence entries when the same issue survives multiple loops.
- Stamp every meaningful pass with the current `artifact_state_label`.
- Stamp every specialist packet and negative-ledger pass with the current
  `artifact_state_id`.
- If a prior signal is no longer current, mark it stale, superseded, reopened, or
  accepted-risk rather than silently dropping it.

## Common ledger shapes

### Findings ledger

- `finding_id`
- `materiality`
- `severity`
- `category`
- `status`
- `evidence`
- `next_action`

### Soundness ledger

- `claim_id`
- `claim_or_obligation`
- `witness_required`
- `witness_status`
- `preservation`
- `progress`
- `inhabitance`
- `minimum_acceptable_fix`

### Invariant ledger

- `invariant_id`
- `name`
- `tier`
- `status`
- `confidence`
- `blast_radius`
- `supporting_evidence`

### Ablation ledger

- `ablation_id`
- `surface`
- `kind`
- `current_obligation`
- `obligation_status`
- `canonical_owner`
- `replacement_path`
- `action`
- `deletion_or_collapse_proof`
- `keep_warrant`
- `status`

### Routing and Budget Ledger

- `task_shape`
- `fixed_point_lane`
- `subagent_mode`
- `specialist_budget_planned`
- `specialist_budget_actual`
- `budget_exceptions`
- `lane_change_history`

### Adversarial Action Ledger

- `action_id`
- `phase`
- `adversary_lane`
- `parallelism_mode`
- `challenged_action`
- `strongest_countercase`
- `packet_status`
- `veto_status`
- `route_delta`
- `evidence_ref`
- `disposition`


## Isomorphic ablation addendum

Ablation Ledger rows that select deletion, collapse, reuse, canonicalization, privatization, or decommissioning must be paired with an Ablative Isomorphism Card unless routed to `validate-first`. The fixed-point gate fails while selected lower-surface routes have missing behavior-preservation proof.
