# Guardrail Blueprint Template

Use this template to produce the final output for `$guards`.

## Problem Statement
- `use_case`:
- `system_boundary`:
- `protected_assets`:

## Success Criteria
- `primary_outcome`:
- `safety_outcome`:
- `operational_outcome`:

## Risk Tier and Enforcement Posture
- `risk_tier`: `low | medium | high | critical`
- `enforcement_default`:
- `human_gate_policy`:

## Threat Scenarios
List 5-12 concrete scenarios.
For each scenario include:
- `scenario_id`
- `attack_path`
- `target_asset`
- `likely_impact`
- `risk_tier`

## Layered Control Stack
For each scenario, describe controls at:
1. Input
2. Context
3. Model
4. Tool pre-call
5. Tool post-call
6. Output
7. Human approval
8. Audit and traceability

## Control Matrix
Use this exact schema:

| scenario_id | threat_type | risk_tier | control_layer | control_pattern | enforcement_mode | evidence_strength | owner | risk_if_missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | prompt_injection | high | tool_pre | argument schema + allowlist | fail_closed_pending_human | pattern | app_platform | unauthorized side effects |

## Residual Risks
For each material risk include:
- `risk_id`
- `description`
- `probability`
- `impact`
- `trigger`
- `mitigation`
- `owner`

## Validation and Acceptance Checks
Map requirements to tests:

| requirement_id | requirement | acceptance_check |
| --- | --- | --- |
| R1 | High-risk actions are fail-closed | Scenario test confirms high-risk tool calls require human approval |

## Rollout and Monitoring
- `phase_1`:
- `phase_2`:
- `phase_3`:
- `key_metrics`:
- `alert_conditions`:

## Rollback and Abort Criteria
- `abort_trigger_1`:
- `abort_trigger_2`:
- `rollback_action`:
- `resume_condition`:

## Implementation Brief
Provide executable handoff items:

| step | owner | success_criteria |
| --- | --- | --- |
| Define tool boundary policy | application engineering | tool allowlist and argument schema are approved and versioned |
