# One-change mode

Use this mode when the task is: "If you could change one thing about this changeset, what would you change?"

## Rules
- Pick exactly one discretionary improvement unless a tightly coupled follow-on edit is strictly required.
- Prefer the highest-leverage accretive change.
- Prefer a change that improves correctness, soundness, reviewability, or misuse resistance before style or taste.
- Explain why this one change beats the nearest alternatives.
- After implementation, verify the direct benefit and at least one plausible nearby regression surface.

## Good outputs
- the chosen change
- why it dominates
- the narrowest cut
- the proof signal
