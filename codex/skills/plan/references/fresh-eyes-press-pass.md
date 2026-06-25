# Execution Policy Fresh-Eyes Pass

Treat prior readiness as untrusted.

Check:

- source/spec digest and artifact state are current;
- no semantic decision was smuggled into policy compilation;
- regime classification fits the actual causal uncertainty;
- every critical unknown has observable evidence or an explicit block/return;
- each action has bounded effects, failure observations, proof, and rollback;
- policy rules reference only declared atoms and actions;
- every modeled action outcome reaches another rule or terminal state;
- safety rules cover irreversible and authority-sensitive actions;
- potential cannot reward gaming the metric while violating the goal;
- commitment horizon is short enough to remain evidence-responsive;
- success terminal proves the source contract;
- human projection does not contradict EPG.

Return:

```yaml
execution_policy_audit:
  audit_version: EPA-v1
  source_current:
  semantic_drift:
  regime_findings: []
  belief_findings: []
  action_findings: []
  policy_findings: []
  shield_findings: []
  potential_findings: []
  terminal_findings: []
  downstream_findings: []
  blockers: []
  final_call:
    ready |
    revise_policy |
    return_to_spec |
    return_to_grill |
    stale |
    blocked
```

No mandatory innovation addition.
