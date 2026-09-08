# Invariant Review Lens

Start from valid admitted state in the exact bound candidate and try to break its
required law through a permitted operation, alias write, interleaving, composition,
or lifecycle event. Also challenge whether every sanctioned admission establishes
the invariant. Ground the law and supported domain in accessible accepted authority.

Trace:

```text
valid admission -> permitted operation or observation -> violated invariant
```

Inspect the actual ownership and operation surface: constructors, writable aliases,
identity or declared congruence, lifetime, retries, ordering, recovery, and concurrent
transitions. Can transient invalidity escape its owning transition? Does a check
remain valid when the later effect or observation occurs? Account for producers,
consumers, serialization, compatibility, and paths around the intended owner.
Crossing an admission cut does not establish preservation afterward.

Test adequacy of the enforcement locus throughout the required lifetime, not
whether it is the strongest or earliest imaginable locus. A stronger type or earlier
check is not a finding unless it exposes a required guarantee that the existing
mechanism lacks. Inspect the actual preconditions, atomicity, and encapsulation
that could defeat the proposed trace; names and opacity alone are not proof.

Preserve required-valid behavior: the claimed invalid family must not include it,
and migrations must retain accepted identity, ordering, custody, errors,
serialization, and composition. Probe missing finite cases or supported sibling
dimensions without inventing a family. Reject-all is not success. State closure
alone does not discharge required progress or trace behavior; report a concrete
failure of those obligations when discovered rather than declaring them proved.

For each finding, give the accepted invariant, valid starting state or failed
admission, feasible operation/trace, first loss of guarantee, affected observation,
and decisive evidence/countercase. Source evidence may suffice; an unreproduced
race is not thereby refuted. Respect the frozen subject and effect authority.

Return the native structured review object with `findings`, `overall_correctness`,
`overall_explanation`, and `overall_confidence_score`, never a bare status word.
Supported findings retain native `title`, `body`, `confidence_score`, `priority`,
and `code_location` (`absolute_file_path` and `line_range.start`/`line_range.end`).
When no supported findings remain, use an empty `findings` array and
`overall_correctness: "patch is correct"`; use `"patch is incorrect"` only with
supported findings. Disclose material evidence gaps in `overall_explanation`
without asserting complete coverage. This search priority does not
exclude other concrete in-scope defects. Review Fold owns admission. Do not select
repairs, propose member-specific guards, launch authority fanout, or grant mutation.
