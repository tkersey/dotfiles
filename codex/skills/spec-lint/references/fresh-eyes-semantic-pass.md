# Fresh-Eyes Semantic Pass

Before returning `SPEC_READY`, reread the spec as if assigned to implement it and as if assigned to review the implementation later.

Check for objective drift, missing non-goals, hidden second sources of truth, vague proof commands, scaffold-only proof, unmapped requirements, rollback gaps, stale assumptions, and execution-plan content masquerading as spec content.

Any material issue found by this pass belongs in `blocking_errors`, `material_risks`, `rollback_gaps`, `proof_gaps`, or `churn_signals`; do not mark `SPEC_READY: true` until it is fixed or explicitly defaulted/deferred with owner and consequence.
