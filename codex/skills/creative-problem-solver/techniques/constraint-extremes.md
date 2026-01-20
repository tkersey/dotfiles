# Technique: Constraint Extremes (0 / ∞ / absurd)

## One-liner
Set a key variable to zero or infinity, design under that extreme, then extract the invariant principles and interpolate back to reality.

## Use when
- The “real” constraint is ambiguous or self-imposed.
- You want to break a local optimum (“we always do it this way”).
- You want breadth that’s still grounded in constraints.

## Avoid when
- You already know the constraint boundary and need execution.
- The problem is a crisp contradiction (use TRIZ).

## Inputs
- Baseline problem and 1–2 constraints to “extreme”.

## Procedure (fast, 5–10 min)
1. Pick one variable: time, money, risk tolerance, staffing, latency budget, user attention.
2. Run two extremes:
   - Zero: “If we had 0 of this…”
   - Infinity: “If we had unlimited…”
3. Generate 3 options per extreme.
4. Extract 2–3 invariants (what still matters).
5. Create a realistic hybrid option; convert to experiment.

## Procedure (full, 15–25 min)
1. Choose the extremes intentionally
   - Zero / Infinite is default.
   - Also consider: 1 (single-owner), 10×, 1/10×, “must be reversible”, “must be audited”.
2. Design under extremes
   - Under zero: what do we delete, simplify, or automate?
   - Under infinity: what do we measure, specialize, or parallelize?
3. Extract invariants
   - What did both extremes require?
   - What did only one extreme make possible?
4. Interpolate
   - Build a hybrid that keeps the invariant and borrows one extreme lever.
5. Convert to CPS portfolio
   - Map: zero-constraint ideas often become Quick Wins; infinity ideas often become Transformative/Moonshot.

## Prompt bank (copy/paste)
- “If we had 0 budget/0 time/0 people, what would we still do?”
- “If we had infinite budget/infinite time, what would we build?”
- “What stays true in both extremes?”
- “What’s the smallest slice of the ‘infinite’ solution we can test?”

## Outputs (feed CPS portfolio)
- Two extreme designs.
- A set of invariant principles.
- A realistic hybrid experiment.

## Aha targets
- Discovering the real constraint is coordination/attention, not money.
- Identifying an invariant you can optimize around.

## Pitfalls & defusals
- Pitfall: extremes become fantasy → Defusal: extract invariants; bring back to a testable hybrid.
- Pitfall: only one extreme explored → Defusal: run both (zero and infinity).
- Pitfall: output is unscored → Defusal: score for signal + reversibility.

## Examples
### Engineering
Variable: downtime tolerance.
- Zero downtime: blue/green, canary, feature flags.
- Infinite downtime: simplest migration + direct cutover.
Invariants: rollback plan + observability.
Hybrid: phased canary for one service; signal: error rate; escape hatch: rollback switch.

### Mixed domain
Variable: available energy.
- Zero energy: remove steps; shrink scope; automate reminders.
- Infinite energy: deep training plan; coaching; measurement.
Invariants: consistency beats intensity.
Hybrid: tiny daily routine + weekly review; signal: adherence rate; escape hatch: reduce frequency if stress rises.