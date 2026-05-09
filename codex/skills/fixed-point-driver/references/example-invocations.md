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
Use $fixed-point-driver for this task.
Goal: Find all impactful changes, use specialist subagents for read-heavy analysis, and take the artifact set to closure.
Context:
- relevant files and tests
- current CI output
Constraints:
- keep remediation single-threaded
- rerun the full-scope subagent swarm before each de novo review pass
- ask the one-change challenge before final closure
```

## Optimization/search campaign with negative evidence
```md
Use $fixed-point-driver for this task.
Goal: Improve the target benchmark without repeating prior failed routes.
Context:
- current branch vs main
- benchmark command and latest result
- prior reverted diffs, failed benchmark notes, or `.learnings.jsonl` entries
Constraints:
- use `$negative-ledger` before choosing the next implementation route
- allow `negative-ledger-mapper` to run read-only `learnings recall/query` when available
- every Negative Evidence Ledger entry needs a witness, applicability conditions, and reopening criteria
- let `$negative-ledger` query `$learnings` as a source when available, but do not treat a hit as active without current applicability
- do not let negative evidence veto a current route unless it applies to the current artifact state
Done when:
- the selected next change is not an active previously-disconfirmed hypothesis
- newly disconfirmed attempts are captured through `$negative-ledger` and, when durable, `$learnings`
- verification-closure says the changed path and benchmark claim are bounded
```

## Dedicated negative-ledger preflight before fixed-point work
```md
Use $negative-ledger first, then $fixed-point-driver.
Goal: Before another remediation pass, map what we already tried and which failures still apply.
Context:
- current branch and changed paths
- latest test/benchmark output
- commit/revert notes
- `.learnings.jsonl` is available in the repo root
Output:
- active negative evidence
- stale or reopened evidence
- safest next search frontier
- any learnings rows worth appending after this turn
```
