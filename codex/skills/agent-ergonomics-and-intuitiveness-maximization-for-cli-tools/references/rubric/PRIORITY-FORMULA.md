# PRIORITY-FORMULA — Ranking recommendations

Recommendations are ranked by **priority** so Phase 5 implementers know what to fix first. Priority is the product of three components.

```
priority = frequency × score_gap × blast_radius
```

All three components are normalized to `[0, 1]`. The product is in `[0, 1]`. **Store the raw product** in the `priority` field of `recommendations.jsonl` (e.g. `0.0875`) — do **not** pre-multiply by 100 or 1000. The synthesizer sorts by raw priority descending; downstream renderers may multiply by 100 for human-friendly display, but the durable value in JSONL is always raw `[0, 1]`.

---

## frequency: how often agents hit this surface

Estimated from CASS mining (`subagents/cass-miner.md`) + canonical-task usage. The skill samples the user's prior agent sessions and counts how often this `surface_id` was invoked.

| Frequency band | Score | Examples |
|----------------|-------|----------|
| Never seen | 0.05 | A subcommand that exists in source but agents never use |
| Rare (< 1% of sessions) | 0.20 | Niche flags (`--debug-tokens`) |
| Occasional (1–10%) | 0.50 | Subcommand-level flags |
| Common (10–50%) | 0.75 | Top-level subcommands; canonical-task verbs |
| Universal (> 50%) | 1.00 | `<tool>` bare invocation; `<tool> --help` |

If CASS mining wasn't run (skip appetite), default `frequency = 0.5` for canonical-task verbs and `0.3` for everything else, and document in HANDOFF.md.

---

## score_gap: how far below the bar

Computed deterministically from the surface's current weighted_score:

```
score_gap = (1000 - weighted_score) / 1000
```

| weighted_score | score_gap |
|----------------|-----------|
| 1000 | 0.00 (perfect; nothing to fix) |
| 750 | 0.25 |
| 500 | 0.50 |
| 250 | 0.75 |
| 0 | 1.00 (worst) |

The Polish Bar lives at 750, so any surface below 750 contributes positively. If a recommendation would lift across multiple surfaces, use the *worst* surface's score_gap.

---

## blast_radius: how badly does it stay-bad if unfixed

Subjective but rubric-pinned. Three classes:

| Class | Score | Meaning |
|-------|-------|---------|
| Cosmetic | 0.10 | Slight friction; agent eventually finds the right invocation. |
| Workflow | 0.50 | Agent gets stuck or wastes round-trips on a common task. Time-cost meaningful. |
| Blocker | 1.00 | Agent cannot complete a canonical task; or the tool produces silently-wrong results an agent might trust. |

Heuristics for picking:
- A typo not corrected → workflow (0.50).
- A typo not corrected on a flag used in 50%+ of canonical tasks → blocker (1.00).
- An ANSI-color leak into piped stdout → blocker for parseability (1.00); cosmetic for human use (0.10).
- A missing `--help` example → cosmetic (0.10).
- A missing `--json` mode for a read-side verb → workflow (0.50) or blocker (1.00) depending on canonical-task centrality.
- Silent_fail outcome on a typo → blocker (1.00). Always.

For ambiguous cases, default to workflow (0.50) and document in `priority_components.blast_radius_reason`.

---

## Composing priority

Example for R-007 (Levenshtein-1 typo correction for `--json` family):

```jsonc
{
  "frequency": 0.7,        // --json appears in ~70% of canonical-task agent sessions
  "score_gap": 0.5,        // affected surfaces' worst weighted_score is ~500
  "blast_radius": 0.25,    // workflow: agent corrects after one round-trip but with friction
  "priority": 0.0875       // 0.7 × 0.5 × 0.25
}
```

Sort recommendations by priority descending; the top 10 are the synthesizer's output.

---

## When the formula doesn't fit

If two recs have nearly-equal priority but different effort:
- Tie-break on **effort** (smaller diff sketch wins; ship-first principle).
- Tie-break on **risk** (lower risk wins; prefer additive changes over breaking changes).
- Tie-break on **uplift coverage** (rec affecting more surface_ids wins; bundle synergy).

If a rec has very high priority but very high risk (e.g. would force a breaking change to an established CLI), split it into:
1. Pre-rec: add the new flag/verb without removing the old.
2. Main rec: deprecate the old.
3. Post-rec: remove the old (a future pass).

Each gets its own priority computation. The pre-rec usually clears Phase 5 first.

---

## Adapting per-project

Projects can override the default weighting by adding to this file:

```yaml
priority_overrides:
  formula: "frequency × score_gap × blast_radius × project_multiplier"
  project_multiplier: 1.5    # if this is a public OSS tool with high stakes
```

Document overrides in HANDOFF.md and the manifest.

---

## Anti-patterns

- **Don't game frequency by cherry-picking sessions.** Use `cass --robot --limit 1000` and let it sample.
- **Don't claim blast_radius=1.00 for everything below 750.** That's lazy. Score_gap already captures the "below bar" signal.
- **Don't skip CASS mining and pretend frequency=0.5 for everything.** That throws away a third of the priority signal.
- **Don't tie-break on personal preference.** Use the ladder above.
