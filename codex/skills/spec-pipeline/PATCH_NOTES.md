# Patch Notes

Version: `2.1.1`

Clarifies lane selection for automatic same-turn `$plan` handoff.

Key correction:

```text
explicit $spec-pipeline invocation
!= spec_only request
```

In `full` mode, default to `lane=spec_to_plan` unless the user explicitly asks
for spec-only/no-plan output or a material gate blocks planning. A successful,
plan-ready SGR-v2 must tail-call `$plan` or emit `AUTO_PLAN_HANDOFF_REQUIRED` if
same-turn loading is unavailable.

This prevents the regression where an assistant chooses `spec_only` because the
user invoked `$spec-pipeline` rather than separately invoking `$plan`.

Retains the existing fail-closed rules:

- no `<proposed_plan>` from `$spec-pipeline`;
- no auto-plan from gate-only, challenge-only, or lint-only modes;
- no auto-plan with drift, open material questions, failed lint, open subagents,
  or `do_not_execute_before` blockers;
- if the runtime cannot load `$plan`, emit `AUTO_PLAN_HANDOFF_REQUIRED` rather
  than silently stopping or converting to `spec_only`.

Adds:

- `references/lane-selection.md`
- clarified `references/auto-plan-tail-call.md`
- updated OpenAI metadata prompt with the `spec_to_plan` default rule
