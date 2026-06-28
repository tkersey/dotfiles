# Complexity Mitigator Routing Notes

## Activation goal

Increase useful activation without making `$complexity-mitigator` a mandatory dependency of repair, review-closure, or implementation workflows.

The skill should fire as a lightweight preflight when existing-code readability risk is visible:
- simplify / refactor / clean up / untangle;
- hard to read / hard to follow / reviewers stalled;
- nested branches / boolean soup / opaque names;
- cross-file state simulation;
- unclear essential-vs-incidental split.

## Non-goal

Do not restore a broad fix or review-closure dependency. Instead, use Micro Preflight and hand off immediately when implementation or remediation owns the task.

## Success metric

Expected improvement is visible in `seq` as:
- raw mentions in readability/refactor sessions;
- successful activations for analysis-first complexity tasks;
- short preflight artifacts preceding implementation handoff in mixed tasks.
