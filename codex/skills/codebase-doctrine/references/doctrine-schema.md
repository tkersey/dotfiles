# CBD-v1 Schema

```yaml
codebase_doctrine:
  doctrine_version: CBD-v1
  doctrine_id:

  artifact_state:
  request:

  search_ledger: []
  evidence_index: []
  claims: []

  repository_fingerprint:
  system_map:
  authority_map:
  behavioral_model:
  governing_laws: []
  owned_invariants: []
  boundary_rules: []
  failure_families: []
  negative_routes: []
  proof_map:

  contradictions: []
  open_questions: []
  knowledge_routes: []

  repository_root_skill:
  focused_skill_candidates: []
  rejected_skill_candidates: []

  saturation:
  confidence:
  next_actions: []
```

## Required relational checks

- unique IDs;
- evidence references exist;
- laws have owners, observations/counterexamples, and proof obligations;
- invariants have owner/boundary/counterexample/proof;
- failure families map to laws or remain explicitly provisional;
- every durable knowledge item is routed;
- accepted skills pass candidacy;
- focused accepted count ≤ 5;
- exactly one root skill design;
- saturation verdict valid;
- no terminal exhaustive-understanding claim.

## Handoff

```yaml
codebase_skill_handoff:
  handoff_version: CBSH-v1
  doctrine_id:
  artifact_state_id:
  candidate_id:
  proposed_name:
  governing_law_ids: []
  trigger_examples: []
  non_triggers: []
  consequential_decisions: []
  prohibited_routes: []
  required_artifacts: []
  success_signals: []
  failure_signals: []
  protected_doctrine_ids: []
  allowed_package:
  validation:
```
