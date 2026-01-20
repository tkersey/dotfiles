# Technique: Oblique Draw (prompt → lever)

## One-liner
A fast framing reset: draw oblique prompts, pick one, then translate it into a concrete lever or constraint you can apply.

## Use when
- You feel stuck in a local optimum.
- You want a spark without a heavy process.
- You need a fresh angle in under 60 seconds.

## Avoid when
- You need deep tradeoff resolution (use TRIZ).
- You already have many options and need convergence.

## Inputs
- A short oblique prompt deck (or mini-deck below).

## Procedure (fast, 1–3 min)
1. Draw 4 prompts.
2. Pick 1 that feels “slightly wrong but interesting”.
3. Translate into a lever/constraint:
   - “What concrete change does this imply?”
4. Generate 3 options under that lever.

## Procedure (full, 8–12 min)
1. Draw 6 prompts; pick 2.
2. For each prompt:
   - Interpret it in 2 ways (technical + social/process).
   - Derive 2 levers.
3. Converge: keep the lever that creates the strongest Aha.

## Mini-deck (copy/paste)
- Do the opposite of the obvious move.
- Remove a step.
- Make it reversible first.
- Smallest test that could change the plan.
- Shift the bottleneck, not throughput.
- Change the unit of work.
- Swap one constraint for another.
- Borrow a pattern from another domain.
- Reduce coordination, not effort.
- Add a cheap signal.
- Make the default safe.
- Move work off the critical path.

## Prompt bank (translation helpers)
- “If we *removed a step*, which step disappears and what guardrail replaces it?”
- “If we *change the unit of work*, what is the new unit?”
- “If we *make it reversible first*, what’s the rollback/kill switch?”

## Outputs (feed CPS portfolio)
- One lever/constraint that reshapes the option space.

## Aha targets
- A new unit of work.
- A reversible default.
- A gating signal.

## Pitfalls & defusals
- Pitfall: poetic interpretation → Defusal: translation must be a concrete lever.
- Pitfall: prompt drives gimmicks → Defusal: keep it abstract; map to constraints, not surface features.

## Examples
### Engineering
Prompt: “Move work off the critical path.”
Lever: shift validation to async worker.
Options: async validation, staged enforcement, anomaly-triggered strict mode.

### Mixed domain
Prompt: “Reduce coordination, not effort.”
Lever: replace meetings with async decision records.
Options: templates, comment windows, lightweight facilitation; signal: decision cycle time; escape hatch: reintroduce a short sync if clarity drops.