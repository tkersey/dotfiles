# Right-Sized Implementation Kernel

The implementer chooses a route before editing.

```text
no-change
-> validate-only
-> delete-collapse-canonicalize
-> mutate-existing-owner
-> add-new-surface
```

Prefer routes from top to bottom. Move right only when every route to the left is insufficient and the insufficiency is named.

## Route tests

### no-change
Use when current artifacts already satisfy the contract, the request is unsupported, or mutation would be stale, out of scope, or harmful.

### validate-only
Use when the next honest action is proof, characterization, reproduction, or diagnostic work, not production mutation.

### delete-collapse-canonicalize
Use when an existing surface is dead, dominated, duplicate, vestigial, pass-through, non-canonical, or better represented at an existing owner.

### mutate-existing-owner
Use when one canonical owner exists and can truthfully absorb the required behavior.

### add-new-surface
Use only when no-code, validation, deletion/collapse/canonicalization, and existing-owner mutation cannot satisfy the contract.

## Add-new-surface warrant

For any additive production route, answer:

```text
why no-change fails:
why validate-only is insufficient:
why delete/collapse/canonicalize is insufficient:
why existing owner cannot absorb the change:
surface budget consumed:
proof that the new surface earns itself:
```

If the warrant cannot be filled, do not add production code.
