# Technique: Analogy Transfer (borrow a solved pattern)

## One-liner
Borrow a pattern from a solved domain, map roles/resources/invariants, then adapt it into concrete levers for the target problem.

## Use when
- You need novelty but want it anchored to proven mechanisms.
- The problem smells like a known class: routing, triage, queues, fraud, safety systems.
- You want a representation shift (“this is like …”) that still yields actions.

## Avoid when
- The problem is purely combinatorial configuration (use Morphological Analysis).
- The core is a crisp contradiction (use TRIZ).
- The analogy would be politically loaded or distracting.

## Inputs
- Target problem (1–2 sentences).
- Source domain(s) (pick 1–3).

## Procedure (fast, 5–10 min)
1. Pick a source domain with mature solutions (logistics, medicine, security, ecology, manufacturing).
2. Name the borrowed pattern (triage, queueing, canary, escrow, circuit breaker).
3. Map:
   - roles (who/what acts)
   - resources (time, attention, money, capacity)
   - signals (what is measured)
   - failure modes (what goes wrong)
4. Translate into 2–3 candidate levers; rewrite as experiments.

## Procedure (full, 15–25 min)
1. Generate 3 candidate analogies
   - include one “near” domain and one “far” domain.
2. Build a mapping table
   - Target element → Source analog → Imported mechanism.
3. Import constraints carefully
   - Ask: “What *must* be true for the source mechanism to work?”
   - These become assumptions to validate.
4. Adapt, don’t clone
   - Keep the mechanism; change the surface.
5. Converge
   - Prefer levers that are testable and reversible.

## Prompt bank (copy/paste)
- “What solved domain has the same failure mode?”
- “If this were a triage desk / factory line / airport security, what would be the equivalent step?”
- “What is the scarce resource here (capacity/attention/trust)?”
- “What is the imported mechanism, and what assumption does it require?”

## Outputs (feed CPS portfolio)
- A new representation (“this is a queueing/triage problem”).
- 2–5 imported mechanisms.
- A shortlist of experiments.

## Aha targets
- Switching primitives: features → flows; bugs → risk exposure; people → incentives; requests → queues.

## Pitfalls & defusals
- Pitfall: superficial analogy (“it’s like Uber”) → Defusal: name the mechanism (matching, routing, pricing).
- Pitfall: wrong invariants imported → Defusal: list required assumptions explicitly; validate first.
- Pitfall: metaphor without action → Defusal: translation must yield levers + signals.

## Examples
### Engineering
Problem: support queue overload.
Analogy: ER triage.
- Mechanisms: severity routing, fast-path for simple cases, escalation protocols.
Levers: add severity tagging + macros; signal: time-to-first-response; escape hatch: remove tagging if it increases handling time.

### Mixed domain
Problem: team conflicts in meetings.
Analogy: traffic intersection / right-of-way.
- Mechanisms: explicit turns, signaling, a facilitator as traffic light.
Levers: speaking order + facilitation rules; signal: participation distribution; escape hatch: relax structure if it slows discussion too much.