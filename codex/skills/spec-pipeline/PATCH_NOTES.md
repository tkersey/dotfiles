# Patch Notes

Version: `2.1.0`

Adds automatic same-turn `$plan` handoff when `$spec-pipeline` recommends it.

Key change:

```text
SGR-v2 complete + lane=spec_to_plan + plan_allowed=yes + lint pass
+ execution_handoff.next_owner=$plan + no blockers
= same-turn $plan tail-call
```

The change is fail-closed:

- no `<proposed_plan>` from `$spec-pipeline`;
- no auto-plan from gate-only, challenge-only, or lint-only modes;
- no auto-plan with drift, open material questions, failed lint, open subagents, or `do_not_execute_before` blockers;
- if the runtime cannot load `$plan`, emit `AUTO_PLAN_HANDOFF_REQUIRED` rather than silently stopping.

Adds:

- `references/auto-plan-tail-call.md`
- `tools/auto_plan_handoff_gate.py`
- fixtures and tests for eligible and blocked handoffs
