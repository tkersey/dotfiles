---
name: loop
description: "Iterate a markdown list of prompts in order, repeating passes until an explicit stop condition is met. Use when asked to loop over prompts or skills to drive work to completion."
---

# Loop

## Overview
Execute a provided markdown list of prompts serially in the same session, repeating passes until an explicit stop condition is met.

Fail fast: if any step cannot be executed, stop immediately and ask for human input; do not continue to later steps.

## Inputs
- Require a markdown bullet list of prompts.
- Each item is treated as a prompt string; keep it verbatim (it may include `$skill` tokens as plain text).
- Preserve list order; skip blank items.
- Require a clear stop condition using a `Stop when:` block (or `Stop when: <condition>` single line).
- Optional: a `Preflight:` block to request a best-effort dry-run before the first pass.

If the list is missing, ask the user to provide it before proceeding.
If the stop condition is missing or ambiguous, stop and ask for it before starting the loop.

## Workflow
1. Parse the list items into prompt strings (strip bullet markers and leading whitespace).
2. Parse the stop condition into a concrete, checkable predicate.
3. Optional preflight (only if a `Preflight:` block is present):
   - For each prompt in order, do a best-effort "can I run this?" check using read-only inspection.
   - Do not make edits, create files, or run destructive commands during preflight.
   - If any prompt is not actionable, stop and ask for human input before doing any real work.
4. Repeat passes:
   - For each prompt in order, execute it as if the user requested it directly.
   - Do not spawn sub-agents or new sessions.
   - If a step requires human input, ask and pause. Resume at the same step after the user replies.
   - If a step cannot be executed (missing prerequisites, tool error, unclear instruction), stop immediately and ask for human input; do not continue to later steps.
   - After completing the full pass, evaluate the stop condition.
5. When the stop condition is met, exit.

## Notes
- Do not create any loop state files or directories.
- Do not add a max-iteration guard unless the user explicitly asks for one.
- Do not infer a stop condition from the last list item; it must be explicit.

## Stop condition
The stop condition exists to make loop termination checkable and non-guessy. Prefer an explicit, machine-checkable statement.

### Format
Accept either form after the list:

```
Stop when:
- <clear, checkable condition>
```

or:

`Stop when: <clear, checkable condition>`

### Multiple conditions
If multiple bullets are provided, interpret them as AND by default (all bullets must be true).
To request OR semantics, write:

```
Stop when (any):
- <condition A>
- <condition B>
```

### Cadence
Evaluate the stop condition after each full pass unless the user explicitly asks to check after each step.

The condition must be specific enough to evaluate without additional guessing. If it is not, ask for clarification before looping.

## Preflight (optional)
If a `Preflight:` block is present, run a best-effort dry-run before the first pass to catch obvious blockers early.

Format:

```
Preflight:
- <optional notes (any non-empty block enables preflight)>
```

Preflight cannot guarantee success (prompts are arbitrary), but it should detect missing inputs and obvious environmental issues before doing real work.
