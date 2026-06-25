# Doctrine Intent Gate v2

The gate separates discoverable repository facts from user-owned doctrine
choices.

```text
Do not ask the user for facts the repository can answer.
Do not silently choose a doctrine target the user owns.
Do not lock a repository-derived law before repository research.
```

## DIG-v2

```yaml
doctrine_intent_gate:
  gate_version: DIG-v2
  gate_id:
  provisional_artifact_state:
    repository_root:
    repository_name:
    branch:
    head:
    dirty_state:
    tracked_diff_sha256:
    untracked_path_digest:
    captured_at:
  provisional_artifact_state_digest:

  repository_facts_researched:
    - fact_id:
      statement:
      evidence_ref:
      confidence:

  user_request:
    original_ask:
    explicit_target:
    explicit_consumers: []
    explicit_products: []
    explicit_posture:
    explicit_non_goals: []
    explicit_proof_bar:
    explicit_compatibility_posture:

  working_defaults:
    - field:
      value:
      consequence_if_wrong:
      confidence:

  material_user_judgment_gaps:
    - gap_id:
      lane:
      question:
      why_material:
      discoverable_from_artifacts: no
      options: []

  grill_required: yes | no
  reason:
  grill_handoff:
  direct_intent_seed:
  gate:
    doctrine_may_proceed: yes | no
```

## Allowed judgment lanes

```text
target_boundary
consumers
posture
desired_products
correctness_priorities
non_goals
proof_bar
compatibility_posture
versioning_or_migration
persistence
```

## Direct intent seed

A direct seed contains the eventual CDI fields except source metadata, intent ID,
and `doctrine_allowed`.

Use:

```text
primary_correctness_question
primary_risk_or_priority
user_supplied_invariant_hypotheses
```

Do not require a repository-derived `primary_invariant` at intake.

## Compiler

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/intent_compile.py \
  gate.yaml [--grill grill.yaml] --output intent.yaml
```

CDI should be compiler output, not a hand-projected summary.
