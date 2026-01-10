---
name: ralph
description: "Implement the Ralph Wiggum iterative AI loop for Codex/Claude Code: create /ralph-loop and /cancel-ralph commands, wire a stop hook or wrapper loop, persist a fixed prompt, track iterations, and detect a completion promise with safety limits. Use when asked to build or integrate self-referential AI iteration loops, stop hooks, or command wrappers for repeated agent runs."
---

# Ralph

## Overview
Implement a self-referential loop that re-feeds the same prompt until the completion promise appears or a max-iteration limit is reached.

## Workflow Decision Tree
1. **In-session stop hook available**: implement a stop hook that blocks exit and re-injects the prompt.
2. **No stop hook**: implement an external wrapper loop (shell or runner) that repeatedly invokes Codex with the same prompt.

## Step 1: Define Prompt + State Persistence
- Persist the exact prompt to a file (do not mutate between iterations).
- Persist loop state (active flag, iteration count, max iterations, completion promise) in a separate file.
- Keep state in a dedicated directory (e.g., `.ralph/`) to avoid polluting the repo.

Suggested files:
- `.ralph/prompt.md`
- `.ralph/state.json`

## Step 2: Implement Commands
### /ralph-loop
- Accept: `<prompt>`, `--max-iterations <n>` (optional), `--completion-promise <text>` (required).
- Write prompt and state to `.ralph/`.
- Mark loop as active and set iteration to 0.

### /cancel-ralph
- Mark loop inactive and optionally clean up `.ralph/`.

## Step 3: Implement the Loop Engine
### A) Stop hook (preferred)
- On attempted exit, check if loop is active.
- If active and completion promise not yet seen and iteration < max, block exit and re-run with the same prompt file.
- Increment iteration and log the pass.

Pseudo-flow:
- read `.ralph/state.json`
- if inactive: allow exit
- if completion promise found in last output: allow exit
- if iteration >= max: allow exit (and report blocked status)
- else: increment iteration, re-run prompt, block exit

### B) External wrapper loop (fallback)
- Wrap Codex invocation in a `while` loop that replays `.ralph/prompt.md`.
- Stop when completion promise is detected or max iterations reached.

## Step 4: Safety + Escape Hatches
- Always support `--max-iterations` as a hard stop.
- Treat completion promise as exact string match.
- If max iterations reached without completion, print a summary of attempts and blockers.

## Step 5: Prompt Guidance (for users)
- Require explicit completion criteria in the prompt.
- Include a deterministic completion promise (e.g., `<promise>COMPLETE</promise>`).
- If stuck, instruct what to report after N iterations.

## Validation Checklist
- Confirm loop does not mutate the prompt file.
- Confirm iteration counter advances and stops at max.
- Confirm completion promise stops the loop.
- Confirm `/cancel-ralph` exits cleanly.
