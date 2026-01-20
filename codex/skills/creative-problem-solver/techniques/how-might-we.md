# Technique: How Might We (HMW) reframing

## One-liner
Convert observations/complaints into open, solvable prompts that keep constraints visible.

## Use when
- The problem statement is a complaint (“this is confusing”).
- You need an idea-friendly search space.
- You want to expose constraints without killing creativity.

## Avoid when
- You already have a good prompt and need divergence.
- The user wants a concrete plan now.

## Inputs
- Observation(s) and constraints.

## Procedure (fast, 4–7 min)
1. Write the complaint/observation.
2. Extract the desired outcome.
3. Add the key constraint: “without …”.
4. Generate 3 HMW variants (broad, medium, narrow).
5. Pick one; use it to drive ideation.

## Procedure (full, 10–15 min)
1. Gather observations
   - “Users do X”, “We see Y”, “This fails when …”.
2. Translate to HMW prompts
   - Broad: invites exploration.
   - Focused: includes constraints.
   - Experimental: includes measurable signal.
3. Select
   - Choose the prompt that is both generative and testable.

## Prompt bank (copy/paste)
- “How might we <outcome> without <cost>?”
- “How might we make <task> the default, while still allowing <edge case>?”
- “How might we reduce <pain> by 50% in 2 weeks?”

## Outputs (feed CPS portfolio)
- A high-quality ideation prompt.
- A constraint-aware search space.

## Aha targets
- Turning “this is bad” into “we want X under constraints Y.”

## Pitfalls & defusals
- Pitfall: too broad (“How might we improve everything?”) → Defusal: add constraint/timebox.
- Pitfall: too narrow (“How might we add this exact button?”) → Defusal: widen one level.

## Examples
### Engineering
Observation: “This config is confusing.”
HMW: “How might we make setup work by default while still allowing explicit overrides for edge cases?”
Signal: setup time drops; escape hatch: keep advanced overrides behind an ‘expert’ flag.

### Mixed domain
Observation: “I procrastinate on hard tasks.”
HMW: “How might we make starting a hard task frictionless without relying on motivation?”
Signal: starts/week increases; escape hatch: shrink task scope if it increases stress.