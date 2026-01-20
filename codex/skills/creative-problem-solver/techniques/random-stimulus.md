# Technique: Random Stimulus (property transfer)

## One-liner
Pick something unrelated, list its properties, then force-map those properties into the problem to spark new angles (stay abstract to avoid gimmicks).

## Use when
- Framing is stale; you need a fast spark.
- You’re overfitting to the existing solution.

## Avoid when
- You need rigorous contradiction resolution (use TRIZ).
- You already have lots of ideas and need convergence.

## Inputs
- Random word/image/object (or a random page headline).
- A willingness to generate “bad” connections before good ones.

## Procedure (fast, 3–6 min)
1. Draw stimulus.
2. List 8–12 properties (verbs/adjectives).
3. Force-map: “How could our system behave like this property?”
4. Select 1–2 mapped ideas; rewrite as experiments.

## Procedure (full, 10–15 min)
1. Stimulus selection
   - Use a true random source (word list) or pick something in your environment.
2. Property inventory
   - Include: physical properties, behaviors over time, failure modes.
3. Mapping
   - Map properties into: architecture, process, incentives, UX.
4. Converge
   - Pick the idea that most changes representation (Aha) and is testable.

## Prompt bank (copy/paste)
- “List properties (not uses) of <stimulus>.”
- “How could we implement ‘absorbs and releases slowly’ in this problem?”
- “If our process had this property, what would change?”

## Outputs (feed CPS portfolio)
- 5–10 mapped directions, often outside the current local optimum.

## Aha targets
- Importing an unfamiliar primitive (buffering, gating, shedding load, self-healing).

## Pitfalls & defusals
- Pitfall: literal gimmicks → Defusal: map properties, not surface features.
- Pitfall: one mapping and stop → Defusal: force at least 8 properties.

## Examples
### Engineering
Stimulus: “sponge” → absorbs, releases slowly, squeezable.
- Map: add a queue/buffer to absorb spikes and drain steadily.
Signal: reduced tail latency during spikes; escape hatch: disable buffer if it adds delay.

### Mixed domain
Stimulus: “garden” → cultivation, seasons, pruning.
- Map: community growth via onboarding rituals + periodic pruning of low-signal channels.
Signal: engagement quality rises; escape hatch: revert pruning if participation drops.