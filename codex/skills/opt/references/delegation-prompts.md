# $opt Delegation Prompts

The root owns synthesis and goal state. Optimization specialists are read-only. `$refine` performs all authorized package edits.

## Contract modeler

```text
Spawn `skill_contract_modeler` only when the target contract cannot be reconstructed locally without route-changing uncertainty.

specialist_intent:
- target_skill: <skill>
- artifact_state_id: <state>
- scope: <authorized package>
- unresolved_question: <one contract question>
- expected_decision_delta: route | proof | risk
- stop_condition: <exact answer obtained or blocked>

Return specialist-packet-v2. Do not edit files or spawn children.
```

## Decision provenance auditor

```text
Spawn `skill_decision_provenance_auditor` only when attribution or denominator choice can change the tuning decision.

Use structured decision receipts first, explicit attribution second, contract-aligned action third, associated outcome fourth, and co-occurrence last.
Return specialist-packet-v2. Do not edit files.
```

## Outcome skeptic

```text
Spawn `skill_outcome_skeptic` to challenge a proposed causal or outcome claim before mutation.
State the strongest alternative explanation and the evidence required to defeat it.
Return specialist-packet-v2. Do not edit files.
```

## Apply handoff

```text
Use $tune to produce SDC-v2 and a complete REFINE-SKILL-v3 brief.
Then invoke $refine in apply or regression mode.

Required:
- exact target
- source evidence
- gap signature
- expected decision or execution delta
- allowed and forbidden files
- protected contracts
- intervention budget
- future outcome-observation query

The root integrates SRR-v1 and updates any parent goal. No custom agent writes the package.
```
