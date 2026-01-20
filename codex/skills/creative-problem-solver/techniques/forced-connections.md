# Technique: Forced Connections (systematic recombination)

## One-liner
Deliberately connect two unrelated things (or two distant parts of the problem) to generate hybrids; more systematic than Random Stimulus.

## Use when
- You need novelty but want structure.
- You have multiple components/stakeholders and want unexpected pairings.
- You want many medium-quality sparks quickly.

## Avoid when
- The main challenge is an explicit contradiction (use TRIZ).
- You need deep empathy/alignment (use Six Thinking Hats).

## Inputs
- Set A: 5–10 “things” (components, stakeholders, constraints, assets).
- Set B: 5–10 “things” (random words, patterns, other domain solutions).

## Procedure (fast, 6–10 min)
1. List Set A (problem elements).
2. List Set B (randoms or cross-domain patterns).
3. Pick 6–10 pairs; for each: “How could B help A?”
4. Convert best 2 into experiments.

## Procedure (full, 15–25 min)
1. Build a small matrix
   - Rows: problem elements.
   - Columns: cross-domain patterns (e.g., marketplace, subscription, cache, triage, delegation).
2. For each cell, generate one forced connection:
   - “What would it mean to apply <pattern> to <element>?”
3. Converge
   - Select ideas that (a) change representation, (b) are testable.

## Prompt bank (copy/paste)
- “How could <pattern> reduce the cost of <problem element>?”
- “What is the smallest version of <pattern> we could try?”
- “If this were a marketplace / triage desk / assembly line, what would be the equivalent step?”

## Outputs (feed CPS portfolio)
- A list of hybrids (“apply pattern X to element Y”).
- 1–3 high-signal experiments.

## Aha targets
- New decompositions: “this is a routing problem”, “this is a triage problem”, “this is a batching problem”.

## Pitfalls & defusals
- Pitfall: pairings stay abstract → Defusal: force a concrete artifact (API, checklist, policy).
- Pitfall: too many low-value sparks → Defusal: score for signal + reversibility; pick only a few.

## Examples
### Engineering
Set A: login flow, rate limiting, support tickets. Set B: “airport security”, “triage”, “subscription”.
- Triage × support tickets → routing by severity + templated next actions.
- Subscription × rate limiting → tiered limits + burst credits.
Signal: reduced support load / fewer 429s; escape hatch: remove tiers if unfair.

### Mixed domain
Set A: personal finances, exercise, friendships. Set B: “canary”, “batching”, “feedback loop”.
- Feedback loop × finances → weekly review with one metric (burn rate).
- Batching × friendships → one recurring ‘catch-up block’ per week.
Signal: stability/consistency improves; escape hatch: drop ritual if it creates stress.