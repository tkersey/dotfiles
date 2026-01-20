# Technique: Assumption Mapping (de-risk unknowns)

## One-liner
Surface and prioritize assumptions, then design the smallest discriminating tests for the assumptions that are both important and uncertain.

## Use when
- You’re blocked by unknowns or “we don’t know if this will work”.
- You want high-signal options (experiments) rather than more opinions.
- You need to decide what to validate first.

## Avoid when
- The constraints are already clear and execution is the issue.
- You need novelty from scratch (use Random Stimulus / Brainwriting).

## Inputs
- Candidate plan/option (or a few).
- Success criteria (what you care about).

## Procedure (fast, 8–12 min)
1. List 10–15 assumptions (one per line).
2. Rate each (1–5): Importance × Uncertainty.
3. Pick top 3 assumptions.
4. For each: smallest test → expected signal → escape hatch.

## Procedure (full, 20–30 min)
1. Generate assumptions across categories
   - user/customer, technical feasibility, performance, cost, adoption, organizational capacity.
2. Map to a 2×2
   - High importance + high uncertainty = first.
3. Design tests
   - Prefer tests that are:
     - fast, reversible, and give clear information.
   - Convert into options tiers:
     - Quick Win = cheapest test,
     - Strategic = integration test,
     - Advantage/Transformative/Moonshot = deeper bets.

## Prompt bank (copy/paste)
- “What must be true for this to work?”
- “What are we assuming about users/ops/latency/cost?”
- “What is the cheapest test that could falsify this?”
- “What signal would make us stop?”

## Outputs (feed CPS portfolio)
- A prioritized assumption list.
- A set of experiments that directly buy information.

## Aha targets
- Discovering the real blocker is adoption/ownership, not technology.
- Replacing “debate” with “falsification”.

## Pitfalls & defusals
- Pitfall: assumptions are vague → Defusal: rewrite as falsifiable statements.
- Pitfall: tests are too big → Defusal: force a 1-day test first.

## Examples
### Engineering
Plan: add a caching layer.
Assumptions: hit rate will be high; invalidation is manageable; cache won’t create incidents.
Tests: shadow cache + measure hit rate; signal: p95 improves; escape hatch: disable cache flag.

### Mixed domain
Plan: start a new habit.
Assumptions: mornings are available; routine is enjoyable; environment supports it.
Tests: 1-week tiny routine + prepare environment; signal: adherence rate; escape hatch: change time-of-day if adherence is low.