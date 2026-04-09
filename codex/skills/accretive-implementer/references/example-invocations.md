# Example invocations

## General implementation

```md
Use $accretive-implementer for this task.

Goal:
Add an expiration banner to the admin session view.

Context:
- admin/session.tsx
- admin/session.test.tsx

Constraints:
- preserve existing props
- avoid broad UI refactor

Done when:
- the banner appears only for expiring sessions
- existing session rendering still passes tests
```

## Review remediation

```md
Use $accretive-implementer for this task.

Goal:
Address reviewer finding F-03 about stale refresh state.

Context:
- auth/session.ts
- auth/session.test.ts
- reviewer notes pasted below

Constraints:
- preserve the current public API
- keep the fix accretive

Done when:
- the stale refresh path is fixed
- the relevant regression check passes
```

## Non-trivial implementation with explicit seam choice

```md
Use $accretive-implementer for this task.

Goal:
Add request normalization for incoming webhook IDs.

Context:
- webhook/parse.ts
- webhook/types.ts
- webhook/parse.test.ts

Constraints:
- keep raw input and validated IDs separate
- prefer boundary normalization over caller-side cleanup
- avoid new dependencies

Done when:
- normalized IDs are produced at the boundary
- invalid raw input is rejected or represented explicitly
- a targeted proof signal passes
```

## Single-change improvement posture

```md
Use $accretive-implementer for this task.

Goal:
If you could change one thing about this changeset what would you change? Pick the single highest-leverage remaining change and implement it.

Context:
- current branch vs main
- relevant files: auth/session.ts, auth/session.test.ts

Constraints:
- one change only unless a tightly coupled follow-on edit is strictly required
- preserve the public API unless the selected change proves that is insufficient

Done when:
- one dominant improvement is implemented
- its direct benefit and one nearby regression surface are verified
```
