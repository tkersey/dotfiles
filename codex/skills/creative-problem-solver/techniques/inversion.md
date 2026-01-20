# Technique: Inversion (flip the problem)

## One-liner
Flip the objective/assumption, generate “anti-solutions”, then invert them back into concrete levers.

## Use when
- You’re stuck in a local optimum (“we tried everything”).
- You suspect hidden assumptions or sacred cows.
- You want risk insight: “how would this fail?” without full pre-mortem overhead.

## Avoid when
- The problem is already well-framed and you just need execution.
- Morale is fragile and a negative frame will spiral (use Six Thinking Hats first).

## Inputs
- Goal / outcome (1 sentence).
- Constraints (hard/soft).
- Current approach (optional, 1–2 lines).

## Procedure (fast, 3–7 min)
1. Write goal: “We want X.”
2. Invert:
   - “How do we maximize the opposite of X?”
   - or “How do we make X impossible?”
3. Generate 10 “anti-moves” (no critique).
4. Invert each anti-move into a lever (guardrail, default, interface, incentive).
5. Select 1–2 levers; convert to experiments (signal + escape hatch).

## Procedure (full, 12–20 min)
1. Choose inversion mode
   - Failure mode: “How do we guarantee failure?” (risk surfacing)
   - Opposite outcome: “How do we maximize the opposite?” (fresh levers)
   - Constraint flip: “What if constraint C didn’t exist? What new constraints appear?”
2. Anti-move generation
   - Include technical + social + process anti-moves.
3. Mechanism extraction (key step)
   - For each anti-move, ask: “What mechanism makes this harmful?”
   - Name the mechanism (handoff, missing signal, coupling, incentive, latency).
4. Inversion to levers
   - Turn mechanism into a lever:
     - missing signal → add instrumentation/alerts
     - coupling → split boundary / decouple
     - incentive → change ownership/criteria
     - handoff → remove step / clarify interface
5. Converge
   - Pick levers that are high-signal and reversible.

## Prompt bank (copy/paste)
- “How do we make this fail silently?”
- “How do we make it 10× worse?”
- “If we wanted to sabotage this, what would we do?”
- “What assumption is this anti-move exploiting?”
- “What is the inverted safeguard?”

## Outputs (feed CPS portfolio)
- 10 anti-moves.
- 3–5 inverted levers.
- 1–2 experiments with clear signals + escape hatches.

## Aha targets
- Discovering the problem is missing detection, not missing effort.
- Turning a sacred cow into a variable (ownership, default, interface).

## Pitfalls & defusals
- Pitfall: cynicism → Defusal: timebox; inversion-to-lever is mandatory.
- Pitfall: “anti-moves” are just vibes (“be bad”) → Defusal: force mechanisms.
- Pitfall: levers aren’t testable → Defusal: rewrite as smallest reversible experiment.

## Examples
### Engineering
Goal: reduce deploy risk.
Inversion: “How do we guarantee bad deploys?”
- Anti-moves: no staging parity, no rollback, ignore errors.
- Inverted levers: staging parity gates, rollback hooks, error-budget alerts.
Signal: rollback rate drops; escape hatch: temporarily relax parity gate for hotfixes.

### Mixed domain
Goal: improve focus.
Inversion: “How do we guarantee distraction?”
- Anti-moves: notifications on, unclear next task, phone in reach.
- Inverted levers: notification blocks, explicit next-action list, environment design.
Signal: deep-work blocks/week increase; escape hatch: loosen blocks if collaboration suffers.