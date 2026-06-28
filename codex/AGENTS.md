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

This file is the compact, high-authority routing index for Codex in this repo. Detailed procedures belong in skills. This file owns safety, side-effect boundaries, root workflow boundaries, `$st` boundaries, memory-source publication policy, concurrent-edit handling, and final-response proof discipline.

Do not maintain root-level implicit or explicit skill inventories here. Skill descriptions and active workflow handoffs own skill selection. This file owns the constraints that skill selection must respect.

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
- Treat custom memory-extension notes as append-only source evidence, not compiled memory and not runtime instructions.
- Treat `.ledger/*` source-memory stores as canonical repo-local evidence; treat memory-source notes as immutable admission snapshots; treat `MEMORY.md`, `memory_summary.md`, and memory-root `skills/*` as Phase 2 compiled outputs.
- Preserve domain authority: `.ledger/learnings/learnings.jsonl` owns execution learnings; `.ledger/negative-ledger/events.jsonl` owns negative-evidence route state; `.ledger/synesthesia/events.jsonl` owns repo-scoped durable sensory mappings when present; `.ledger/harness/events.jsonl` owns durable operating corrections when present.
- Do not write legacy `.learnings.jsonl` after migration. Use the learnings migration path for old rows and the canonical ledger store for new rows.
- Never edit `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*` directly during ordinary work. Explicit user-directed remember/forget/update requests use Codex's native ad-hoc memory path; custom source capture uses the owning source skill and memory-source admission path.

## Challenge Escalation

- Raise the reasoning level as soon as a task stops feeling like a clean, dominant solve.
- Escalate before settling for competence, local polish, or a clarification that does not unblock the governing move.
- Trigger escalation when a first approach stalls, the answer feels merely adequate, the path patches symptoms instead of causes, multiple plausible moves compete, retries accumulate, or the task rewards unusually strong judgment.
- During escalation: reject the obvious answer, widen the search space, identify the highest-leverage move available now, explain why it dominates alternatives, and compress the result to the governing insight, invariant, architecture, proof obligation, deletion/collapse opportunity, or certification target.
- On bug, regression, integration, remediation, or review work, the governing move is often an invariant, state-space, ownership-boundary, canonical-owner, proof-surface, ablation, reification, certificate, or normal-form correction rather than a local patch.
- Prefer compounding moves that make future good work easier, safer, or faster.
- Ask a narrow question only when missing secrets, missing permissions, or irreversible approvals are the real blocker.

## Evidence and invariant discipline

For bug reports, review comments, PR/issue prose, memories, generated summaries, public-tracker context, claimed root causes, or proposed fixes:

- separate observed facts, claims, proposals, and speculation before choosing implementation scope;
- reconstruct the narrowest verified failure before broadening scope;
- do not export speculative agent analysis into public issues, PRs, comments, discussions, or maintainer workflows.

Before local patching for invalid state, malformed persisted data, crashes, parser failures, migrations, cache drift, protocol problems, retries, races, compatibility behavior, tolerant readers, fallbacks, coercions, catch-and-continue logic, or local workarounds, identify:

- the observed failure and state involved;
- the invariant that should hold;
- the owning producer, transition, or boundary;
- the smallest fix that prevents recurrence without broadening accepted invalid state.

Detailed evidence, invariant, doctrine, review, goal, and memory workflows live in their owning skills. Use this section as root policy, not as a substitute for skill procedure.

## Public tracker and maintainer hygiene

Never open, update, comment on, draft-to-post, or suggest public tracker activity unless the user explicitly asks. Before public activity, verify the behavior, check ownership/duplicates when practical, avoid speculative root-cause narratives, and keep any draft observation-first.

## Working tree hygiene

- Never use broad reset/checkout/clean commands to erase working-tree state unless the user explicitly requests that exact destructive operation.
- Treat `.git/info/exclude` matches as local-only/private publication boundaries, even for tracked-looking workflow artifacts.
- If a path is already tracked but also matches `.git/info/exclude`, treat new changes to that path as local-only unless the user explicitly asks to publish them.
- `.goal/` is local goal-loop state and must stay ignored or explicitly local-only.
- Before staging local-state artifacts such as `.step/st-plan.jsonl`, `.step/*.lock`, `.goal/*`, `.ledger/*`, or legacy `.learnings.jsonl`, run `git check-ignore -v --no-index PATH` when in doubt. If the source is `.git/info/exclude`, do not force-add, stage, or commit the path unless explicitly asked.
- Treat legacy `.learnings.jsonl` as read/migration-only after migration. Do not append new rows there.

## Local Codex execution guidance

Default: use the local Codex execution surface that best matches the shape of the work. Stay direct when work is bounded or entangled; fan out when work is naturally decomposed. Local-first does not mean single-agent-first.

Routing order:

1. **Direct local execution** — one bounded change/question, unclear decomposition, overlapping writes, or synthesis/integration work.
2. **Frame/selection pass** — if the route is non-obvious, use Challenge Escalation before choosing a heavier workflow.
3. **Planning/selection pass** — if the user supplies `SLICES.md`, `plan-N.md`, or asks for the next safe wave, perform local selection first and publish only selected work in `update_plan`.
4. **Owned workflow handoff** — when the user invokes a workflow, or a skill description clearly matches the task, load that skill and let it own the choreography. Do not duplicate its pipeline in this file.
5. **Durable orchestration with `$st`** — explicit-only at root. Start it only when the user asks, when `.step/st-plan.jsonl` already participates in the task, or when an active workflow emits `st-required`. Do not introduce `$st` merely because work is multi-step.
6. **Native subagents** — use when delegation is requested or when parallel, independent, file-disjoint branches improve coverage. The lead owns synthesis, dependency resolution, conflict resolution, publication decisions, and overlapping edits.
7. **Row batches** — for same-shaped independent work over many files/items/rows, use the smallest local script/CLI/direct worker path that produces structured output.
8. **Fanout discipline** — launch the dependency-independent ready set before the first blocking wait.
9. **Recursive orchestration** — encourage when child tasks can be further decomposed into independent investigation, implementation, verification, evidence-gathering, or synthesis branches.

Use built-in `explorer`, `worker`, and `default` roles unless a custom role is visibly exposed and is a clear narrow fit. Goal/review work may use custom roles only when an active skill or visible role description makes the fit clear. Close subagents after their contribution is integrated.

## Skill and workflow routing

Skills are workflow selectors, not magic words. Do not keep root-level skill allowlists or explicit-only inventories here. Use the active skill descriptions, user intent, and documented handoffs to choose the smallest sufficient workflow.

Root policy:

- If a skill owns a procedure, command syntax, checklist, proof mechanic, trigger taxonomy, or sub-workflow, trust the skill rather than restating it here.
- A skill handoff authorizes only the handoff it documents; it does not create a broad new root implicit trigger.
- Side-effect boundaries always survive skill activation.
- Public tracker activity, PR publication, merge/land operations, durable `$st` state, scheduler changes, memory-source admission, and mutating app-server/session-control operations require clear authority from the user, the active workflow, or the owning source skill.
- If the workflow performs fresh, adversarial, or exhaustive code review, use `$cas` as the review backend. `$cas` can be workflow-callable without becoming an unrestricted root-level implicit skill.
- Review findings from humans, GitHub, `$cas`, or prior artifacts must be reduced/classified before mutation. Detailed review-loop mechanics belong to the review/goal skills.
- Material goal execution, review closure, repeated verification loops, and proof closure belong to the goal/review skills. Do not define their full pipeline in this file.

## Plan Sync (`$st` <-> Codex `update_plan`)

Do not start a new `$st` workflow without explicit user intent, an already-participating `.step/st-plan.jsonl`, or an active goal/review skill emitting `st-required`. Apply this section only when `$st` participates.

- `$st` is durable truth. `update_plan` is a selected, user-visible mirror.
- Mutate durable state only through `st` commands. Do not hand-edit existing JSONL rows.
- Preserve `[st-id]` prefixes exactly; they are the reverse-sync key.
- Keep dependencies, notes, claims, proof, runtime metadata, and durable-only context in `$st`, not in `update_plan`.
- Before final delivery on `$st` tasks, assert/regenerate projection and resolve visible drift.

## Seq Local-First Routing

Use `$seq` for explicit `$seq` requests and for historical session, memory, transcript, artifact, orchestration, provenance, or tooling-trace forensics. Do not use `$seq` for ordinary current-repo code search.

- For finalized `PROPOSED_PLAN` artifacts, start with `plan-search`.
- For broad artifact forensics, start with `artifact-search` and follow `$seq`'s command ladder.
- Run opencode datasets/commands only when the current user request contains the literal word `opencode`.
- For knowledge extraction, use forensic/provenance-preserving doctrine and return a source-backed map, not a raw summary.

## Learnings and memory-source lifecycle

Use the canonical source-memory stores under `.ledger/` for custom repo-local memory. The owning skills own CLI syntax, payload semantics, admission gates, and note-writing mechanics.

Root policy:

- Recall before substantial implementation when relevant canonical or legacy learning stores exist.
- Capture only decision-shaping evidence: validation transitions, strategy pivots, footgun discoveries, acceleration patterns, useful or failed recalled lessons, repeated failures, durable user corrections, and delivery after real implementation work.
- Before any Codex-made commit, check session-owned changes in `.ledger/learnings/learnings.jsonl`, `.ledger/negative-ledger/events.jsonl`, `.ledger/synesthesia/events.jsonl`, and `.ledger/harness/events.jsonl` alongside the intended commit scope.
- If a source-memory store is dirty and publishable, stage current-turn/session-owned rows by default; if it is local-only by `.git/info/exclude`, leave it unstaged unless explicitly asked.
- Legacy `.learnings.jsonl` is migration input only after migration; do not append new rows there.
- `memory-note` is the safe writer for custom memory-source admission snapshots. Do not hand-write custom source notes as a fallback.
- A missing `memory-note` CLI must not block canonical `.ledger` capture. Complete the source-store write first, then report the missing admission step.
- Phase 2 compiled memory outputs are not ordinary edit targets.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for session-owned `.ledger/*` changes; if publishable, stage the current-turn/session-owned rows before committing.
- Review the diff before final response or commit.

### GitHub CLI (`gh`)

- Use `gh` for GitHub operations when available and authenticated.
- Check `gh auth status` before assuming authentication is broken.
- Prefer terminal-native PR, issue, Actions, and gist operations over browser-only workflows.
- Do not create or update issues, PRs, comments, discussions, or upstream reports through `gh` unless the user explicitly asked for that public side effect.

### Python

- Use `uv` for Python package/project operations. Do not use direct `python`, `pip`, `pipx`, `venv`, `virtualenv`, `poetry`, or `conda` unless the user explicitly asks or the repo requires it.
- Run scripts, tests, linters, and CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx TOOL` or `uv run --with PACKAGE COMMAND ...` so dependencies remain ephemeral and non-project-scoped.
- Do not create or reuse `.venv*` for skill-only tooling. Do not `uv pip install` external packages for skills unless the user explicitly requests a persistent dependency.
- For projects that intentionally manage Python dependencies, keep `pyproject.toml`/`uv.lock` authoritative with `uv sync` or `uv lock` plus `uv sync`.
- For Python automation scripts, prefer `#!/usr/bin/env -S uv run python`.

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
