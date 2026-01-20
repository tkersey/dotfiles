# Technique: Lotus Blossom (structured breadth)

## One-liner
Expand outward from a core problem: generate 8 related sub-ideas, then treat each as a new center and expand again (breadth without chaos).

## Use when
- You want lots of ideas but with structure.
- Unbounded brainstorming turns into noise.
- You need coverage across multiple angles (tech/process/people).

## Avoid when
- You already have many ideas and need convergence (use Affinity Diagramming).
- You need contradiction resolution (use TRIZ).

## Inputs
- Core problem statement.

## Procedure (fast, 10–15 min)
1. Center: write the core problem.
2. Petals: write 8 related sub-areas.
3. Expand: pick 2 petals and generate 8 actions each.
4. Converge: choose 3 actions; rewrite as experiments.

## Procedure (full, 20–35 min)
1. First ring (8 petals)
   - Use categories like: tooling, process, incentives, training, observability, rollouts, ownership, customer experience.
2. Second ring
   - For each petal, create 8 specific actions.
3. Converge
   - Cluster by intent.
   - Select one per CPS tier; attach signals + escape hatches.

## Prompt bank (copy/paste)
- “What are 8 adjacent areas that influence this outcome?”
- “For this petal, what are 8 concrete actions?”
- “What would be the smallest reversible action in this petal?”

## Outputs (feed CPS portfolio)
- 16–72 ideas with good coverage.
- Natural mapping to tiers (some petals yield Quick Wins, others Moonshots).

## Aha targets
- Realizing the solution is multi-lever (not one change).

## Pitfalls & defusals
- Pitfall: petals are vague (“improve quality”) → Defusal: petals must be categories with concrete actions.
- Pitfall: expansion repeats the same idea → Defusal: force each petal to be a different domain.

## Examples
### Engineering
Core: “reduce production incidents.”
Petals: testing, observability, rollouts, ownership, training, tooling, oncall, architecture.
Expand “rollouts”: canary, feature flags, staged deploy, rollback automation.
Signal: incidents/week drop; escape hatch: start with one service.

### Mixed domain
Core: “improve health.”
Petals: sleep, food, exercise, stress, environment, habits, social, tracking.
Expand “environment”: prep healthy food, remove junk, place workout gear.
Signal: consistency increases; escape hatch: shrink scope if it overwhelms.