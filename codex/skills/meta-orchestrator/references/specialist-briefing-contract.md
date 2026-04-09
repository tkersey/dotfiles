# Packet-Native Specialist Briefing Contract

Use this contract when a specialist custom subagent reports back to `meta-orchestrator`.

The goal is to emit a briefing that is already close to the canonical ledgers and can be moved into the Closure Handoff Packet with minimal normalization.

## Exact response shape

Return exactly one of these and nothing else:

```text
<SPECIALIST_PACKET role="<role>" schema="v1">
artifact_state_label: <state>
scope: <scope>
focus: <focus>
artifact_summary: <summary>
top_material_signals:
- signal_id: ...
  category: ...
  materiality: ...
  severity: ...
  evidence: ...
  why_it_matters: ...
  implicated_surfaces: ...
  impacted_invariants: ...
  recommended_posture: ...
unresolved_signals:
- signal_id: ...
  category: ...
  materiality: ...
  severity: ...
  evidence: ...
  why_it_matters: ...
  implicated_surfaces: ...
  impacted_invariants: ...
  recommended_posture: ...
domain_ledger:
- ...
suggested_next_checks:
- ...
residual_uncertainty:
- ...
routing_call: <one line>
</SPECIALIST_PACKET>
```

Or, if a valid packet cannot be produced:

```text
SPECIALIST_PACKET_INVALID: <reason>
```

Do not add markdown fences, `Echo:`, acknowledgements, progress updates, or any prose before or after the packet.

## Required section order

1. **Specialist Briefing Header**
2. **Top Material Signals**
3. **Unresolved Signals**
4. **Domain Ledger**
5. **Suggested Next Checks**
6. **Residual Uncertainty**
7. **Routing Call**

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
- Use the exact packet wrapper and key names shown above.
- Use `routing_call:` as the final line inside the packet; do not invent role-specific closing labels.
- If you cannot produce a valid packet, return `SPECIALIST_PACKET_INVALID: <reason>` and stop.
- This is an internal specialist packet, not a user-facing final answer: do not include `Echo:`, repo-instruction acknowledgements, progress updates, or any other response wrapper.
- Do not turn the briefing into a general essay.
- Do not propose code changes unless the parent explicitly asks for remediation advice.
