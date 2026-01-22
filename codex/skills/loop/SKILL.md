---
name: loop
description: "Iterate a markdown list of prompts in order, repeating passes until an explicit stop condition is met. Use when asked to loop over prompts or skills to drive work to completion."
---

# Loop

## Overview
Execute a provided markdown list of prompts sequentially in the same session, repeat passes until an explicit stop condition is met.

## Inputs
- Require a markdown bullet list of prompts.
- Each item is treated as a prompt string; keep it verbatim (it may include `$skill` tokens as plain text).
- Preserve list order; skip blank items.
- Require a clear stop condition using a `Stop when:` block.

If the list is missing, ask the user to provide it before proceeding.
If the stop condition is missing or ambiguous, stop and ask for it before starting the loop.

## Workflow
1. Parse the list items into prompt strings (strip bullet markers and leading whitespace).
2. Parse the `Stop when:` block into a concrete, checkable condition.
3. Repeat passes:
   - For each prompt in order, execute it as if the user requested it directly.
   - Do not spawn sub-agents or new sessions.
   - If a step requires human input, ask and pause; resume the loop after the user replies.
   - After completing the full pass, evaluate the stop condition.
4. When the stop condition is met, exit.

## Notes
- Do not create any loop state files or directories.
- Do not add a max-iteration guard unless the user explicitly asks for one.
- Do not infer a stop condition from the last list item; it must be explicit.

## Stop condition format
Require a separate block after the list:

```
Stop when:
- <clear, checkable condition>
```

The condition must be specific enough to evaluate after each full pass without additional guessing. If it is not, ask for clarification before looping.
