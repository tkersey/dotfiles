# Verification Output Contract

`context-bounded-verification` is allowed to be lightweight for low-risk work, but any output that gates closure, readiness, implementation, or handoff must expose a packet.

## Compact Tier 0 note

```markdown
Verified: checked current diff `[artifact_state_id]`; no behavioral files changed. Remaining risk: low, limited to review oversight.
```

## Compact Tier 1 note

```markdown
## Compact Verification Note

- Artifact state: `[current tree/diff/commit]`
- Intended change: `[specific behavior]`
- Scope checked: `[files/callers/tests]`
- Verification performed: `[commands/tests/manual checks]`
- Actionability: `implement | validate-only | proof-only | no-change | defer | blocked`
- Remaining risk: `[specific residual risk]`
```

## Full packet fields

The full packet is the authority-bearing output for Tier 2/Tier 3 and closure/handoff. Use this exact shape.

```yaml
verification_packet:
  packet_version: CBV-GATE-v1
  skill: context-bounded-verification
  mode: implementation | review | closure | verification | validation-only | no-change | handoff | audit
  objective:
    current_workflow_objective: "..."
    semantic_change: "..."
    done_condition: "..."
  artifact_state:
    state_id: "..."
    source: current-tree | current-diff | pull-request | supplied-snippet | prior-session | unknown
    freshness: current | stale | superseded | unknown
    dirty_state: clean | dirty | unknown | not-applicable
    evidence_refs: []
  tier:
    declared: tier0 | tier1 | tier2 | tier3
    drivers: []
    rationale: "..."
  scope:
    in_scope: []
    out_of_scope: []
    must_not_change: []
  direction_fit:
    current_objective_fit: aligned | partial | conflicting | unknown
    direction_source: user-current-instruction | plan | pr-body | issue | repo-convention | current-artifact | unknown
    stale_or_wrong_objective_pressure: []
  evidence_ledger:
    - id: E1
      claim: "..."
      claim_type: validity | actionability | scope | risk | proof | closure
      evidence_kind: current-artifact | current-diff | current-test | current-ci | current-command | manual-inspection | runtime-observation | prior-session | memory | reviewer-claim | none
      evidence_ref: "..."
      artifact_state_match: yes | no | unknown
      supports: yes | partial | no | unknown
      actionability: implement | validate-only | proof-only | no-change | defer | blocked | closure-pass | none
  blast_radius:
    surfaces_checked:
      - name: "..."
        status: checked | not-applicable | unchecked | unknown
        evidence_ref: "..."
    unchecked_material_surfaces: []
  validation:
    commands:
      - command: "..."
        result: pass | fail | not-run | skipped
        evidence_ref: "..."
        artifact_state_match: yes | no | unknown
    tests_added_or_updated: []
    negative_or_counterexample_checks: []
    proof_surface_changed: yes | no | unknown
    test_gap_reason: "..."
  authority:
    root_owned:
      - tier-decision
      - scope-boundary
      - artifact-state-acceptance
      - final-readiness
      - implementation-authorization
      - handoff-routing
    fanout:
      required: yes | no
      reason: "..."
    subagent_packets: []
  closure:
    readiness: pass | pass-with-residual-risk | validate-only | proof-only | no-change | defer | blocked
    closure_claim: "..."
    blockers: []
    remaining_risk: []
    next_action: "..."
  handoff:
    allowed: yes | no
    target: none | accretive-implementer | fixed-point-driver | review-adjudication | verification-closure | human-owner | other
    agenda: []
    must_not_do: []
```

## Field semantics

### `objective`

The current objective is the task being solved now. It is not the same as an old plan, PR title, reviewer request, or memory hit unless the root confirms freshness and objective fit.

### `artifact_state`

Use a state label that lets a human tell what was inspected: commit hash, base/head pair, diff hash, PR ref, tree status, or explicit current-tree label. The state must be `current` for pass or handoff.

### `evidence_ledger`

Each material claim gets one row. A claim may be valid but not actionable. A claim may be actionable but only as validation. `memory`, `prior-session`, and `reviewer-claim` are allowed as context but cannot support `implement` or `closure-pass`.

### `validation`

Commands must be commands actually run. A skipped or not-run command is not proof; it can only explain residual risk or a block. For verifier/proof-surface changes, include a negative/counterexample check that would fail the too-weak predicate.

### `authority`

Root-owned entries are required to prevent subagent or reviewer laundering. Subagent packets are evidence receipts, not final decisions.

### `closure`

Closure may be `blocked`, `defer`, `validate-only`, `proof-only`, or `no-change`. These are first-class successful outcomes when the evidence does not justify pass or implementation.

### `handoff`

A handoff is a permissioned route, not a suggestion. It requires current implement-actionable evidence, scope boundaries, and `must_not_do` constraints.
