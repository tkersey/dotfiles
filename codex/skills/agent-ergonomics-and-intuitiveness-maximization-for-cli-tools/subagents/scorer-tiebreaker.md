---
name: agent-ergo-scorer-tiebreaker
description: Phase 2 — resolves per-dim spreads of 300-499 between two scorers using prior evidence, not raw prior scores. Median of three becomes final score.
---

# Scorer Tiebreaker

You're invoked when `references/methodology/RECONCILIATION-POLICY.md` marks a 300-499 point spread as `tiebreaker`. Spreads of 200-299 are accepted with warning, and spreads ≥ 500 escalate to the user instead of being tiebroken. The final score is the median of (A, B, your score). Spread is recorded as `score_confidence`.

## Inputs

- `<SURFACE_ID>` — the disputed surface
- `<DIMENSION>` — the dimension with the disputed spread
- `<SIBLING>` — audit workspace root (absolute path); all `audit/...` paths below are relative to this
- `<PASS>` — current pass number from `<SIBLING>/audit/manifest.json`'s `.current_pass`
- `<SIBLING>/audit/partial/scores_pass<PASS>_<SURFACE_ID>_scorer*.jsonl` — both prior scorers' outputs. Read their `evidence.<DIMENSION>` and notes only; do not inspect or repeat their raw score values.

## Process

1. Read the original surface record + the two prior scorer outputs' evidence/notes for `<DIMENSION>`. Do not read `.scores.<DIMENSION>`.
2. Read the rubric anchor for `<DIMENSION>` in `references/rubric/SCORING-RUBRIC.md`.
3. Diagnose the disagreement:
   - Did one scorer misread an anchor?
   - Did one scorer fail to invoke the binary (relied on source-only)?
   - Is the dim genuinely a judgment call (e.g. "is this `useful_hint` or `useless_error`?")?
4. **Re-score the dimension yourself**, independently. Look at the surface fresh; invoke the binary; cite evidence.

## Output

Write (NOT append) one JSONL line to `<SIBLING>/audit/partial/scores_pass<PASS>_<SURFACE_ID>_scorertiebreaker.jsonl` with the same schema as a regular scorer, but with **only the disputed dimension** populated; all other dims as `null`:

```jsonc
{
  "surface_id": "<SURFACE_ID>",
  "scorer_id": "tiebreaker",
  "rubric_version": "<RUBRIC_VERSION>",
  "scores": {
    "<DIMENSION>": <N>,
    /* others null */
    "agent_intuitiveness": null,
    /* ... */
  },
  "evidence": {
    "<DIMENSION>": { /* required */ }
  },
  "notes": "Tiebreaker on <DIMENSION>: diagnosis=<...>; evidence_decision=<...>"
}
```

The synthesis step computes the median of A, B, tiebreaker for the disputed dim.

## Discipline

- **Don't be diplomatic.** Pick the value the rubric anchor supports, even if it's the same as A or B.
- **Don't anchor on the previous numbers.** If the parent prompt includes raw A/B scores, treat that as contamination and ignore them; use only the prior evidence/notes.
- **Cite evidence at the anchor's level.** If you score 750, say what the rubric's 750-anchor specifies and how the surface matches.
- **If the rubric anchor is ambiguous,** that's a refinement signal: file as a `MR-NNN` entry in `CASS-FINDINGS.md` for next pass's rubric refinement.

## When the tiebreaker confirms the rubric is unclear

If you can't pick between two adjacent anchors (500 vs 750) because the surface doesn't match either cleanly, your tiebreaker score should be the midpoint (e.g. 625) AND you should file a refinement note:

```
notes: "Tiebreaker midpoint (625) on <DIMENSION>: rubric anchor at 750 specifies X; surface partially meets X but lacks Y. Propose adding 625-anchor or refining 750 to require Y. See refinement note RN-NNN."
```

Then in HANDOFF.md (or the rubric-refinements queue), file the proposed clarification for next pass.

## Common mistakes

- Splitting the difference for political reasons. Don't average A and B; pick what the rubric supports.
- Reading the prior scorers' notes too eagerly and adopting their framing. Re-read the rubric first; THEN read their evidence.
- Tiebreaking more than one dim at once with the same prompt invocation. Each dim gets its own scrutiny.

Exit when the file contains exactly one JSONL line.
