# Proof playbook

Use this when writing or repairing Lean proofs.

## First simplification ladder

Try the cheapest tactics first:

```lean
rfl
simp
simpa
simp_all
```

Use `simp [definitionName]` to expose only the definitions needed.

Use `simp only [...]` when proof stability matters.

## Structure the proof

Common structural moves:

```lean
intro h
constructor
cases h
rcases h with ⟨a, b, c⟩
refine ⟨_, _⟩
have h1 : P := by ...
suffices h2 : Q by ...
change NewGoal
show NewGoal
```

## Rewrite deliberately

```lean
rw [h]
rw [← h]
nth_rewrite 1 [h]
```

Use `rw` when the selected rewrite is the central idea. Use `simp` when many canonical simplifications are needed.

## Induction strategy

Use data induction when the theorem follows the shape of an inductive value.

Use functional induction when the theorem follows the recursive call graph.

Before induction, consider generalizing:

- accumulators
- suffixes or prefixes
- environment parameters
- state values
- continuation values

A weak theorem often becomes provable after strengthening it.

## Arithmetic and algebra

Use tactics that match the domain:

```lean
omega       -- linear Nat/Int arithmetic
linarith    -- linear ordered algebra, when available
nlinarith   -- nonlinear arithmetic, when available
ring        -- polynomial identities
norm_num    -- numeric goals
```

Only use tactics available in the pinned toolchain and current imports.

## Search suggestions

These can be useful during development:

```lean
exact?
apply?
aesop?
```

Inspect generated suggestions before finalizing.

## Solver-style automation

`grind`, `aesop`, and similar tactics can be appropriate after the goal is normalized.

Avoid using one large automation block as a substitute for a missing invariant, missing helper lemma, or wrong theorem statement.

For important correctness theorems, prefer small helper lemmas and a readable proof skeleton.

## When stuck

1. Print the current goal mentally or with editor support.
2. Replace implicit shape with explicit `show` or `change`.
3. Unfold exactly one definition.
4. Search for constructor-specific lemmas.
5. Prove a local `have` for the key step.
6. Extract a helper theorem.
7. Strengthen the induction hypothesis.
8. Re-run theorem discovery under the local imports.
9. Consider whether the theorem is false.

## Counterexample discipline

If a theorem appears false:

- build a concrete counterexample with `#eval` when executable
- state why the theorem cannot hold
- propose the minimally corrected theorem
- do not weaken the theorem silently
