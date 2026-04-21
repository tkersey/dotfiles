---
name: latent-move
description: Use this skill as a read-only workflow-starting composite skill for coding move selection before implementation. It must visibly run or emulate the sequence $latent-diver -> $creative-problem-solver -> $accretive -> $dominance, optionally using .codex/agents read-only subagents only as evidence lenses, then stop with a Dominant Move Brief. Trigger for ambiguous architecture, refactor, debugging, performance, integration, migration, stalled work, repeated failures, competing implementation paths, or explicit requests to use latent-move, latent-diver, creative-problem-solver, accretive, and dominance together. Do not edit code, apply patches, or invoke an executor from this skill.
---

# Latent Move

## Intent

Latent Move is the **read-only workflow skill** that finds the latent dominant coding move before implementation.

Its mandatory companion-skill spine is:

```text
$latent-diver
  -> $creative-problem-solver
  -> $accretive
  -> $dominance
  -> Dominant Move Brief
  -> stop
```

The output is a **Dominant Move Brief**, not a patch.

Optional custom subagents under `.codex/agents/*.toml` are only read-only evidence lenses. They do not replace the companion skills, do not decide the move, and do not execute anything.

This skill may recommend `fixed-point-driver` as a later executor, but it must not invoke it.

## Non-negotiable workflow rule

For a normal Latent Move pass, the final answer must make the companion-skill workflow visible.

Include a `Workflow Trace` section with these four rows in this order:

1. `$latent-diver`
2. `$creative-problem-solver`
3. `$accretive`
4. `$dominance`

Each row must state:

- `status`: invoked | emulated | skipped | unavailable | failed
- `reason`
- `output artifact`
- `handoff`

Rules:

- Prefer `invoked` when the Codex environment supports explicit skill invocation.
- Use `emulated` only when nested skill invocation is unavailable; still follow that skill's contract directly.
- Use `skipped` only when the user explicitly requested a narrow later phase or supplied a complete prior phase artifact.
- If the user requested `latent-move` or the full workflow, do not skip any of the four companion phases.
- Subagent activity never counts as one of the four rows.

## Companion skills are phases

Use these companion skills as the primary workflow phases.

### 1. `$latent-diver`

Purpose: discover the hidden frame before options are generated.

Expected output artifact: **Latent Frame Set**.

It should surface:

- hidden assumptions
- non-obvious problem representations
- latent constraints
- opportunity surfaces
- overlooked risks
- reframing pressure
- evidence needed to support or reject each frame

Do not let `$latent-diver` choose the final move.

### 2. `$creative-problem-solver`

Purpose: generate the option space from the latent frame.

Expected output artifact: **Five-Tier Portfolio**.

It should include:

- Quick Win
- Strategic Play
- Advantage Play
- Transformative Move
- Moonshot
- Artifact Spine
- accretive artifact per tier
- expected signal per tier
- escape hatch per tier

Do not treat the portfolio as selection.

### 3. `$accretive`

Purpose: compress the portfolio and nominate the strongest accretive move.

Expected output artifact: **Candidate Compression + Nominee**.

It should include:

- two to four plausible candidates
- target lane
- nominee, or explicit abstention
- why the nominee wins
- why next-best alternatives lose
- first proof signal

Force recommendation mode. Do not execute.

### 4. `$dominance`

Purpose: adversarially validate or reject the nominee.

Expected output artifact: **Dominance Verdict**.

It must return exactly one:

- `Winner`
- `No dominant move`
- `Insufficient evidence`

A winner requires comparable candidates, project-state evidence, a credible first proof signal, bounded diff risk, and clear material advantage over alternatives.

## Optional read-only subagents

Custom subagents live under `.codex/agents/*.toml`.

Use them only as evidence lenses around the companion-skill spine:

- `state_cartographer`: map project state before `$latent-diver`
- `latent_evidence_scout`: collect latent evidence before `$latent-diver`
- `constraint_miner`: identify hard constraints before portfolio generation
- `proof_surface_mapper`: find proof surfaces before `$accretive`
- `candidate_red_team`: attack nominee before `$dominance`
- `brief_auditor`: check final brief before output

Subagents must be read-only. They must not edit files, apply patches, run formatters, run migrations, install dependencies, start services, mutate project state, or claim final decisions.

Read `references/subagent-contract.md` before using subagents.

## Reference files

Use these references as needed:

- `references/workflow.md`: phase algorithm and routing rules
- `references/skill-trace.md`: required visible trace format
- `references/ledgers.md`: ledger schemas
- `references/subagent-contract.md`: optional read-only subagent packet contract
- `references/dominance-standard.md`: dominance gates
- `references/dominant-move-brief.md`: final brief templates

## Entry-state detection

Classify the request into exactly one entry state:

- `unframed-problem`: goal, failure, or success criteria are unclear.
- `frame-known`: problem is defined but viable moves are not mapped.
- `portfolio-exists`: multiple options already exist.
- `candidate-set-exists`: two to five plausible moves already exist.
- `proposed-winner-exists`: one move has already been nominated.
- `evidence-gap-known`: a named fact blocks comparison.
- `execution-requested`: user asks to implement, but selection has not been adjudicated.
- `review-only`: user wants judgment without implementation.

If the user explicitly asks for the full Latent Move workflow, do not collapse to a later phase even if one candidate looks obvious.

## Orchestration algorithm

1. Establish entry state.
2. Create an artifact state label.
3. Build a compact Evidence Snapshot from user input and direct inspection.
4. Optionally run the smallest helpful set of read-only subagents.
5. Run `$latent-diver`, or mark `emulated` if explicit nested skill invocation is unavailable.
6. Feed the Latent Frame Set into `$creative-problem-solver`.
7. Feed the Five-Tier Portfolio into `$accretive`.
8. Optionally run `candidate_red_team` if the nominee is risky, flashy, broad, or close to an alternative.
9. Feed candidates, nominee, evidence, and red-team pressure into `$dominance`.
10. Produce a Dominant Move Brief with a visible Workflow Trace.
11. Stop. Do not execute.

## Stop states

Use exactly one final state:

- `dominant-move`: one move survived dominance and has a credible first proof signal.
- `no-dominant-move`: candidates were comparable, but no move clearly dominates.
- `needs-evidence`: a missing fact blocks fair comparison.
- `needs-decision`: a user, product, architecture, or scope decision blocks selection.
- `blocked`: missing access, tooling, or context prevents a meaningful pass.

## Final report shape

Use these sections in this order:

- Workflow
- Entry State
- Subagent Mode
- Evidence Snapshot
- Workflow Trace
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
- Never let subagents replace `$latent-diver`, `$creative-problem-solver`, `$accretive`, or `$dominance`.
- Never silently emulate a companion skill; if emulated, mark it in the Workflow Trace.
- Never let `$latent-diver` choose the final move by itself.
- Never let `$creative-problem-solver` portfolio generation count as selection.
- Never let `$accretive` nomination count as validation.
- Never let `$dominance` validate a candidate with no credible proof signal.
- Never promote speculative upside as dominance.
- Never prefer a flashy move over a boring move that wins on leverage, proof, or reversibility.
- Never recommend execution without a first proof signal.
- Never claim artifact readiness.
- Never call a Dominant Move Brief a completed implementation.
- Never hide missing evidence.
- Never omit Workflow Trace or Do Next.
