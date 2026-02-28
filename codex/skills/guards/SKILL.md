---
name: guards
description: Generate provider-agnostic AI agent guardrail blueprints and control matrices from a use case. Use when designing or reviewing agent safety architecture, prompt-injection and tool-misuse defenses, risk-tiered human approval gates, or auditable enterprise guardrail policies using industry patterns across top providers.
---

# guards

## Mission

Turn ambiguous "add guardrails" requests into an implementation-ready guardrail architecture.
Produce provider-agnostic outputs that application engineers can execute without choosing a model vendor first.

## Output Contract

Always return a structured plan plus a control matrix.
The response must include these headings in this order:
1. Problem Statement
2. Success Criteria
3. Risk Tier and Enforcement Posture
4. Threat Scenarios
5. Layered Control Stack
6. Control Matrix
7. Residual Risks
8. Validation and Acceptance Checks
9. Rollout and Monitoring
10. Rollback and Abort Criteria
11. Implementation Brief

Never output provider-specific SDK instructions in default mode.
If a user explicitly requests provider mappings, keep them in a separate appendix titled `Provider Mapping (Optional)`.

## Request Contract

Model requests as `GuardrailBlueprintRequest v1`.
Required fields:
- `use_case`: one-sentence workload description
- `actor_profile`: who can trigger the agent and from where
- `tool_surface`: tools or side-effecting actions the agent can invoke
- `data_sensitivity`: `public | internal | confidential | regulated`
- `autonomy_level`: `assistant | semi_autonomous | autonomous`
- `regulatory_context`: baseline policy context
- `risk_tolerance`: `low | medium | high`

Defaults:
- `regulatory_context = US enterprise baseline`
- `risk_tolerance = medium`
- `freshness_mode = pattern_only`

When required fields are missing, ask only the minimum judgment-call questions needed to classify risk tier and tool boundary.

## Control Taxonomy (Fixed)

Map every threat scenario across this layer order:
1. Input controls
2. Context controls
3. Model controls
4. Tool pre-call controls
5. Tool post-call controls
6. Output controls
7. Human approval controls
8. Audit and traceability controls

Each scenario must include at least one control in every applicable layer.

## Enforcement Policy (Risk-Tiered Mixed Mode)

Apply this default policy unless the user overrides it:
- `low`: monitored allow with explicit logging and anomaly detection
- `medium`: allow with guardrails and sampled human review
- `high`: fail-closed for side-effecting actions unless explicit human approval
- `critical`: fail-closed by default with mandatory human approval and dual-control where possible

Hard rule:
- High and critical scenarios must not be fail-open.

## Workflow

1. Normalize the request into `GuardrailBlueprintRequest v1`.
2. Define the system boundary and identify side-effecting tools.
3. Classify risk tier by data sensitivity, autonomy level, and blast radius.
4. Build 5-12 concrete threat scenarios with attack paths and target assets.
5. Map layered controls using the fixed taxonomy.
6. Assign enforcement mode and human gate behavior per scenario.
7. Produce residual risk register with explicit owners.
8. Define acceptance checks and rollback triggers.
9. Cross-check control choices against `references/industry_patterns.md`.
10. Emit the final plan and control matrix using the template in `references/blueprint_template.md`.

## Evidence and Freshness Modes

Use one mode and state it in the output:
- `pattern_only` (default): synthesize provider-agnostic industry patterns.
- `hybrid`: cite sources for high-risk controls and decision-critical claims.
- `strict_source_cited`: cite sources for all major control recommendations.

When the prompt asks for "latest" provider specifics, verify against primary docs before finalizing.

## Quality Gates

Before completing, verify all gates:
1. Provider-agnosticity: no vendor-locked implementation steps in the main output.
2. Layer coverage: each high-risk scenario includes applicable controls across layers.
3. Enforcement correctness: high and critical scenarios include fail-closed behavior.
4. Residual risk completeness: each material risk has probability, impact, trigger, and owner.
5. Traceability: each major requirement maps to at least one acceptance check.
6. Operability: includes monitoring signals plus rollback/abort criteria.

## Non-Goals

- No legal opinions or jurisdiction-specific legal advice.
- No guarantee that any control makes compromise impossible.
- No deployment automation scripts or runtime policy engine implementation.
- No provider-specific code generation unless explicitly requested.

## Deliverable Checklist

1. Structured plan with all required headings.
2. Control matrix with standardized columns.
3. Residual risk register with explicit ownership.
4. Acceptance checks tied to requirements.
5. Rollout and rollback criteria.
6. Explicit mode declaration (`pattern_only`, `hybrid`, or `strict_source_cited`).

## Reference

- Template: `references/blueprint_template.md`
- Pattern baseline: `references/industry_patterns.md`
