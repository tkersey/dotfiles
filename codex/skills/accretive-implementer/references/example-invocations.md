# Example invocations

## Planned feature

```md
Use $accretive-implementer for this task.

Goal: add a "remember device" option to the sign-in flow.
Context:
- auth/session.ts
- auth/session.test.ts
- auth/ui/LoginForm.tsx
Constraints:
- preserve the current public API
- fit the existing auth architecture
- keep the change reviewable
Done when:
- the new behavior works end to end
- affected invariants still hold
- targeted verification passes
```

## Bug fix

```md
Use $accretive-implementer for this task.

Goal: fix the session refresh regression.
Context:
- auth/session.ts
- auth/session.test.ts
- failing CI logs
Constraints:
- preserve the current public API
- no broad refactor
Done when:
- the failure mechanism is identified
- the narrowest defensible patch is applied
- targeted verification passes
```

## Review remediation

```md
Use $accretive-implementer for this task.

Goal: address the review finding about retry ordering on the queue worker.
Context:
- queue/retry.ts
- queue/retry.test.ts
- reviewer notes about ordering and duplicate delivery
Constraints:
- preserve ordering and at-least-once behavior
- keep the change small and reviewable
Done when:
- the material review finding is resolved
- invariants are preserved
- verification covers the changed path
```
