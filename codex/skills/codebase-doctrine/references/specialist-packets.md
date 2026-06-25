# Specialist Assignments and Packets

Every specialist receives a bounded assignment:

```yaml
codebase_doctrine_assignment:
  assignment_version: CBDA-v1
  assignment_id:
  worker:
  artifact_state_id:
  intent_id:
  scope:
  allowed_question_ids: []
  allowed_evidence_lanes: []
  allowed_update_keys: []
  objective:
  stop_condition:
```

Every specialist returns one packet:

```yaml
codebase_doctrine_packet:
  packet_version: CBDP-v2
  worker:
  assignment_id:
  artifact_state_id:
  intent_id:
  scope:
  evidence_lanes: []
  questions_addressed: []
  facts:
    - claim_id:
      claim_class: fact
      statement:
      evidence_refs: []
      question_ids: []
      artifact_state_id:
      confidence:
  inferences:
    - claim_id:
      claim_class: inference
      statement:
      evidence_refs: []
      question_ids: []
      artifact_state_id:
      confidence:
  contradictions: []
  open_questions: []
  proposed_doctrine_updates: {}
  stale: no
  final_call: usable | partial | no_material_signal | blocked
```

Validate with the assignment:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/packet_gate.py packet.yaml \
  --assignment assignment.yaml
```

The gate enforces worker identity, artifact state, intent, scope, assigned
questions, evidence lanes, allowed update keys, fact/inference separation, and
wrapper-leakage rejection.

Workers do not spawn children, edit files, create skills, or own final doctrine.
