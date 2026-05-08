---
name: agent-ergo-triangulator
description: Phase 4 / Phase 7 — multi-model verification (Claude + Codex + Gemini) for top-N recommendations or fresh-eyes findings. Reconciles disagreement.
---

# Triangulator

Multi-model verification harness. Used in Phase 4 (top-N recs) and Phase 7 (fresh-eyes). Reconciles disagreement between Claude, Codex, and Gemini.

Reads from / writes to `<SIBLING>/audit/triangulation/`.

## Inputs

- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- `<TRIANGULATION_ID>` — what's being triangulated: `R-NNN` (a recommendation) or `FE-N` (a fresh-eyes round). NOTE: this is *not* the target CLI repo (`<TARGET>` elsewhere in the skill); it identifies the subject of triangulation.
- `<SUBJECT>` — the JSONL line or markdown excerpt being reviewed
- Triangulation appetite: `peer-claude` (two Claude subagents) or `multi-model` (Claude + Codex + Gemini)

## Process

For each model, send the verbatim prompt from `references/methodology/TRIANGULATION.md § Phase 4 triangulation prompt` (or Phase 7 fresh-eyes prompts).

Capture each model's response as `<SIBLING>/audit/triangulation/<TRIANGULATION_ID>_<MODEL>.json`.

Apply the reconciliation matrix from `TRIANGULATION.md`:

| Claude | Codex | Gemini | Action |
|--------|-------|--------|--------|
| agree × 3 | | | Stand. `consensus_diff: null`. |
| agree × 2 + 1 dissent | | | Treat as critique. Revise. `consensus_diff: <dissent>`. |
| agree × 1 + 2 dissent | | | Suspect. Pause. `consensus_diff: <both>`. |
| disagree × 3 | | | Drop the rec. File underlying surface as exploratory bead. |

If `peer-claude` (no Codex/Gemini): two Claude responses; agreement → stand; disagreement → revise. Less rigorous but cheaper.

## Output

For each target:

```jsonc
{
  "target": "R-007",
  "subject_summary": "Levenshtein-1 typo correction",
  "models_consulted": ["claude_opus_4_7", "codex_5_5", "gemini_3_1_pro"],
  "responses": {
    "claude_opus_4_7": {"agreement": "agree", ...},
    "codex_5_5": {"agreement": "agree_with_revisions", "alternative_approach": "..."},
    "gemini_3_1_pro": {"agreement": "agree"}
  },
  "reconciliation": "agree_with_revisions × 1 → revise rec to address codex's concern",
  "consensus_diff": "codex notes startup precomputation is wasteful; revise to pre-compute table once at startup",
  "completed_at": "<ISO8601>"
}
```

Append to the rec's `triangulation` field in `<SIBLING>/audit/recommendations.jsonl`. If revision is required, update `diff_sketch` and `expected_uplift_per_dim`.

## Discipline

- **Don't ask the same model twice and call it triangulation.** Multi-model means different model families.
- **Spawn fresh contexts** — each model agent must start without prior audit context.
- **Don't reconcile by averaging.** Use the matrix.
- **Document every reconciliation decision.** The synthesizer + future readers need to know why a rec was revised.

## Output to main agent

Print summary:

```
triangulation complete for <TRIANGULATION_ID>:
  consensus: <agreement_pattern>
  action: <stand|revise|suspect|drop>
  consensus_diff: <one-line>
```

Exit when triangulation files are written.
