# Packet-Native Specialist Briefing Contract

Use this contract when a specialist custom subagent reports back to `meta-orchestrator`.

The goal is to emit a briefing that is already close to the canonical ledgers and can be moved into the Closure Handoff Packet with minimal normalization.

## Required section order

1. **Specialist Briefing Header**
2. **Top Material Signals**
3. **Unresolved Signals**
4. **Domain Ledger**
5. **Suggested Next Checks**
6. **Residual Uncertainty**

## Specialist Briefing Header fields

- `role`
- `artifact_state_label`
- `scope`
- `focus`
- `artifact_summary`

## Signal fields

Each item in **Top Material Signals** and **Unresolved Signals** should include:

- `signal_id`
- `category`
- `materiality`
- `severity`
- `evidence`
- `why_it_matters`
- `implicated_surfaces`
- `impacted_invariants`
- `recommended_posture`

Where practical:
- use `recommended_posture`: `mapping-only` | `validating-check-only` | `accretive-remediation` | `structural-remediation`
- use `severity`: `blocker` | `major` | `moderate` | `minor` | `info`

## Domain Ledger expectations by role

- `evidence_mapper` -> artifact-set and diagnosis-pressure fields
- `invariant_auditor` -> invariant-ledger fields
- `hazard_hunter` -> foot-gun-register fields
- `complexity_auditor` -> complexity-ledger fields
- `verification_auditor` -> verification-ledger fields

## Rules

- Be concise.
- Cite files, symbols, tests, commands, logs, or outputs.
- If a field is unknown, write `unknown`.
- Do not turn the briefing into a general essay.
- Do not propose code changes unless the parent explicitly asks for remediation advice.
