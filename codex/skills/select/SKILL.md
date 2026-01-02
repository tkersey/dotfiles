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
- Tie-break: priority → strongest signals → earliest in `bd ready`.
- Readiness gate: never start a bead if required scaffolding or prerequisites are missing; add deps and restart selection.

## Workflow
1. Run `bd ready` and keep the returned order.
2. If any ready features exist, `bd show <id>` for each and score (risk/hardness/blast).
3. Otherwise, score ready items by type order and priority.
4. Check readiness for the top candidate (repo-only):
   - Confirm required scaffolding/infra exists in the repo (app skeleton, build config, migrations, auth setup, etc.).
   - If something is missing, look for an existing prerequisite bead and link it first:
     - Link: `bd dep add <candidate-id> <dep-id> -t blocks`
   - Only create a new prerequisite bead if none exists:
     - Create: `bd create "Scaffold: <thing>" --type=task --priority=<p>`
     - Link: `bd dep add <candidate-id> <dep-id> -t blocks`
   - Re-run `bd ready` and restart selection if you added any deps.
5. Pick the highest-scored ready bead after the readiness gate passes.
6. Mark it in progress: `bd update <id> --status in_progress`.
7. Comment rationale: `bd comments add <id> "Selected first: <short rationale>"`.

## Output
- Print: `Selected <id>: <rationale>`.
- If `bd ready` is empty, report "No ready work" and stop.
- If deps were added, print: `Blocked <id> on <dep-ids>; re-run selection`.
