# Integration notes

Recommended `$actuating` handoff language:

```text
Use `$recursion-scheme-planner` after `$spec-pipeline` when the accepted spec has nontrivial decomposition, repeated classes, review campaigns, branch choices, proof fanout, or parallel subagent opportunities. Skip it for direct one-shot execution.
```

Recommended `$goal-actuating` handoff language:

```text
If no Scheme Plan exists and the work shape is unclear, ask `$recursion-scheme-planner` to select the loop shape before generating a work graph.
```

Recommended goal-focus HYL handoff:

```text
When the parent /goal has staged structure, emit a subgoal ladder whose frames become parent-owned HYL goal-focus frames. Do not swap the primary /goal for child objectives. Use references/goal-focus-hylo-driver.md as the canonical specification.
```

Recommended root routing:

```text
$recursion-scheme-planner is explicit-only at root. It may run by documented handoff from `$actuating` or `$goal-actuating`.
```
