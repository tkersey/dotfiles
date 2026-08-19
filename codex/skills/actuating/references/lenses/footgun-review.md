# Footgun Review Lens

Independently inspect the exact bound subject for an easy or obvious use that a
reasonable caller, maintainer, or operator could mistake for safe success.

For each material finding name:

```text
actor
easy path
reasonable belief
hidden fact
plausible consequence
affected law or boundary
smallest mitigation class
```

Prioritize unsafe defaults, silent degradation, ambiguous authority, partial
success, lifecycle traps, idempotency or concurrency traps, compatibility traps,
and copyable unsafe examples.

Return one structured `clean` or `findings` verdict. Do not implement, choose the
architecture, launch `$footgun-finder`, invoke companion skills, persist an
artifact, or grant mutation or closeout.
