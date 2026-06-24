# AC-v2 — Acceptance Contract and Sealed Observation Language

AC-v2 is the intent authority for one review campaign.

```yaml
acceptance_contract:
  contract_version: AC-v2
  contract_id:
  campaign_id:
  fingerprint:

  source:
    plan_refs: []
    issue_refs: []
    pr_intent_refs: []
    compatibility_baseline_refs: []

  goal:
    goal_id:
    statement:

  required:
    - requirement_id:
      statement:
      source_refs: []
      observable_witnesses: []

  compatibility:
    - obligation_id:
      statement:
      baseline_ref:
      observable_witnesses: []

  forbidden:
    - prohibition_id:
      statement:
      source_refs: []
      observable_witnesses: []

  permitted_but_unrequired:
    - behavior_id:
      statement:
      reason:

  non_goals:
    - non_goal_id:
      statement:
      source_refs: []

  proof_bar:
    - proof_id:
      statement:
      command_or_surface:

  observation_language:
    actors: []
    operations: []
    states: []
    transitions: []
    externally_visible_results: []
    failure_observations: []
    authority_observations: []

  horizon:
    state:
      open |
      sealed |
      rebased
    sequence:
    sealed_at:
    prior_fingerprint:
    rebase_reason:
    rebase_authority:

  authority:
    accepted_by:
    accepted_at:
    change_requires_explicit_rebase: yes

  gate:
    sources_bound:
    required_behavior_nonempty:
    observation_language_nonempty:
    non_goals_explicit:
    proof_bar_present:
    horizon_consistent:
    seal_allowed:
```

## Semantics

```text
required / compatibility / forbidden
  may admit counterexamples and justify kernel obligations

permitted_but_unrequired
  may remain supported but cannot justify adding code

non_goals / outside language
  cannot enter delivery without rebase
```

## Rebase

A rebase is an explicit campaign event.

It:

- increments horizon sequence;
- records old and new fingerprints;
- invalidates CEB, MBK, RC, design, conformance, PHI, and closure receipts;
- requires renewed authority;
- never happens implicitly because a reviewer found something interesting.
