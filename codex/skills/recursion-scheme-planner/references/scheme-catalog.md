# Recursion scheme catalogue for coding-agent planning

This catalogue is a practical planning map. It is not a theorem-prover and not a reason to add ceremony. Use a scheme only when it changes route, proof, decomposition, memory, or stop behavior.

| Scheme | Planning question | Coding-agent route |
|---|---|---|
| Direct | Is there no recursive structure? | Do one bounded action and verify. |
| Catamorphism | What evidence must be folded into a verdict? | `$evidence-fold`, `$review-fold`, `$proof-patch`. |
| Anamorphism | What work must be unfolded from the seed? | `$goal-workgraph`, scout fanout. |
| Hylomorphism | Can we unfold work and fold evidence repeatedly? | `$goal-actuating` / `$goal-grind`. |
| Paramorphism | Do edits require original structure plus summary? | AST/span/file-preserving refactor. |
| Apomorphism | Can we reuse a solved subtree or pattern? | Reuse nodes, codemods, templates, previous fixes. |
| Histomorphism | Do prior attempts matter? | Attempt ledger, `$failure-memory`, anti-oscillation. |
| Futumorphism | Do we need lookahead or competing futures? | Branch race with common verifier. |
| Zygomorphism | Must artifact and proof be produced together? | Proof-carrying patch / PR handoff. |
| Dynamorphism | Are subproblems repeated and memoizable? | Representative failure classes, migration memoization. |
| Chronomorphism | Need both history and lookahead? | Long-horizon debug/review/perf loops. |
| Metamorphism | Transform old representation into new one? | Fold old model, unfold new implementation. |
| Mutumorphism | Are subproblems mutually recursive? | Coordinated plan, often `$st` or serial integration. |
| Parallel traversal | Are leaves independent? | Bounded subagents with strict fan-in. |

## Scheme compositions

Most real coding tasks use combinations:

```text
review resolve-and-fix = cata(CAS findings) + dyna(review classes) + hylo(accepted fixes) + zygo(proof) + terminal CAS fixed point
migration = ana(package/error matrix) + dyna(class memoization) + hylo(apply/prove) + cata(repo evidence)
hard debug = histo(attempts) + futu(strategy branches) + hylo(action/evidence)
refactor = para(original code) + meta(old->new shape) + zygo(proof)
parallel PR review = ana(review classes) + parallel traversal + cata(resolve/fan-in)
```

## Clean CAS fixed point

For `resolve-and-fix` and exhaustive review:

```text
3 consecutive clean normalized CAS review runs
```

A clean normalized run is a fold result, not raw absence of comments. Duplicate, rejected, out-of-scope, already-proven proof-only, follow-up, or already-resolved findings do not dirty the run.
