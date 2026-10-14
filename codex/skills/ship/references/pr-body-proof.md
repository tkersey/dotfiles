# PR Body Proof

`$ship` owns only one marker-bounded block:

```md
<!-- ship-proof:start -->
Describe the concrete problem and resulting behavior in one or two sentences.

Validation: `<command>` — pass/fail/blocked/not-run, with relevant scope or limits.
<!-- ship-proof:end -->
```

Scale the prose to the change and follow a repository PR template when present.
Use headings or lists only when they help a reviewer. Include material risks,
deferred work, incomplete validation, and draft/readiness caveats when applicable;
omit empty sections and routine "none" statements. Preserve consequential scope
and compatibility changes in the human description.

Keep operation enums, compatibility modes, and routine repository/branch/SHA
fields in the [Ship record](ship-record.md), rather than repeating them in every
PR body. Include an exact identity in prose when it is needed to interpret the
validation or the change. A record does not replace reviewer-relevant evidence.

For an existing PR, read the current body and replace exactly one complete
managed block. Append the block when neither marker exists. Preserve everything
outside the block byte-for-byte. Block instead of editing when markers are
unbalanced, duplicated, or ambiguous.

For `update-and-promote`, update the managed block before marking the PR ready.
After every mutation, read back the PR and require exactly one matching managed
block plus the expected repository, base, head, open state, and draft state.

Do not claim all checks pass if a validation category was missing or not run.
Do not include credentials, tokens, private paths, or sensitive command
arguments in proof text.
