# Example Invocations

## Tier 1 local bug fix

Use compact output:

```markdown
## Compact Verification Note

- Artifact state: `git diff -- service/parser.py tests/test_parser.py`
- Intended change: reject empty quoted identifiers instead of accepting them as empty strings.
- Scope checked: parser helper, two direct callers, parser tests.
- Verification performed: `pytest tests/test_parser.py -q` passed.
- Actionability: `implement`
- Remaining risk: no integration parser roundtrip test was run.
```

## Tier 2 proof-surface closure

Emit and gate a full packet:

```bash
python codex/skills/context-bounded-verification/tools/context_verification_gate.py /tmp/cbv-packet.md
```

A valid closure packet may say `pass-with-residual-risk`, not global pass:

```yaml
verification_packet:
  packet_version: CBV-GATE-v1
  skill: context-bounded-verification
  mode: closure
  objective:
    current_workflow_objective: "Close the proof gap for provider-route certificate support."
    semantic_change: "Checker now requires selected provider identity, not witness presence."
    done_condition: "Wrong-provider negative fixture fails old logic and passes current logic."
  artifact_state:
    state_id: "head:abc123 base:def456 diff:provider-route-proof"
    source: current-diff
    freshness: current
    dirty_state: dirty
    evidence_refs: ["git diff -- src/cert.zig tests/cert_route.zig"]
  tier:
    declared: tier2
    drivers: ["proof-surface", "generated-artifact"]
    rationale: "Verifier semantics changed."
  scope:
    in_scope: ["provider route checker", "route mismatch regression"]
    out_of_scope: ["provider selection", "routing optimizer"]
    must_not_change: ["matching provider certificates still pass"]
  direction_fit:
    current_objective_fit: aligned
    direction_source: user-current-instruction
    stale_or_wrong_objective_pressure: []
  evidence_ledger:
    - id: E1
      claim: "Predicate compares selected provider ref."
      claim_type: proof
      evidence_kind: current-artifact
      evidence_ref: "src/cert.zig:120-155"
      artifact_state_match: yes
      supports: yes
      actionability: closure-pass
    - id: E2
      claim: "Wrong-provider same-kind witness is rejected."
      claim_type: proof
      evidence_kind: current-test
      evidence_ref: "tests/cert_route.zig:test rejects wrong provider"
      artifact_state_match: yes
      supports: yes
      actionability: closure-pass
  blast_radius:
    surfaces_checked:
      - name: generated-artifact
        status: checked
        evidence_ref: "src/cert.zig:120-155"
      - name: tests
        status: checked
        evidence_ref: "tests/cert_route.zig:44-89"
    unchecked_material_surfaces: []
  validation:
    commands:
      - command: "zig build test --summary all"
        result: pass
        evidence_ref: "terminal log 2026-05-29"
        artifact_state_match: yes
    tests_added_or_updated: ["wrong-provider route mismatch regression"]
    negative_or_counterexample_checks: ["wrong-provider same-kind witness rejected"]
    proof_surface_changed: yes
    test_gap_reason: "none known"
  authority:
    root_owned: [artifact-state-acceptance, final-readiness, handoff-routing, implementation-authorization, scope-boundary, tier-decision]
    fanout:
      required: no
      reason: "Single proof surface with direct command evidence."
    subagent_packets: []
  closure:
    readiness: pass-with-residual-risk
    closure_claim: "Current diff appears ready for review on the provider-route proof surface."
    blockers: []
    remaining_risk: ["Full downstream integration not run."]
    next_action: "Open PR or ask human owner to review route semantics."
  handoff:
    allowed: no
    target: none
    agenda: []
    must_not_do: []
```

## Valid blocked packet

A block can pass the gate when it is explicit:

```yaml
closure:
  readiness: blocked
  closure_claim: "Cannot claim readiness because the current checkout differs from the test output."
  blockers:
    - "Rerun `zig build test` after final diff."
  remaining_risk:
    - "Old command output may not represent current tree."
  next_action: "Rerun proof on current tree, then re-gate."
handoff:
  allowed: no
  target: none
  agenda: []
  must_not_do: []
```

## Invalid laundering patterns

These should fail the gate:

- `artifact_state.freshness: stale` with `closure.readiness: pass`;
- `evidence_kind: memory` with `actionability: implement`;
- Tier 2 pass with only manual intuition and no command/test/CI/runtime proof;
- proof-surface changed with no negative fixture;
- handoff allowed without `must_not_do` boundaries;
- implementation handoff when readiness is `validate-only`.
