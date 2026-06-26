# GCR-v2 Self-Invalidation Rule

A command that emits a GCR-v2 authority receipt must not invalidate the session projection that the receipt later validates.

Valid implementations:

1. `st compile aperture` is read-only with respect to plan/session projection state.
2. If compile must refresh projection state, it refreshes the bound session view before GCR validation and emits the refreshed view digest.
3. Projection refresh and authority receipt generation are split into separate commands.

Invalid implementation:

```text
session view certified at plan sequence N
compile aperture appends plan sequence N+1
GCR-v2 validates against session view N
GCR-v2 denies stale session view
```

This is internally coherent but unusable as an execution gate. `$actuating` must treat this result as a tooling blocker, not as a reason to patch outside controller authority.
