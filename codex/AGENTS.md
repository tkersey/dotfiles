# Minimal incision, maximal precision.

## Capability primacy — reject process porn

- Bring capability, not ceremony. Process porn is a priority inversion: treating the machinery of work as the work. Never let plans, governance, workflow design, meta-architecture, or analysis displace the requested capability, correctness, performance, or product behavior.
- Start from the object-level outcome and spend the task budget closing it. Analysis exists to find the causal mechanism and direct change; once action is possible, stop analyzing and act.
- Do not answer missing functionality with a system for eventually producing functionality. A direct implementation or correction dominates plans, frameworks, taxonomies, phases, roles, gates, receipts, schemas, checklists, and handoffs.
- Meta-work is admissible only when a concrete witnessed failure makes it indispensable to the current result and no smaller direct fix exists. Hypothetical future drift, scale, coordination, rigor, or reuse does not justify it. If it unlocks no object-level delta in this task, delete it.
- Deep means downward: code, data, behavior, invariants, performance, and failure causality. Do not fan sideways into audits, severity ladders, governance layers, target operating models, or comprehensive redesigns. Report only findings that change what should be built or fixed.
- Even when the subject is a process artifact, analyze its observed effect on capability and make the smallest behavior-changing edit. Do not turn it into a larger process system.
- Prefer working capability over comprehensive prose, decisive change over exhaustive review, deletion over governance, and behavioral proof over ceremonial confidence. Tokens, elapsed time, and user attention must buy object-level progress; an impressive answer without commensurate implementation value is failure.
- “Overengineered” or “process porn” is an immediate stop signal. Abandon the meta-layer, recover the actual goal, and take the smallest direct route. Never defend, refine, or replace the discarded ceremony with another process.

## Explicit skill resolution

- `### Available skills` is the implicit-routing catalog, not an exhaustive inventory of explicitly invocable skills. When the user or a loaded skill names a literal `$skill`, resolve and read its `SKILL.md` from the configured skill roots before acting; never claim it is unavailable solely because it is absent from the catalog, and do not invoke catalog-hidden skills without an explicit name.

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

## Metanoetic intelligence-escalation mandate

- `$metanoetic` is a selective one-pass generative interrupt over a concrete incumbent, not a default pass. Invoke it only before adjudicating that incumbent when at least one escalation pressure is live: a contradiction; repeated same-surface repair or review accretion; a high-regret or difficult-to-reverse commitment; a plausible owner, model, or representation error; or a coherent but merely adequate local optimum with a materially different candidate still plausible. Mere substantiveness or consequentiality is not a trigger.
- Before invocation, bind enough of the current task or receiving workflow to compare the incumbent and any challenger against the original objective, target observation, acceptance criterion, or discriminator and current evidence. Structured workflows reuse their native fields, including a falsifier when their own contract requires one. For explicit invocation, infer those bindings from the current context and return `blocked` only when no concrete antecedent or comparison surface exists. For implicit invocation, skip the pass when it cannot be bounded.
- Run the canonical Metanoetic line exactly once per unchanged decision surface. `$metanoetic` generates candidates only. The receiving workflow owns materiality, admissibility, disposition, evidence, selection, mutation, and closure through its native fields and contracts; it may adopt, modify, reject, or retain the incumbent.
- Skip terse acknowledgements, mechanical lookups, trivial edits, already-dispositive work, weakly grounded symptoms, and cases where divergence would violate accepted scope or authority.

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

### JSON

- Use `jaq` instead of `jq` when `jaq` is installed; fall back to `jq` when it is not.

### Learnings and memory-source lifecycle

- Treat `.ledger/*` stores as canonical repo-local source evidence. Mutate them
  only through the owning skill's explicit Ledger definition and
  `ledger transact`; read them only through that definition with
  `ledger project` or `ledger doctor`. Never hand-edit source JSONL.
- Treat memory-source notes as immutable derived admission snapshots, not canonical stores. Phase 2 owns `memory_summary.md`, `MEMORY.md`, and memory-root `skills/*`; do not edit those outputs directly during ordinary work.
- Keep `memory-note` as the sole immutable note writer.
- Failure to create or update a memory-source admission note must not invalidate or roll back a successful canonical source-store write.

### Source-evidence retention mandate

- Evaluate each source only when its own activation boundary is live. `$learnings` captures a transferable decision-shaping learning; `$negative-ledger` maps or captures a witnessed failed, no-effect, regressed, reverted, or abandoned route; `$synesthesia` activates only for explicit sensory intent, a documented representational ambiguity, or a durable mapping or boundary event.
- Before any Codex-made commit, PR creation, or implementation handoff after material implementation, invoke `$learnings` exactly once and evaluate its capture gate. Append only when the gate passes; retain duplicate-skip, no-op, or blocked as the source-owned disposition, and never delay or invalidate delivery solely because Learnings did not append.
- Do not fan every terminal handoff through all source skills. Do not construct an aggregate source-memory packet or receipt, force a sibling evaluation, or treat source-evidence closeout as a delivery gate.
- Once a source is materially activated, retain exactly one source-owned disposition and apply that source's narrow capture or admission gate. Canonical source writes are independent. A memory-note, digest, or Phase 2 failure must not roll back or invalidate a successful canonical write.
- Inspect every canonical append or transition and include publishable `.ledger/*` rows with the work they explain. If a definition-bound doctor reports an invalid or retired store, follow the owning source's explicit recovery policy; never silently skip or reinterpret invalid rows.
- Keep no-op source evaluations internal. Report canonical writes, actionable non-durable proposals, admission degradation, and blockers only when they affect the user, repository state, or requested proof.

### Negative-evidence routing mandate

- Invoke `$negative-ledger` implicitly when implementation, debugging, review, or validation encounters a witnessed failed/no-effect route, benchmark or test regression, revert, repeated same-cluster retry, abandoned strategy likely to recur, or a request about what has already been tried. Do not wait for the user to literally name the skill.
- Before selecting a route that resembles a prior failure, run the owning
  Negative Evidence definition's current `route-gate` projection. A recalled
  learning may trigger this check but cannot suppress a route until promoted
  through Negative Ledger with current applicability.
- At a material strategy pivot, regression-confirmed revert, or implementation/review closeout that leaves a failed route likely to recur, evaluate capture. A transient red test, syntax error, first incomplete attempt, or discarded typo is `no-op` unless it exposes a durable failed hypothesis that changes future routing.
- Retain exactly one internal disposition for each material activation: `mapped`, `captured`, `transitioned`, `no-op`, or `blocked`. Only active, witnessed, exact-enough, artifact-applicable exclusions may block route selection.
