# Technique: Reverse Brainstorming (make it worse → invert)

## One-liner
Generate ways to cause failure or maximize pain, then invert each into a safeguard or opportunity. Great for risk surfacing and plan hardening.

## Use when
- You’re stuck and need to expose hidden assumptions.
- You need to harden an approach against failure.
- The team is optimistic and blind to risk.

## Avoid when
- Morale is low and the group spirals (use Six Thinking Hats first).
- You need pure novelty (use Provocation / Synectics).

## Inputs
- Target outcome + current approach.

## Procedure (fast, 6–10 min)
1. Ask: “How do we guarantee this fails / gets worse?”
2. Generate 10–20 ‘anti-ideas’.
3. Invert each into a safeguard or design requirement.
4. Select 2 safeguards; rewrite as experiments.

## Procedure (full, 15–25 min)
1. Reverse prompt
   - “How do we maximize X (bad thing) while appearing to try?”
2. Anti-idea generation
   - Include social/process failures, not just technical.
3. Inversion
   - Convert anti-ideas into:
     - guardrails, checks, rollouts, incentives, ownership rules.
4. Converge
   - Pick the safeguard with the best signal and reversibility.

## Prompt bank (copy/paste)
- “How do we make this fail silently?”
- “How do we create the most customer pain?”
- “How do we make this unmaintainable in 3 months?”
- “What would a malicious or lazy version of us do?”

## Outputs (feed CPS portfolio)
- A risk inventory.
- A shortlist of safeguards as options (often excellent Quick Wins).

## Aha targets
- Hidden coupling points.
- A missing signal/metric (“we wouldn’t even know it failed”).

## Pitfalls & defusals
- Pitfall: cynical spiral → Defusal: timebox; inversion is mandatory.
- Pitfall: inversion yields platitudes (“communicate more”) → Defusal: force concrete mechanisms.

## Examples
### Engineering
Prompt: “How do we guarantee bad deploys?”
- Anti-ideas: no staging parity, no rollback, ignore errors.
- Inversions: staging parity checks, rollback hooks, error-budget alerts.
Signal: rollback rate decreases; escape hatch: disable parity gate if it blocks hotfixes.

### Mixed domain
Prompt: “How do we make a partnership worse?”
- Anti-ideas: avoid hard conversations, assume intent, never apologize.
- Inversions: scheduled check-ins, explicit expectations, repair rituals.
Signal: fewer recurring conflicts; escape hatch: adjust cadence if it feels forced.