# Recursion-scheme map for coding agents

This reference keeps the theory available without forcing it into every user-facing response.

| Scheme | Plain-language role | Coding-agent use |
|---|---|---|
| Anamorphism | Unfold a seed into work | Turn a goal, spec, review target, or failure into a work list or branch set. |
| Catamorphism | Fold evidence into a result | Turn tests, logs, diffs, CAS findings, and artifacts into a verdict. |
| Hylomorphism | Unfold then fold repeatedly | The normal goal loop: choose work, act, verify, fold evidence, continue or stop. |
| Paramorphism | Fold while keeping original structure | Refactor code while retaining file/spans/AST needed for precise edits. |
| Apomorphism | Unfold while reusing existing solved pieces | Reuse templates, known fixes, codemods, prior subplans, or previous solutions. |
| Histomorphism | Fold with access to prior results | Use attempt history to avoid cycling in debugging or review remediation. |
| Futumorphism | Unfold with lookahead | Branch-race multiple strategies before choosing. |
| Zygomorphism | Produce result plus proof sidecar | Generate code and proof/risk summary together. |
| Dynamorphism | Memoized recursion | Cluster repeated failures and solve one representative before bulk application. |
| Chronomorphism | History plus lookahead | Long-horizon coding agents that use both attempt memory and strategy search. |

## The useful practical form

```text
seed -> unfold work -> act -> fold evidence -> update memory -> proof -> stop or continue
```

Use this to prevent generic while-loops.
