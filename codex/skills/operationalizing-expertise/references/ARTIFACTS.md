# Artifacts and Deltas

Use this when you need a deterministic, multi-agent artifact loop (Track B).

## Delta Contract (minimum)

A delta is a single JSON object, one per block. It is the only accepted write format.

```json
{
  "operation": "ADD|EDIT|KILL",
  "section": "hypothesis_slate|predictions_table|discriminative_tests|assumption_ledger|anomaly_register|adversarial_critique|research_thread",
  "target_id": "H1" | null,
  "payload": { ... },
  "rationale": "why"
}
```

Rules:
- ADD requires target_id = null and a complete payload.
- EDIT requires target_id and only the fields to change.
- KILL requires target_id and a reason in payload.
- Research thread is singleton: only EDIT.

## Deterministic Merge Rules

- Deltas are applied in timestamp order; ties broken by stable sender ordering.
- ID generation is deterministic by section prefix + increment.
- KILL sets tombstone fields; item remains for audit.
- Missing required fields or invalid sections are lint errors, not silent drops.

## Lint Gates (examples)

- Missing third alternative in hypothesis slate.
- Missing anchors in any item that claims evidence.
- Section min/max counts (e.g., at least 2 hypotheses).
- Invalid section name or malformed payload shape.

## Join-Key Contract

The join-key is the thread_id:
- Agent Mail thread_id
- Artifact filename (`artifacts/<thread_id>.md` or `.json`)
- Session/tmux session name

Pick a convention and never change it.

## Storage Layout (example)

```
artifacts/
  RS-20251230-cell-fate.md
  RS-20251230-cell-fate.json
.research/
  hypotheses/RS-20251230-cell-fate-hypotheses.json
  hypothesis-index.json
```

## Compile Pipeline (example)

```
Kickoff -> Agent deltas -> Parse -> Merge -> Lint -> Render -> Persist
```

