# Latent Move Ledgers

Maintain these ledgers across the workflow. Use durable statuses. If a field is unknown, write `unknown`; do not omit it.

## Evidence Ledger

- `evidence_id`
- `source`
- `artifact_surface`
- `claim_supported`
- `confidence`
- `scope`
- `limitations`
- `freshness`
- `used_by`

## Latent Frame Ledger

- `frame_id`
- `latent_frame`
- `hidden_assumption`
- `non_obvious_surface`
- `reframe_pressure`
- `why_it_matters`
- `supporting_evidence`
- `risk_if_ignored`
- `routing_pressure`

## Constraint Ledger

- `constraint_id`
- `constraint`
- `type`: technical | product | time | compatibility | safety | operational | unknown
- `source`
- `hardness`: hard | soft | unknown
- `impact_on_moves`
- `open_question`

## Portfolio Ledger

- `tier`: Quick Win | Strategic Play | Advantage Play | Transformative Move | Moonshot
- `move`
- `artifact_spine`
- `expected_signal`
- `escape_hatch`
- `score_signal`
- `score_accretion`
- `score_ease`
- `score_reversibility`
- `score_speed`
- `open_question`

## Candidate Ledger

- `candidate_id`
- `move`
- `source_tier`
- `target_lane`
- `leverage_claim`
- `material_axis`
- `proof_surface`
- `minimum_viable_diff`
- `reversibility`
- `implementation_risk`
- `status`: active | eliminated | nominee | rejected | unknown
- `reason`

## Dominance Ledger

- `verdict`: Winner | No dominant move | Insufficient evidence
- `winner`
- `ranking`
- `why_it_dominates`
- `why_others_lose`
- `confidence`
- `first_proof_signal`
- `fastest_discriminating_check`
- `evidence_gates_failed`
- `residual_risk`

## Proof Signal Ledger

- `proof_id`
- `candidate_id`
- `first_proof_signal`
- `check_type`: test | benchmark | trace | typecheck | repro | static audit | doc-backed behavior | manual inspection | other
- `expected_result`
- `failure_interpretation`
- `cost`
- `executor_needed`: none | human | fixed-point-driver | other
- `limitations`

## Specialist Briefing Ledger

- `role`
- `artifact_state_label`
- `scope`
- `top_signals`
- `unresolved_signals`
- `ledger_updates`
- `agreement_pressure`
- `routing_call`
- `status`: ok | blocked | transport-invalid | stale
- `stale`

## Residual Uncertainty

- `assumptions`
- `environment_limits`
- `known_unknowns`
- `decision_gates`
- `execution_risks`
- `non_goals`
