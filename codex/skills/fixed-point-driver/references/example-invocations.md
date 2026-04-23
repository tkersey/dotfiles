# Example invocations

## Exhaustive hardening to a material fixed point

```md
Use $fixed-point-driver for this task.

Goal:
Drive this changeset to a material fixed point.

Context:
- current branch vs main
- auth/session.ts
- auth/session.test.ts
- CI logs

Constraints:
- keep remediation accretive by default
- use read-only specialist subagents when broad exploration is needed
- do not stop just because the first obvious findings are fixed

Done when:
- no unresolved material finding remains
- the pre-closure one-change challenge yields no impactful accretive improvement
- verification-closure returns ready or a bounded blocking gate
```

## PR reviews to closure

```md
Use $fixed-point-driver for this task.

Goal:
Adjudicate the PR comments, implement accepted work, and drive the branch to closure.

Context:
- reviewer comments pasted below
- current branch vs main
- relevant files listed below

Constraints:
- start with $review-adjudication if comment relevance is still unclear
- preserve public APIs unless structural evidence proves they are insufficient
- rerun full-scope review after any material remediation
```
