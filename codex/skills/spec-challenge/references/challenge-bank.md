# Invariant Challenge Bank

Use one strong critique, not a broad checklist.

## Authority

- Does this create a second authority?
- Which surface owns truth after migration?
- Can stale derived state override canonical state?

## Proof

- Does this prove runtime behavior, not just scaffold shape?
- Does the proof command cover the changed path?
- Is integration proof required but absent?

## Compatibility

- Does this preserve public API compatibility?
- Does this silently change a protocol, schema, or CLI contract?
- Is migration required but unnamed?

## Performance / comptime

- Does this preserve zero-cost abstraction?
- Does this introduce runtime dispatch where compile-time resolution was expected?
- Does this allocate or synchronize in the hot path?

## Operations

- Does rollback work after partial deployment?
- What happens under dirty worktree, stale cache, repeated retry, or partial failure?
- Does observability disappear at the moment it is needed?
