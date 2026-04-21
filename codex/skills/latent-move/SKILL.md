---
name: latent-move
description: Use this skill when a coding task needs read-only move selection before implementation: surface latent frames, collect project-state evidence with optional read-only subagents, generate a five-tier option portfolio, nominate one accretive move, adversarially validate whether it dominates, and stop with a canonical Dominant Move Brief. Trigger for ambiguous architecture, refactor, debugging, performance, integration, migration, stalled work, repeated failures, competing implementation paths, or requests to use latent-diver, creative-problem-solver, accretive, and dominance together. Do not edit code, run write-heavy agents, or invoke an executor from this skill.
---

# Latent Move

## Intent

Latent Move is a read-only adjudication workflow. It does not ask, "What is a good plan?" It asks, "Which move is latent in the current project state, materially dominant over the alternatives, and ready to hand to a human or executor with a concrete first proof signal?"

The output is a **Dominant Move Brief**, not a patch.

Coordinate these companion skills when available:

- `latent-diver` for hidden frames, implicit assumptions, non-obvious surfaces, and reframing pressure
- `creative-problem-solver` for a five-tier option portfolio
- `accretive` for nominating one high-leverage move or abstaining
- `dominance` for adversarial validation of the nominated move

This skill may recommend `fixed-point-driver` as a later executor, but it does not invoke it.

## Core doctrine

- **UNSOUND**: reject unsupported conclusions and label unknowns instead of guessing.
- **MECHANISTIC**: reason through failure mechanisms, contracts, state transitions, coupling, and side effects.
- **ACCRETIVE**: prefer moves that create durable leverage: stronger invariants, better proof surfaces, simpler interfaces, reusable artifacts, or reduced future cost of change.
- **TRACEABLE**: tie major claims to files, symbols, tests, docs, commands, traces, logs, failures, constraints, or user-provided evidence.
- **LATENT-SEEKING**: look for the hidden move implied by the artifact, not merely the obvious next task.
- **ADVERSARIAL**: try to falsify the proposed winner before endorsing it.
- **MATERIAL**: focus on consequential correctness, capability, safety, reliability, compatibility, performance, verification, interface, and maintainability risk.
- **CANONICAL**: use stable ledgers and a stable final brief rather than ad hoc summaries.
- **NON-EXECUTING**: do not edit files, apply patches, commit, merge, or invoke write-heavy implementation agents.
- **SUBAGENTS-AS-LENSES**: read-only subagents supply evidence and pressure signals; they do not decide.

## Scope boundary

Allowed:

- inspect repository state
- read files, docs, tests, traces, logs, issues, PRs, and user constraints
- run read-only searches
- ask optional read-only subagents for evidence packets
- synthesize latent frames
- generate candidate moves
- rank and adjudicate candidates
- produce a Dominant Move Brief
- recommend an executor or human next step

Disallowed:

- editing files
- applying patches
- formatting or rewriting code
- creating commits or branches
- invoking write-heavy agents
- running implementation loops
- claiming the artifact is ready
- treating a recommendation as validation of completed work

If the user explicitly asks for execution, finish Latent Move first. Then report that the Dominant Move Brief is ready for a separate executor such as `fixed-point-driver`.

## Reference files

Read the relevant reference file only when needed:

- `references/workflow.md`: full phase algorithm and routing rules
- `references/ledgers.md`: canonical ledger schemas
- `references/subagent-contract.md`: read-only subagent packet contract and degradation handling
- `references/dominance-standard.md`: dominance gates and candidate scoring pressure
- `references/dominant-move-brief.md`: final brief templates for all stop states

## Entry-state detection

Classify the request into exactly one entry state before routing:

- `unframed-problem`: the goal, failure, or success criteria are unclear.
- `frame-known`: the problem is defined but viable moves are not yet mapped.
- `portfolio-exists`: the user or prior turn already supplied multiple options.
- `candidate-set-exists`: two to five plausible moves already exist.
- `proposed-winner-exists`: one move has already been nominated.
- `evidence-gap-known`: the next decision depends on a specific missing fact.
- `execution-requested`: the user asks to implement, but the move has not yet been adjudicated.
- `review-only`: the user wants judgment on a proposed move without implementation.

If the user explicitly asks for the full Latent Move workflow, do not collapse to a later phase even if one candidate appears obvious.

## Phase selection

Choose the first applicable phase:

1. Start with `latent-diver` when the problem is ambiguous, underframed, stalled, or likely hiding a better representation.
2. Start with `creative-problem-solver` when the frame is clear but options are needed.
3. Start with `accretive` when a portfolio or candidate set already exists and selection is needed.
4. Start with `dominance` when a proposed winner already exists and needs adversarial validation.
5. Start with evidence gathering when a named evidence gap blocks fair comparison.
6. Never start with execution.

## Companion skill use

When explicit nested skill invocation is supported, use:

- `$latent-diver`
- `$creative-problem-solver`
- `$accretive`
- `$dominance`

If explicit nested invocation is unavailable, perform the same phase contracts directly.

### `latent-diver` contract

Use as a read-only discovery lens. Expected output: hidden assumptions, latent frames, non-obvious opportunity surfaces, overlooked risks, reframing pressure, and evidence needed to support or reject each frame. Do not let `latent-diver` choose the final move by itself.

### `creative-problem-solver` contract

Use to generate the option space. Expected output: current Double Diamond stage, working definition and success criteria when weak, Artifact Spine, and a five-tier portfolio: Quick Win, Strategic Play, Advantage Play, Transformative Move, Moonshot. Each option needs an accretive artifact, expected signal, and escape hatch.

Inside Latent Move, do not stop for human tier selection unless the user explicitly requested interactive selection. The portfolio is input to candidate compression, not execution.

### `accretive` contract

Use to compress the option space. Expected output: target lane, current-state evidence, two to four plausible moves, one nominee only if it clearly dominates nearby alternatives, why the nominee wins, why next-best alternatives lose, first proof signal, and abstention if no move clearly dominates.

Force recommendation mode. Do not execute even if the move looks obvious.

### `dominance` contract

Use as the adversarial gate. Expected verdicts: `Winner`, `No dominant move`, or `Insufficient evidence`.

A `Winner` requires comparable candidates, project-state evidence, no failed evidence gate, a credible first proof signal, bounded diff risk, and a clear material advantage over alternatives.

## Optional read-only subagents

Use subagents only when they improve evidence quality or reduce blind spots. Prefer the smallest relevant swarm.

Project-scoped custom subagents live under `.codex/agents/*.toml`, not inside this skill's `agents/` directory. This skill expects these custom agent names when available:

- `state_cartographer`
- `latent_frame_scout`
- `constraint_miner`
- `proof_surface_mapper`
- `candidate_red_team`
- `brief_auditor`

The skill-local `agents/openai.yaml` file is only skill metadata for Codex UI/policy configuration.

Use an initial read-only swarm when the repo surface is broad, the task is architectural, a failure has repeated, the next move is not obvious, hidden constraints are likely, or the user requested subagents.

Use `candidate_red_team` when the nominee looks flashy, high-risk, broad, or close to the runner-up.

Use `brief_auditor` when the final brief will be handed to an executor or human.

Subagents are read-only. They must not edit files, apply patches, run formatters, run migrations, install dependencies, start services, mutate project state, or claim final decisions.

See `references/subagent-contract.md` before using subagents.

## Orchestration summary

1. Establish entry state.
2. Create an artifact state label.
3. Build the initial Evidence Ledger from user input and direct inspection.
4. Decide whether to use a small read-only subagent swarm.
5. Normalize subagent packets into the Specialist Briefing Ledger.
6. Run the latent pass.
7. Run the five-tier portfolio pass.
8. Compress the portfolio into two to four plausible candidates.
9. Nominate one move only if it clearly dominates.
10. Run the dominance gate.
11. Stop with exactly one final state and a Dominant Move Brief.
12. Do not execute.

Read `references/workflow.md` for the full algorithm.

## Stop states

Use exactly one final state:

- `dominant-move`: one move survived dominance and has a credible first proof signal.
- `no-dominant-move`: candidates were comparable, but no move clearly dominates.
- `needs-evidence`: a missing fact blocks fair comparison.
- `needs-decision`: a user, product, architecture, or scope decision blocks selection.
- `blocked`: missing access, tooling, or context prevents a meaningful pass.

## Final report shape

Use concise sections:

- Workflow
- Entry State
- Subagent Mode
- Evidence Snapshot
- Latent Signals
- Portfolio Summary
- Candidate Compression
- Dominance Verdict
- Dominant Move Brief
- Residual Uncertainty
- Final State
- Do Next

`Do Next` must be last and use this exact field set:

```text
## Do Next
- owner: skill | user | fixed-point-driver | human | none
- action:
- why:
- state: dominant-move | no-dominant-move | needs-evidence | needs-decision | blocked
```

## Hard rules

- Never edit code.
- Never apply patches.
- Never invoke write-heavy implementation subagents.
- Never use concurrent write-heavy agents.
- Never treat subagents as authorities.
- Never let `latent-diver` choose the final move by itself.
- Never let `creative-problem-solver` portfolio generation count as selection.
- Never let `accretive` nomination count as validation.
- Never let `dominance` validate a candidate with no credible proof signal.
- Never promote speculative upside as dominance.
- Never prefer a flashy move over a boring move that wins on leverage, proof, or reversibility.
- Never recommend execution without a first proof signal.
- Never claim artifact readiness.
- Never call a Dominant Move Brief a completed implementation.
- Never hide missing evidence.
- Never ask for clarification when a best-effort brief can state assumptions and decision gates.
- Never use malformed specialist output as evidence.
- Never relay raw malformed specialist output to the user.
- Never omit the final `Do Next`.
