# Technique: Six Thinking Hats (parallel perspectives)

## One-liner
Sequence the whole group (or your own thinking) through the same perspectives to stop debate-by-advocacy and surface tradeoffs cleanly.

## Hats (mnemonic)
- White: facts, data, unknowns.
- Red: feelings, intuitions, morale, fear.
- Black: risks, failure modes, downsides.
- Yellow: benefits, upside, opportunity.
- Green: new ideas, alternatives, hybrids.
- Blue: process, decision, next steps.

## Use when
- Alignment is hard; people talk past each other.
- The conversation keeps mixing analysis with advocacy.
- Stakes are high and you need an audit trail of tradeoffs.

## Avoid when
- You need raw idea volume fast (use Brainwriting / Brainstorming).
- The core is a crisp contradiction needing invention (use TRIZ).

## Inputs
- Decision or proposal under discussion.
- Timebox per hat (2–5 minutes each).

## Procedure (fast, 10–15 min)
1. Blue (setup): define the decision + constraints + timebox.
2. White: list facts + unknowns (no interpretation).
3. Black + Yellow: enumerate risks *and* benefits (separately).
4. Green: generate 5–10 alternatives/hybrids.
5. Blue (close): decide next smallest reversible step (or what info would decide).

## Procedure (full, 20–30 min)
1. Blue (setup)
   - State: “We are deciding between …”.
   - Define: what would make this a good decision (success criteria).
2. White
   - Facts, constraints, baselines, metrics.
   - Unknowns that would flip the decision.
3. Red
   - Name the human reality: anxiety, excitement, trust, fatigue.
   - Treat feelings as data (not as proof).
4. Black
   - Failure modes; hidden costs; second-order effects.
5. Yellow
   - Benefits; leverage; what becomes easier later.
6. Green
   - Hybrids: “How do we get 80% of the upside with 20% of the risk?”
   - “Both/and” designs; staged rollouts.
7. Blue (close)
   - Convert top 1–2 candidates into experiments (signal + escape hatch).

## Prompt bank (copy/paste)
- White: “What do we *know* vs assume?”
- Red: “What are we worried will happen? What are we hoping happens?”
- Black: “How could this fail? What are the sharp edges?”
- Yellow: “What upside is worth the risk?”
- Green: “What hybrid option gets the benefit without the worst downside?”
- Blue: “What’s the smallest reversible step that yields signal?”

## Outputs (feed CPS portfolio)
- A structured tradeoff inventory.
- 1–3 hybrid options that often beat polarized debate.

## Aha targets
- Discovering a hidden constraint (White) or hidden fear (Red) driving the debate.
- Converting “argument” into “experiment”.

## Pitfalls & defusals
- Pitfall: mixing hats (“Black” critique during “Green”) → Defusal: enforce hat purity.
- Pitfall: Red becomes manipulation → Defusal: treat feelings as signals, not conclusions.
- Pitfall: never deciding → Defusal: Blue must end with a next step or an info-gathering plan.

## Examples
### Engineering
Decision: “Move to managed DB.”
- White: current costs, incident history, latency SLOs.
- Black: lock-in, migration risk, data egress cost.
- Yellow: ops time saved, reliability, scaling.
- Green: hybrid: managed read replicas first; phased cutover.
- Blue: experiment: migrate one non-critical service; signal: incident rate + latency.

### Mixed domain
Decision: “Switch roles or stay put.”
- White: compensation, growth paths, workload.
- Red: boredom, anxiety, identity.
- Black: risk of regret, loss of expertise.
- Yellow: skill compounding, renewed motivation.
- Green: hybrid: internal rotation / side project first.
- Blue: experiment: 2-week shadowing + informational interviews; signal: energy + clarity.