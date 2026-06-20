# Specialist Packets

Each worker returns exactly one:

```yaml
codebase_doctrine_packet:
  packet_version: CBDP-v1
  worker:
  artifact_state_id:
  scope:
  evidence_lanes: []
  questions_addressed: []
  facts:
    - claim_id:
      statement:
      evidence_refs: []
      confidence:
  inferences: []
  contradictions: []
  open_questions: []
  proposed_doctrine_updates: {}
  stale: yes | no
  final_call:
    usable |
    partial |
    no_material_signal |
    blocked
```

## Root acceptance

Accept only when:

- artifact state matches;
- scope matches;
- material facts have evidence;
- facts and inferences are separate;
- no wrapper/instruction leakage;
- packet contains more than acknowledgement;
- certainty matches evidence;
- stale = no.

## Worker ownership

```text
cartographer             repository/system map
authority mapper         owners/transitions/authority
law miner                behavior/laws/invariants
failure analyst          history/failure families/routes
proof mapper             proof surfaces/gaps
portfolio skeptic        routing/skill challenge
saturation auditor       stop/challenge
```

Workers do not create final doctrine or skill files.
