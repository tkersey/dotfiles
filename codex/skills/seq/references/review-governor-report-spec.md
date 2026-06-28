# Review Governor Report Spec

Future review-closure reports should include governor compliance, not just workflow mentions.

Required sections:

- finding-to-route matrix;
- cluster trajectory;
- decision impact;
- skill obligation matrix;
- governor compliance;
- material improvement score;
- recommendation carry-forward;
- report confidence;
- report value score.

Key new fields:

```yaml
governor_compliance:
  mutation_permits_required:
  mutation_permits_emitted:
  mutations_after_stop_rule_without_permit:
  mutations_after_stop_rule_with_positive_production_net:
  positive_production_net_embargo_required:
  owner_coarseness_gate_required:
  boundary_inventory_required:
  negative_ledger_operational:
  proof_matrix_gate_required:
```

The report should answer whether every same-cluster post-recurrence mutation was explicitly permitted.
