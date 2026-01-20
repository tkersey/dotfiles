# Technique: SCAMPER (mutate a baseline)

## One-liner
A structured mutation engine for an existing approach: Substitute, Combine, Adapt, Modify, Put to use, Eliminate, Reverse.

## Use when
- You have a baseline solution but need better variants.
- You need incremental creativity without a full reset.
- You want a prompt set that reliably produces options.

## Avoid when
- You have no baseline at all (use Brainstorming / Brainwriting).
- The real issue is “we want X but it worsens Y” (use TRIZ).

## Inputs
- The baseline (current solution / plan / API / workflow).
- A target outcome + constraints.

## Procedure (fast, 8–12 min)
1. Write baseline in 1–2 lines.
2. Run SCAMPER prompts; generate 2–3 variants per letter.
3. Pick 3 variants; rewrite as experiments (signal + escape hatch).

## Procedure (full, 15–25 min)
1. Baseline inventory
   - List components/steps (A → B → C).
   - Identify the bottleneck step.
2. SCAMPER sweep
   - S: Substitute a component (tool, actor, interface).
   - C: Combine steps or responsibilities.
   - A: Adapt from a neighboring domain.
   - M: Modify magnitude/frequency/ordering.
   - P: Put to use elsewhere (repurpose assets).
   - E: Eliminate a step/permission/decision.
   - R: Reverse direction, order, ownership, or default.
3. Converge
   - Choose 1 variant that optimizes Speed, 1 that optimizes Reversibility, 1 that optimizes Signal.

## Prompt bank (copy/paste)
- Substitute: “What if a different owner/tool does this step?”
- Combine: “What if we merge these two steps into one boundary?”
- Adapt: “Where have we solved a similar constraint?”
- Modify: “What if we do this 10× less often / 10× more often?”
- Put to use: “What existing thing can we repurpose?”
- Eliminate: “What’s the smallest safe version with fewer steps?”
- Reverse: “What if the default is the opposite?”

## Outputs (feed CPS portfolio)
- A set of variants anchored to the baseline (easier to justify).
- A shortlist of hardened experiments.

## Aha targets
- A reversible default.
- Removing a step without losing safety (replace with a guardrail).

## Pitfalls & defusals
- Pitfall: generating variants that violate constraints → Defusal: keep constraints visible at top.
- Pitfall: only “Modify” gets used → Defusal: enforce at least one idea per letter.
- Pitfall: variants lack testability → Defusal: rewrite top variants into measurable experiments.

## Examples
### Engineering
Baseline: flaky test suite.
- Eliminate: remove shared global state.
- Combine: merge setup into a single fixture.
- Reverse: test boundary contracts instead of internals.
Signal: flake rate drops; Escape hatch: revert fixture change if it breaks too many tests.

### Mixed domain
Baseline: weekly team status meeting.
- Eliminate: remove the meeting; replace with async updates.
- Reverse: start with blockers first, not accomplishments.
- Substitute: rotate facilitator.
Signal: fewer interruptions + clearer priorities; Escape hatch: restore a 15-min meeting if blockers rise.