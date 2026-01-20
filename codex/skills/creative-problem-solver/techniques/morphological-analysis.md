# Technique: Morphological Analysis (explore combinations)

## One-liner
Map the solution space as dimensions × values, then systematically enumerate non-obvious hybrids.

## Use when
- You’re designing an architecture/product/process with interchangeable components.
- You suspect the best option is a hybrid of familiar pieces.
- You keep debating single variables instead of the full design space.

## Avoid when
- The problem is a single contradiction (use TRIZ).
- You need a conceptual leap, not a configuration search (use Synectics / Provocation).

## Inputs
- A system boundary: what you’re designing.
- 4–8 dimensions that are meaningfully independent.

## Procedure (fast, 10–15 min)
1. List 4–6 dimensions.
2. For each, list 3–6 plausible values.
3. Enumerate 10–20 combinations (not all; sample smartly).
4. Prune with constraints; pick 3 combos; rewrite as experiments.

## Procedure (full, 25–45 min)
1. Define dimensions (orthogonal axes)
   - Ask: “If we change this, does it force changes in the others?” If yes, it’s not independent.
   - Prefer dimensions like: interface, storage, coordination, rollout, ownership, incentives.
2. Populate values
   - Include boring defaults + one extreme per axis.
3. Generate combinations
   - Start with the baseline combination.
   - Then deliberately vary 1 axis at a time, then 2 axes at a time.
   - Add 2–3 “wild” combos.
4. Constraint prune
   - Eliminate combinations that violate hard constraints.
   - Identify the “feasible frontier” (what remains).
5. Converge
   - Pick 3 combos: fastest-to-ship, safest-to-run, most-leverage.

## Prompt bank (copy/paste)
- “What are the real dimensions here (what can vary independently)?”
- “What value on this axis would be the extreme opposite?”
- “What hybrid is ‘boring + one wild axis’?”
- “Which combination violates constraints fastest (so we can prune)?”

## Outputs (feed CPS portfolio)
- A map of the design space (dimensions + values).
- A shortlist of hybrid architectures/options.

## Aha targets
- Discovering an axis you weren’t considering (ownership, rollout, incentives).
- A hybrid that dominates because it mixes ‘safe’ and ‘fast’ axes.

## Pitfalls & defusals
- Pitfall: dimensions overlap → Defusal: merge or re-define until axes are orthogonal.
- Pitfall: combinatorial explosion → Defusal: sample combos; prune aggressively with constraints.
- Pitfall: “values” are too abstract → Defusal: force concrete choices (SQL vs KV, manual vs automated).

## Examples
### Engineering
Design: internal feature-flag platform.
Dimensions:
- Storage: SQL / KV / hosted.
- Evaluation: server-side / client-side.
- Rollout: canary / percentage / cohort.
- Control: UI / config-file / API.
- Safety: audit logs / approvals / none.
Enumerate combos; pick: “KV + server-side + percentage + API + audit logs” as MVP; signal: adoption + incident rate.

### Mixed domain
Design: a personal learning routine.
Dimensions:
- Time: 10m / 30m / 60m.
- Format: reading / exercises / teaching.
- Cadence: daily / 3×week / weekly.
- Accountability: solo / buddy / public.
Sample combos; pick a reversible MVP: “30m exercises 3×week with buddy check-in”; signal: consistency rate; escape hatch: reduce time if adherence drops.