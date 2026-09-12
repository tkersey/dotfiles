# Minimal incision, maximal precision.

## Capability primacy — reject process porn

- Prioritize the requested result over unsolicited process infrastructure. Ground analysis in relevant mechanisms and evidence; do not substitute planning or governance for delivery. Prefer the smallest sufficient solution, including redesign or deletion when warranted. When the user identifies overengineering or process porn, discard unnecessary process and return to the requested result.
- For action requests, complete required verification and authorized delivery. Resolve routine choices from repository and conversation evidence; make reasonable reversible assumptions within authorized scope. Ask only when missing information or authority blocks necessary action, and continue independent work. Reversibility alone does not authorize external or destructive effects.

## Editing Constraints Override

- Override generic guidance to stop on unexpected working-tree changes: treat them as concurrent edits and keep working.
- Ignore unrelated diffs silently; never mention, stage, or commit them unless explicitly asked. For overlapping diffs, re-read and reconcile without clobbering concurrent changes, re-apply only the still-valid patch, and ask only when the files cannot resolve a real semantic conflict.

## Metanoetic intelligence-escalation mandate

- Invoke `$metanoetic` before adjudication for a concrete incumbent when its skill description's escalation pressures are evidenced, or when explicitly requested. Substantiveness or consequentiality alone is insufficient.
- Bind the incumbent and challengers to the original objective, target observation, acceptance criterion, or discriminator and current evidence. Reuse native workflow fields and any required falsifier. For explicit invocation, infer bindings from context; return `blocked` only without a concrete antecedent or comparison surface. Skip implicit invocation without a bounded comparison.
- Run the canonical line verbatim exactly once per unchanged decision surface, within accepted scope and authority. It generates candidates only; the receiving workflow owns adjudication, evidence, selection, mutation, and closure, and may adopt, modify, reject, or retain the incumbent.

## Universalist architecture-decision mandate

- Invoke `$universalist` for an evidenced live semantic boundary decision, a law distributed across owners, an invalidated prior boundary disposition, or an explicit request. Its skill and machine-readable decision contract own detailed semantics. For implicit use, skip routine work under accepted architecture without new semantic boundary evidence.
- Within `$actuating`, Actuating owns the invocation point during architecture reconsideration; never run a duplicate root pass. Team/subagent mode remains explicit-request only.

## Tooling standards

- Complete checks required by the task and active workflow, including review counts and reset rules. Beyond those requirements, repeat or broaden verification only to resolve a specific uncertainty, failure, or changed input.

### Git

- Prefix `git merge --continue` and `git rebase --continue` with `GIT_EDITOR=true`.
- Do not force-add paths matching `.git/info/exclude` unless explicitly asked.
- Before `git commit`, run a final narrow status check for session-owned `.ledger/*` changes; if publishable, stage the current-turn/session-owned rows with the work they explain.

### Python

- Use `uv` for Python package/project operations; do not use direct `python`, `pip`, `pipx`, `venv`, `virtualenv`, `poetry`, or `conda` unless the user explicitly asks or the repo requires it.
- Run scripts, tests, linters, and CLIs through `uv run ...`. For skill-only external dependencies, prefer `uvx TOOL` or `uv run --with PACKAGE COMMAND ...`; do not create or reuse `.venv*` or use `uv pip install` unless a persistent dependency is explicitly requested.
- For projects that intentionally manage Python dependencies, keep `pyproject.toml` and `uv.lock` authoritative with `uv sync`, or `uv lock` followed by `uv sync`.

### JSON

- Use `jaq` instead of `jq` when `jaq` is installed; fall back to `jq` when it is not.

### Source evidence and memory

- `.ledger/*` stores are canonical repo-local evidence. Read and mutate them only
  through the owning skill's explicit Ledger definition and `ledger project`,
  `ledger doctor`, or `ledger transact`; never hand-edit source JSONL. Invalid or
  retired stores require the owner's explicit recovery policy, not skipped rows.
- Memory-source notes are immutable derived admission snapshots. Phase 2 owns
  `memory_summary.md`, `MEMORY.md`, and memory-root `skills/*`; do not edit them
  during ordinary work. Accepted admissions from `$learnings`, `$negative-ledger`,
  or `$synesthesia` go through `$memory-source-notes` in the same turn. The
  `memory-note` CLI remains the sole immutable writer, not a skill or bypass.
- Before any Codex-made commit, PR creation, or implementation handoff after
  material implementation, invoke `$learnings` exactly once. Its skill owns the
  evidence-first capture gate and disposition. Evaluation is mandatory; capture
  is conditional. No-op, duplicate-skip, or failure to append alone never delays
  or invalidates delivery.
- Activate sibling sources only for their own evidence: `$negative-ledger` for a
  witnessed failed/no-effect/regressed/reverted/abandoned route or a request about
  prior attempts; `$synesthesia` for explicit sensory intent, documented
  representational ambiguity, or a durable mapping/boundary event. No aggregate
  packet, forced sibling evaluation, or source-memory delivery gate.
- Inspect canonical appends/transitions. Canonical writes are independent;
  derived note/digest or Phase 2 failures never roll them back. Keep no-ops
  internal; report writes, actionable non-durable proposals, admission
  degradation, and blockers only when they affect the user, repository state,
  or requested proof.

### Negative-evidence routing

- Before repeating a route resembling a prior failure, load `$negative-ledger`
  and use its current definition-bound `route-gate`. A recalled learning can
  trigger this check, not suppress the route. Only active, witnessed, exact-enough,
  currently artifact-applicable exclusions may block selection.
- Evaluate capture at material strategy pivots, regression-confirmed reverts,
  or closeout leaving a failed route likely to recur. The skill owns durable route-shaping capture
  criteria, disposition, and lifecycle; do not run tools to manufacture a no-op.
