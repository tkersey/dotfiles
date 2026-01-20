---
name: creative-problem-solver
description: Lateral-thinking playbook for options and trade-offs; always deliver a five-tier strategy portfolio.
---

# Creative Problem Solver

## Contract (one assistant turn)
- Deliver options, then stop and ask for human input before executing.
- Always include a five-tier portfolio: Quick Win, Strategic Play, Advantage Play, Transformative Move, Moonshot.
- For each option: expected signal + escape hatch.
- Run an Aha Check after reframing.
- Track provenance (technique → Aha Y/N). If the same technique triggers Aha twice in a row, switch techniques next round.
- Keep a short Knowledge Snapshot + Decision Log.

## When to use
- Progress is stalled or blocked.
- Repeated attempts fail the same way.
- The user asks for options, alternatives, tradeoffs, or a strategy portfolio.
- The problem is multi-constraint, cross-domain, or high-uncertainty (architecture, migration, integration, conflict resolution).

## Quick start
1. Choose lane: Fast Spark or Full Session.
2. Reframe once (pick one tool, or run Oblique Draw).
3. Aha Check. If none, reframe once more.
4. Generate the five-tier portfolio.
5. Score options (1–5): Signal, Ease, Reversibility, Speed.
6. Ask the user to choose a tier or update constraints.
7. Close with an Insights Summary.

## Mode check
- Pragmatic (default): ship-this-week options only.
- Visionary: only when asked for long-horizon strategy or systemic change.

## Lane selector
- Fast Spark: skip ideation; produce the portfolio directly.
- Full Session: diverge (10–30 ideas), cluster, score, then select one option per tier.

## Reframing toolkit
Pick one:
- Inversion: flip the current approach. Reference: `codex/skills/creative-problem-solver/techniques/inversion.md`.
- Analogy transfer: borrow a pattern from a solved domain. Reference: `codex/skills/creative-problem-solver/techniques/analogy-transfer.md`.
- Constraint extremes: set a key variable to zero or infinity. Reference: `codex/skills/creative-problem-solver/techniques/constraint-extremes.md`.
- First principles: rebuild from basic facts. Reference: `codex/skills/creative-problem-solver/techniques/first-principles.md`.

## Oblique draw (optional)
Use when framing is stale. Reference: `codex/skills/creative-problem-solver/techniques/oblique-draw.md`.
1. Draw 4 prompts, pick 1, apply it.
2. Translate it into a concrete lever/constraint.

Mini-deck (if no deck is available):
- Do the opposite of the obvious move.
- Remove a step.
- Make it reversible first.
- Smallest test that could change the plan.
- Shift the bottleneck, not throughput.
- Change the unit of work.
- Swap one constraint for another.
- Borrow a pattern from another domain.

## Aha Check (required)
- Definition: a restructuring insight (new representation/model).
- Output: one-line insight. If none, reframe once more before generating options.

## Portfolio rule
Every response must include all five tiers.

## Option template
```
Quick Win:
- Expected signal:
- Escape hatch:

Strategic Play:
- Expected signal:
- Escape hatch:

Advantage Play:
- Expected signal:
- Escape hatch:

Transformative Move:
- Expected signal:
- Escape hatch:

Moonshot:
- Expected signal:
- Escape hatch:
```

## Scoring rubric (1–5, no weights)
- Signal: how much new information this yields.
- Ease: effort/complexity to try.
- Reversibility: ease of undoing.
- Speed: time-to-learn.

Preference: high Signal + Reversibility, then Ease + Speed.

## Technique rules (progressive disclosure)
- Pick 1 technique by default (use 2–3 only if you’re still blocked).
- After selecting a technique, consult its reference doc in `codex/skills/creative-problem-solver/techniques/`.
- Chat disclosure: include only `Reframe used: <technique>` + a one-line “why”; don’t paste the technique script unless the user asks.

## Technique picker (choose 1; rarely 2)
- No Aha → Provocation (PO) or Forced Connections or Synectics or TRIZ.
- Need a fast spark → Oblique Draw or Random Stimulus.
- Need to mutate an existing thing → SCAMPER.
- Need lots of ideas fast (low debate) → Brainwriting 6-3-5.
- Need structured combinations → Morphological Analysis.
- Need to resolve contradictions → TRIZ.
- Need parallel perspectives / alignment → Six Thinking Hats.
- Need to surface failure modes early → Pre-mortem or Reverse Brainstorming.
- Need to de-risk unknowns (what to validate first) → Assumption Mapping.
- Need momentum + traceability → CPS Cycle.

## Technique library (index; use 1–3)
- Inversion — `codex/skills/creative-problem-solver/techniques/inversion.md`
- Analogy Transfer — `codex/skills/creative-problem-solver/techniques/analogy-transfer.md`
- Constraint Extremes — `codex/skills/creative-problem-solver/techniques/constraint-extremes.md`
- First Principles — `codex/skills/creative-problem-solver/techniques/first-principles.md`
- CPS Cycle (Clarify → Ideate → Develop → Implement) — `codex/skills/creative-problem-solver/techniques/cps-cycle.md`
- Brainstorming — `codex/skills/creative-problem-solver/techniques/brainstorming.md`
- Brainwriting 6-3-5 — `codex/skills/creative-problem-solver/techniques/brainwriting-6-3-5.md`
- SCAMPER — `codex/skills/creative-problem-solver/techniques/scamper.md`
- Six Thinking Hats — `codex/skills/creative-problem-solver/techniques/six-thinking-hats.md`
- TRIZ — `codex/skills/creative-problem-solver/techniques/triz.md`
- Morphological Analysis — `codex/skills/creative-problem-solver/techniques/morphological-analysis.md`
- Synectics — `codex/skills/creative-problem-solver/techniques/synectics.md`
- Provocation (PO) — `codex/skills/creative-problem-solver/techniques/provocation-po.md`
- Random Stimulus — `codex/skills/creative-problem-solver/techniques/random-stimulus.md`
- Forced Connections — `codex/skills/creative-problem-solver/techniques/forced-connections.md`
- Reverse Brainstorming — `codex/skills/creative-problem-solver/techniques/reverse-brainstorming.md`
- Pre-mortem — `codex/skills/creative-problem-solver/techniques/pre-mortem.md`
- Mind Mapping — `codex/skills/creative-problem-solver/techniques/mind-mapping.md`
- Affinity Diagramming — `codex/skills/creative-problem-solver/techniques/affinity-diagramming.md`
- How Might We — `codex/skills/creative-problem-solver/techniques/how-might-we.md`
- Crazy 8s — `codex/skills/creative-problem-solver/techniques/crazy-8s.md`
- Storyboarding — `codex/skills/creative-problem-solver/techniques/storyboarding.md`
- Lotus Blossom — `codex/skills/creative-problem-solver/techniques/lotus-blossom.md`
- Assumption Mapping — `codex/skills/creative-problem-solver/techniques/assumption-mapping.md`
- Oblique Draw — `codex/skills/creative-problem-solver/techniques/oblique-draw.md`

## Templates
Decision Log:
- Decision:
- Rationale:
- Alternatives considered:
- Evidence/signal:
- Reversible? (Y/N):
- Next decision point:

Assumptions & Constraints:
- Assumptions to validate:
- Known constraints (time/budget/policy/tech):
- Unknowns to de-risk:
- Non-goals:

Knowledge Snapshot:
- New facts:
- New risks/constraints:
- Plan-changing signals:
- Technique provenance (technique → Aha Y/N):
- Aha Check:
- Open questions:

## Deliverable format
- Lane (Fast Spark / Full Session).
- Reframe used.
- Aha Check (one line).
- Five-tier portfolio with signals + escape hatches.
- Scorecard + brief rationale.
- Decision Log + Assumptions/Constraints.
- Human Input Required (choose tier or update constraints).
- Insights Summary.

## Activation cues
- "need options" / "alternatives" / "tradeoffs" / "portfolio"
- "brainstorm" / "ideate"
- "stuck" / "blocked" / "nothing works"
- "outside the box" / "fresh angles"
- "ambiguous" / "uncertain" / "unknowns"
- "architecture" / "system design" / "migration" / "integration"
