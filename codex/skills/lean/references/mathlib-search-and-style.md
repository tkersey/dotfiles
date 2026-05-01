# Mathlib search and style

Use this reference when looking for library theorems, choosing names, or managing simplification.

## Do not invent theorem names

Before using a theorem, confirm it by one of:

```lean
#check theorem_name
#print theorem_name
```

or by inspecting local or dependency source files that match the pinned project version.

## Search strategy

Search for:

- the head symbol in the goal
- constructor names
- namespace names
- nearby theorem naming patterns
- suffixes such as `_assoc`, `_comm`, `_left`, `_right`, `_eq`, `_iff`, `_of_`

Local source search is often better than web search because it matches the pinned dependency version.

## Namespace discipline

Prefer names consistent with nearby files.

If a theorem is ambiguous, qualify it:

```lean
List.map_append
Nat.add_assoc
```

Open namespaces sparingly in library code. In local proofs, temporary `open` statements are usually fine if they match the file style.

## Naming new theorems

Use names that reveal the statement.

For program correctness:

- `foo_eq_spec`
- `foo_sound`
- `foo_complete`
- `foo_refines_spec`
- `foo_preserves_inv`
- `foo_roundtrip`
- `foo_idempotent`

For helper lemmas, follow local style and make the head symbol discoverable.

## `simp` lemmas

Add `[simp]` only when the lemma is:

- directionally simplifying
- terminating under repeated use
- broadly useful
- not context-specific

Avoid `[simp]` on lemmas that expand definitions into large terms, reverse canonical forms, or create loops.

## Stable proofs

Prefer:

```lean
simp only [foo, bar, baz]
```

when a proof is important and broad `simp` is too sensitive to future library changes.

Use broad `simp` freely in small local proofs when maintainability is not harmed.

## Rewriting style

Use `rw` for deliberate transformations and `simp` for canonical simplification.

Long chains of `rw` usually indicate one of:

- a missing helper lemma
- a normalization proof that should use `simp`
- an associativity/commutativity problem that needs `ring`, `omega`, or a domain tactic
- a theorem statement that should use a canonical form
