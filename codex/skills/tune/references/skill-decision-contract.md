# SKDC-v1

A Skill Decision Contract makes consequential skill behavior observable over time.

```yaml
skill_decision_contract:
  contract_version: SKDC-v1
  skill:
    name:
    kind: decision | execution | evidence | orchestration | mixed
    source_fingerprint:
  triggers:
    - trigger_id:
      description:
      cue_literals: []
      cue_regexes: []
      exclusions: []
  routes:
    - route_id:
      description:
      aliases: []
      terminal: yes | no
  clauses:
    - clause_id:
      trigger_refs: []
      expected_routes: []
      prohibited_routes: []
      required_artifacts: []
      success_signals: []
      failure_signals: []
      rationale:
  instrumentation:
    decision_receipt: required | optional | not-needed
    rationale:
```

Stable IDs are more important than prose stability.

Do not encode every instruction as a clause.

Contracts should cover consequential decisions that future evidence can observe.
