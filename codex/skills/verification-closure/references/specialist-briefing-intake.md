# Specialist briefing intake

Specialist briefings are high-signal inputs. They are not proof by themselves.

## Expected roles

- `verification_auditor`: direct-path, regression, and critical-invariant coverage
- `invariant_auditor`: invariant grading and unknown-critical pressure
- `hazard_hunter`: misuse and foot-gun pressure
- `complexity_auditor`: incidental complexity and reviewability pressure
- `evidence_mapper`: implicated surfaces and true execution path
- `negative-ledger-mapper`: prior failed routes, active/stale/reopened negative evidence, and safest next frontier

## Intake rules

1. Normalize every briefing into one or more closure gates.
2. Look for direct supporting evidence before upgrading confidence.
3. Validate `artifact_state_id`, `artifact_state_label`, scope, packet status, and stale flag.
4. Require a Specialist Value Receipt for every specialist packet.
5. If two briefings materially conflict, design the smallest resolving check.
6. If a briefing raises a material concern that cannot be directly tested, decide whether it is:
   - bounded by other direct evidence,
   - an accepted residual risk,
   - or a not-ready blocker.
7. Do not repeat broad de novo review. Closure is for proof and gating.
8. Do not let a specialist own final pass/fail.

## Value receipt intake

Every packet should have:

```yaml
specialist_value_receipt:
  role: "..."
  packet_status: accepted | stale | transport-invalid | wrong-scope | timeout | superseded
  artifact_state_id_match: yes | no | unknown
  scope_match: yes | no | unknown
  uncertainty_class: evidence | soundness | invariant | hazard | complexity | verification | negative-evidence | other
  route_changed: yes | no
  finding_added: yes | no
  proof_changed: yes | no
  risk_retired: yes | no
  value: positive | neutral | negative
  used_for: "..."
  reason: "..."
```

`value: positive` requires at least one material decision delta: route change, finding addition, proof change, or risk retirement.

## Negative-ledger-mapper intake

For `negative-ledger-mapper`, closure asks:
- Did it identify active applicable negative evidence?
- Did it mark stale/superseded/reopened evidence with support?
- Did it change route choice, proof choice, one-change challenge, or safest next frontier?
- Are all learnings hits backed by evidence and applicability checks?
- Does any active negative evidence keep the closure gate open?

## Minimal synthesis pattern

Use briefings to answer:
- What is the single highest-signal next check?
- Which critical invariant is still open?
- Which material foot-gun is still unbounded?
- Which complexity concern is a real closure blocker versus a residual design risk?
- Which active negative evidence, if any, blocks closure?
- Which specialist packets were value-positive, neutral, or rejected?
