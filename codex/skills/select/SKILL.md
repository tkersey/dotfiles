---
name: select
description: "Explicit-only: pick the next `bd ready` bead via risk-first heuristics; mark in progress and comment."
---

# Select

## Intent
Choose the next bead by risk, hardness, and blast radius; mark it `in_progress` and leave a short rationale comment.

## Selection rubric
- Feature-first: if any ready items are `feature`, evaluate all ready features (`bd show`).
- Type order (fallback): `task` > `bug` > `epic` > `chore`.
- Priority: P0 > P1 > P2 > P3 > P4.
- Risk: migrations, auth/security, infra, data loss/consistency, breaking API/CLI, perf regressions, ambiguous acceptance.
- Hardness: vague scope, multiple subsystems, unknown deps, heavy verification.
- Blast radius: widely used modules, shared config, CI/build pipeline, core user paths.
- Tie-break: priority → strongest signals → earliest in `bd ready`.

## Workflow
1. Run `bd ready` and keep the returned order.
2. If any ready features exist, `bd show <id>` for each and score (risk/hardness/blast).
3. Otherwise, score ready items by type order and priority.
4. Pick one bead.
5. Mark it in progress: `bd update <id> --status in_progress`.
6. Comment rationale: `bd comment <id> "Selected first: <short rationale>"`.

## Output
- Print: `Selected <id>: <rationale>`.
- If `bd ready` is empty, report "No ready work" and stop.
