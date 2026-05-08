# TRIANGULATION — Multi-model verification harness

The skill optionally cross-checks Phase 4 (top-N recommendations) and Phase 7 (fresh-eyes) against multiple models. Use when triangulation appetite is `multi-model` AND `/multi-model-triangulation` is installed.

Two passes worth triangulating:
- **Phase 4 top recs** — the synthesis agent has one bias; independent reads from Codex + Gemini surface different blind spots.
- **Phase 7 fresh-eyes** — bugs Claude catches are different from bugs Codex catches are different from bugs Gemini catches; the union is high-value.

Don't triangulate Phase 1 (inventory is mechanical) or Phase 2 (scorers are already paired). Don't triangulate Phase 5 application (one model implements; the others review in Phase 7).

---

## Phase 4 triangulation prompt (per recommendation)

Send to Codex:

```
You are an independent reviewer. The skill `agent-ergonomics-and-intuitiveness-maximization-for-cli-tools` produced this recommendation:

<RECOMMENDATION_JSONL_LINE>

The surface in question is <SURFACE_DESCRIPTION_FROM_INVENTORY>.

Your task:
1. Do you AGREE with the recommendation as stated?
2. Is the diff_sketch the right approach, or is there a cleaner one?
3. Is the expected_uplift_per_dim plausible?
4. Is the risk note complete?
5. Is the test_plan sufficient to catch regression?
6. Is there a competing recommendation that would address the same surface better?

Answer in this JSON shape:
{
  "agreement": "agree" | "disagree" | "agree_with_revisions",
  "alternative_approach": "<if any, otherwise null>",
  "uplift_assessment": "plausible" | "optimistic" | "pessimistic",
  "risk_gaps": "<list of risks the rec missed, or null>",
  "test_gaps": "<list of regression cases the test wouldn't catch, or null>",
  "competing_recommendation": "<if any, otherwise null>"
}

DO NOT propose unrelated improvements. Stay scoped to this single recommendation.
```

Send to Gemini: identical prompt.

Each response is appended to `<SIBLING>/audit/triangulation/<RECOMMENDATION_ID>_<MODEL>.json`.

---

## Reconciliation logic

The synthesizer reads all three responses and applies the rules:

| Claude | Codex | Gemini | Action |
|--------|-------|--------|--------|
| agree | agree | agree | Recommendation stands. Mark `triangulation.consensus_diff: null`. |
| agree | agree | disagree | Treat dissent as critique. Revise rec to address it. Mark `triangulation.consensus_diff: <gemini's concern>`. |
| agree | disagree | disagree | Two-thirds disagreement. Recommendation is suspect. Pause; reconsider. Mark `triangulation.consensus_diff: <both concerns>`. Likely revise or split. |
| disagree | disagree | disagree | All three disagree. Drop recommendation. File the underlying surface as a separate exploratory bead. |
| agree_with_revisions × 3 | | | Apply the union of revisions. |
| Mixed agree + agree_with_revisions | | | Apply the revisions. |

Examples (from real audit output):

```
R-007 (levenshtein-1 typo correction):
  Claude: agree
  Codex: agree_with_revisions — "consider precomputing the closest-match table at startup; recomputing per-error is wasteful"
  Gemini: agree

  Action: revise diff_sketch to include startup precomputation. Re-score expected_uplift_total (still +600). Revise risk: "negligible startup cost; ~50µs for typical flag count".
```

```
R-014 (auto-rerun on stale cache):
  Claude: agree
  Codex: disagree — "auto-rerun changes side-effect surface; should require explicit --refresh"
  Gemini: disagree — "agrees with Codex; auto-rerun violates safety_with_recovery"

  Action: revise to "add --refresh flag; emit warning when cache is stale; do NOT auto-rerun." Re-score expected_uplift (drops from +500 to +300; still worthwhile).
```

---

## Phase 7 fresh-eyes triangulation

Phase 7 already runs the three calibrated prompts (verbatim, see `PHASES.md`). With `multi-model`:

- Round 1: Claude runs all three prompts.
- Round 2: Codex runs all three prompts.
- Round 3: Gemini runs all three prompts.

Each round produces findings. The union is the fix list.

Phase 7 termination is now: **all three rounds come up clean (only trivial edits) in two consecutive cycles.** That's a stricter bar than single-model fresh-eyes, but appropriate for Swarm-tier work.

---

## When triangulation isn't worth it

- **Single-surface-rescore.** Overkill.
- **Tiny tools.** Three models reviewing 5 verbs is wasteful.
- **Audit-only mode.** No code changes; no high-stakes decisions to triangulate.
- **The user is debugging the methodology itself.** Single-model is faster.

Stick with `peer-claude` (two Claude subagents from different contexts) for those cases. It catches a lot of single-model blind spots without the orchestration tax.

---

## Cost / latency budget

| Tier | Triangulation calls per pass | Wall-time tax |
|------|------------------------------|----------------|
| Solo / Pair / Squad | 0 (or peer-claude only) | Free / +20% |
| Squad with optional triangulation | 10–20 | +1–2h |
| Swarm | 30–50 | +3–6h |

If the budget is tight, prioritize triangulating Phase 4 top-5 recs (highest uplift) and skip Phase 7 triangulation.
