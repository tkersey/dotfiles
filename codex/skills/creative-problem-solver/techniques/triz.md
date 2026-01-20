# Technique: TRIZ (resolve contradictions)

## One-liner
When a tradeoff feels like a false dichotomy, TRIZ forces you to state the contradiction precisely and then escape it via separation principles (and a small set of “inventive principles”).

## Use when
- You want X, but it worsens Y (speed vs safety, flexibility vs simplicity).
- You keep oscillating between two bad extremes.
- “Pick one” feels intellectually dishonest.

## Avoid when
- You need breadth from scratch (use Brainstorming / Morphological Analysis).
- The problem is mostly politics/alignment (use Six Thinking Hats).

## Inputs
- Contradiction statement: “We want <improve>, but that worsens <degrade>.”
- Context constraints (what cannot change).

## Procedure (fast, 8–12 min)
1. Write the contradiction.
2. Ask the 4 separation questions:
   - time? space? condition? parts vs whole?
3. Generate 5–10 candidate “both/and” moves.
4. Pick 2 candidates; rewrite as experiments (signal + escape hatch).

## Procedure (full, 20–35 min)
1. Specify the system
   - What is the “thing” and its boundary?
   - What is the resource you can exploit (time, space, information, attention, unused capacity)?
2. State the contradiction cleanly
   - Improve parameter: what you want.
   - Worsen parameter: what gets harmed.
3. Separation principles (primary)
   - Separation in time: do the expensive thing later/earlier/asynchronously.
   - Separation in space: apply strictness only in the risky area.
   - Separation on condition: enforce only when certain risk signals trigger.
   - Separation between parts/whole: optimize subsystem while preserving system behavior.
4. Inventive principles (lightweight set)
   - Segmentation: split into parts (shard, split responsibility).
   - Taking out: remove the painful part from the critical path.
   - Intermediary: add a buffer/queue/cache/proxy.
   - Feedback: add sensing + control loops (error budgets, alerts).
   - Parameter change: change frequency, magnitude, granularity.
   - Local quality: vary behavior by segment (hot path vs cold path).
5. Converge
   - Select the highest-signal, most reversible candidate.

## Prompt bank (copy/paste)
- “How can we get X *sometimes* without paying Y *always*?”
- “What if strictness applies only to the risky slice?”
- “What can we move off the critical path?”
- “What cheap signal can gate the expensive check?”
- “What buffer can absorb volatility?”

## Outputs (feed CPS portfolio)
- 5–10 “both/and” candidates.
- A crisp explanation of *why* a candidate escapes the tradeoff (good for persuasion).

## Aha targets
- A new separation dimension (time/space/condition) that collapses the contradiction.
- A gating signal that makes strictness conditional.

## Pitfalls & defusals
- Pitfall: vague contradiction (“better UX but worse UX”) → Defusal: quantify X and Y.
- Pitfall: solutions are just “accept the tradeoff” → Defusal: force separation questions first.
- Pitfall: over-engineering → Defusal: prefer the smallest reversible separation.

## Examples
### Engineering
Contradiction: “We want faster responses, but strict validation slows requests.”
- Separation in time: accept fast writes, validate asynchronously, reject on next write.
- Separation on condition: validate strictly only when anomaly signals fire.
- Intermediary: queue/buffer; validate in worker.
Signal: p95 latency improves without higher invalid-rate; Escape hatch: flip flag to synchronous validation.

### Mixed domain
Contradiction: “We want flexibility, but we need reliability.”
- Separation in time: weekly planning (reliability) + daily flexibility window.
- Separation by condition: strict rules only when high-risk tasks appear.
- Segmentation: separate ‘core commitments’ from ‘nice-to-haves’.
Signal: fewer missed deadlines without loss of autonomy; Escape hatch: loosen constraints if morale drops.