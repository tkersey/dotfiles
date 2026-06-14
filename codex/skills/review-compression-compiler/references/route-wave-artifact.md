# Route-Wave Artifact

`$resolve` publishes route/RCP/RDP/negative-ledger/universalist decisions into a first-class artifact.

Suggested path:

```text
.step/proof/resolve/<resolve-run-id>/review-wave-<n>.route.yml
```

Shape includes:

```yaml
resolve_review_wave_packet:
  packet_version: RRW-v1
  route_receipts: []
  rcp_packets: []
  rdp_packets: []
  negative_evidence:
    pass_status: pass | fail | not-required
    active_exclusions: []
    captured_failures: []
    reopened_entries: []
  universalist_checks: []
  falsification_rules: []
  gate:
    route_receipts_complete: pass | fail
    negative_evidence_complete: pass | fail | not-required
    rcp_required_packets_present: pass | fail | not-required
    distillation_required_packets_present: pass | fail | not-required
    universalist_checks_complete: pass | fail | not-required
    rent_paid_or_not_applicable: pass | fail | not-required
    implementation_handoff_allowed: yes | no
```

If a decision is not in a route-wave artifact or a final visible `Resolve route artifact:` line, it does not count for closure.
