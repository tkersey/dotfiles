# `$st` Multi-Plan Workspace Audit

Native specification:

```text
SEQ_ST_MULTI_PLAN_AUDIT_SPEC.md
```

Required datasets:

```text
st_workspaces
st_plans
st_cross_plan_edges
st_claims
st_resource_conflicts
st_session_views
st_gcr_v2
st_changesets
st_integrations
st_proof_invalidations
```

Audit:

```text
plan isolation
missing/ambiguous plan selection
claims per agent and plan
stale fencing attempts
resource conflict denials
session projection isolation
workspace aperture utilization
cross-plan blockers
change sets outside claims
branch-epoch proof invalidation
integration queue latency and failures
legacy `.step` writes
```

Do not treat path mentions or artifact maintenance as workflow execution.
Controller receipts and state are higher-authority than assistant prose.
