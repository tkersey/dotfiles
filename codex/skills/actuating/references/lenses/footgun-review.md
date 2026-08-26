# Footgun Review Lens

Independently search the exact bound candidate for an easy path that appears safe
but bypasses the admitted construction.

Prioritize:

```text
alternate constructors or public mints
compatibility, recovery, retry, migration, or serialization bypasses
adapters that reinterpret raw state independently
partial-success or lifecycle paths that skip admission
unsafe examples that teach callers to bypass the canonical owner
```

For each finding name the actor, easy path, reasonable belief, hidden bypass,
consequence, and affected law. Return `clean` or `findings`. Do not select or
implement a repair.
