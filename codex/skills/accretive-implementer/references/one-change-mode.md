# Single-change improvement posture

Use this posture when the task is effectively:

> If you could change one thing about this changeset what would you change?

## Goal

Choose and implement the single highest-leverage remaining change without turning the task into a grab bag of extras.

## Selection rubric

Prefer the candidate that most improves one or more of these at acceptable churn:
- correctness
- misuse resistance
- invariant clarity or preservation
- verification strength
- consequential maintainability

## Required internal check

Before implementing the winning candidate, determine:
- the contract delta it improves
- the invariant it strengthens, preserves, or clarifies
- the stable boundary where the change should live
- why the change should not be smaller and should not be larger
- the proof signal that will confirm the benefit

## Rules

- Compare alternatives only enough to identify the dominant change.
- Keep the implementation singular.
- Do not smuggle in sibling cleanups or second-choice improvements.
- If the best remaining change is blocked by constraints or requires structural redesign, say so explicitly.
- If no remaining change is clearly worth the churn, say `no impactful accretive improvement`.
