---
name: select
description: "Preflight bead work: verify beads are in use, confirm explicit start/continue, identify active bead or select next `bd ready`, clarify done criteria, and scope audit before marking `in_progress`."
---

# Select

## Overview
Run the preflight for bead-based work: ensure beads apply, pick or confirm the active bead, clarify what "done" means, and contain scope before implementation.

## Workflow
1. Confirm explicit invocation to start or continue bead work; if unclear, ask.
2. Check beads usage: run `rg --files -g '.beads/**' --hidden --no-ignore`.
   - If no paths, do not use `bd`; stop and ask for the correct workflow.
3. Check active bead: `bd in_progress`.
   - If exactly one, use it and skip selection.
   - If multiple, ask which to proceed.
4. If none active, select the next bead using the rubric below and mark `in_progress` (work bead + epic if applicable).
5. Restate "done" in 1-2 sentences from the bead description/acceptance criteria.
6. Clarify requirements until implementable; ask only judgment-call questions.
7. Audit working tree for scope containment (`git status -sb`, `git diff`); ignore unrelated diffs.

## Selection rubric
- Feature-first: if any ready items are `feature`, evaluate all ready features (`bd show`).
- Type order (fallback): `task` > `bug` > `epic` > `chore`.
- Epic rule: only mark an `epic` `in_progress` when you also mark a child bead `in_progress`.
- Priority: P0 > P1 > P2 > P3 > P4.
- Risk: migrations, auth/security, infra, data loss/consistency, breaking API/CLI, perf regressions, ambiguous acceptance.
- Hardness: vague scope, multiple subsystems, unknown deps, heavy verification.
- Blast radius: widely used modules, shared config, CI/build pipeline, core user paths.
- Parallelism impact (balance with risk): prefer beads that unlock more blocked work or establish a contract/checkpoint when risk is in the same tier.
- Soft deps: if a ready bead has `tracks`/`related` pointing to another ready bead, apply a soft penalty and prefer the tracked-first item.
- Tie-break: priority -> strongest signals -> earliest in `bd ready`.
- Workstream diversity: only as a final tie-break and only if it increases parallelism (never if it reduces ready work).
- Readiness gate: never start a bead if required scaffolding or prerequisites are missing; add deps and restart selection.

## Scoring notes (lightweight)
- Base score comes from the existing rubric (risk/hardness/blast/priority).
- Parallelism nudges (apply only within the same risk tier):
  - Role: contract/checkpoint +2; integration +1; implementation +0.
  - Unlock count: +1 per blocked bead unlocked (cap at +3).
  - Soft deps: -2 if it tracks/relates another ready bead; 0 otherwise.
- Unlock count: count outgoing `blocks` edges to non-ready beads.

Example rationale comment:
```
Selected first: contract bead in Backend API; unlocks 2 blocked items; lower risk tie with feature P1.
```

## Selection workflow
1. Run `bd ready` and keep the returned order.
2. If any ready features exist, `bd show <id>` for each and score (risk/hardness/blast/parallelism).
3. Otherwise, `bd show <id>` for each ready item and score by type order, priority, and parallelism.
4. Extract from each bead comment (if present):
   - `Workstream`
   - `Role` (contract/integration/checkpoint/implementation)
   - `Parallelism impact` (unlock count)
5. Weigh `tracks`/`related` edges: if a ready bead tracks/relates another ready bead, apply a soft penalty and prefer the tracked-first item.
6. Check readiness for the top candidate (repo-only):
   - Confirm required scaffolding/infra exists in the repo (app skeleton, build config, migrations, auth setup, etc.).
   - If something is missing, look for an existing prerequisite bead and link it first:
     - Link: `bd dep add <candidate-id> <dep-id> -t blocks`
   - Only create a new prerequisite bead if none exists:
     - Create: `bd create "Scaffold: <thing>" --type=task --priority=<p>`
     - Link: `bd dep add <candidate-id> <dep-id> -t blocks`
   - Re-run `bd ready` and restart selection if you added any deps.
7. Pick the highest-scored ready bead after the readiness gate passes.
8. If the pick is an `epic`, resolve it to a concrete work bead:
   - Inspect the epic (`bd show <epic-id>`) and pick a ready child `task`/`bug`/`chore` to work on.
   - If no child bead is ready, create/unblock one and restart selection (only set the epic `in_progress` alongside a started child bead).
9. Mark the concrete work bead `in_progress`: `bd update <work-id> --status in_progress`.
10. If `bd show <work-id>` lists a parent epic, mark it `in_progress` too: `bd update <epic-id> --status in_progress`.
11. Comment rationale: `bd comments add <work-id> "Selected first: <short rationale>"`.

## Output
- Print: `Selected <work-id>: <rationale>` (include `epic <epic-id>` if applicable; select a concrete work bead).
- If `bd ready` is empty, report "No ready work" and stop.
- If deps were added, print: `Blocked <id> on <dep-ids>; re-run selection`.
- If an in-progress bead exists, report `Active <work-id>` and proceed.
