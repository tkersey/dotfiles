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
- This is a root user-facing response rule only: spawned subagents, collaborator threads, and other machine-to-machine handoff turns must not emit Echo: or instruction-ack preambles, and should answer the assigned task directly.
- Do not include `Echo:` inside generated files, patches, code blocks, JSON/YAML/TOML intended for machine consumption, email bodies, PR bodies, commit messages, or artifacts the user asked to copy verbatim. Put Echo only in the surrounding chat response.

## Hylo Actuating Governance

`$actuating` is the explicit user-facing workflow. For material actuation it must not operate as a hidden loop.

Governing law:

```text
No hidden loop.
No material mutation without unfold.
No continuation without fold.
No completion without terminal algebra.
```

Routing:

```text
$actuating
  -> $spec-pipeline in gate-only/no-plan mode when the implementation spec is not already accepted
  -> $recursion-scheme-planner when recursive topology is nontrivial
  -> $agent-loop-schemes for ALSR-v1/HYL-v1 when material loop governance is required
  -> $goal-actuating to interpret HYL-v1 and emit HSR-v1
  -> ATCG-v1 terminal closure
  -> $proof-patch or explicit $ship handoff
```

`$recursion-scheme-planner` and `$agent-loop-schemes` are explicit-only at root. They may run by documented handoff from `$actuating` or `$goal-actuating`.

Material `$actuating` runs must establish one of these before first material mutation:

```text
direct_action fused exemption
current ALSR-v1 + HYL-v1
$st owns the work with current control receipt
```

If none exists, stop with:

```text
actuation verdict: blocked-loop-contract-missing
```

If ALSR/HYL is stale against branch/head/diff, stop with:

```text
actuation verdict: blocked-loop-contract-stale
```

Review loops default to resolve-and-fix unless the user explicitly requests no implementation:

```text
$cas review
  -> $review-fold
  -> optional review-class-fanout
  -> resolve pass
  -> optional branch-race
  -> $goal-grind only for accepted code-change liabilities
  -> optional patch-fanout only for disjoint accepted liabilities
  -> $evidence-fold
  -> 3 clean normalized $cas review runs
  -> $proof-patch
  -> ATCG-v1
```

Subagent parallelism must be bounded by the work graph / HYL frontier. The lead owns goal scope, review resolution, integration, CAS clean-run counting, proof closure, and `$ship` handoff. Subagents may not update PRs, resolve threads, broaden scope, or declare completion.

`$ship` remains the owner of PR creation, update, promotion, publication, and other public delivery state.

Do not post PR comments, resolve threads, update public trackers, create PRs, update PR bodies, or publish delivery artifacts without explicit user intent or a terminal `$ship` handoff whose side-effect boundary permits that action.

## Skill routing

Root-level implicit activation is intentionally narrow.

Implicit skills:

```text
$goal-actuating
$goal-contract
$goal-workgraph
$goal-grind
$evidence-fold
$review-fold
$failure-memory
$proof-patch
$grill-me
$seq
$learnings
```

Every other skill is explicit-only at root unless an already-active skill's documented workflow hands off to it. Explicit-only includes, but is not limited to:

```text
$actuating
$recursion-scheme-planner
$agent-loop-schemes
$cas
$review-adjudication
$codebase-doctrine
$memory-source-notes
$negative-ledger
$synesthesia
$zig
$logophile
$universalist
$spec-pipeline
$plan
$st
$fixed-point-driver
$ship
$land
$ms
$prove-it
```

A handoff does not create an independent root implicit trigger. `$cas` may be used as the review backend by an active workflow, but CAS control mutations still require clear intent. `$ship` may be used by an active workflow for PR publication/update only when publication intent is explicit or inherited from an accepted spec/handoff.

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

Use the canonical source-memory stores under `.ledger/` for custom repo-local memory. The owning skills own CLI syntax, payload semantics, admission gates, and note-writing mechanics.

Root policy:

- Treat `$learnings` as implicitly in scope for substantial implementation, fixes, refactors, debugging, tests, validation transitions, commit/PR/handoff closeout, wrap-up, repeated failures, strategy pivots, footgun discoveries, acceleration patterns, and durable user corrections when a canonical or legacy learning store may exist.
- Do not wait for the user to literally say `$learnings` when prior repo-local learning could change route selection, verification order, migration handling, tool choice, or closeout obligations.
- Whenever `$learnings` is implicitly in scope for recall, capture, commit closeout, PR handoff, or wrap-up, evaluate `$synesthesia` too with `ledger --source synesthesia`; append only when the Synesthesia durable mapping or activation-boundary gate passes. If no durable authority exists but the turn exposes a reusable sensory phrase, activation boundary, or representational ambiguity with an engineering translation, treat it as a non-durable candidate for routing; otherwise keep the no-op internal.
- Keep source-memory bookkeeping out of normal final replies. Do not add trailing `learnings: ...`, `duplicate-skip: ...`, `0 records appended: ...`, `synesthesia: candidate: ...`, or `synesthesia: 0 records appended: ...` report lines just to prove the lifecycle ran. Surface learning/synesthesia outcomes only when they changed repo-visible state, need user action, explain a blocker/error, or the user explicitly asks.
- Recall before substantial implementation when relevant canonical or legacy learning stores exist. Use focused task, failure-surface, tool, path, and error-class terms; pass path hints when known; prefer `--drop-superseded`. Treat recall as input to current artifact inspection, not a replacement for it.
- Capture only decision-shaping evidence: validation transitions, strategy pivots, footgun discoveries, acceleration patterns, useful or failed recalled lessons, repeated failures, durable user corrections, and delivery after real implementation work.
- If a recalled learning looks like failed-hypothesis or route-exclusion evidence, do not block directly from the learning row. Verify current applicability and promote through Negative Ledger (`ledger capture`, then `ledger export`) when it qualifies.
- Before the first learning append in a repo, or before commit closeout when learning capture is warranted, run `ledger doctor --source learnings`. If it reports `legacy-only`, run `ledger migrate --source learnings --dry-run --mode copy` and `ledger migrate --source learnings --mode copy` before appending.
- Before the first Synesthesia append in a repo, run `ledger doctor --source synesthesia`; if it reports `notes-only`, migrate only when an explicit copy import is intended, and never treat ordinary metaphorical prose as a durable event.
- Before any Codex-made commit, check session-owned changes in `.ledger/learnings/events.jsonl`, `.ledger/negative-ledger/events.jsonl`, `.ledger/synesthesia/events.jsonl`, and `.ledger/harness/events.jsonl` alongside the intended commit scope.
- If a source-memory store is dirty and publishable, stage current-turn/session-owned rows by default; if it is local-only by `.git/info/exclude`, leave it unstaged unless explicitly asked.
- Legacy `.learnings.jsonl` is migration input only after migration; do not append new rows there.
- `memory-note` is the safe writer for custom memory-source admission snapshots. Do not hand-write custom source notes as a fallback.
- A missing `memory-note` CLI must not block canonical `.ledger` capture. Complete the source-store write first, then report the missing admission step.
- Phase 2 compiled memory outputs are not ordinary edit targets.

Synesthesia routing:

- Treat `$synesthesia` as implicitly in scope when the user asks what software feels, sounds, looks, moves, weighs, or resembles; asks for compare-by-feel analysis; literal analysis leaves multiple plausible structural, temporal, interaction, or boundary interpretations that a reversible sensory model could distinguish; an owning workflow documents such an ambiguity; or the user asks to reuse, correct, reject, retract, or remember an established sensory mapping.
- Do not wait for the user to literally say `$synesthesia` when a concrete representational ambiguity could change diagnosis, explanation, route selection, or lifecycle obligations. Do not activate it merely because work concerns architecture, performance, readability, maintainability, flaky behavior, onboarding, API/UX quality, refactoring, or a strange bug; those domains keep their technical owners unless the sensory lens itself distinguishes alternatives.
- Activation boundary: use `$synesthesia` for explicit sensory requests or when literal analysis leaves multiple plausible structural, temporal, interaction, or boundary interpretations and a reversible sensory model could distinguish them. Non-activation boundary: do not use it for routine architecture, performance, readability, flaky or strange-bug, UX, or refactor work unless the sensory lens itself changes diagnosis, explanation, route selection, or lifecycle obligations. Verification: every activation must name the explicit sensory request or the concrete representational ambiguity it is expected to distinguish.
- Start from literal evidence, separate observations from hypotheses, choose the minimum sufficient modality, and translate every material sensory statement into concrete engineering meaning with uncertainty, a falsifier, and a next move.
- Whenever `$synesthesia` is evaluated from the `$learnings` lifecycle, source-memory closeout, or a durable mapping/boundary request, run the candidate pass: append a durable row when explicit or repeated accepted authority exists; keep non-durable candidates and no-op outcomes out of normal final replies unless they need user action, explain a blocker/error, or the user explicitly asks.
- Before the first Synesthesia append in a repo, run `ledger doctor --source synesthesia`; if it reports `notes-only`, migrate only when an explicit copy import is intended. Do not treat `notes-only` as the substantive reason for zero capture, and do not infer durable authority from assistant-authored novelty or ordinary metaphorical prose.
- For an explicit durable mapping or boundary, append the canonical `.ledger/synesthesia/events.jsonl` row first with `ledger capture --source synesthesia --kind <kind> --json -`; when global admission is warranted, hand off to `$memory-source-notes` in the same turn.
- The generated current-state digest refreshes automatically after a successful append; digest failure does not roll back the canonical row.
