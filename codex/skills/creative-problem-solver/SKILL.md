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
- Inversion: flip the current approach.
- Analogy transfer: borrow a pattern from a solved domain.
- Constraint extremes: set a key variable to zero or infinity.
- First principles: rebuild from basic facts.

## Oblique draw (optional)
Use when framing is stale.
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

## Technique picker
- No Aha → run one insight-biased technique (Lateral Thinking, Forced Connections, TRIZ) before options.
- Need a fast spark → Oblique Draw.
- Need to mutate an existing thing → SCAMPER.
- Need lots of ideas fast → Brainwriting 6-3-5.
- Need structured combinations → Morphological Analysis.
- Need to resolve contradictions → TRIZ.
- Need parallel perspectives → Six Thinking Hats.

## Technique library (use 1–3)
- CPS cycle: Clarify → Ideate → Develop → Implement.
  A simple session skeleton that prevents looping: clarify scope/constraints, diverge on options, strengthen the best candidates into experiments (signals + escape hatches), then execute the smallest step.
  Use it when you need momentum and traceability more than novelty.
  Example: Clarify “reduce deploy risk,” ideate rollout patterns, develop a canary experiment with a rollback trigger, then implement it for one service.
- Brainstorming: defer judgment; go for quantity; build; welcome wild ideas.
  Run a timed divergence phase where you only generate possibilities, then switch explicitly into critique/selection afterward.
  The rules protect fragile ideas long enough for recombination to happen.
  Example: In 10 minutes, list 30 ways to cut CI time; only after that, shortlist and score.
- Brainwriting 6-3-5: quiet idea generation; reduces groupthink.
  Each round: write 3 ideas in 5 minutes, then “pass” them for others to build on; six participants can yield up to 108 ideas in ~30 minutes.
  Use it when discussion is dominated by loud voices, or adapt it solo by doing multiple timed rounds and iterating on your earlier list.
  Example: Do three 5-minute rounds of “3 ideas,” then build on the prior round’s ideas (by you or others) instead of debating them.
- SCAMPER: Substitute/Combine/Adapt/Modify/Put to use/Eliminate/Reverse.
  Treat each verb as a prompt to mutate an existing approach (“What can we eliminate?”, “What can we reverse?”) and generate variants fast.
  Works best once you have a baseline solution and want creative improvements without starting from zero.
  Example: For a flaky test suite, Eliminate shared state, Combine setup steps, Modify timeouts, Reverse by testing the boundary contract instead of internals.
- Six Thinking Hats: facts/emotions/risks/benefits/creativity/process.
  Everyone adopts the same perspective in sequence (e.g., White facts → Red emotions → Black risks → Yellow benefits → Green ideas → Blue process) to reduce debate and surface tradeoffs cleanly.
  Use it when alignment is hard, stakes are high, or the conversation keeps mixing analysis with advocacy.
  Example: Evaluate “move to managed DB” by listing facts (costs), risks (lock-in), benefits (ops time), creative hybrids (split read replicas), then decide next step.
- TRIZ: formal contradiction resolution.
  State the contradiction (“we want X, but that worsens Y”), then look for separation principles or inventive principles that preserve both goals.
  Use it for engineering-style tradeoffs (performance vs safety, speed vs quality) where “pick one” feels like a false dichotomy.
  Example: Want faster responses but strict validation slows requests → separate in time by validating asynchronously and rejecting on next write.
- Morphological analysis: explore combinations across dimensions.
  List the key dimensions of the solution and the plausible values for each, then systematically combine them to discover non-obvious hybrids.
  Great for architecture/design spaces where components can be mixed-and-matched (storage, interface, rollout, constraints).
  Example: Dimensions: state store (SQL/KV), sync (push/pull), rollout (flag/canary), auth (OIDC/key) → enumerate combinations to find a viable MVP.
- Synectics: analogy ladder (direct → personal → symbolic).
  Force a new representation by stepping through layered analogies: “it’s like…”, “if I were it…”, “the symbol/metaphor is…”.
  Helpful when you need a conceptual leap, not just incremental variation.
  Example: Treat your alerting system as a “smoke detector,” then as “me being woken up,” then as “signal vs noise” to redesign thresholds and routing.
- Lateral thinking/provocation: generate a provocation, extract a usable lever.
  Make a deliberately “wrong” statement (often marked as PO), then ask what would make it workable and extract a principle/constraint you can apply.
  Best when conventional reasoning keeps returning the same answers; the translation back into action is the point.
  Example: PO “no one writes docs” → lever: auto-generate docs from code/examples and make the workflow require updating examples, not prose.
- Random stimulus: map properties of a random word/image to the problem.
  Pick something unrelated, list its properties, then force connections to spark new angles (stay abstract to avoid gimmicky literalism).
  Use it as a fast spark when your framing feels stale.
  Example: Random word “sponge” → properties: absorbs, releases slowly → idea: add a queue/buffer to absorb traffic spikes and drain steadily.
- Reverse brainstorming: “how do we make it worse?”, then invert.
  Generate ways to cause failure or maximize pain, then invert each into a safeguard or opportunity.
  This surfaces hidden assumptions and risk vectors, which is useful when you’re stuck or need to harden a plan.
  Example: “How do we guarantee bad deploys?” → skip staging, no rollback, hidden errors → invert into staging parity, rollback hooks, and visible error budgets.
- Mind mapping: expand and organize the space.
  Start from a central problem and radiate branches for stakeholders, causes, constraints, and solution threads, adding sub-branches as they appear.
  Use it to externalize working memory and reveal clusters and gaps that suggest the next reframe.
  Example: Center “slow onboarding,” branch into permissions, tooling, docs, environments, sample data; the emptiest branch often points to the next lever.
- Affinity diagramming: cluster ideas, name themes.
  After divergence, group raw ideas by similarity (often silently first), then label clusters with the underlying intent/theme.
  Use it to converge from a messy list into a few directions you can score and select.
  Example: Cluster a brainstorm into themes like “automation,” “guardrails,” “education,” then pick one representative experiment per theme.
- How Might We: reframe complaints into solvable prompts.
  Convert observations into open-ended, constructive questions that keep constraints visible (“How might we reduce onboarding time without sacrificing safety?”).
  Use it early to turn problem statements into an idea-friendly search space.
  Example: “This config is confusing” → “How might we make setup work by default, while still allowing explicit overrides for edge cases?”
- Crazy 8s: rapid variation sketches.
  Produce eight distinct variations in eight minutes to force range and escape your first idea.
  Most common for UI/UX, but it also works as “8 text-only variants” for APIs, checklists, or architectures.
  Example: Generate eight CLI designs for the same task (flags-only, interactive prompts, config-file-first, guided wizard, presets, etc.) and compare tradeoffs.
- Storyboarding: visualize end-to-end flow.
  Describe (or sketch) the sequence from trigger to outcome, including handoffs, decision points, and failure modes.
  Use it to uncover missing steps and to locate where “expected signal” can be measured.
  Example: Storyboard “incident → triage → mitigation → follow-up,” then mark the step where the best signal is “MTTR drops” and what instrumentation enables it.
- Lotus blossom: expand outward from a core problem.
  Surround the central problem with eight related sub-ideas, then treat each sub-idea as a new center and expand again.
  Use it when you want structured breadth without the chaos of unbounded brainstorming.
  Example: Core “reduce production incidents,” petals like testing/observability/rollouts/oncall; expand each petal into eight specific actions to populate the portfolio.

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
