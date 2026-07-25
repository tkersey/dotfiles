# EPG-v1 — Execution Policy Graph

```yaml
execution_policy_graph:
  policy_version: EPG-v1
  policy_id:
  plan_id:
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

  architectonic:
    mode:
      not_required |
      explicit
    reason:
    seams:
      - seam_id:
        authority:
          source_fixed |
          source_bounded |
          plan_local
        boundary:
          owner:
          source:
          target:
        axis:
          data_shape |
          behavior |
          syntax_semantics |
          composition |
          representation |
          ownership |
          context |
          transport |
          proof
        typed_hole:
          object |
          map |
          representation |
          interpreter |
          composition |
          equivalence |
          owner |
          proof
        live_obligation_refs: []
        required_observation_refs: []
        compatibility_and_migration: []
        host_capabilities: []
        incumbent:
          organization:
          factor_refs: []
        candidate_movements:
          preserve:
          restrict_admitted_domain:
          strengthen_representation_or_owner:
          ablate_or_normalize:
        disposition:
          selected |
          evidence_conditioned |
          underdetermined |
          obstructed
        selected_organization:
        decision_observation_refs: []
        factors:
          - factor_id:
            owner:
            live_obligation_refs: []
            obligation_status:
              live |
              moved |
              expired |
              duplicated |
              invalid |
              unknown
            disposition:
              preserve |
              factor |
              quotient |
              ablate |
              normalize |
              introduce
        law:
        falsifier:
        residual_obligations: []
        invalidators: []
    composition:
      seam_dependency_edges:
        - from_seam_ref:
          to_seam_ref:
          relation:
      independent_seam_sets: []
    conceptual_compression:
      live_obligation_refs: []
      independent_factor_refs: []
      independent_owner_refs: []
      exceptional_path_refs: []
      dominated_factor_refs: []

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
      architectonic_seam_refs: []
      realizes_factor_refs: []
      retires_factor_refs: []
      preservation_observation_refs: []
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
        terminal_threshold:
    baseline_expectation: {}

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

  # Omit on initial plans. Include only when revising an existing EPG.
  revision_summary:
    parent_diff_ref:
    policy_changes: []
    semantic_changes: []
    source_changes: []
    # The remaining fields exist only when architecture changed.
    architectonic_changes:
      - seam_ref:
        prior_organization:
        successor_organization:
        relation:
          preserve |
          restrict |
          strengthen |
          factor |
          quotient |
          ablate |
          normalize |
          replace
    plan_transport:
      preserved_action_refs: []
      revised_action_refs: []
      retired_action_refs: []
      introduced_action_refs: []
    square_results:
      - seam_ref:
        horizontal_before_refs: []
        vertical_change_refs: []
        horizontal_after_refs: []
        preserved_observation_refs: []
        result:
          commutes |
          fails |
          underdetermined
        falsifier:

```

## Architectonic laws

- `architectonic.mode = not_required` is legal only when the plan makes no
  consequential architecture or abstraction decision. `reason` explains why
  escalation is unnecessary. `seams` must be empty; composition,
  conceptual-compression, and action architectonic fields may be omitted. If
  present, they must be empty.
- `architectonic.mode = explicit` requires at least one consequential seam and
  complete action binding for every affected seam.
- A consequential action must reference the seam it realizes, migrates, preserves,
  or retires.
- An action may realize or retire a factor only when the factor's owning seam appears
  in the action's `architectonic_seam_refs`.
- An action must not realize a factor whose disposition is `quotient`, `ablate`, or
  a superseded `normalize` predecessor.
- A `source_fixed` seam may be preserved or returned to source authority; it may not
  be silently replaced.
- A `source_bounded` or `plan_local` seam may change during synthesis when the
  resulting plan transport preserves required observations and authority.
- Raw counts in `conceptual_compression` are comparison evidence, not a scalar
  optimization objective.
- Architecture changes partition affected actions into preserved, revised, retired,
  and introduced sets.
- A square result of `fails` blocks convergence. `underdetermined` requires an
  observation-conditioned route or blocker.
- `gate` and `handoff` are not EPG fields. The policy may not certify its own
  readiness or select its eventual consumer.
- EPG-v1 is a source plan, not runtime state or execution authority. A compatible
  execution-policy compiler may privately lower it to an opaque compiled policy.
- Optional validation uses
  `seq execution-policy-compile --file <epg.json> --format json`; accept only
  `compiled: true`, require `execution-policy-compiler/v1`, and bind its
  `source_policy_digest` to the emitted source. Compiler absence does not block Plan
  emission.
- The compiler's private normalized representation is transient and must not be
  persisted as another Plan artifact.

For a bounded local action inside an unchanged exact boundary, the architectonic
surface is only:

```yaml
architectonic:
  mode: not_required
  reason: "One bounded documentation edit inside an unchanged exact boundary."
  seams: []

actions:
  - action_id: ACTION-DOC-FIX
```

## Runtime ownership

`source.artifact_state` records the repository state against which Plan synthesized
the EPG. It does not claim that state remains current.

Plan may declare facts needed by policy conditions, but it never marks runtime facts
as satisfied. Runtime currentness, completed or failed actions, resolved unknowns,
closed obligations, observed potential, active work, decisions, and transition
receipts belong to the policy consumer.

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

Every condition atom must be declared by a fact, observation outcome, action,
unknown, obligation, terminal state, or explicit custom atom declaration.

## Closure law

Every action outcome and architectonic decision observation used by the model must
lead to at least one:

```text
later policy rule
terminal state
shield response
explicit replan/authority return
```

An action or architectural outcome whose success or failure leaves the policy with
no lawful successor is incomplete.
