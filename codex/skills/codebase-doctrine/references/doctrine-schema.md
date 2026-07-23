# CBD-v2 schema

CBD-v2 is a closed graph, not a prose outline.

```yaml
codebase_doctrine:
  doctrine_version: CBD-v2
  doctrine_id:

  intent:
    codebase_doctrine_intent: {}
  artifact_state: {}
  request:
    mode: doctrine | deep
    scope:
    depth:

  search_ledger: []
  evidence_index: []
  claims: []

  repository_fingerprint: {}
  system_map: {}
  authority_map:
    authorities: []
  behavioral_model: {}
  governing_laws: []
  owned_invariants: []
  boundary_rules: []
  failure_families: []
  negative_routes: []
  proof_map:
    proof_surfaces: []

  contradictions: []
  open_questions: []
  knowledge_routes: []

  repository_root_skill: null
  focused_skill_candidates: []
  rejected_skill_candidates: []
  specialist_receipts: []

  saturation: {}
  confidence: {}
  next_actions: []
```

Relational requirements include:

- DIG/grill deterministically compiled to valid CDI-v2;
- artifact state bound to the CDI digest;
- question/evidence and evidence/claim reverse links close;
- every evidence item uses the current artifact state;
- laws and invariants have current or target authority and proof posture;
- proof IDs resolve and executed proof is current;
- canonical negative routes cite ledger IDs and projection fingerprints;
- every durable active claim has exactly one primary route;
- every candidate criterion cites evidence;
- zero skills is valid;
- saturation is relationally proved.

Use `schemas/cbd-v2.schema.json` as the structural description. CBD-v2 must
satisfy the relational closure requirements above.
