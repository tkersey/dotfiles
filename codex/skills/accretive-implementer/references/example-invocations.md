# Example invocations

## Implementation from a plan

```md
Use $accretive-implementer for this task.

Goal:
Implement session refresh retry fencing.

Context:
- auth/session.ts
- auth/session.test.ts
- design notes pasted below

Constraints:
- preserve the current public API
- prefer the canonical existing auth path
- add no helper/wrapper unless the existing owner cannot absorb the behavior

Done when:
- the feature is implemented or a no-change/validate-only route is justified
- the changed path is directly checked
- assumptions, surface delta, and witnesses are surfaced
```

## Remediation from review-adjudication handoff

```md
Use $accretive-implementer for this task.

Agenda Intake:
- Resolution Warrant: RW-002, permitted_action=mutate-code
- permitted scope: auth/session.ts, auth/session.test.ts
- forbidden actions: new public API, fallback flag, broader auth refactor
- proof required: targeted session refresh regression

Goal:
Implement the accepted review agenda without reopening broad adjudication.
```

## Fixed-point-driver handoff

```md
Use $accretive-implementer for this implementation handoff.

implementation_handoff:
  target_skill: accretive-implementer
  artifact_state_id: branch=feature/session head=abc123 diff=auth-session phase=post-review
  truth_unit_ids: [TU-001]
  selected_rewrite: tighten-owner
  permitted_route: mutate-existing-owner
  permitted_scope:
    - auth/session.ts
    - auth/session.test.ts
  forbidden_actions:
    - new public symbols
    - fallback flag
    - compatibility alias
  surface_budget:
    production_surface: zero_or_negative
    added_helpers_allowed: no
    added_wrappers_adapters_allowed: no
    added_flags_or_fallbacks_allowed: no
    public_symbols_allowed: no
    compatibility_paths_allowed: no
  ablation_status: local-preflight
  addition_escrow_policy: not-allowed
  proof_required:
    - targeted session refresh regression
```

## Validate-only route

```md
Use $accretive-implementer for this task.

Goal:
Determine whether the reported retry bug still exists.

Constraint:
Do not change production code unless the repro fails against current artifacts.
```

## Delete/collapse/canonicalize route

```md
Use $accretive-implementer for this task.

Goal:
Fix the duplicated session-expiry behavior by choosing the canonical owner and deleting or collapsing the duplicate caller-side repair.

Done when:
- one owner remains
- behavior is preserved
- a targeted proof passes
```

## Fast mode

```md
Use $accretive-implementer in Fast mode for this task.

Goal:
Apply the one accepted right-sized fix and show only the execution bottom line.
```
