# Technique: Brainstorming (Diverge → Converge)

## One-liner
A timed divergence phase that protects fragile ideas, followed by an explicit converge phase (score, select, harden).

## Use when
- You need breadth quickly (options explosion), then selection.
- The current solution space feels prematurely narrow.
- The group keeps judging too early (or you keep self-censoring).

## Avoid when
- You need a single high-signal reframe (use Synectics / Provocation).
- The problem is a crisp contradiction (use TRIZ).

## Inputs
- Problem prompt (ideally a “How might we…” question).
- Timebox and an explicit phase boundary.

## Procedure (fast, 5–12 min)
1. Set the rules (30 seconds): defer judgment; quantity; build; welcome wild.
2. Diverge (3–7 min): generate 15–30 raw ideas.
3. Converge (2–5 min): cluster → pick top 5 → harden into experiments.

## Procedure (full, 15–30 min)
1. Frame
   - Convert to a solvable prompt: “How might we <outcome> without <cost>?”
   - State constraints and non-goals.
2. Diverge (10–15 min)
   - Generate 30–60 ideas.
   - Force variety: alternate domains (tech/process/people), alternate units (per request/per day/per user).
3. Converge (5–10 min)
   - Cluster; name themes.
   - Pick one candidate per theme.
   - Convert candidates into CPS options (signal + escape hatch).

## Prompt bank (copy/paste)
- “Give me 20 ways to reduce X without increasing Y.”
- “What would we do if budget were 10× smaller?”
- “What would we do if budget were 10× larger?”
- “What would we do if we couldn’t hire?”
- “What would we do if we had to delete half the system?”

## Outputs (feed CPS portfolio)
- 30–60 raw ideas.
- 3–7 themed clusters.
- 1 hardened experiment per tier (Quick Win → Moonshot).

## Aha targets
- A new axis/dimension to explore (time, scope, ownership, interface, incentives).
- A reframed constraint (“can’t do X” becomes “must do X safely”).

## Pitfalls & defusals
- Pitfall: “brainstorming” becomes debate → Defusal: enforce phase boundary; critique only in converge.
- Pitfall: all ideas are variants of the first → Defusal: force domain jumps (tech ↔ process ↔ incentives).
- Pitfall: output is a list, not options → Defusal: rewrite top ideas as experiments with measurable signals.

## Examples
### Engineering
Prompt: “How might we cut CI time in half without reducing confidence?”
- Diverge: parallelize, cache, split tests, quarantine flakes, pre-commit checks, profiling.
- Converge: pick 3: test sharding + cache + flake quarantine; define signals (median CI time, flake rate).

### Mixed domain
Prompt: “How might we improve customer support response time without burning out the team?”
- Diverge: routing by topic, office hours, macros, self-serve docs, SLA tiers.
- Converge: experiment: add macro library + triage queue for 2 weeks; signal: response time + satisfaction; escape hatch: revert macros if quality drops.