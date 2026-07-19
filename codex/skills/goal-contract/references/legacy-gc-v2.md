# Frozen legacy GC-v2

Use this reference only for an existing goal whose immutable protocol marker is
`legacy-actuating-v1`. Historical readers remain valid; do not reinterpret,
upgrade in place, or mix this shape with artifact-kernel semantics.

~~~yaml
goal_contract:
  version: GC-v2
  goal_id:
  objective:
    summary:
    mode: direct | goal | review | debug | migration | hardening
    non_goals: []
  source:
    kind: accepted-spec | direct-goal
    source_ref:
    source_digest:
    execution_authority_ref:
    authority_owner: spec-pipeline | user
    current: true | false
  artifact_scope:
    repo:
    base_sha:
    branch:
    head_sha:
    state_fingerprint:
    allowed_paths: []
  done:
    success_state: []
    explicitly_not_done_when: []
    stop_when: success | blocked | invalid-proof
  verification:
    primary_checks: []
    secondary_checks: []
    negative_checks: []
    artifacts_to_inspect: []
    unavailable_checks: []
  constraints:
    must_preserve: []
    forbidden_changes: []
    compatibility: []
    public_behavior: preserve | may-change-with-proof | unspecified
  review_policy:
    active: true | false
    relation_to_goal: in-scope-only | include-nearby-risk | adjudicate-all
    default_disposition: classify-before-resolution
    repair_policy: correctness-refinement
    strategy_owner: review-resolution/v1
    reabstraction_trigger:
      - repeated-class
      - ownership-boundary
      - dominated-abstraction
      - new-semantic-machinery
  authority:
    mutation_requested: true | false
    dependency_changes_allowed: true | false
    public_effects: forbidden | ship-only
    unsupported_coordination_required: true | false
  ambiguity:
    discoverable_facts_to_research: []
    human_owned_decisions: []
    assumptions_allowed: []
~~~

Continue to use the frozen legacy projection into `actuation-open/v1`, its
existing verifier-backed obligations, and its established review and closure
semantics. New goals and artifact-kernel goals must not select this format.
