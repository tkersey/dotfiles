# Example invocations

## Exhaustive patch hardening
```md
Use $fixed-point-driver for this task.

Goal:
Drive the current changeset to a material fixed point.

Context:
- current branch vs main
- auth/session.ts
- auth/session.test.ts

Constraints:
- use read-only specialists for evidence collection
- keep remediation single-threaded
```

## PR review remediation with adjudication
```md
Use $fixed-point-driver for this task.

Goal:
Adjudicate current PR comments, implement only the accepted agenda, and drive the branch to a material fixed point.

Inputs:
- reviewer comments pasted below
- current diff
- seq-backed rationale recovery is allowed when intent is unclear
```
