# CBD-v1 Schema

```yaml
codebase_doctrine:
  doctrine_version: CBD-v1
  doctrine_id:

  intent:
    codebase_doctrine_intent:
      intent_version: CDI-v1
      intent_id:
      source:
      target:
      consumers: []
      posture:
      desired_products: []
      primary_invariant:
      correctness_priorities: []
      non_goals: []
      proof_bar:
      compatibility_posture:
      persistence_posture:
      skill_portfolio_requested:
      enforcement_routing_requested:
      assumptions: []
      deferred_questions: []
      doctrine_allowed:

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

## Intent checks

- CDI-v1 is valid and `doctrine_allowed` is yes.
- Artifact state carries the same `intent_id`.
- If source is `grill`, a grill packet digest is present.
- Scope, consumers, posture, products, non-goals, and proof bar are explicit.
- CBD output does not silently expand beyond included boundaries or products.

Legacy CBD-v1 without intent may be inspected with a warning, but new doctrine generation should validate with:

```bash
python3 codex/skills/codebase-doctrine/tools/doctrine_gate.py \
  --require-intent doctrine.yaml
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
  intent_id:
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
