# Universalist Check

The universalist check prevents repeated existing-owner repairs from hiding a missing boundary artifact.

## Required field

```yaml
universalist_check:
  considered: yes | no
  trigger:
    same_cluster_findings: 0
    existing_owner_repair_attempted: yes | no
    missing_boundary_artifact: yes | no
    duplicated_projection: yes | no
    protocol_or_state_machine_missing: yes | no
    generated_provenance_gap: yes | no
    public_contract_drives_internals: yes | no
    effect_or_callback_ir_missing: yes | no
    repeated_existing_owner_repairs: yes | no
  decision: use-universalist | not-needed | blocked
  reason: "..."
  boundary_packet_ref: "none | path-or-inline-id"
```

## Must consider when

- same-cluster findings >= 2;
- existing-owner repair already attempted;
- add-new-surface candidate;
- public/fallback/compatibility/parser-tolerance surface candidate;
- repeated boundary/protocol/state-machine review findings.

## Decision meanings

- `use-universalist`: run `$universalist` or emit root-equivalent `universal_boundary_packet`.
- `not-needed`: existing owner / lower abstraction route is sufficient.
- `blocked`: boundary artifact question is unresolved; no mutation.
