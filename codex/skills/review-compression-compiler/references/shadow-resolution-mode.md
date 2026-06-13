# Shadow Resolution Mode

Shadow mode is a diagnostic arena, not a default.

## Use when

- same cluster repeatedly reappears after fixes;
- exploratory fixes are useful but should not become final architecture;
- review churn is likely to produce scar tissue.

## Concept

```text
main branch stays clean
shadow branch/worktree accumulates exploratory evidence
compiler synthesizes final normal form
main branch receives only compressed patch
```

## Rules

- This skill does not create or mutate the shadow branch.
- Shadow diffs are evidence, not final design.
- The final selected normal form must still pay abstraction rent and provide proof.
- Do not transplant exploratory wrappers/helpers without rent.
