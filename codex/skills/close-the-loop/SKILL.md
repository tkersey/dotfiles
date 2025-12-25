---
name: close-the-loop
description: Process-first rulebook for forcing tight feedback loops after code changes. Use when Codex has produced or finished working code, needs to verify changes, or the user asks for feedback loops, validation, tests, logs, checks, or a tight loop. Enforce at least one feedback signal (static analysis, runtime logs, unit tests, UI automation), local-first then CI.
---

# Close the Loop

## Overview
Enforce a best-effort feedback loop after every code change so you always observe at least one real signal before claiming success.

## Quick start
1. Choose the tightest available loop in priority order: static analysis, runtime logs, unit tests, UI automation.
2. Run or obtain at least one signal; if none exist, say so and propose the smallest new signal (add a log, add a focused test, or a minimal automation step).
3. Report the signal, what was run or observed, and the next action.

## Workflow
1. Identify what "working code" means for the change (feature path, bug reproduction, or contract).
2. Select the tightest loop available; prefer local execution and smallest scope.
3. Execute the loop or ask for the exact command or environment if unknown.
4. Summarize the outcome and update confidence; if the signal is weak, add the next-tightest loop.

## Guardrails
- Require at least one feedback signal for each change.
- Local-first, CI-second. Use CI when local is unavailable, flaky, or non-representative.
- Be strongly worded and persistent about closing the loop, but proceed best-effort.
- If you cannot run the loop, explicitly state the gap and propose how the user can run it.

## Resources
- `references/feedback-loops.md` - selection heuristics, checklist, and fallback options.

## Activation cues
- "feedback loop"
- "verify changes"
- "validation"
- "add tests/logs/checks"
- "tight loop"
- "working code is done"
- "completed the task"
