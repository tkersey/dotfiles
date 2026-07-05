# EPG-v1 — Execution Policy Graph

```yaml
execution_policy_graph:
  policy_version: EPG-v1
  policy_id:
  revision:
  parent:
    policy_id:
    digest:
  created_at:
  profile:
    fast |
    balanced |
    strict |
    campaign

  source:
    mode:
      spec_handoff |
      direct_brief |
      existing_policy_revision
    authority:
    source_refs: []
    source_digest:
    spec_id:
    spec_governance_ref:
    artifact_state:
      repo_bound:
      repository:
      branch:
      base:
      head:
      dirty_fingerprint:
    locked_decision_refs: []
    current:
      yes |
      no |
      unknown

  goal:
    objective:
    obligations:
      - obligation_id:
        statement:
        source_refs: []
        terminal_predicate_refs: []
        proof_refs: []
    terminal_predicates:
      - predicate_id:
        statement:
        atom:
    safety_invariants:
      - invariant_id:
        statement:
        violation_atom:
        source_refs: []
    forbidden_states:
      - forbidden_id:
        statement:
        atom:
        response_terminal:

  regime:
    kind:
      clear |
      complicated |
      complex |
      chaotic
    confidence:
      high |
      medium |
      low
    rationale:
    reclassify_on_observation_refs: []

  belief:
    facts:
      - fact_id:
        atom:
        statement:
        evidence_refs: []
        confidence:
          high |
          medium |
          low
        invalidators: []
    unknowns:
      - unknown_id:
        statement:
        consequence_if_wrong:
        decision_relevance:
        evidence_required: []
        observation_refs: []
        status:
          open |
          resolved |
          blocked
        urgency:
          critical |
          high |
          medium |
          low

  observations:
    - observation_id:
      source_kind:
        command |
        test |
        metric |
        inspection |
        user_decision |
        external_event
      command_or_evidence:
      predicate:
      freshness:
      evidence_schema:
      resolves_unknown_refs: []
      outcomes:
        - outcome:
          atom:

  actions:
    - action_id:
      kind:
        inspect |
        probe |
        decide |
        mutate |
        prove |
        stabilize |
        deploy |
        rollback
      owner:
      preconditions:
        all: []
        any: []
        none: []
      requires_actions: []
      mutation_boundary:
        kind:
          repository |
          external |
          docs |
          none
        paths: []
        symbols: []
      lock_roots: []
      expected_effects:
        facts_added: []
        unknowns_resolved: []
        obligations_closed: []
        potential_delta: {}
      expected_observation_refs: []
      failure_observation_refs: []
      proof_obligations:
        - proof_id:
          statement:
          evidence_kind:
          command_or_evidence:
          artifact_binding:
      rollback:
        trigger_atoms: []
        action_id:
        instructions:
      utility:
        obligation_reduction:
        information_gain:
        downstream_unlock:
        proof_gain:
        execution_cost:
        irreversible_risk:
        semantic_surface_growth:
        rework_risk:
      repeatable:

  policy:
    selection:
      lexicographic_utility
    utility_order:
      - maximize: obligation_reduction
      - maximize: information_gain
      - maximize: downstream_unlock
      - maximize: proof_gain
      - minimize: irreversible_risk
      - minimize: semantic_surface_growth
      - minimize: rework_risk
      - minimize: execution_cost
    rules:
      - rule_id:
        priority:
        when:
          all: []
          any: []
          none: []
        candidate_action_ids: []
        terminal:
        rationale:
        obligation_refs: []
        unknown_refs: []
        evidence_refs: []
        replan_if_atoms: []
    tie_breakers:
      - lowest_irreversible_risk
      - lowest_semantic_surface_growth
      - action_id

  potential:
    lexicographic_order: []
    dimensions:
      - dimension_id:
        statement:
        direction:
          minimize |
          maximize
        current_value:
        terminal_threshold:
    initial: {}

  safety_shield:
    rules:
      - shield_id:
        when:
          all: []
          any: []
          none: []
        forbids_action_ids: []
        forbids_action_kinds: []
        requires_atoms: []
        response:
          block |
          rollback |
          return_to_spec
        reason:

  horizon:
    mutation_actions_max:
    evidence_actions_max:
    delivery_transitions_max:

  initial_state:
    state_version: EPS-v1
    state_id:
    satisfied_atoms: []
    completed_actions: []
    failed_actions: []
    resolved_unknowns: []
    closed_obligations: []
    current_potential: {}
    active_action_id:

  terminal_states:
    success:
      when:
        all: []
        any: []
        none: []
      proof_refs: []
    blocked:
      when:
        all: []
        any: []
        none: []
    return_to_spec:
      when:
        all: []
        any: []
        none: []
    rollback:
      when:
        all: []
        any: []
        none: []

  invalidators:
    - invalidator_id:
      condition:
      required_action:
      affected_refs: []

  challenge:
    candidate:
    disposition:
    reason:
    affected_refs: []
    source_change_required:

  revision_summary:
    parent_diff_ref:
    policy_changes: []
    semantic_changes: []
    source_changes: []

  handoff:
    next_owner:
      actuating |
      spec-pipeline |
      grill-me |
      blocked
    runtime_ready:
    mutation_allowed: no
    gate_result:
      pass |
      stale |
      return_to_spec |
      return_to_grill |
      blocked
    reason:

  gate:
    source_current:
    semantic_drift:
      none |
      authorized |
      unauthorized
    obligations_covered:
    critical_unknowns_observable_or_blocked:
    actions_bounded:
    policy_references_valid:
    policy_closed:
    safety_shield_complete:
    potential_complete:
    terminal_states_complete:
    downstream_runtime_ready:
    fresh_eyes_blockers:
    policy_ready:
```

## Atom namespace

Atoms are stable strings:

```text
fact:<fact-id>
obs:<observation-id>=<outcome>
action:<action-id>=success
action:<action-id>=failure
unknown:<unknown-id>=resolved
unknown:<unknown-id>=blocked
obligation:<obligation-id>=closed
terminal:<name>
custom:<stable-id>
```

Every condition atom must be declared by a fact, observation outcome, action, unknown, obligation, terminal state, or explicit custom atom declaration.

## Closure law

Every action outcome used by the model must lead to at least one:

```text
later policy rule
terminal state
shield response
explicit replan/authority return
```

An action whose success or failure leaves the policy with no lawful successor is incomplete.
