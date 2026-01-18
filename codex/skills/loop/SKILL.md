---
name: loop
description: "Iterate a markdown list of $skill invocations in order, repeating passes until beads are exhausted (bd ready empty and no in_progress). Use when asked to loop over skills to drive bead work to completion."
---

# Loop

## Overview
Execute a provided markdown list of $skill invocations sequentially in the same session, repeat passes until beads are done, then run bd sync once.

## Inputs
- Require a markdown bullet list.
- Each item must start with `$skill` and may include trailing args; keep the invocation string verbatim.
- Preserve list order; skip blank items or bullets without a `$` prefix.

If the list is missing, ask the user to provide it before proceeding.
If `.beads/` is missing, stop and explain that loop termination depends on bd.

## Workflow
1. Parse the list items into invocation strings (strip bullet markers and leading whitespace).
2. Repeat passes:
   - For each invocation in order, execute it as if the user requested it directly.
   - Do not spawn sub-agents or new sessions.
   - If a step requires human input, ask and pause; resume the loop after the user replies.
   - After completing the full pass (and optionally after any item), check the stop condition.
3. Stop condition (both must be true):
   - `bd ready --limit 1 --json` returns no items.
   - `bd list --status in_progress --limit 1 --json` returns no items.
4. When the stop condition is met, run `bd sync` once and exit.

## Notes
- Do not create any loop state files or directories.
- Do not add a max-iteration guard unless the user explicitly asks for one.
