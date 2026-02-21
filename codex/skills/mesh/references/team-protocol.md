# Team Protocol (Coder / Reducer / Fixer / Feedback)

This protocol defines role boundaries and handoff envelopes for the four-agent coding team.

## Role boundaries

- `coder`: authoring-only; produces candidate changes and proof signals.
- `reducer`: simplifies incidental complexity while preserving invariants.
- `fixer`: safety authority for invariant/regression concerns.
- `feedback`: doctrine-fit scoring and actionable improvement guidance.

No role should assume another role's final authority domain.

## TeamTaskEnvelope v1

```json
{
  "task_id": "st-123",
  "objective": "one-sentence objective",
  "scope": ["path/or/glob/**"],
  "constraints": ["no dependency additions"],
  "invariants": ["must keep API stable"],
  "proof_command": "uv run pytest tests/x.py -k target",
  "conflict_class_hint": "unknown",
  "deadline_class": "feature"
}
```

## AgentResultEnvelope v1

```json
{
  "agent": "coder",
  "task_id": "st-123",
  "status": "proposed",
  "artifact_ref": "diff-or-ledger-id",
  "evidence": ["pytest passed: 12 passed"],
  "rubric_scores": {
    "contract_clarity": 5,
    "invariant_strength": 4,
    "minimal_incision": 4,
    "proof_credibility": 5,
    "legibility_trace": 4
  },
  "recommended_next": "handoff"
}
```

## Handoff requirements

Coder handoff must include:

1. declared invariants
2. proof command and result
3. known risk notes
4. scope boundaries touched

Reducer/fixer/feedback responses must include:

1. decision (`accept`, `rework_required`, or `blocked` semantics)
2. concrete action items
3. evidence references
