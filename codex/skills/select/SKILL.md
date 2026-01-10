---
name: select
description: "Explicit-only: pick the next `bd ready` bead via risk-first heuristics; verify dependency/readiness, add missing deps, then mark in progress and comment."
---

# Select

## Intent
Choose the next bead by risk, hardness, and blast radius; gate on codebase readiness and dependencies before marking `in_progress`; leave a short rationale comment.

## Selection rubric
- Feature-first: if any ready items are `feature`, evaluate all ready features (`bd show`).
- Type order (fallback): `task` > `bug` > `epic` > `chore`.
- Priority: P0 > P1 > P2 > P3 > P4.
- Risk: migrations, auth/security, infra, data loss/consistency, breaking API/CLI, perf regressions, ambiguous acceptance.
- Hardness: vague scope, multiple subsystems, unknown deps, heavy verification.
- Blast radius: widely used modules, shared config, CI/build pipeline, core user paths.
- Parallelism impact (balance with risk): prefer beads that unlock more blocked work or establish a contract/checkpoint when risk is in the same tier.
- Soft deps: if a ready bead has `tracks`/`related` pointing to another ready bead, apply a soft penalty and prefer the tracked-first item.
- Tie-break: priority → strongest signals → earliest in `bd ready`.
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

## Workflow
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
8. Mark it in progress: `bd update <id> --status in_progress`.
9. Comment rationale: `bd comments add <id> "Selected first: <short rationale>"`.

## Output
- Print: `Selected <id>: <rationale>`.
- If `bd ready` is empty, report "No ready work" and stop.
- If deps were added, print: `Blocked <id> on <dep-ids>; re-run selection`.
