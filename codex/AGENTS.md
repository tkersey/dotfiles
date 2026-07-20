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

### Language-surface pass

- Run `$logophile` as a final language-only pass on every non-trivial root response and human-facing artifact. Preserve facts, modality, uncertainty, scope, ownership, sequence, identifiers, code, paths, flags, schemas, protocol literals, and operational decisions; skip terse acknowledgements or status updates and machine-consumed surfaces.

## Universalist boundary mandate

- Invoke `$universalist` whenever implementation, refactoring, review, migration, or resolution considers a code boundary.
- A boundary is considered when work creates, changes, preserves, validates, migrates, bypasses, removes, or resolves how values, effects, state, evidence, authority, or observable behavior cross modules/packages/APIs, public/internal contracts, DTOs/schemas/codecs, parsers/validators, storage/wire formats, syntax/interpreters/compilers, pure/effect handlers, state machines/protocols, plugins/tools/CLIs, processes, repositories, or deployment surfaces.
- This mandate applies during ordinary feature implementation and PR/review resolution, including `$resolve`.
- Activation is mandatory; escalation is proportional. If the existing boundary is already exact, record the preserved boundary, law, and falsifier, then continue the normal workflow without inventing a new abstraction.
- Universalist team/subagent mode remains explicit-request only.

## Tooling standards

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not stage unrelated diffs.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for session-owned `.ledger/*` changes; if publishable, stage the current-turn/session-owned rows before committing.
- Review the diff before final response or commit.

### Python

- Use `uv` for Python package/project operations. Do not use direct `python`, `pip`, `pipx`, `venv`, `virtualenv`, `poetry`, or `conda` unless the user explicitly asks or the repo requires it.
- Run scripts, tests, linters, and CLIs through `uv run ...`.
- For skill-only external dependencies, prefer `uvx TOOL` or `uv run --with PACKAGE COMMAND ...` so dependencies remain ephemeral and non-project-scoped.
- Do not create or reuse `.venv*` for skill-only tooling. Do not `uv pip install` external packages for skills unless the user explicitly requests a persistent dependency.
- For projects that intentionally manage Python dependencies, keep `pyproject.toml`/`uv.lock` authoritative with `uv sync` or `uv lock` plus `uv sync`.

### Learnings and memory-source lifecycle

- Treat `.ledger/*` stores as canonical repo-local source evidence. Mutate them only through their owning skills or CLIs; never hand-edit source JSONL.
- Treat memory-source notes as immutable derived admission snapshots, not canonical stores. Phase 2 owns `memory_summary.md`, `MEMORY.md`, and memory-root `skills/*`; do not edit those outputs directly during ordinary work.
- Treat legacy `.learnings.jsonl` as migration input only; never append new rows after migration.
- Failure to create or update a memory-source admission note must not invalidate or roll back a successful canonical source-store write.

### Source-memory checkpoint mandate

- After a terminal `complete` or `ready-to-ship` closure decision, complete the delivery handoff or report and only then run the source-memory checkpoint: `closure -> handoff/report -> source-memory evaluation`. Source-memory evaluation is not a prerequisite for and must not delay code closure, a Codex-made commit, or a PR handoff. Complete `$ledger ensure` once for the workflow, construct one freshness-bound `source-memory-checkpoint-input/v1` packet, and evaluate Learnings, Synesthesia, and Negative Ledger even when the user did not name them.
- Require exactly one source-owned disposition from each participant: Learnings `appended|duplicate-skip|no-op|blocked`; Synesthesia `appended|candidate|no-op|blocked`; Negative Ledger `mapped|captured|transitioned|no-op|blocked`. A participant invoked with `checkpoint_context=source-memory-checkpoint/v1` evaluates only its own contract and must not invoke the coordinator or a sibling participant.
- Preserve source authority and conditional effects. Do not force low-value canonical rows or memory admission. Record canonical and admission outcomes separately; an admission or digest failure after a canonical write makes the checkpoint `degraded` and must not roll back that write or the established delivery closure.
- Retain one current `source-memory-checkpoint/v1` receipt and validate it with `ledger validate source-memory-checkpoint`. A later material code, evidence, route, or authority change invalidates the prior checkpoint; re-establish closure and complete the resulting handoff or report before reevaluating. Missing participants, stale/invalid evidence, or required canonical failures make source-memory closeout `blocked`, but source-memory status cannot gate, delay, invalidate, or roll back delivery. Only the separate current exact Negative Ledger pre-route gate may block a selected route before execution.
- Inspect every canonical append or transition and include publishable `.ledger/*` rows with the work they explain. If Learnings doctor reports `legacy-only` or `invalid`, follow `$learnings` migration policy; never silently discard invalid legacy records, and preserve/report every explicitly skipped legacy span.
- Keep ordinary all-no-op checkpoints internal. Report canonical writes, actionable Synesthesia candidates, admission degradation, and blockers.

### Negative-evidence routing mandate

- Invoke `$negative-ledger` implicitly when implementation, debugging, review, or validation encounters a witnessed failed/no-effect route, benchmark or test regression, revert, repeated same-cluster retry, abandoned strategy likely to recur, or a request about what has already been tried. Do not wait for the user to literally name the skill.
- Before selecting a route that resembles a prior failure, query or map the current repo-local ledger. A recalled learning may trigger this check but cannot suppress a route until promoted through Negative Ledger with current applicability.
- At a material strategy pivot, regression-confirmed revert, or implementation/review closeout that leaves a failed route likely to recur, evaluate capture. A transient red test, syntax error, first incomplete attempt, or discarded typo is `no-op` unless it exposes a durable failed hypothesis that changes future routing.
- Retain exactly one internal disposition for each material activation: `mapped`, `captured`, `transitioned`, `no-op`, or `blocked`. Only active, witnessed, exact-enough, artifact-applicable exclusions may block route selection.
