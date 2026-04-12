# Version-sensitive features and release-aware behavior

## The pinned toolchain wins

Lean projects are highly version-sensitive.

Always treat:

- `lean-toolchain`
- the project's current dependency lock state
- the repo's existing syntax and tactic usage

as more authoritative than the newest online examples.

## Version-aware mindset

When adapting code, ask:

- is this syntax available in the pinned toolchain?
- is this tactic built into core Lean here, or only available through imports?
- does the current mathlib snapshot expose the theorem or tactic under the same name?
- did release notes add a suggestion mode or tactic refinement that the current repo may not have yet?

## Important feature checkpoints

Use these as rough gates, not as a substitute for reading the actual toolchain.

- `exact?` and `apply?` are in core Lean in modern Lean 4 workflows.
- `fun_induction` and `fun_cases` are newer than the earliest Lean 4 releases and are particularly useful for proofs following recursive definitions.
- `grind` became a mainstream tactic in later Lean 4 releases; older repos may rely on other automation instead.
- suggestion-enabled forms like `simp? +suggestions` or `grind +suggestions` are newer still.

If a tactic from docs is rejected by the local toolchain, do not fight the repo. Fall back to the more conservative proof method that the current version supports.

## Docs can be ahead of stable

Official reference materials and mathlib docs may reflect release candidates or very recent versions. That is useful for ideas, but dangerous as a source of copy-paste code for an older repo.

Therefore:

- use the docs for concepts
- use the local project for final syntax
- prefer proofs that rely on basic stable primitives when possible

## Release-aware proof strategy

When a repo is on an older toolchain:

- prefer straightforward structural proofs over newer automation
- avoid fancy suggestion features
- expect to write more explicit helper lemmas
- keep syntax conservative

When a repo is on a newer toolchain:

- exploit better suggestion tools to search faster
- still simplify the final proof
- avoid overfitting to one new experimental tactic if a short stable proof exists

## Practical fallback ladder

If a modern feature is missing, fall back in this order:

1. explicit helper lemma
2. `cases` / `induction`
3. `simp` / `rw`
4. smaller domain-specific tactics already used in the repo
5. only then consider changing the proof architecture

The point is to preserve compatibility without giving up correctness.
