# PR Body Proof

`$ship` owns only one marker-bounded block:

```md
<!-- ship-proof:start -->
## Summary
- What changed and why.

## Proof
- `<command>`: pass/fail/blocked/not-run

## Scope
- repository:
- branch:
- head:
- base:
- base SHA:

## Risks
- None identified, or concise residual risks.

## Follow-ups
- None, or explicitly deferred work.

## Readiness
- Operation: create | update | update-and-promote | blocked
- Final state: ready | draft | preserve
- SHIP-v1 compatibility mode: ready | draft | update-existing | promote-draft | blocked
- Reason:
- Caveats:
<!-- ship-proof:end -->
```

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
