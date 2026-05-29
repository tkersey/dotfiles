# Authority fanout for adversarial-reviewer

Use custom read-only Codex agents to parallelize review without turning extra analysis into extra findings.

## Agents

- `adv_review_evidence_authority`
- `adv_review_soundness_authority`
- `adv_review_invariant_scope_authority`
- `adv_review_hazard_footgun_authority`
- `adv_review_complexity_remediation_authority`
- `adv_review_verification_authority`
- `adv_review_finding_skeptic`

## Parent rules

1. Launch all required lanes before waiting when the review is broad or implementation-bound.
2. Keep all workers read-only.
3. Give every worker the same `artifact_state_id`, `review_surface_id`, candidate IDs, and exact scope.
4. Require packet-native outputs.
5. Reject stale, wrong-scope, no-evidence, acknowledgement-only, generic, or wrapper-leaking packets.
6. Treat packets as bounded authority, not votes.
7. Root may downgrade any candidate but may not upgrade a vetoed/unresolved candidate into a material finding.
8. Missing required authority coverage blocks `change_agenda_allowed`.

## Minimal launch prompt

```text
Use the adversarial-reviewer authority panel. Spawn read-only custom agents:
- adv_review_evidence_authority
- adv_review_soundness_authority
- adv_review_invariant_scope_authority
- adv_review_hazard_footgun_authority
- adv_review_complexity_remediation_authority
- adv_review_verification_authority
- adv_review_finding_skeptic

Assign artifact_state_id=<...>, review_surface_id=<...>, candidate ids=<...>, scope=<...>. Require authority_packet YAML. Root will synthesize; workers must not edit files.
```
