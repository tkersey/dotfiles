# Feedback Loops Reference

## Purpose
Close the loop after every code change by observing at least one concrete signal that validates the change.

## Signal ladder (tightest first)
1. Static analysis: lint, typecheck, format checks, or other fast static guards.
2. Runtime logs: run the narrowest path and read logs or counters tied to the change.
3. Unit tests: run the smallest test set that exercises the change.
4. UI automation: run the smallest UI or E2E flow that proves the behavior.

## Decision checklist
- What is the smallest loop that touches the changed behavior?
- Can it run locally and finish quickly?
- Can it be scoped to the changed module, endpoint, or path?
- Is the output observable and unambiguous?
- If the signal is weak, can you add the next-tightest loop?

## Fallbacks when no loop exists
- Add a single log line or counter tied to the change.
- Add a focused unit test that asserts the new behavior.
- Add a minimal automation step (script or UI flow) to validate the path.
- Ask the user to run the loop and report the output if you cannot run it.

## Reporting template
Signal:
Run or observe:
Result:
Confidence:
Next action:

## Best-effort stance
Be explicit about missing signals, propose the smallest possible loop, and proceed only when a real signal exists or the user accepts the gap.
