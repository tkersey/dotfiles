# Technique: CPS Cycle (Clarify → Ideate → Develop → Implement)

## One-liner
A session skeleton that prevents looping: clarify scope/constraints, diverge on options, strengthen the best into experiments (signal + escape hatch), then take the smallest reversible step.

## Use when
- You’re stuck in circular debate or vague requirements.
- You need traceability more than novelty.
- The problem is multi-constraint and needs “good next moves”, not “the answer”.

## Avoid when
- The user already picked a direction and only needs execution steps.
- You only need a quick reframe (use Oblique Draw / Random Stimulus).

## Inputs (minimum viable)
- Goal: one sentence.
- Constraints: time, budget, policy, tech, people.
- Unknowns: what would change the plan.

## Procedure (fast, 5–10 min)
1. Clarify: write the contract: “Working means …”. Name 1–3 hard constraints.
2. Ideate: generate 10–20 candidates without critique.
3. Develop: pick 3 candidates; rewrite each as an experiment:
   - Hypothesis → Expected signal → Escape hatch.
4. Implement (conceptual): propose the smallest reversible next action for the best candidate.

## Procedure (full, 20–45 min)
1. Clarify
   - State: goal, non-goals, constraints, stakeholders.
   - Separate: *symptoms* (what hurts) vs *mechanism* (why it hurts).
   - Pick the optimization target (speed, quality, cost, morale, risk) explicitly.
2. Ideate (diverge)
   - Generate 30+ candidates; label each with a verb (“reduce”, “split”, “cache”, “delegate”, “rename”, “automate”).
   - Mix domains: technical levers + process levers + incentive levers.
3. Develop (converge)
   - Cluster by intent; keep 3–5 clusters.
   - Pick 1 representative per cluster and harden it:
     - prerequisites, risks, reversibility, “how we’ll know”.
4. Implement (plan)
   - Convert hardened candidates into the five-tier CPS portfolio.
   - Ask for the user’s tier choice; do not execute.

## Prompt bank (copy/paste)
- Clarify
  - “If this worked, what would be observably different?”
  - “What must *not* change?”
  - “What constraint is non-negotiable?”
  - “What’s the smallest ‘good enough’ outcome?”
- Ideate
  - “List 20 ways to change the bottleneck.”
  - “What would we do if we couldn’t change X?”
  - “What would we do if we had to ship in 48 hours?”
- Develop
  - “What is the expected signal within 1 day / 1 week?”
  - “What’s the escape hatch if this is wrong?”
  - “What’s the minimal reversible experiment?”

## Outputs (feed CPS portfolio)
- A crisp contract sentence.
- A list of candidate moves (divergent).
- 3–5 hardened experiments with signals + escape hatches.

## Aha targets
- Re-represent the problem as a bottleneck, a queue, a mismatch of incentives, or an interface boundary.
- Replace “pick the best” with “run the fastest discriminating experiment”.

## Pitfalls & defusals
- Pitfall: staying in Clarify forever → Defusal: timebox; move unknowns into “assumptions to validate”.
- Pitfall: ideation polluted by critique → Defusal: two explicit phases; no scoring during divergence.
- Pitfall: “implement” becomes execution → Defusal: stop at “next smallest reversible step” + ask.

## Examples
### Engineering
Goal: reduce deploy risk.
- Clarify: “Working means we can deploy daily with <1 rollback/week.”
- Ideate: canary, feature flags, contract tests, staged rollout, shadow traffic.
- Develop: canary experiment with rollback trigger (error budget breach).
- Implement: ship canary for one service; measure rollback rate.

### Mixed domain
Goal: improve cross-team alignment.
- Clarify: “Working means fewer surprise dependencies in sprint week 2.”
- Ideate: weekly dependency review, shared roadmap board, single owner per dependency.
- Develop: experiment: 30-min weekly “dependency sync” for 2 sprints.
- Implement: run it twice, measure surprises/interruptions, stop if it adds >30 min overhead.