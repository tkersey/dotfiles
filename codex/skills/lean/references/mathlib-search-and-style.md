# Theorem discovery, mathlib search, and style

## Never fabricate library facts

The single biggest unforced error in Lean work is inventing theorem names that look plausible.

Instead:

1. identify the key symbols in the goal
2. inspect candidates with `#check`
3. inspect full declarations with `#print`
4. search the repo and dependencies for the actual theorem family
5. use the theorem only after confirming its name and type

If a theorem name is uncertain, qualify the namespace instead of guessing.

## Local search routine

Search in this order:

1. the current file and nearby files
2. imported modules in the current project
3. `.lake/packages/...` for dependency sources if available
4. mathlib docs or project docs if the environment allows it

Search by the head symbol, constructor, or property name rather than by English paraphrase.

## Match local naming and namespace style

Follow the surrounding file.

Common choices you should preserve if already present:

- `namespace ... end`
- `open scoped ...`
- local notation blocks
- qualified names versus unqualified names
- theorem names that match nearby naming patterns

Do not rename widely used declarations casually.

## `simp` hygiene

Use `simp` with intent.

Good uses:

```lean
simp [foo, bar]
simpa using h
simp at h
simp_all
```

For more stability:

```lean
simp only [lemma1, lemma2, ...]
```

Mark a theorem with `[simp]` only when:

- it rewrites to something clearly simpler
- the orientation is canonical
- repeated application will terminate cleanly
- it will help many goals, not just one special proof

Do **not** add `[simp]` to expansive rewrites, reversible equations, or lemmas whose right-hand side is not obviously simpler.

## `rw` hygiene

Use `rw` when the selected rewrite itself is the proof idea.

Examples:

- reassociating arithmetic in a chosen place
- replacing a term using a hypothesis
- rewriting only one occurrence before another tactic finishes the goal

If you find yourself chaining a long sequence of `rw`s just to expose a normal form, switch to `simp` or a helper lemma.

## Imports

Keep imports minimal but honest.

- add imports only when they really provide required definitions or tactics
- prefer an existing broader project import if that is the local convention
- do not remove an import just because your edited declaration no longer needs it if nearby declarations still do

## Axioms and trust

When foundational trust matters, check what the theorem depends on.

Useful final step:

```lean
#print axioms myTheorem
```

This is especially valuable if classical logic, choice, or imported heavy machinery might matter to the user.

## Scratch work

Use temporary `example` blocks or local helper theorems while searching for the proof. Remove them unless they add lasting explanatory value.

A well-placed private helper theorem is usually better than a dead scratch example left in the file.

## Style preference for final answers

When returning Lean code to the user:

- give the final compilable declaration(s)
- keep the explanation short
- mention any nonobvious helper lemma or invariant
- mention any required import or version-sensitive feature if relevant
