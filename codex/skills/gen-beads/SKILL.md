---
name: gen-beads
description: Convert a project plan written in a Markdown file into a complete bd beads graph (tasks, subtasks, dependencies) using only bd for creation and edits, then review and optimize each bead. Use when asked to beadify a plan document (plan.md, plan-*.md, DESIGN/IMPLEMENTATION/ARCHITECTURE docs, or any planning markdown) or to generate bd tasks from a plan.
---

# Gen Beads

## Overview
Transform a markdown plan into a comprehensive bead graph with clear dependencies and rich, self-documenting comments. Optimize for parallel execution: prefer a DAG of independent workstreams with explicit join points, not a single linear chain.

## Inputs

- Path to the plan markdown file
- Any scope boundaries, sequencing constraints, or priority guidance
- Any workflow constraints (e.g. “no stacked PRs”, “close on merge”, “must be linear”, “use molecules”, etc.)

## Defaults (override if the user says otherwise)

- Parallel-first: maximize unblocked work (`bd ready` should surface multiple items whenever possible).
- Use `blocks` only for true prerequisites; use `tracks`/`related` for “nice to do first”.
- Close a bead when its PR is opened; stacked PRs are acceptable.
- Medium granularity: each bead should be independently PR-able.
- Add frequent checkpoint/integration beads (planned join points).
- Include a small metadata block in each bead comment:
  - `Workstream: <name>`
  - `Role: contract | implementation | integration | checkpoint`
  - `Parallelism impact: unlocks <n> beads` (best-effort)
- No agent routing labels; assignment stays manual.
- Use molecules only for repeatable checklists.

## Workflow

1. Locate and read the plan file. Ask for the exact file path if multiple candidates exist.
2. Extract major workstreams, tasks, risks, milestones, and implied dependencies.
3. Identify “contracts” that can decouple workstreams (API shapes, schemas, interfaces, CLI signatures, config formats).
4. If any dependency is ambiguous but would become a `blocks` edge, ask targeted questions before committing to it.
5. Generate beads using the "Generate Step Prompt" verbatim. Use only bd commands to create beads and add dependencies.
6. Evaluate every bead using the "Review Prompt" verbatim, revising beads via bd only.
7. Report what was created/updated and list any remaining ambiguities.

## Generate Step Prompt (use verbatim)

```
OK so please take ALL of that and elaborate on it more and then create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is totally self-contained and self-documenting (including relevant background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions and thought process and how it serves the over-arching goals of the project.)

Parallelization rules (critical):
- Build a DAG, not a single linear chain. If you find yourself making “each bead depends on the previous”, stop and re-structure into parallel workstreams.
- First, identify major workstreams (e.g. frontend/backend, data model/API, infra/CI, docs/migrations, etc.) and create an epic (or parent bead) per workstream.
- Create explicit “contract” beads (API/spec/schema/interface/config format decisions) so multiple workstreams can proceed in parallel.
- Add checkpoint/integration beads as join points that depend on multiple parallel beads, to force frequent feedback loops.

Dependency rules:
- Use `blocks` only when the dependent work truly cannot start without the prerequisite.
- If a dependency is uncertain and would become `blocks`, ask the human before adding it.
- For “recommended order”, “nice-to-have-first”, or “reduces rework”, prefer `tracks` or `related` over `blocks`.

PR + granularity assumptions:
- Each bead should be independently PR-able (medium granularity).
- Assume a bead is considered “done” when its PR is opened; stacked PRs are acceptable.
- Do not add agent routing labels; keep assignment manual.

For every bead, include clear acceptance criteria and at least one verification signal (test/build/lint command or a precise manual check).
Include a short metadata block in the bead comment:
- Workstream: <name>
- Role: contract | implementation | integration | checkpoint
- Parallelism impact: unlocks <n> beads (best-effort)

Example comment footer:
```
Workstream: Backend API
Role: contract
Parallelism impact: unlocks 3 beads
```

Example rationale line (optional, short):
```
Rationale: contract first to unblock 3 parallel implementations.
```

Use only the `bd` tool to create and modify the beads and add the dependencies.
```

## Review Prompt (use verbatim)

```
Check over each bead super carefully-- are you sure it makes sense? Is it optimal? Could we change anything to make the system work better for users? If so, revise the beads. It's a lot easier and faster to operate in "plan space" before we start implementing these things!

Also: audit the dependency graph for parallelism.
- If the graph is mostly linear, refactor it: split into workstreams, introduce contract beads, and reduce `blocks` edges.
- Ensure `blocks` is used only for true prerequisites; downgrade soft ordering to `tracks`/`related`.
- Ensure there are frequent checkpoint/integration join points.
- Ensure each bead is independently PR-able with clear acceptance + verification.
- Ensure each bead comment includes the Workstream/Role/Parallelism metadata block.
- Run `bd ready` after you’ve created the graph. If it only surfaces one item because the graph is unnecessarily linear, revise dependencies until parallel work is available (subject to true prerequisites).
```

## Guardrails

- Use only bd commands to create, modify, and wire dependencies; do not hand-edit bead files.
- Preserve plan intent. If the plan is inconsistent or missing critical details, ask targeted questions before deciding.
- Prefer parallelizable workstreams with explicit join points over a single long chain.
- Prefer small, composable beads with explicit prerequisites over monolithic tasks.
- Use molecules only for repeatable checklists (not as the default structure).

## Output Expectations

- A coherent bead graph with tasks, subtasks, and dependencies designed for parallel execution.
- A short summary of what was created/changed and any open questions.
