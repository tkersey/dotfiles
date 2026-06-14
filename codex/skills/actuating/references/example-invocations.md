# Example Invocations

## Full plan-to-PR

```md
Use $actuating for this task.

Plan:
@docs/plans/refactor-cache-boundary.md

Goal:
Turn the plan into durable $st tasks, implement all steps with $fixed-point-driver, run the repo's build/lint/test suite, and use $ship to open a PR once validation passes.

Constraints:
- use $zig for Zig files/toolchain proof
- do not merge
- do not stop until every in-scope $st task is complete or explicitly blocked
```

## Pasted plan

```md
Use $actuating.

Turn the plan below into $st tasks and implement it through PR.
Use language-specific skills when the repo surface calls for them.
Ship only after builds, lints, and tests pass.

<plan>
...
</plan>
```

## Resume existing graph

```md
Use $actuating.

There is already an active .step/st-plan.jsonl. Continue executing it through $fixed-point-driver. Do not ship until every in-scope task is complete and full validation passes.
```
