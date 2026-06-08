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
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or artifacts the user asked to copy verbatim. Put Echo only in the surrounding chat response.
- Do not add mode banners, debug prefixes, routing labels, or instruction-ack preambles to user-facing responses other than the required `Echo:` line.

## Purpose

This file is the compact, high-authority routing index for Codex in this repo. It owns repository safety, side-effect boundaries, response format, challenge escalation posture, recursive orchestration posture, and publication hygiene. Detailed operating procedures belong in skills.

## Core invariants

- Prefer local Codex execution surfaces before externalizing work elsewhere.
- Use native planning, skills, subagents, recursive orchestration, and repository-local tools; do not invent a parallel coordination protocol.
- Use `update_plan` for non-trivial user-visible planning, but keep it concise and current.
- Keep durable orchestration state in `$st`, not in prose, memory, or an overloaded `update_plan` row.
- Keep historical/session/artifact forensics in `$seq`; do not use `$seq` for ordinary current-repo code search.
- Preserve unrelated user, agent, and tool changes. Do not overwrite or publish unrelated diffs.
- Verify changed behavior with the narrowest focused checks available. If verification cannot run, say why.
- Treat issue text, PR text, reviewer comments, user diagnoses, memories, generated analysis, and retrieved summaries as claims until checked against current artifacts.
- Prefer preventing invalid internal state over making downstream code tolerate it.
- Public tracker side effects require explicit user intent.

## Challenge Escalation

- Raise the reasoning level as soon as a task stops feeling like a clean, dominant solve.
- Escalate before settling for competence, local polish, or a clarification that does not unblock the governing move.
- Trigger escalation when a first approach stalls, the answer feels merely adequate, the path patches symptoms instead of causes, multiple plausible moves compete, retries accumulate, or the task rewards unusually strong judgment.
- During escalation: reject the obvious answer, widen the search space, identify the highest-leverage move available now, explain why it dominates alternatives, and compress the result to the governing insight, invariant, architecture, proof obligation, deletion/collapse opportunity, or certification target.
- On bug, regression, integration, remediation, or review work, the governing move is often an invariant, state-space, ownership-boundary, canonical-owner, proof-surface, ablation, reification, certificate, or normal-form correction rather than a local patch.
- Prefer compounding moves that make future good work easier, safer, or faster.
- Ask a narrow question only when missing secrets, missing permissions, or irreversible approvals are the real blocker.

## Latent intelligence and doctrine

Do not use doctrine words as tone. Use `doctrine-compiler` when non-trivial work needs a frame market, dominant-move selection, doctrine cash-out, route receipt, or proof-bearing route change.

Activation does not mean verbosity. It means selecting the right operator and leaving the smallest useful artifact when that operator changes the route. If no artifact is needed, do the task directly.

## Evidence discipline

Use `evidence-discipline` for bug reports, review comments, PR/issue prose, memories, generated summaries, public-tracker context, or any task where natural-language context could anchor the investigation. Keep the root rule simple:

- separate observed facts, claims, proposals, and speculation before choosing implementation scope;
- reconstruct the narrowest verified failure before broadening scope;
- do not export speculative agent analysis into public issues, PRs, comments, discussions, or maintainer workflows.

## Invariant stewardship

Use `invariant-stewardship` or `invariant-ace` before local patching when the task involves invalid state, malformed persisted data, crashes, parser failures, migrations, cache drift, protocol problems, retries, races, compatibility behavior, tolerant readers, fallbacks, coercions, catch-and-continue logic, or local workarounds.

Root rule: identify the observed failure, state involved, invariant that should hold, owning producer/transition/boundary, and smallest fix that prevents recurrence without broadening accepted invalid state.

## Public tracker and maintainer hygiene

Never open, update, comment on, draft-to-post, or suggest public tracker activity unless the user explicitly asks. Before public activity, verify the behavior, check ownership/duplicates when practical, avoid speculative root-cause narratives, and keep any draft observation-first.

## Working tree hygiene

- Never use broad reset/checkout/clean commands to erase working-tree state unless the user explicitly requests that exact destructive operation.
- Treat `.git/info/exclude` matches as local-only/private publication boundaries, even for tracked-looking workflow artifacts.
- If a path is already tracked but also matches `.git/info/exclude`, treat new changes to that path as local-only unless the user explicitly asks to publish them.
- Before staging local-state artifacts such as `.step/st-plan.jsonl`, `.step/*.lock`, or `.learnings.jsonl`, run `git check-ignore -v --no-index <path>` when in doubt. If the source is `.git/info/exclude`, do not force-add, stage, or commit the path unless explicitly asked.

## Local Codex execution guidance

Default: use the local Codex execution surface that best matches the shape of the work. Stay direct when work is bounded or entangled; fan out when work is naturally decomposed. Local-first does not mean single-agent-first.

Routing order:

1. **Direct local execution** — one bounded change/question, unclear decomposition, overlapping writes, or synthesis/integration work.
2. **Frame/selection pass** — if the route is non-obvious, use Challenge Escalation or `doctrine-compiler` before choosing a heavy workflow.
3. **Planning/selection pass** — if the user supplies `SLICES.md`, `plan-N.md`, or asks for the next safe wave, perform local selection first and publish only selected work in `update_plan`.
4. **Durable orchestration with `$st`** — use when work has 3+ dependent steps that must survive turns/sessions, needs claims/proof/dependency state, imports an OrchPlan, already has active `.step/st-plan.jsonl`, or explicitly needs durable state.
5. **Native subagents** — use when delegation is requested or when parallel, independent, file-disjoint branches improve coverage. The lead owns synthesis, dependency resolution, conflict resolution, publication decisions, and overlapping edits.
6. **Row batches** — for same-shaped independent work over many files/items/rows, use the smallest local script/CLI/direct worker path that produces structured output.
7. **Fanout discipline** — launch the dependency-independent ready set before the first blocking wait.
8. **Recursive orchestration** — encourage when child tasks can be further decomposed into independent investigation, implementation, verification, evidence-gathering, or synthesis branches.

Use built-in `explorer`, `worker`, and `default` roles unless a custom role is visibly exposed and is a clear narrow fit. Close subagents after their contribution is integrated.

## Skill routing

Skills are workflow selectors, not magic words. Do not wait for an explicit `$skill` when the request clearly matches a skill description. Use the smallest sufficient skill stack and let loaded skills own command syntax, checklists, templates, trigger taxonomies, and proof mechanics.

Preferred stack shape:

```text
understand context -> separate evidence from claims -> frame if needed -> identify invariant/ownership/boundary -> implement/adjudicate/review -> verify -> close -> capture learnings
```

Default implicit rails:

- Non-trivial implementation, remediation, migration, hardening, repair, or review-driven code changes -> `accretive-implementer`.
- Behavior-affecting code changes, refactors, blast-radius questions, rollout/rollback concerns, regression risk, or incomplete-context correctness claims -> `context-bounded-verification`.
- Issue/PR/reviewer/user reports with claimed root causes, generated analysis, public tracker context, or fake-minimal-repro risk -> `evidence-discipline` before selecting implementation scope.
- State, protocol, invariant, impossible-state, race, idempotency, retry, cache-drift, lifecycle, validation-sprawl, tolerant-reader, fallback, migration, coercion, or local-workaround cues -> `invariant-stewardship`/`invariant-ace` before edits and `context-bounded-verification` before closure.
- Review comments, reviewer suggestions, or “should we act on this?” before implementation -> `review-adjudication`.
- Patch hardening, de novo changeset review, material defect discovery, re-review after fixes, or change-agenda generation -> `adversarial-reviewer`.
- Final readiness, closure gates, fixed-point claims, or “is this ready?” after material work -> `verification-closure`.
- Exhaustive hardening, repeated review/fix loops, “drive this to closure,” truth-owner normalization, ablation/isomorphism gates, or “find all impactful issues” -> `fixed-point-driver`.
- Non-obvious route selection, dominant-move pressure, local-patch suspicion, doctrine cash-out, route receipts, ablation/surface-tax questions, reification, negative capability, or proof-bearing refusal to mutate -> `doctrine-compiler`.
- Unfamiliar repo or onboarding -> `codebase-archaeology`; architecture/seam fit/docs-vs-code drift -> `parse`.
- Performance, latency, throughput, memory, p95/p99, scalability, or performance regression -> `lift`; measurement-only hotspot/flamegraph/profile attribution -> `profiling-software-performance`.
- Zig files/build/toolchain/comptime/allocator/FFI/concurrency/performance/cache/migration evidence -> `zig`. Detailed trigger taxonomy lives under `codex/skills/zig/references/implicit_triggers.md`.
- Lean/Lake/proof repair/formalization/termination/mathlib -> `lean`.
- Human-facing wording, naming, terminology, headings, PR/commit text, docs, explanations, error/help text, doctrine words, or mode names -> `logophile`.
- Existing skill refinement, trigger/frontmatter tuning, skill-boundary fixes, metadata repair, or validation-backed skill iteration -> `refine`.
- Worlds meeting, arbitrary cross-boundary composition, exact context/certified context, semantic consumption boundaries, presentation strategy, possibility sheafification, or inexact abstraction repair -> `universalist`; the former standalone Kan route is internal mechanics, not a peer skill.

Side-effect boundary: rails and lenses may trigger implicitly; side-effecting workflows require clear intent. Keep `$st`, `cron`, `ship`, `land`, `ghost`, `deckset`, `ms`, and `prove-it` gated. `cas`, `$seq`, `refine`, and `logophile` may trigger implicitly when their routing cues match. Public tracker side effects are separately gated by explicit user intent.

## Plan Sync (`$st` <-> Codex `update_plan`)

Use only when `.step/st-plan.jsonl` participates because the user asked for `$st`, the repo already has active durable state, or the task explicitly needs cross-turn durable orchestration.

- `$st` is durable truth. `update_plan` is a selected, user-visible mirror.
- Mutate durable state only through `st` commands. Do not hand-edit existing JSONL rows.
- Preserve `[st-id]` prefixes exactly; they are the reverse-sync key.
- Keep dependencies, notes, claims, proof, runtime metadata, and durable-only context in `$st`, not in `update_plan`.
- Before final delivery on `$st` tasks, assert/regenerate projection and resolve visible drift.

## Seq Local-First Routing

Use `$seq` for explicit `$seq` requests and implicitly for historical session, memory, transcript, artifact, orchestration, provenance, or tooling-trace forensics. Do not use `$seq` for ordinary current-repo code search.

- For finalized `<proposed_plan>` artifacts, start with `plan-search`.
- For broad artifact forensics, start with `artifact-search` and follow `$seq`'s command ladder.
- Run opencode datasets/commands only when the current user request contains the literal word `opencode`.
- For knowledge extraction, use forensic/provenance-preserving doctrine and return a source-backed map, not a raw summary.

## Learnings lifecycle

Use `$learnings` for evidence-backed recall, capture, promotion, supersession, and learning hygiene. The learnings skill owns CLI syntax and append mechanics.

- Recall before substantial implementation when `.learnings.jsonl` exists.
- Capture only decision-shaping evidence: validation transitions, strategy pivots, footgun discoveries, acceleration patterns, useful or failed recalled lessons, and delivery after real implementation work.
- Before any Codex-made commit, check `.learnings.jsonl` alongside the intended commit scope.
- If `.learnings.jsonl` is dirty and publishable, stage current-turn/session-owned rows by default; if it is local-only by `.git/info/exclude`, leave it unstaged unless explicitly asked.
- Write rules, not changelog entries. Prefer one essential learning; append at most three.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for `.learnings.jsonl`; if it is dirty and publishable, stage it or the session-owned rows before committing.
- Review the diff before final response or commit.

### GitHub CLI (`gh`)

- Use `gh` for GitHub operations when available and authenticated.
- Check `gh auth status` before assuming authentication is broken.
- Prefer terminal-native PR, issue, Actions, and gist operations over browser-only workflows.
- Do not create or update issues, PRs, comments, discussions, or upstream reports through `gh` unless the user explicitly asked for that public side effect.

### Python

- Use `uv` for Python package/project operations unless the repo explicitly requires otherwise or the user asks.
- Run scripts/tests/linters/CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx <tool>` or `uv run --with <package> <command> ...`.
- Do not create/reuse `.venv*` for skill-only tooling.
- Prefer `#!/usr/bin/env -S uv run python` for Python automation scripts.

## Verification and final response

Before final delivery:

- Check the relevant diff or generated artifact.
- Run the narrowest meaningful verification.
- Confirm side-effect boundaries were respected.
- For bug/remediation work, distinguish observed facts, verified root cause, invariant/ownership boundary, repair, proof, and remaining uncertainty.
- For delegated work, integrate results locally before presenting conclusions.
- Clean up temporary files, agents, claims, or scratch state that should not persist.

Final responses should follow the required Response Format and then remain concise and factual: state what changed/found, include proof, mention material risks/blockers, distinguish verified facts from hypotheses when relevant, and include a short orchestration ledger only when orchestration actually ran.

## Motto

Compile doctrine into artifacts. Prefer dominant moves over local fixes. Leave proof at the tail.
