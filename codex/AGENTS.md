# Minimal incision, maximal precision.

## Editing Constraints Override

You may see generic Codex guidance that says to stop immediately when unexpected working-tree changes appear. In this repo, the intended working-tree policy is more specific:

- If unexpected diffs appear, keep working; treat them as concurrent edits.
- Unrelated diffs: ignore and continue silently; do not mention them; never stage or commit them unless explicitly asked.
- Overlapping diffs in files you're editing: re-read as needed, reconcile without clobbering concurrent changes, re-apply only the still-valid part of your patch, and continue. Ask only when the overlap creates a real semantic conflict that cannot be resolved from the files.

## Response Format

- Echo: include `Echo:` with the most recent user message (max two lines, truncate with `...`) exactly once per user turn, in the final assistant response only. Do not include Echo in intermediary/progress updates.
- If a question block appears before Insights/Next Steps, place the Echo line immediately before that block; otherwise place it at the top.
- The Echo line must be standalone and followed by exactly one blank line before any other text.
- This requirement applies even when using skills or templates.
- This is a root user-facing response rule only: spawned subagents, collaborator threads, and other machine-to-machine handoff turns must not emit `Echo:` or instruction-ack preambles, and should answer the assigned task directly.
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or any artifact the user asked to copy verbatim. Put Echo only in the surrounding chat response.

## Challenge Escalation

- Raise the reasoning level as soon as a task stops feeling like a clean, dominant solve.
- Escalate before settling for competence, local polish, or a clarification that does not unblock the governing move.
- Trigger escalation when a first approach stalls, the answer feels merely adequate, the path patches symptoms instead of causes, multiple plausible moves compete, retries accumulate, or the task rewards unusually strong judgment.
- During escalation: reject the obvious answer, widen the search space, identify the highest-leverage move available now, explain why it dominates alternatives, and compress the result to the governing insight/invariant/architecture.
- Prefer compounding moves that make future good work easier, safer, or faster.
- Ask a narrow question only when missing secrets, missing permissions, or irreversible approvals are the real blocker.

## Purpose

This file is a compact, high-authority routing index for Codex in this repo. Use task-specific skills for detailed procedures. This file owns implicit-trigger policy, side-effect boundaries, repository safety, response format, challenge escalation, and recursive orchestration posture.

## Core invariants

- Prefer local Codex execution surfaces before externalizing work elsewhere.
- Use native planning, skills, subagents, recursive orchestration, and repository-local tools; do not invent a parallel coordination protocol.
- Use `update_plan` for non-trivial user-visible planning, but keep it concise and current.
- Keep durable orchestration state in `$st`, not in prose, memory, or an overloaded `update_plan` row.
- Keep historical/session/artifact forensics in `$seq`; do not use `$seq` for ordinary current-repo code search.
- Preserve unrelated user, agent, and tool changes. Do not overwrite or publish unrelated diffs.
- Verify changed behavior with the narrowest focused checks available. If verification cannot run, say why.
- Do not add mode banners, debug prefixes, routing labels, or instruction-ack preambles to user-facing responses other than the required `Echo:` line.

## Working tree hygiene

- Never use broad reset/checkout/clean commands to erase working-tree state unless the user explicitly requests that exact destructive operation.
- Treat `.git/info/exclude` matches as local-only/private publication boundaries, even for tracked-looking workflow artifacts.
- If a path is already tracked but also matches `.git/info/exclude`, treat new changes to that path as local-only unless the user explicitly asks to publish them.
- Before staging local-state artifacts such as `.step/st-plan.jsonl`, `.step/*.lock`, or `.learnings.jsonl`, run `git check-ignore -v --no-index <path>` when in doubt. If the source is `.git/info/exclude`, do not force-add, stage, or commit the path unless explicitly asked.

## Local Codex execution guidance

Default: use the local Codex execution surface that best matches the shape of the work. Stay direct when work is bounded or entangled; fan out when work is naturally decomposed. Do not create a second execution stack.

Routing order:

1. **Direct local execution** — one bounded change/question, unclear decomposition, overlapping writes, or synthesis/integration work.
2. **Planning/selection pass** — if the user supplies `SLICES.md`, `plan-N.md`, or asks for the next safe wave, perform local selection first and publish only selected work in `update_plan`.
3. **Durable orchestration with `$st`** — use when work has 3+ dependent steps that must survive turns/sessions, needs claims/proof/dependency state, imports an OrchPlan, already has active `.step/st-plan.jsonl`, or explicitly needs durable state.
4. **Native subagents** — use when delegation is requested or when parallel, independent, file-disjoint branches improve coverage. The lead owns synthesis, dependency resolution, conflict resolution, publication decisions, and overlapping edits.
5. **Row batches** — for same-shaped independent work over many files/items/rows, use the smallest local script/CLI/direct worker path that produces structured output.
6. **Fanout discipline** — launch the dependency-independent ready set before the first blocking wait.
7. **Recursive orchestration** — encourage when child tasks can be further decomposed into independent investigation, implementation, verification, evidence-gathering, or synthesis branches.

Use built-in `explorer`, `worker`, and `default` roles unless a custom role is visibly exposed and is a clear narrow fit. Close subagents after their contribution is integrated.

## Skill routing

Skills are workflow selectors, not magic words. Do not wait for an explicit `$skill` when the request clearly matches a skill description. Use the smallest sufficient skill stack.

When multiple skills apply, prefer this stack shape:

```text
understand context -> escalate frame if useful -> lock invariants -> implement -> verify/review -> close -> capture learnings
```

### Skill stack map

Treat skills as stage owners, lenses, validators, or side-effecting workflows rather than interchangeable peers.

- Evidence / recall: `seq`, `chronicle`, `learnings`, `codebase-archaeology`.
- Divergence / opportunity: `latent-diver`, `ideate`, `creative-problem-solver`, `glaze`, `asi`.
- Modeling / invariants: `algebra-driven-design`, `kan`, `universalist`, `invariant-ace`.
- Reduction / simplification: `reduce`, `abstraction-cartographer`, `abstraction-tax-auditor`, `altitude-adjudicator`, `one-seam-operator`.
- Decision gating: `grill-me`, `spec-gate`, `dominance`, `spec-challenge`.
- Specification: `spec-pipeline`, `spec-lint`, `plan`.
- Execution: `accretive-implementer`, `one-seam-operator`, `fixed-point-driver`, `tk`.
- Verification / closure: `context-bounded-verification`, `adversarial-reviewer`, `prove-it`, `verification-closure`.
- Publication / lifecycle: `ship`, `fin`, `auto`, `learnings`.
- Language surface: `logophile`.

Use `codex/skills/.system/routing-regression/skill-stack-map.md` as the fuller stage map.

### Activation cost discipline

Prefer the lowest-cost skill that fully satisfies the task. Escalate only when the current answer is materially underpowered, the prompt explicitly asks for the heavier workflow, or the task's risk/complexity requires it.

Use `codex/skills/.system/routing-regression/activation-costs.json` as the cost manifest.

Default cost posture:

- `low`: safe implicit rails such as `logophile` for human-facing wording only.
- `medium`: bounded forensic or gate checks such as `seq`, `chronicle`, `spec-gate`, and `spec-lint`.
- `high`: substantial workflows such as `ideate`, `algebra-driven-design`, `kan`, `reduce`, `universalist`, `spec-pipeline`, and `auto`.
- `extreme`: multi-turn proof engines such as `prove-it`.

Do not invoke an extreme or high-cost workflow merely because it is adjacent. Route to the smallest sufficient stage owner first, then hand off only when the output packet proves the next stage is needed.

### Implicit default rails

- Non-trivial implementation, remediation, migration, hardening, repair, or review-driven code changes -> `accretive-implementer`.
- Behavior-affecting code changes, refactors, blast-radius questions, rollout/rollback concerns, regression risk, or incomplete-context correctness claims -> `context-bounded-verification`.
- State, protocol, invariant, impossible-state, race, idempotency, retry, cache-drift, lifecycle, or validation-sprawl cues -> `invariant-ace` before edits.
- Patch hardening, de novo changeset review, material defect discovery, or re-review after fixes -> `adversarial-reviewer`.
- Final readiness, closure gates, fixed-point claims, or "is this ready?" after material work -> `verification-closure`.
- Review comments, reviewer suggestions, or "should we act on this?" before implementation -> `review-adjudication`.
- Exhaustive hardening, repeated review/fix loops, "drive this to closure," or "find all impactful issues" -> `fixed-point-driver`.

### Challenge escalation skills

- Use `glaze` for a deeper pass, `latent-diver` for non-obvious frames, `accretive` for the single dominant high-leverage move, `dominance` to judge competing moves, and `asi` when a 10x/systemic ambition pass with concrete cash-out is useful.
- Escalation is repeatable when new friction, evidence, frames, or leverage appears.

### Repo understanding and structural lenses

- Unfamiliar repo, onboarding, systematic exploration -> `codebase-archaeology`.
- Architecture, repo dialect, seam fit, placement, dependency direction, docs-vs-code drift -> `parse`.
- Local readability, branching, control-flow, cognitive complexity -> `complexity-mitigator`.
- Stronger shape-of-truth, seam, model, invariant boundary, conceptual compression -> `universalist`.
- Too many layers, frameworks, dependencies, tools, adapters, abstractions, or indirection -> `reduce`.
- Behavior-preserving simplification, DRY, isomorphic refactor, net-negative LOC objective -> `simplify-and-refactor-code-isomorphically`.
- Broad repo/security/API/UX/performance/copy/CLI/maintainability/launch audit -> `codebase-audit`.
- Interface/flow/CLI UX/accessibility/cognitive-load/usability review -> `ux-audit`.

### Performance, language, and proof rails

- Optimization, latency, throughput, memory, p95/p99, scalability, performance regression -> `lift`.
- Measurement-only hotspot/flamegraph/profile attribution -> `profiling-software-performance`; hand off to `lift` for code changes.
- Zig files/toolchain/comptime/allocator/FFI/concurrency/performance -> `zig`.
- Lean/Lake/proof repair/formalization/termination/mathlib -> `lean`.
- Human-facing wording, naming, terminology, headings, PR/commit text, docs, explanations, error/help text, doctrine words -> `logophile`.
- Absolute claims, proof gauntlets, adversarial stress tests, or explicit "prove it" requests -> `prove-it`; do not trigger its heavy loop merely because ordinary verification is useful.

### Discovery, strategy, and planning

- Fuzzy product/project opportunity, "what should we build/improve?", or evidence-backed ideation -> `ideate`.
- Options, tradeoffs, strategy portfolio, divergent approaches, or multiple viable directions before choosing -> `creative-problem-solver`.
- Ambiguous/conflicting requirements where implementation would be premature -> `grill-me`.
- Serious planning artifact, plan refinement, architecture plan, implementation campaign, or decision-complete `<proposed_plan>` output -> `plan`.
- Decision-complete spec automation -> `spec-pipeline`; plan-readiness gate -> `spec-gate`; implementation-readiness lint -> `spec-lint`; single invariant challenge -> `spec-challenge`.

### Modeling boundaries

- Use `algebra-driven-design` when the governing question is domain algebra: carriers, operations, observations, laws/non-laws, effects, interpreters, policy laws, law-derived architecture, and property/trace/parity tests.
- Use `kan` when the governing question is a boundary equation: extension across `K`, lift through `P`, compatibility facade, generated target semantics, public projection, defunctionalized boundary IR, Yoneda/Coyoneda representation, and categorical witness/law tests.
- Use `universalist` when the main question is the smallest honest construction that makes repeated obligations or impossible states explicit.
- Use `reduce` when the user asks to remove layers or lower abstraction while preserving behavior.

### Lifecycle and publication

- Evidence-backed recall/capture/promotion/supersession/learning hygiene -> `$learnings`.
- Durable task state/dependencies/claims/proof/checkpoints -> `$st`.
- Session/transcript/artifact/memory/orchestration/provenance/tool-trace forensics -> `$seq`.
- Open/update a PR without merging -> `ship`.
- Merge/land/finish a PR -> `fin`, after required checks, approvals, and explicit merge/land intent.
- Evidence-backed autonomous skill improvement -> `auto`, with protected-skill, sanitized-summary, validation, branch, PR, and merge guardrails.

### Tightly gated skills

- `cas`: only clear app-server transport/detached review-session/review-session control cues.
- `cron`: only clear local automation or schedule-management intent.
- `ghost`: only explicit/very clear ghost/spec package, portable reproduction bundle, or generated proof/test harness package intent.
- `deckset`: only decks/slides/presentations/Deckset output.
- `ms`: skill creation/editing; `refine`: existing-skill refinement.

### Side-effect boundary

Rails and lenses may trigger implicitly. Side-effecting workflows require clear intent. Keep `$st`, `$seq`, `cas`, `cron`, `ship`, `fin`, `ghost`, `deckset`, `ms`, `refine`, and `prove-it` gated. `logophile` may trigger implicitly for human-facing language but must preserve semantics and machine-consumed syntax.

## Plan Sync (`$st` <-> Codex `update_plan`)

Use only when `.step/st-plan.jsonl` participates because the user asked for `$st`, the repo already has active durable state, or the task explicitly needs cross-turn durable orchestration.

- `$st` is durable truth. `update_plan` is a selected, user-visible mirror.
- Mutate durable state only through `st` commands. Do not hand-edit existing JSONL rows.
- Preserve `[st-id]` prefixes exactly; they are the reverse-sync key.
- Keep dependencies, notes, claims, proof, runtime metadata, and durable-only context in `$st`, not in `update_plan`.
- Before final delivery on `$st` tasks, assert/regenerate projection and resolve visible drift.

## Seq Local-First Routing

Use `$seq` for explicit `$seq` requests and for historical session, memory, transcript, artifact, orchestration, provenance, or tooling-trace forensics. Do not use `$seq` for ordinary current-repo code search.

- For finalized `<proposed_plan>` artifacts, start with `plan-search`.
- For broad artifact forensics, start with `artifact-search` and follow `$seq`'s command ladder.
- Run opencode datasets/commands only when the current user request contains the literal word `opencode`.

## Learnings lifecycle

Use the native `learnings` CLI. Treat learnings as a closed loop: recall before implementation, capture only decision-shaping evidence, promote repeated lessons into durable policy, supersede stale records, and audit whether recalled memory improved execution.

### Recall before implementation

- If `.learnings.jsonl` exists in the repo root, run request-aware recall before substantial implementation.
- Distill the request to 4-8 focused terms.
- Use `learnings recall --query "<query>" --limit 5 --drop-superseded`.
- Treat recalled learnings as constraints or hypotheses to verify, not unquestioned truth.

### Capture checkpoints

Run `$learnings` before final response, commit, PR, or handoff only when a decision-shaping checkpoint occurred: validation transition, strategy pivot, footgun discovery, acceleration pattern, useful/failed recalled learning, meaningful pause, or delivery after real implementation work.

Quality gate:

1. Decision delta: would this change what the next agent does?
2. Transferability: does it apply beyond this exact incident?
3. Counterfactual: if ignored, is there predictable failure/cost/missed leverage?

Write rules, not changelog entries. Prefer one essential learning; append at most three.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Review the diff before final response or commit.

### GitHub CLI (`gh`)

- Use `gh` for GitHub operations when available and authenticated.
- Check `gh auth status` before assuming authentication is broken.
- Prefer terminal-native PR, issue, Actions, and gist operations over browser-only workflows.

### Python

- Use `uv` for Python package/project operations unless the repo explicitly requires otherwise or the user asks.
- Run scripts/tests/linters/CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx <tool>` or `uv run --with <package> <command> ...`.
- Do not create/reuse `.venv*` for skill-only tooling.
- Prefer `#!/usr/bin/env -S uv run python` for Python automation scripts.

## Verification and final response

Before final delivery:

- Check relevant diff or generated artifact.
- Run the narrowest meaningful verification.
- For `$st` work, confirm durable and mirrored plans are not visibly drifting.
- For delegated work, integrate results locally before presenting conclusions.
- Clean up temporary files, agents, claims, or scratch state that should not persist.

Final responses should follow the required Response Format and then remain concise and factual: state what changed/found, include proof, mention material risks/blockers, and include a short orchestration ledger only when orchestration actually ran.
