# Common ledgers

Use ledger fields consistently across skills and specialist outputs.

## Canonical identifiers

- Keep stable IDs for findings, invariants, hazards, checks, and passes when the same issue survives multiple loops.
- Stamp every meaningful pass with the current `artifact_state_id` or `artifact_state_label`.
- If a prior signal is no longer current, mark it stale rather than silently dropping it.

## Packet-native specialist footer

Every specialist output should end with the shared specialist packet fields when the workflow requires packet validation:

- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `top_material_signals`
- `unresolved_signals`
- `agreement_pressure`
- `stale`
- `final_call`

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

### Verification ledger

- `direct_changed_path`
- `claimed_failure_mechanism`
- `regression_surface`
- `checks_run`

### Surface delta receipt

- `production_files_touched`
- `production_insertions`
- `production_deletions`
- `public_symbols_added`
- `helpers_wrappers_adapters_added`
- `flags_branches_state_variants_added`
- `duplicate_shadow_paths_retired`
- `tests_proofs_added`
- `net_surface_call`

## State labels

Use stable, phase-aware labels such as:

- `loop-01-post-build`
- `loop-02-post-review`
- `targeted-validation-01`
- `closure-candidate-03`
- `right-sized-route-validate-only`
- `surface-budget-larger-with-warrant`
