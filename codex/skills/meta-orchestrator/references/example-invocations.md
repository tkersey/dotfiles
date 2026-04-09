
# Example invocations

Tail-weighted note: final reports should end with `Final State` and `Do Next`.

## PR review remediation to closure

```md
Use $meta-orchestrator for this task.

Goal:
Address the current PR review comments and bring the branch to review-ready closure.

Context:
- current branch vs main
- reviewer comments pasted below
- relevant files: auth/session.ts, auth/session.test.ts

Constraints:
- preserve public APIs unless a review comment proves they are insufficient
- after the artifact set reaches a candidate material fixed point, ask: "If you could change one thing about this changeset what would you change?"
- route any accepted answer to $accretive-implementer
- after that implementation, rerun full-scope de novo review before closure

Done when:
- every material review comment is either implemented or rebutted with evidence
- the one-change challenge yields no impactful accretive improvement
- verification-closure says the branch is ready or clearly states the blocking gaps
```

## Exhaustive hardening with subagents

```md
Use $meta-orchestrator for this task.

Goal:
Find all impactful changes, use specialist subagents for read-heavy analysis, and take the artifact set to closure.

Context:
- relevant files and tests
- current CI output

Constraints:
- keep remediation single-threaded
- start with the smallest informative specialist set and only expand to the full swarm if the surface is broad and packet transport is clean
- rerun the full-scope subagent swarm before each de novo review pass only when transport remains clean; otherwise fall back to local synthesis
- specialist outputs must be exactly one `<SPECIALIST_PACKET ...>` or one `SPECIALIST_PACKET_INVALID: <reason>` line; no `Echo:`, no instruction acknowledgements, and no verbatim subagent trace leakage into the parent report
- ask the one-change challenge before final closure
```
