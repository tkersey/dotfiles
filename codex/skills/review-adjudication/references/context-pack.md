# Context pack for review adjudication

Use this pack to supply just enough context for `$review-adjudication` without
flooding the model with the whole repository.

## Required review-comment context

```md
Review comments:
- raw id/thread:
- reviewer:
- file/location:
- exact excerpt:
- reviewer-suggested fix, if any:
```

If comments are copied from GitHub, preserve thread IDs, comment IDs, file paths,
line numbers, reviewer names, and exact excerpts.

## Required artifact context

```md
Current artifacts:
- branch/diff summary:
- touched files:
- relevant tests:
- CI/local proof status:
- PR description or stated goal:
```

Current artifacts outrank memory and reviewer intuition.

## Required constraint context

```md
Constraints:
- intended change:
- explicit non-goals:
- compatibility posture:
- ownership boundaries:
- proof bar:
```

## Optional context

Add only when needed:

- current failing test output
- relevant code excerpts
- prior session rationale recovered with `$seq`
- project conventions or style guide
- release compatibility constraints
- migration plan

## Anti-bloat rule

Do not include the whole repo, long prior-session summaries, or unrelated review
threads by default. Expand context only when it can change grounding, scope,
freshness, concern validity, proposed-fix validity, or handoff shape.
