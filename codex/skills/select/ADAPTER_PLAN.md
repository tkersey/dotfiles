# Select adapter: plan-N.md

## Intent
`plan-N.md` is planning context, not a task source.

## When used
- Only select this adapter if no higher-precedence source is available.

## Output
- Emit an empty OrchPlan with warnings.
- Also emit pipelines from `codex/skills/select/PIPELINES.md`.

Notes:
- Set `source.kind: plan` and `source.locator` to the chosen `plan-N.md`.
- In Decision Trace, `pick` should be `none`.
- In pipeline guidance, recommend seeding workstreams plus `contract`/`checkpoint` tasks before execution slicing.
