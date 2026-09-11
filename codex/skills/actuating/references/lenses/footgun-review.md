# Footgun Review Lens

Start from a reasonable actor's action at the exact bound candidate's interface,
then follow the difference between what that actor would reasonably expect and
what actually happens. A trap need not bypass admission: lawful internal states
and canonical operations can still produce misleading or dangerous effects.

Ground the expectation in accessible accepted contracts, documentation, examples,
names and defaults in context, or established supported usage. Do not invent an
obligation to prevent every imaginable misunderstanding. Predict the relevant
normal, failure, or lifecycle behavior from that caller-facing surface before
inspecting the implementation; compare the actual path and effects rather than
retrofitting the expectation to the code. This sharpens the same inquiry, not a
new review stage. Trace:

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

Return the native structured review object with `findings`, `overall_correctness`,
`overall_explanation`, and `overall_confidence_score`, never a bare status word.
Supported findings retain native `title`, `body`, `confidence_score`, `priority`,
and `code_location` (`absolute_file_path` and `line_range.start`/`line_range.end`).
When no supported findings remain, use an empty `findings` array and
`overall_correctness: "patch is correct"`; use `"patch is incorrect"` only with
supported findings. Disclose material evidence gaps in `overall_explanation`
without asserting complete coverage. This search priority does not
exclude other concrete in-scope defects. Review Fold owns admission. Do not select
mitigations, implement repairs, or launch companion reviews or a standalone ledger.
