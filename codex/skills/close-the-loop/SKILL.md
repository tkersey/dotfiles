---
name: close-the-loop
description: Force at least one feedback signal after code changes (static checks, logs, tests, UI); prefer local over CI.
---

# Close the Loop

## Intent
Require at least one real feedback signal after any code change before declaring success.

## Quick start
1. Pick the tightest available loop: static analysis → runtime logs → unit tests → UI automation.
2. Run (or obtain) at least one signal. If none exist, propose the smallest new one (log, focused test, minimal automation).
3. Report what ran, what happened, and what’s next.

## Workflow
1. Define “working” for this change (feature path, bug reproduction, contract).
2. Choose the tightest loop and smallest scope; prefer local execution.
3. Run it (or ask for the exact command/environment if unknown).
4. If confidence is weak, add the next-tightest loop.

## Guardrails
- No “done” claims without a signal.
- Local-first, CI-second (use CI when local is unavailable, flaky, or non-representative).
- If you cannot run the loop, state the gap and give the user exact commands.

## References
- `references/feedback-loops.md`

## Activation cues
- "feedback loop"
- "verify changes"
- "validation"
- "add tests/logs/checks"
- "tight loop"
- "working code is done"
- "completed the task"
