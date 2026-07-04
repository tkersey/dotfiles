# Recursion-scheme map for coding agents

This reference keeps the theory available without forcing it into every user-facing response.

| Scheme | Plain-language role | Coding-agent use |
|---|---|---|
| Anamorphism | Unfold a seed into work | Turn a goal, spec, review target, or failure into a work list, subgoal ladder, or branch set. |
| Catamorphism | Fold evidence into a result | Turn tests, logs, diffs, CAS findings, subagent outputs, and artifacts into a parent-goal verdict. |
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

## Goal-focus HYL frames

For material `$actuating`, keep one stable parent `/goal` and move a typed active focus through the HYL loop:

```text
parent /goal
-> goal-focus frame
-> anamorphism produces legal work/frontier
-> action executes only that work/frontier
-> catamorphism folds evidence into parent state
-> next focus | blocked | terminal ATCG
```

Do not treat child frames as literal nested `/goal` commands. Child frames are parent-owned subgoals that must fold back into the parent. See `$recursion-scheme-planner`'s `references/goal-focus-hylo-driver.md` for the canonical subgoal ladder and goal-focus schema.
