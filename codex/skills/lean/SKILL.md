---
name: lean
description: "Use this skill for Lean 4 work: writing programs, fixing proofs, formalizing specifications, proving correctness of implementations, handling termination proofs, using mathlib effectively, and diagnosing Lake/toolchain issues. Do not use it for Coq, Isabelle, Agda, or generic pseudocode unless the user explicitly asks for a comparison."
---

# Lean

You are working in Lean 4. Produce compilable Lean code first, then give a concise explanation of what changed and why.

## Core objective

Write Lean programs and proofs that:

- compile under the project's pinned toolchain
- avoid unsound shortcuts
- state the intended specification explicitly
- prove that the implementation satisfies that specification

## First-pass triage

Before editing, inspect:

- `lean-toolchain`
- `lakefile.lean` or `lakefile.toml`
- the root imports of the file you are changing
- whether the project imports `Mathlib`
- the failing declaration, theorem, or build target

Then classify the task:

- program synthesis
- proof repair
- termination repair
- theorem search / refactor
- correctness proof for an implementation
- build / dependency / namespace problem

Treat the pinned toolchain as authoritative. Do **not** assume code from newer docs, newer mathlib docs, or release notes will work unchanged in the current repo.

## Non-negotiables

- Do not leave `sorry`, `admit`, or new `axiom`s unless the user explicitly asks for placeholders.
- Do not invent theorem names. Confirm every lemma with local search, `#check`, `#print`, or repository inspection before relying on it.
- Avoid `partial` unless the user explicitly wants runtime partiality or nontermination. Prefer total definitions and prove termination.
- Keep the implementation and theorem statement aligned. If the spec is wrong, say so and change it deliberately.
- Match existing namespaces, notation, and file style unless a small refactor clearly improves the result.

## Standard Lean workflow

1. Reproduce the issue on the smallest declaration or `example` block that still fails.
2. Interrogate the environment:
   - `#check`
   - `#print`
   - `#eval` for executable pure code
3. Normalize before searching for fancy tactics:
   - `rfl`
   - `simp`
   - `simpa`
   - `simp_all`
4. Use targeted rewriting only when you want a specific transformation:
   - `rw`
   - `nth_rewrite`
   - `conv`
5. Structure the proof explicitly:
   - `intro`
   - `constructor`
   - `cases` / `rcases`
   - `refine`
   - `have`
   - `suffices`
   - `change`
6. Match recursive code with the right induction principle:
   - `induction` on the inductive input
   - `fun_induction` when the theorem follows the recursive call structure of a function
7. Escalate to automation only after the goal is simplified:
   - `exact?`
   - `apply?`
   - `aesop?`
   - `grind`
   - arithmetic or algebra tactics that fit the imported libraries
8. Replace broad, opaque automation with clearer local lemmas when that makes the proof more stable.

## Writing verified programs

Always separate these concerns:

1. **Specification**  
   Write the clearest pure definition or theorem statement that captures correctness.

2. **Implementation**  
   Write the executable function. If performance matters, an optimized implementation is fine.

3. **Refinement proof**  
   Prove the implementation agrees with the specification.

Use this pattern aggressively:

- simple declarative model
- optimized helper / tail-recursive function / array-based function
- theorem proving equivalence to the model

Keep `IO` at the boundary. Prove correctness for the pure core first, then wrap it in `IO` if needed.

For invariants, prefer:

- structures carrying data plus proofs
- `Subtype`
- explicit propositions in theorem statements

Do not reach for highly indexed encodings unless they genuinely simplify the API and proof burden.

For arrays, mutable refs, or imperative-looking `do` code:

- reason using the logical model of the data
- discharge bounds proofs locally
- prove the imperative or optimized version matches a simpler pure specification

## When a proof is stuck

Use this order:

1. restate the goal with `show` or `change`
2. expose definitions with `simp [defs...]` or selective unfolding
3. inspect available hypotheses and constructors
4. prove a helper lemma on the exact recursive shape you need
5. switch from data induction to functional induction if recursion drives the theorem
6. search the imported library again
7. only then try heavier automation

If a tactic finds a proof script, simplify it before finalizing unless the generated script is already short and stable.

## Completion checklist

Before finishing:

- run the correct project-aware build/check command
- confirm there are no unsolved goals
- confirm there are no placeholder proofs unless explicitly requested
- ensure imports are minimal and justified
- if foundational trust matters, check for unexpected axioms

## Reference map

Read these files selectively:

- setup, toolchains, Lake, mathlib caches: `references/setup-and-workflow.md`
- tactic selection and proof debugging: `references/proof-playbook.md`
- program-correctness patterns and proof architecture: `references/program-correctness.md`
- theorem discovery, naming, and simplification hygiene: `references/mathlib-search-and-style.md`
- version-sensitive features and release-aware behavior: `references/version-sensitive-features.md`
