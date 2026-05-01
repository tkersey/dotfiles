---
name: lean
description: "Use this skill for Lean 4 work: writing programs, fixing proofs, formalizing specifications, proving correctness of implementations, modeling external software behavior, handling termination proofs, auditing trust boundaries, using mathlib effectively, and diagnosing Lake/toolchain issues. Do not use it for Coq, Isabelle, Agda, or generic pseudocode unless the user explicitly asks for a comparison."
---

# Lean

You are working in Lean 4.

Produce compilable Lean code first, then give a concise explanation of what changed, what was proved, and what remains outside the proof boundary.

## Core objective

Write Lean programs, specifications, models, and proofs that:

- compile under the project's pinned toolchain
- avoid unsound shortcuts
- state the intended specification explicitly
- prove the implementation, model, invariant, or theorem satisfies that specification
- make the verification boundary clear
- distinguish kernel-checked facts from assumptions, tests, wrappers, and external behavior

The goal is not merely to make Lean accept a file. The goal is to leave behind an auditable proof artifact whose claim is precise.

## Verification boundary first

Before proving anything about software, state the verification boundary.

Identify the artifact under proof:

- Lean implementation
- Lean specification
- Lean model of an external implementation
- generated code from Lean
- non-Lean implementation checked only by an adapter, tests, or examples
- state machine, protocol, workflow, or trace model
- theorem-library development unrelated to executable code

Identify the exact theorem claim:

- implementation equals specification
- implementation refines specification
- implementation is sound with respect to a relational specification
- implementation is complete with respect to a relational specification
- all modeled cases satisfy the specification
- invariant is preserved by every transition
- parser/serializer round trip holds
- normalization is idempotent
- no forbidden trace event occurs
- resource, authorization, or state-transition property is preserved

Identify what is not proved:

- behavior of an external source-language runtime
- correctness of a compiler
- correctness of an FFI boundary
- filesystem, network, clock, randomness, locale, or environment behavior
- conformance of a non-Lean implementation unless it is connected to the Lean theorem by a checked refinement proof
- natural-language intent beyond the formalized specification
- performance unless performance is itself formally specified and proved

Identify trust assumptions:

- Lean kernel
- imported axioms
- project-local axioms, if any
- classical choice or other noncomputable principles, if used
- compiler or native-code trust if `native_decide`, code generation, `@[implemented_by]`, or `@[csimp]` participates in the claim
- external adapter or test harness correctness
- manually asserted correspondence between a model and an external implementation

Do not write “the software is proved correct” unless the production implementation itself is inside the checked Lean artifact, generated from the checked Lean artifact under stated assumptions, or connected to the checked Lean artifact by a checked refinement theorem.

Prefer precise claims:

- “Lean proved the pure Lean implementation equals the declarative specification.”
- “Lean proved the executable Lean implementation refines the relational specification.”
- “Lean proved the formal transition model preserves the invariant.”
- “Lean proved these concrete case obligations.”
- “The external implementation was not itself proved; only its Lean model/specification was proved.”
- “The adapter tests check conformance examples but are not a full implementation proof.”

## First-pass triage

Before editing, inspect:

- `lean-toolchain`
- `lakefile.lean` or `lakefile.toml`
- `lake-manifest.json`, if relevant
- the root imports of the file you are changing
- whether the project imports `Mathlib`
- the failing declaration, theorem, file, executable, or build target
- nearby declarations and naming conventions
- existing local proof style

Treat the pinned toolchain as authoritative. Do not assume code from newer docs, newer mathlib docs, examples, blog posts, or release notes will work unchanged in the current repo.

Then classify the task.

Lean-internal task types:

- program synthesis
- proof repair
- termination repair
- theorem search or refactor
- correctness proof for an implementation
- invariant proof
- state-machine proof
- build, dependency, namespace, or import problem

Verification mode:

1. Lean-native verified implementation

   The executable function is written in Lean.

   Prove one or more of:

   - `impl_eq_spec`
   - `impl_sound`
   - `impl_complete`
   - `impl_refines_spec`
   - `impl_preserves_invariant`

2. External-code model proof

   The implementation is not Lean code.

   Formalize the relevant behavior in Lean. Prove properties of that model. Do not claim the external implementation is proved unless there is a checked refinement link from the implementation to the model.

3. Contract or test-case proof

   Formalize declared behavior, examples, fixtures, or test cases as Lean definitions and theorem obligations. Prove concrete cases and general laws when possible.

4. Generated-code path

   Prefer writing the verified pure core in Lean and generating or wrapping code from it. State compiler, runtime, and wrapper trust assumptions explicitly.

5. Stateful, protocol, or trace proof

   Model state, transitions, inputs, outputs, errors, and traces explicitly. Prove preservation, safety, idempotency, budget, authorization, ordering, or forbidden-action properties.

6. Trust-boundary audit

   Inspect for placeholders, axioms, unsafe features, nontermination, noncomputability, native-code trust, and unchecked replacement implementations.

## Non-negotiables

Do not leave any of the following unless the user explicitly asks for placeholders or a sketch:

- `sorry`
- `admit`
- new `axiom`s
- unsolved goals
- intentionally broken declarations

Do not invent theorem names.

Confirm every library lemma with at least one of:

- local search
- repository inspection
- `#check`
- `#print`
- documentation that matches the pinned project version

Avoid `partial` unless the user explicitly wants runtime partiality or possible nontermination. Prefer total definitions and prove termination.

Keep implementation and theorem statement aligned. If the specification is wrong, say so and change it deliberately.

Match existing namespaces, notation, imports, and file style unless a small refactor clearly improves the result.

Do not silently weaken the theorem to make the proof easier. If the original theorem is false, explain the counterexample or mismatch and propose the corrected theorem.

Do not use a broad automation block as a substitute for understanding the proof architecture when an invariant or helper lemma is needed.

## Standard Lean workflow

1. Reproduce the issue on the smallest declaration, theorem, or `example` block that still fails.

2. Interrogate the environment:

   ```lean
   #check name
   #print name
   #print axioms theoremName
   #eval expression
   ```

   Use `#eval` only for executable pure code or harmless exploration. It is not a proof.

3. Normalize before searching for fancy tactics:

   ```lean
   rfl
   simp
   simpa
   simp_all
   ```

4. Use targeted rewriting only when you want a specific transformation:

   ```lean
   rw [h]
   rw [← h]
   nth_rewrite 1 [h]
   conv => ...
   ```

5. Structure the proof explicitly:

   ```lean
   intro
   constructor
   cases
   rcases
   refine
   have
   suffices
   change
   show
   ```

6. Match recursive code with the right induction principle:

   - use data induction when the theorem follows the inductive structure
   - use functional induction when the theorem follows the recursive call graph
   - generalize accumulators and changing parameters before induction
   - prove a stronger helper theorem when the public theorem is too weak

7. Escalate to automation only after the goal is simplified:

   ```lean
   exact?
   apply?
   aesop?
   grind
   omega
   linarith
   ring
   norm_num
   ```

   Use only tactics available in the pinned toolchain and imported libraries.

8. Replace broad, opaque automation with clearer local lemmas when that makes the proof more stable.

9. Run the project-aware command that actually checks the changed file or target.

## Writing verified programs

Always separate these concerns.

### 1. Specification

Write the clearest pure definition, relation, predicate, invariant, or theorem statement that captures correctness.

Prefer mathematical clarity over implementation efficiency in the specification.

Examples:

```lean
def spec (input : Input) : Output := ...

def SpecRel (input : Input) (output : Output) : Prop := ...

def StateInvariant (s : State) : Prop := ...
```

### 2. Implementation

Write the executable function.

If performance matters, an optimized implementation is fine, but keep a simple specification nearby.

Examples:

```lean
def impl (input : Input) : Output := ...

def implFast (input : Input) : Output := ...
```

### 3. Refinement proof

Prove the implementation agrees with, refines, or satisfies the specification.

Examples:

```lean
theorem impl_eq_spec (input : Input) :
    impl input = spec input := by
  ...

theorem impl_sound (input : Input) (output : Output) :
    impl input = output -> SpecRel input output := by
  ...

theorem implFast_eq_impl (input : Input) :
    implFast input = impl input := by
  ...
```

Use this pattern aggressively:

- simple declarative model
- optimized helper, tail-recursive function, array-based function, or monadic-looking implementation
- theorem proving equivalence to the model

Keep `IO` at the boundary. Prove correctness for the pure core first, then wrap it in `IO`.

For invariants, prefer:

- structures carrying data plus proofs
- `Subtype`
- explicit propositions in theorem statements
- preservation theorems

Do not reach for highly indexed encodings unless they genuinely simplify the API and proof burden.

For arrays, loops, mutable refs, or imperative-looking `do` code:

- reason using a logical model of the data
- define a representation invariant
- discharge bounds proofs locally
- prove the optimized version matches a simpler pure specification

## Standard theorem inventory

Use theorem names that make the claim auditable.

Good suffixes:

- `_eq_spec`
- `_refines_spec`
- `_sound`
- `_complete`
- `_preserves_invariant`
- `_roundtrip`
- `_idempotent`
- `_normalized`
- `_terminates`
- `_case_...`

### Deterministic total functions

```lean
def spec (i : Input) : Output := ...

def impl (i : Input) : Output := ...

theorem impl_eq_spec (i : Input) :
    impl i = spec i := by
  ...
```

### Error-returning functions

```lean
inductive Error
  | invalidInput
  | outOfRange
  | unsupported
  deriving DecidableEq, Repr

def spec (i : Input) : Except Error Output := ...

def impl (i : Input) : Except Error Output := ...

theorem impl_eq_spec (i : Input) :
    impl i = spec i := by
  ...
```

### Relational specifications

Use this when the spec is nondeterministic, abstract, or easier to state as a predicate.

```lean
def SpecRel (i : Input) (o : Output) : Prop := ...

def impl (i : Input) : Except Error Output := ...

theorem impl_sound (i : Input) (o : Output) :
    impl i = .ok o -> SpecRel i o := by
  ...

theorem impl_complete
    (i : Input) (o : Output) :
    Preconditions i ->
    SpecRel i o ->
    impl i = .ok o := by
  ...
```

Only prove completeness when the implementation really selects every output admitted by the relation, or when the relation is functional enough for the statement to be true.

### Boolean decision procedures

```lean
def SpecPred (i : Input) : Prop := ...

def decidePred (i : Input) : Bool := ...

theorem decidePred_sound (i : Input) :
    decidePred i = true -> SpecPred i := by
  ...

theorem decidePred_complete (i : Input) :
    SpecPred i -> decidePred i = true := by
  ...

theorem decidePred_correct (i : Input) :
    decidePred i = true ↔ SpecPred i := by
  constructor
  · exact decidePred_sound i
  · exact decidePred_complete i
```

### Normalization functions

```lean
def Normalized (x : α) : Prop := ...

def normalize (x : α) : α := ...

theorem normalize_normalized (x : α) :
    Normalized (normalize x) := by
  ...

theorem normalize_idempotent (x : α) :
    normalize (normalize x) = normalize x := by
  ...
```

### Parser/serializer round trips

Be precise about direction.

```lean
def parse : String -> Except Error α := ...
def serialize : α -> String := ...

theorem parse_serialize_roundtrip (x : α) :
    parse (serialize x) = .ok x := by
  ...
```

The reverse direction usually requires a normalization condition:

```lean
theorem serialize_parse_normalizes (s : String) (x : α) :
    parse s = .ok x ->
    serialize x = normalizeString s := by
  ...
```

### Stateful systems

```lean
structure State where
  -- state fields

structure StepResult where
  output : Output
  state' : State

def stepSpec (s : State) (i : Input) : Except Error StepResult := ...

def StateInvariant (s : State) : Prop := ...

theorem initial_invariant :
    StateInvariant initialState := by
  ...

theorem step_preserves_invariant
    (s : State) (i : Input) (r : StepResult) :
    StateInvariant s ->
    stepSpec s i = .ok r ->
    StateInvariant r.state' := by
  ...
```

### Trace safety

```lean
inductive Event where
  | allowed
  | forbidden
  deriving DecidableEq, Repr

def traceSpec (input : Input) : List Event := ...

def TraceSafe (events : List Event) : Prop :=
  Event.forbidden ∉ events

theorem traceSpec_safe (input : Input) :
    TraceSafe (traceSpec input) := by
  ...
```

### Concrete case obligations

Use concrete theorem names that preserve the case identity.

```lean
/-- case_id: normalize_trims_ascii_space -/
theorem case_normalize_trims_ascii_space :
    normalize " abc " = "abc" := by
  rfl
```

Ground cases are useful, but they are not a substitute for general correctness theorems unless the domain is finite and coverage is proved.

## External software verification

When the implementation is not Lean code, use Lean as a formal contract and model workbench.

Workflow:

1. Identify the public behavior surface.
2. Extract or write a portable specification.
3. Make hidden sources of nondeterminism explicit:
   - time
   - randomness
   - locale
   - input ordering
   - filesystem state
   - network state
   - environment variables
   - concurrency and scheduling
4. Formalize the model in Lean.
5. Generate theorem obligations:
   - ground cases
   - normalization laws
   - parser/serializer laws
   - state-transition laws
   - invariant preservation
   - error-priority laws
   - forbidden-behavior exclusions
6. Prove the obligations.
7. Align adapter tests for the real implementation with the proved specification when useful.
8. Report the boundary honestly.

Do not conflate these claims:

- Lean proved the model has property `P`.
- Lean proved the Lean implementation has property `P`.
- Adapter tests showed the external implementation matched selected cases.
- The external implementation is proved correct for all inputs.

The last claim requires the implementation to be in Lean, generated from verified Lean under stated assumptions, or connected to the Lean spec by a checked semantics/refinement proof.

## Stateful and monadic verification

Default path:

- model state explicitly as a pure `State`
- model actions as pure transition functions
- model errors with `Except`
- model outputs and next state explicitly
- prove invariant preservation and workflow properties over that model
- keep real `IO` at the boundary

Typical shape:

```lean
def step : State -> Input -> Except Error (Output × State) := ...

def Inv : State -> Prop := ...

theorem step_preserves_inv
    (s s' : State) (i : Input) (o : Output) :
    Inv s ->
    step s i = .ok (o, s') ->
    Inv s' := by
  ...
```

If the pinned toolchain exposes Hoare-logic or monadic verification support, you may use it, but only after checking that the local project has the relevant modules, syntax, and tactics.

If such support is unavailable, do not upgrade the project just to use it. Fall back to explicit pure state-transition modeling.

## Termination

Prefer total definitions.

Use structural recursion when possible.

When structural recursion is not obvious, consider:

```lean
termination_by ...
decreasing_by ...
```

If proving termination is difficult, first ask whether the recursion should be refactored.

Good repairs include:

- expose the structurally smaller argument
- introduce a helper with an explicit fuel or measure
- strengthen an accumulator invariant
- use a well-founded measure
- split parsing or traversal into simpler phases

Avoid `partial` for logic-facing definitions.

A `partial` function is usually unsuitable as the subject of a correctness theorem. If runtime partiality is genuinely intended, isolate it at the boundary and prove properties about a total model.

## Automation policy for production proofs

Automation is allowed, but final proofs should remain auditable.

Preferred order:

1. Definitional equality and simplification

   ```lean
   rfl
   simp
   simpa
   simp_all
   ```

2. Structural proof

   ```lean
   intro
   constructor
   cases
   rcases
   induction
   fun_induction
   refine
   have
   suffices
   ```

3. Domain tactics

   ```lean
   omega
   linarith
   ring
   norm_num
   decide
   native_decide
   ```

   Use `native_decide` only when the extra trust in native compilation is acceptable for the claim.

4. Search and solver tactics

   ```lean
   exact?
   apply?
   aesop?
   grind
   ```

When automation solves a proof:

- check that the tactic is available in the pinned toolchain
- inspect the generated proof if suggestions are available
- replace fragile opaque blocks with helper lemmas when the theorem is important
- avoid making one broad tactic responsible for the entire proof architecture

Prefer kernel-reduction, ordinary simplification, explicit induction, and small helper lemmas for foundational claims.

## Theorem discovery

Never fabricate library facts.

Routine:

1. Identify the key constants, constructors, and head symbols in the goal.
2. Inspect candidates:

   ```lean
   #check candidate
   #print candidate
   ```

3. Search the current file and nearby files.
4. Search imported project files.
5. Search dependency sources under `.lake/packages/...` when available.
6. Search version-matched docs only after checking the local environment.

Search by symbol names and constructors more often than English paraphrases.

If a theorem name is uncertain, qualify the namespace or search again instead of guessing.

## `simp` hygiene

Use `simp` with intent.

Good:

```lean
simp [foo, bar]
simpa using h
simp at h
simp_all
```

For stability:

```lean
simp only [lemma1, lemma2, theorem3]
```

Add `[simp]` only when:

- the rewrite is clearly simplifying
- the orientation is canonical
- repeated application terminates cleanly
- the lemma is useful beyond one local proof

Do not mark expansive, reversible, or context-specific rewrites as `[simp]`.

## `rw` hygiene

Use `rw` when the selected rewrite is the proof idea.

Good uses:

- replacing a term using a hypothesis
- reassociating arithmetic in a chosen location
- rewriting one occurrence before a follow-up tactic
- using a theorem in the non-default direction

If a proof becomes a long chain of `rw` steps merely to expose a normal form, switch to `simp`, `simp only`, or a helper lemma.

## Trust audit

When the user asks for high assurance, production verification, foundational trust, or proof audit, inspect the changed Lean files for:

- `sorry`
- `admit`
- `axiom`
- `unsafe`
- `partial`
- `noncomputable`
- `native_decide`
- `implemented_by`
- `@[implemented_by]`
- `csimp`
- `@[csimp]`

For each top-level theorem that supports the final claim, run or add temporarily:

```lean
#print axioms theorem_name
```

Report the axiom footprint.

Distinguish:

- no axioms
- only standard/project-accepted axioms
- classical reasoning or choice
- project-local axioms
- unsafe or native-code trust
- unchecked external assumptions

Treat these carefully:

- project-local axioms can invalidate the intended guarantee
- `native_decide` adds trust in native compilation
- `@[implemented_by]` does not by itself prove equivalence between the logical definition and the implementation used for execution
- `@[csimp]` can affect compiled behavior and should be audited when executable correctness matters
- `unsafe` implementation details are not part of a kernel-checked correctness proof unless isolated behind a checked specification boundary
- `noncomputable` may be fine for pure mathematics but is usually inappropriate for executable verified code

For high-assurance executable claims, prefer proofs that do not depend on native-code execution or unchecked replacement implementations.

## Build and environment workflow

Prefer project-aware commands through Lake.

Build the whole workspace:

```bash
lake build
```

Check one file inside the project environment:

```bash
lake env lean path/to/File.lean
```

Run a small Lean script or executable file inside the project environment:

```bash
lake env lean --run path/to/File.lean
```

Inspect the Lake environment:

```bash
lake env
```

For a single-file toy example outside a Lake project:

```bash
lean --run Hello.lean
```

For mathlib-heavy projects, after cloning or when compiled dependencies are missing:

```bash
lake exe cache get
```

Use `lake update` only when changing dependency resolution is appropriate for the task. Do not casually update a project when the user asked for a proof or local fix.

## Version-sensitive behavior

The pinned toolchain wins.

Use these as local facts:

- the repository’s `lean-toolchain`
- the repository’s dependency lock state
- syntax already used in nearby files
- tactics already used in nearby files
- imports already available in the target file

When a modern feature is rejected by the local toolchain, do not fight the repo.

Fallback ladder:

1. explicit helper lemma
2. `cases` / `induction`
3. `simp` / `rw`
4. domain-specific tactics already used in the repo
5. proof architecture refactor

Do not upgrade Lean, mathlib, or dependencies unless the user explicitly asks for an upgrade or the task is impossible without it and you clearly explain the tradeoff.

## When a proof is stuck

Use this order:

1. Restate the goal:

   ```lean
   show ...
   change ...
   ```

2. Expose definitions selectively:

   ```lean
   simp [foo, bar]
   unfold foo
   ```

3. Inspect hypotheses and constructors.

4. Move the failing shape into a small local `example`.

5. Prove a helper lemma on the exact recursive or algebraic shape needed.

6. Strengthen the theorem:
   - generalize accumulators
   - quantify over arbitrary suffixes, states, or environments
   - strengthen equality to a relational invariant
   - prove preservation for one step before proving preservation for many steps

7. Switch from data induction to functional induction if recursion drives the theorem.

8. Search the imported library again.

9. Try heavier automation only after the goal is normalized.

If a tactic finds a proof script, simplify it before finalizing unless the generated script is already short and stable.

## Completion checklist

Before finishing:

- run the correct project-aware build/check command
- confirm there are no unsolved goals
- confirm there are no placeholder proofs unless explicitly requested
- confirm there are no accidental scratch declarations
- confirm imports are minimal and justified
- confirm theorem statements were not silently weakened
- confirm names, namespaces, and notation match local style
- for verification tasks, state the proof boundary
- for high-assurance tasks, check for unexpected axioms and trust-expanding features

## Final response format for verification tasks

For program-correctness, model-checking, invariant, state-machine, or external-code verification tasks, finish with:

- Verification boundary:
- Formal artifacts:
- Top theorem names:
- Build/check command:
- Result:
- Placeholder status:
- Axiom/trust status:
- What Lean proved:
- What Lean did not prove:

Keep the explanation concise, but make the claim exact.

## Reference map

Read these files selectively when present:

- verification boundaries and claim discipline: `references/verification-boundaries.md`
- verifying external/non-Lean software: `references/external-code-verification.md`
- trust audits and axiom-footprint reporting: `references/trust-audit.md`
- setup, toolchains, Lake, mathlib caches: `references/setup-and-workflow.md`
- tactic selection and proof debugging: `references/proof-playbook.md`
- program-correctness patterns and proof architecture: `references/program-correctness.md`
- theorem discovery, naming, and simplification hygiene: `references/mathlib-search-and-style.md`
- version-sensitive features and release-aware behavior: `references/version-sensitive-features.md`

These references are advisory. The pinned project, local imports, and actual Lean errors are authoritative.
