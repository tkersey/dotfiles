# CAS Worker Attribution Special Spec

This is a `$seq` / CAS tooling gap, not a `$resolve` implementation requirement.

Desired surface:

```bash
seq cas-lane-attribution --session-id <resolve-session> --format json
```

Expected shape:

```yaml
cas_lane_attribution:
  parent_resolve_session:
  lane_id:
  receipt_id:
  target_head:
  worker_session_candidates: []
  declared_worker_skills: []
  review_verdict:
  finding_ids: []
  confidence:
```

Until tooling exists, reports should mark CAS worker attribution as partial/manual when needed.
