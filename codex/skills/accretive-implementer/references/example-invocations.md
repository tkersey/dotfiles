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
