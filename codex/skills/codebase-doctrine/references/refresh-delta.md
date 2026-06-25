# Refresh Delta

A refresh never silently rewrites history.

```yaml
codebase_doctrine_delta:
  delta_version: CBDD-v1
  delta_id:
  prior_doctrine_id:
  prior_artifact_state_id:
  new_artifact_state_id:
  changed_paths: []
  invalidated_ids: []
  retained_ids: []
  added_ids: []
  modified_ids: []
  proof_rechecks: []
  intent_drift:
    detected: yes | no
    resolution:
  resulting_doctrine_id:
```

The identity partitions are disjoint. Changed laws, invariants, and proof
surfaces require proof rechecks.

If intent changed, the delta records the mismatch; only user resolution or an
accepted new CDI-v2 authorizes the new target.
