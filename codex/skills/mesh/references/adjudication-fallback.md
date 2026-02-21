# Adjudication and Deadlock Fallback

Use this routing when role outputs conflict.

## Primary class routing

1. `safety_invariant` -> `fixer` final authority
2. `complexity_perf` -> `reducer` final authority
3. `style_doctrine` -> `feedback` final authority

## Classification flow

1. Attempt initial class assignment from task metadata and critiques.
2. If class is ambiguous, run one explicit classification round.
3. If two or more roles converge on one class, use that class.
4. If no class convergence, mark `adjudication_deadlock`.

## Deadlock fallback

When deadlock occurs:

1. Persist decision log with all candidate classes and objections.
2. Block task with code `adjudication_deadlock`.
3. Require one narrowed re-run scoped to a single disputed point.
4. Do not promote task during deadlock.

## Decision record format

Record:

1. `task_id`
2. selected conflict class (or `none`)
3. final authority role
4. winning decision
5. losing alternatives
6. required follow-up action
