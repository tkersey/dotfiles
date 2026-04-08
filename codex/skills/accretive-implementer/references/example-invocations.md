
# Example invocations

Tail-weighted note: when reporting results, end with `Execution Bottom Line`.

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
```
