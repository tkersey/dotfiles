# Technique: Synectics (analogy ladder)

## One-liner
Force a new representation by climbing analogies: direct → personal → symbolic (→ sometimes fantasy), then translate the metaphor back into concrete levers.

## Use when
- You need a conceptual leap, not incremental tweaks.
- The team keeps re-describing the problem in the same terms.
- You want an “Aha” via a new model.

## Avoid when
- The problem is mostly combinatorial configuration (use Morphological Analysis).
- The key blocker is a contradiction (use TRIZ).

## Inputs
- A crisp target: what you want to improve.
- Willingness to be temporarily “weird” (metaphor phase).

## Procedure (fast, 6–10 min)
1. Direct analogy: “This is like a …” (pick 3).
2. Personal analogy: “If I were the system, I would feel …”.
3. Symbolic analogy: compress into a short metaphor (“signal vs noise”, “leaky bucket”).
4. Translate: extract 3 actionable levers implied by the metaphor.

## Procedure (full, 15–25 min)
1. Direct analogies (3–5)
   - Pick domains with mature solutions (medicine, logistics, manufacturing, ecology).
2. Personal analogy
   - Take the perspective of the constrained element (user, oncall, subsystem).
3. Symbolic analogy
   - Find the “two-word truth” (e.g., “attention tax”, “trust debt”).
4. Translation back to action
   - For each metaphor, list properties, then map to:
     - constraints, levers, failure modes, and measurable signals.
5. Converge
   - Select the metaphor that changes the problem representation the most.

## Prompt bank (copy/paste)
- “This system is like a … (pick 3 wildly different domains).”
- “If I were the bottleneck, what would I want?”
- “What is the two-word symbol here?”
- “What does the metaphor imply we should *remove*, *buffer*, or *route*?”

## Outputs (feed CPS portfolio)
- A new representation (metaphor) + 3 concrete levers.
- A shortlist of experiments derived from those levers.

## Aha targets
- Swapping the primitive: from “features” to “flows”, from “bugs” to “risk exposure”, from “customers” to “queues”.

## Pitfalls & defusals
- Pitfall: metaphor stays cute and literal → Defusal: force translation into constraints/levers/signals.
- Pitfall: endless metaphors → Defusal: timebox; pick the strongest representation shift.
- Pitfall: analogy cherry-picks → Defusal: generate multiple and compare.

## Examples
### Engineering
Problem: noisy alerting.
- Direct: smoke detector, spam filter, airport security.
- Personal: “I am the oncall; I’m being woken up for nothing.”
- Symbolic: “signal vs noise.”
Levers: severity routing, deduplication, error budgets, alert thresholds; signal: pages/week + MTTR.

### Mixed domain
Problem: recurring conflict in meetings.
- Direct: traffic intersection, orchestra, court trial.
- Personal: “I’m the quiet participant; I can’t merge into the conversation.”
- Symbolic: “right-of-way.”
Levers: facilitation rules, speaking order, explicit turn-taking; signal: participation distribution; escape hatch: revert if meetings slow down.