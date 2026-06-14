# Route-Wave Artifact

`$resolve` publishes route/RCP/universalist decisions into a first-class artifact.

Suggested path:

```text
.step/proof/resolve/<resolve-run-id>/review-wave-<n>.route.yml
```

Shape:

```yaml
resolve_review_wave_packet:
  packet_version: RRW-v1
  resolve_run_id:
  artifact_state_id:
    branch:
    base_sha:
    head_sha:
    target_fingerprint:
  review_wave:
    backend:
    receipt_id:
    finding_ids: []
  route_receipts:
    - review_item_id:
      adjudication_route:
      rcp_required: yes | no
      rcp_packet_id:
      universalist_check_required: yes | no
      universalist_decision: use-universalist | not-needed | blocked
      selected_route:
      proof_required: []
  rcp_packets:
    - packet_id:
      packet_status:
      selected_normal_form:
      abstraction_rent_status:
      proof_matrix_summary:
      commit_boundary:
  universalist_checks:
    - packet_id:
      decision:
      boundary_packet_ref:
      prior_not_needed_falsified: yes | no
  falsification_rules:
    - cluster_id:
      if_same_cluster_reappears:
      prior_decision_invalidated:
      next_required_action:
  gate:
    route_receipts_complete: pass | fail
    rcp_required_packets_present: pass | fail | not-required
    universalist_checks_complete: pass | fail | not-required
    rent_paid_or_not_applicable: pass | fail | not-required
    implementation_handoff_allowed: yes | no
```

If a route/RCP/universalist decision is not in a route-wave artifact or a final visible `Resolve route artifact:` line, it does not count for closure.
