# 04 — Plan Source Contract Gate

`plan_source_contract_gate.py` is the fail-closed receiver gate for `$plan`.

## Command

```bash
uv run python codex/skills/plan/tools/plan_source_contract_gate.py <psc-file>
```

The input may be YAML or JSON and may contain either:

```yaml
plan_source_contract: ...
```

or a raw PSC-v1 object.

## Required checks

The gate passes only when:

```text
contract_version = PSC-v1
source_owner = spec-pipeline
implementation_spec present
decision_packet present
proof_bar present
target_branch present
top-level do_not_execute_before empty
sgr_v2.spec_governance_receipt present
SGR-v2.mode in {full, repair}
SGR-v2.status = complete
SGR-v2.lane = spec_to_plan
SGR-v2.gate.plan_allowed = yes
SGR-v2.gate.material_open_questions_remaining = no
SGR-v2.lint.verdict = pass
SGR-v2.lint.blocked_handoff = no
SGR-v2.execution_handoff.ready_for_plan = yes
SGR-v2.execution_handoff.next_owner = $plan
SGR-v2.execution_handoff.do_not_execute_before empty
SGR-v2.auto_plan_handoff.eligible = yes
SGR-v2.auto_plan_handoff.invocation in {same_turn_tail_call, manual}
```

`manual` is allowed only for a later explicit `$plan` invocation after
`AUTO_PLAN_HANDOFF_REQUIRED`.

## Failure

On failure, print a concise missing/invalid field list and exit non-zero.

Do not continue planning from a failed PSC-v1.
