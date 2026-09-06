# Footgun Review Lens

Start from a reasonable actor's action at the exact bound candidate's interface,
then follow the difference between what that actor would reasonably expect and
what actually happens. A trap need not bypass admission: lawful internal states
and canonical operations can still produce misleading or dangerous effects.

Ground the expectation in accessible accepted contracts, documentation, examples,
names and defaults in context, or established supported usage. Do not invent an
obligation to prevent every imaginable misunderstanding. Trace:

```text
actor -> plausible action -> evidence-backed expectation
      -> hidden hazard or contract mismatch -> actual consequence
```

Prioritize defaults, flags, copied examples, partial-success and fallback results,
retries, cancellation, cleanup, permissions, irreversible operations, and lifecycle
boundaries. Does a dry run still mutate? Does success hide skipped work? Does a
cancellation acknowledgment imply effects stopped when they did not? Also retain
alternate constructors, public mints, recovery, migration, serialization, and
adapters that bypass or independently reinterpret the intended authority.

Follow the actual path, preconditions, and externally visible effects. Inspect
existing opt-ins, warnings, safe defaults, enforcement, caller obligations, and
companion changes that could refute or narrow the trap. A warning does not waive
an accepted safety contract; a merely hypothetical actor does not establish a
hazard. Invalid input at a covered trust boundary may itself require safe rejection.

For each finding, name the actor, easy path, reasonable belief and its source,
hidden hazard or contract mismatch, concrete consequence, affected obligation,
and decisive evidence/countercase. Use the smallest source trace or authorized
reproduction; keep unknown premises explicit rather than inventing a bypass.

Return `findings` for supported findings, otherwise `clean`; disclose material
evidence gaps without asserting complete coverage. This search priority does not
exclude other concrete in-scope defects. Review Fold owns admission. Do not select
mitigations, implement repairs, or launch companion reviews or a standalone ledger.
