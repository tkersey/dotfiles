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

## Global worker identity

Agent `name` values are global registry identities, even when their TOML file
names differ.

The Codebase Doctrine proof worker must use:

```text
file:   codex/agents/codebase-doctrine-proof-mapper.toml
name:   codebase_doctrine_proof_mapper
packet: worker: codebase_doctrine_proof_mapper
```

The existing general-purpose worker remains:

```text
name: proof_surface_mapper
```

Do not give both workers the same internal `name`.

## Root acceptance

Accept only when:

- artifact state matches;
- scope matches;
- material facts have evidence;
- facts and inferences are separate;
- no wrapper/instruction leakage;
- packet contains more than acknowledgement;
- certainty matches evidence;
- stale = no;
- worker identity is one of the workflow-specific names below.

The packet gate deliberately rejects the legacy Codebase Doctrine packet value
`proof_surface_mapper` with a migration diagnostic.

## Worker ownership

```text
codebase_cartographer                repository/system map
authority_state_mapper               owners/transitions/authority
behavioral_law_miner                 behavior/laws/invariants
failure_forensics_analyst            history/failure families/routes
codebase_doctrine_proof_mapper       proof surfaces/gaps
doctrine_portfolio_skeptic           routing/skill challenge
search_saturation_auditor            stop/challenge
```

Workers do not create final doctrine or skill files.
