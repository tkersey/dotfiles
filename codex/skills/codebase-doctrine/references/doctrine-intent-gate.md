# Doctrine Intent Gate

The gate prevents two opposite failures:

```text
asking users for repository facts that should be researched
and
silently choosing a doctrine target the user did not authorize
```

## DIG-v1

```yaml
doctrine_intent_gate:
  gate_version: DIG-v1
  gate_id:
  provisional_artifact_state:
    repository_root:
    repository_name:
    branch:
    head:
    dirty_state:
    captured_at:
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
  working_defaults:
    - field:
      value:
      consequence_if_wrong:
      confidence:
  material_user_judgment_gaps:
    - gap_id:
      lane:
        target_boundary |
        consumers |
        posture |
        desired_products |
        correctness_priorities |
        non_goals |
        proof_bar |
        persistence
      question:
      why_material:
      discoverable_from_artifacts: no
      options: []
  grill_required: yes | no
  reason:
  grill_handoff:
  direct_intent_candidate:
  gate:
    doctrine_may_proceed: yes | no
```

## Research minimum

Before asking about intent, inspect enough to know:

```text
whether the repository is one coherent product or several
major subsystems and cross-cutting flows
build/test/deployment roots
existing architecture or repository guidance
existing repository-specific skills
evidence of security, compatibility, performance, or operational priorities
```

Do not run the full doctrine workflow merely to decide whether to ask a question.

## User judgment test

A gap belongs in the grill queue only when:

```text
it is not directly discoverable
and
its answer may change search scope, doctrine posture, output shape,
proof obligations, knowledge routing, or skill candidacy
```

## Safe defaults

A default is acceptable when:

- the repository is coherent;
- the user's wording strongly implies it;
- the consequence of being wrong is low or easily reversible;
- the default is recorded in CDI-v1;
- later evidence can reopen it without invalidating large amounts of work.

## Grill-required examples

```text
A monorepo includes unrelated services and libraries.
The user says "correctness doctrine" but may mean current facts or target design.
A skill portfolio may be unwanted; the user may want an atlas only.
Security versus compatibility priorities materially change the law/proof search.
The requested proof bar could mean code reading, executable proof, or production evidence.
```

## Grill-not-required examples

```text
The target subsystem is named explicitly.
The user explicitly asks for atlas plus skill candidates.
Survey mode is requested.
An existing CDI-v1 remains applicable during refresh.
The missing item is a file path or build command discoverable from the repository.
```

## Re-entry

A research-triggered re-entry is allowed once when the discovered system contradicts the locked target.

Re-entry is not allowed merely because the analysis found more detail.
