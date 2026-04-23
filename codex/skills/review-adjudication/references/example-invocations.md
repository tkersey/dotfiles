# Example invocations

## Review the review
```md
Use $review-adjudication for this task.

Goal:
Determine which current PR review comments are actually relevant before changing code.

Context:
- current branch vs main
- reviewer comments pasted below
- relevant files: auth/session.ts auth/session.test.ts
- current CI status: one failing test, reviewer asked for a refactor and an API rename

Constraints:
- treat comments as claims, not truths
- use $seq if the original why of this PR is unclear
- do not implement changes yet

Done when:
- each comment is classified
- the bottom line says what to act on, rebut, defer, or investigate
- the handoff agenda says whether this should go to $accretive-implementer or $fixed-point-driver
```

## Fast adjudication
```md
Use $review-adjudication in fast mode.

Comments:
1. This should be a helper.
2. The retry path looks non-idempotent.
3. Please rename the public method to refreshSessionNow.
4. Add a property-based test.

Return only the fast output.
```

## Intent recovery first
```md
Use $review-adjudication for this task.

Goal:
Figure out whether these review comments still make sense given why this PR exists.

Constraints:
- explicitly use $seq to recover the PR why from sessions and memories
- prefer session-backed evidence over memory-only recall
- do not change code
```
