# Technique: First Principles (rebuild from facts)

## One-liner
Strip the problem to facts, separate assumptions, then reconstruct the solution from a minimal model and explicit invariants.

## Use when
- You suspect cargo-culting (“we do it because we always did”).
- The existing framing is politically or historically constrained.
- You need a clean contract: what must be true vs what’s optional.

## Avoid when
- The core difficulty is alignment/feelings (use Six Thinking Hats first).
- You already have a high-confidence plan and only need execution.

## Inputs
- Goal: one sentence.
- Context: what system/people/process you’re actually changing.

## Procedure (fast, 6–12 min)
1. Facts: list 5–10 things you believe are true (observations, measurements).
2. Assumptions: list 5–10 things you’re assuming (could be false).
3. Invariants: what must not break? (safety, trust, correctness, policy).
4. Minimal model: write the simplest “mechanism” sentence (e.g., “latency is dominated by network hops”).
5. Rebuild: generate 3 options that satisfy invariants; convert to experiments.

## Procedure (full, 20–35 min)
1. Bound the system
   - What’s in scope? what’s out?
2. Decompose the goal
   - Outcome metric + constraints (time/risk/cost).
3. Facts vs assumptions
   - Facts must be observable or widely validated.
   - Assumptions become “unknowns to de-risk”.
4. Derive constraints/invariants
   - “We must …” statements.
5. Construct from primitives
   - Use primitives like: queues, caches, ownership, incentives, interfaces, feedback loops.
6. Converge
   - Choose the smallest reversible option that yields the most signal.

## Prompt bank (copy/paste)
- “What do we *know* (measured), not believe?”
- “What are we assuming because it’s convenient?”
- “What invariant must not be violated?”
- “If we could rebuild from scratch, what primitives would we use?”
- “What is the cheapest experiment that tests the core assumption?”

## Outputs (feed CPS portfolio)
- Facts list + assumptions list.
- A minimal mechanism model.
- 1–3 reconstructed options with explicit invariants.

## Aha targets
- Swapping “solution talk” for “mechanism talk”.
- Finding the real constraint (e.g., ownership or feedback speed).

## Pitfalls & defusals
- Pitfall: pretending assumptions are facts → Defusal: label unknowns explicitly.
- Pitfall: analysis paralysis → Defusal: timebox; stop after minimal model.
- Pitfall: rebuilding ignores reality → Defusal: re-check constraints and organizational capacity.

## Examples
### Engineering
Goal: speed up API responses.
Facts: p95 is dominated by 3 downstream calls; cache hit rate is low.
Assumptions: caching is safe; data staleness is acceptable.
Invariants: correctness for writes; auditability.
Rebuild: reduce hops, add cache with explicit staleness budget, async validation.
Signal: p95 improves; escape hatch: cache flag off.

### Mixed domain
Goal: reduce burnout.
Facts: overtime correlates with context switching; recovery time is low.
Assumptions: saying ‘yes’ is required for success.
Invariants: maintain key relationships and core commitments.
Rebuild: protect deep-work blocks, reduce commitments, add recovery rituals.
Signal: weekly energy score; escape hatch: reintroduce one commitment if outcomes slip.