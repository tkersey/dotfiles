# Common ledgers

Use ledger fields consistently across skills and specialist outputs.

## Canonical identifiers
- Keep stable IDs for findings, invariants, hazards, checks, and passes when the same issue survives multiple loops.
- Stamp every meaningful pass with the current `artifact_state_label`.
- Stamp every specialist packet with the current `artifact_state_id`.
- If a prior signal is no longer current, mark it stale rather than silently dropping it.

## Packet-native specialist footer
Every specialist output should end with:
- `artifact_state_id`
- `artifact_state_label`
- `scope`
- `top_material_signals`
- `unresolved_signals`
- `agreement_pressure`: `aligned` | `mixed` | `conflicting` | `unknown`
- `stale`: `yes` | `no` | `unknown`
- one-line final call

Reject specialist output as `transport-invalid` when it contains raw transport wrappers, root-only response text such as `Echo:`, queued prompts, multiple packets, or no packet.

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

## State labels
Use stable, phase-aware labels such as:
- `loop-01-post-build`
- `loop-02-post-review`
- `targeted-validation-01`
- `closure-candidate-03`

Use state IDs that bind a packet to the current code shape, such as:
- `branch=feature/foo head=abc123 diff=changed-paths-sha phase=prepatch`
- `branch=feature/foo head=abc123 diff=changed-paths-sha phase=post-fixture-refresh`
