# Compaction Resume

The resume packet should make full skill rereads unnecessary.

Persist after:

```text
authority receipt change
ASL state transition
matrix frontier change
FPS result
proof gate change
compaction warning
```

Resume order:

1. read current ASL;
2. verify repository, plan, authority receipt, and artifact fingerprints;
3. read referenced VMX/PDAG/FPS artifacts;
4. verify active skill fingerprints;
5. reread only changed skills or the active route reference;
6. continue from `next_frontier`.

If fingerprints differ:

```text
ASL state = return_to_frontier
mutation_allowed = no
```

If the resume packet is missing or stale:

```text
mutation_allowed = no
continuation_allowed = no
```

Do not reconstruct the frontier from `update_plan` or chat prose. Rebuild the
loop contract through the owning skill or stop with the canonical blocker.
