# Example invocations

Tail-weighted note: final reports should end with `Final State` and `Do Next`.

## PR review remediation to closure

```md
Use $fixed-point-driver for this task.

Goal: Address the current PR review comments and bring the branch to review-ready closure.

Context:
- current branch vs main
- reviewer comments pasted below
- relevant files: auth/session.ts, auth/session.test.ts

Constraints:
- preserve public APIs unless a review comment proves they are insufficient
- start with the narrowest sound closure path
- automatically escalate to focused or exhaustive saturation if material evidence warrants it
- after the artifact set reaches a candidate material fixed point, ask: "If you could change one thing about this changeset what would you change?"
- route any accepted answer to $accretive-implementer
- after that implementation, rerun the required de novo review for the active escalation level before closure

Done when:
- every material review comment is either implemented or rebutted with evidence
- every active escalation trigger is resolved, bounded, or saturated
- the one-change challenge yields no impactful accretive improvement or its accepted change has been implemented and re-reviewed
- verification-closure says the branch is ready or clearly states the blocking gaps
```

## Progressive closure without explicit exhaustion words

```md
Use $fixed-point-driver for this task.

Goal: Take this changeset to a material fixed point.

Context:
- current branch vs main
- relevant files and tests
- current CI output

Constraints:
- do not ask me whether to be exhaustive
- begin with the cheapest sound path that can expose material risk
- automatically escalate if scope, invariants, hazards, verification gaps, or stale evidence require saturation
- keep remediation single-threaded

Done when:
- the active escalation level is justified in the Escalation Ledger
- no unresolved material finding remains
- final verification-closure has consumed the latest handoff packet
```

## Exhaustive hardening with subagents

```md
Use $fixed-point-driver for this task.

Goal: Find all impactful changes, use specialist subagents for read-heavy analysis, and take the artifact set to closure.

Context:
- relevant files and tests
- current CI output

Constraints:
- enter Level 2 exhaustive saturation immediately
- keep remediation single-threaded
- rerun the full-scope subagent swarm before each de novo review pass unless unchanged-state reuse is valid
- ask the one-change challenge before final closure
```
