# Patch Notes

Version: `4.2.0`

Adds explicit receiver support for `$spec-pipeline` same-turn tail-calls.

Key additions:

```text
plan_source_contract / PSC-v1
plan_source_contract_gate.py
PSR-v1 source_contract binding
```

The fix pairs with `$spec-pipeline` v2.2.0:

```text
full plan-ready SGR-v2
-> lane=spec_to_plan
-> PSC-v1
-> $plan validates PSC-v1
-> fixed-point execution policy
-> <proposed_plan>
```

`$plan` must fail closed when the SGR-v2 is missing, blocked, drifted,
spec_only, not lint-passing, not ready_for_plan, not owned by `$plan`, or has a
non-empty `do_not_execute_before` list.
