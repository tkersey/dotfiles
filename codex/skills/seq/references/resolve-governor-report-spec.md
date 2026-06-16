# Resolve Governor Report Spec

Future `$resolve` reports should include governor compliance, not just skill mentions.

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
  mutations_after_stop_rule:
  mutations_after_stop_rule_with_positive_production_net:
  positive_production_net_embargo_required:
  owner_coarseness_gate_required:
  boundary_inventory_required:
  negative_ledger_operational:
  proof_matrix_gate_required:
```

The report should answer whether code growth was blocked or justified after recurrence.
