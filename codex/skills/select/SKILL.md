---
name: select
description: "Explicit-only: choose the next bead from bd ready using risk-first heuristics; mark it in progress and comment with rationale."
---

# Select

## Overview
Selects the next bead to work on by prioritizing risk, hardness, and blast radius. Prefers features, weights priority, marks the chosen bead in progress, and leaves a rationale comment.

## Selection rubric
- **Feature-first:** If any ready items are `feature`, evaluate *all* ready features with `bd show`.
- **Type order (fallback):** If no features are ready, consider types in order: `task` > `bug` > `epic` > `chore`.
- **Priority weighting:** Prefer higher priority (P0 > P1 > P2 > P3 > P4).
- **Risk signals:** migrations, schema changes, auth/security, infra changes, data loss/consistency, breaking API/CLI changes, perf regressions, ambiguous acceptance.
- **Hardness signals:** vague scope, multiple subsystems, heavy verification burden, unknown deps.
- **Blast radius signals:** widely used modules, shared config, CI/build pipeline, core user paths.
- **Tie-breakers:** higher priority → stronger risk/hardness/blast signals → earlier in `bd ready` list.

## Workflow
1) Run `bd ready` and capture the ready list order.
2) If any ready features exist, run `bd show <id>` for each feature and score risk/hardness/blast from the description/design/acceptance/notes.
3) If no features exist, evaluate ready items by type order, using priority and description-based signals.
4) Pick a single bead.
5) Mark it in progress:
   - `bd update <id> --status in_progress`
6) Comment the rationale:
   - `bd comment <id> "Selected first: <short risk/hardness/blast + priority rationale>"`

## Output
- Print a single line: `Selected <id>: <rationale>`.
- If `bd ready` is empty, report "No ready work" and stop.
