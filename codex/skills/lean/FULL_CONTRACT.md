---
name: lean
description: "Use for deliberate Lean 4 work: proof repair, theorem development, verified programs, model/specification design, external-code models, state-machine or trace invariants, termination proofs, Std/mathlib theorem discovery, Lake/toolchain diagnosis, and high-assurance trust audits. Do not use for Lean management/process-improvement, Coq/Isabelle/Agda/Rocq work, or informal pseudocode unless comparison or translation to Lean 4 is requested."
---

# Lean

You are working in Lean 4. The default deliverable is a checked Lean artifact: a compiling file, theorem, definition, model, or precise diagnostic. Prose is secondary and must not overclaim what Lean checked.

## Operating contract

1. **Pinned environment wins.** Use the repository's `lean-toolchain`, Lake configuration, lock/manifest state, imports, and nearby style as authoritative. Do not upgrade Lean, Std, mathlib, or dependencies unless the user explicitly asks or the task is otherwise impossible and the tradeoff is stated.
2. **Boundary before claim.** For any correctness, verification, safety, state-machine, parser, serializer, protocol, or external-code task, identify the artifact under proof, the theorem claim, the trusted assumptions, and what remains outside Lean.
3. **Compilability before explanation.** Produce Lean code/proofs that check under the project command. When that is not possible, state the exact failing command, first real error, and next proof obligation.
4. **No fake certainty.** Do not invent theorem names, imports, syntax, or tactic availability. Confirm library facts by local search, `#check`, `#print`, dependency source, or documentation matching the pinned version.
5. **No silent weakening.** If the requested theorem is false or mismatched with the implementation, give a counterexample or mismatch explanation, then propose the minimal corrected statement.
6. **No hidden placeholders.** Do not leave `sorry`, `admit`, new `axiom`s, unsolved goals, intentionally broken declarations, or scratch `example`s unless the user explicitly requests a sketch. Report any remaining placeholders.
7. **Trust-expanding features are visible.** `unsafe`, `partial`, `noncomputable`, `native_decide`, `decide +native`, `@[implemented_by]`, `@[csimp]`, external code, generated code, IO, FFI, clocks, filesystems, networks, randomness, concurrency, and adapters must be isolated or reported when relevant to the claim.

## First-pass triage

Classify the task before editing.

- **Proof repair / theorem development:** fix a failing theorem, lemma, tactic script, import, or namespace issue.
- **Verified Lean program:** implement a pure Lean function and prove `impl = spec`, soundness, completeness, refinement, round trip, idempotence, or invariant preservation.
- **External-code model:** model non-Lean behavior in Lean and prove properties of the model; do not claim the external implementation is proved unless there is a checked refinement/semantics link.
- **Stateful/protocol/trace verification:** model states, transitions, inputs, outputs, errors, traces, and prove preservation/safety/progress properties.
- **Termination repair:** make recursive definitions total using structural recursion, measures, well-founded recursion, or explicit fuel.
- **Build/toolchain diagnosis:** resolve Lake, import, cache, namespace, dependency, or version issues without unrequested upgrades.
- **Trust audit:** inspect proof placeholders, axioms, native evaluation, unsafe/runtime trust, external boundaries, and theorem statements.
- **Exploratory learning:** write small checked examples first; scale only after the local pattern works.

## Mandatory project inspection

When inside a repository, inspect before proposing version-sensitive code:

```bash
cat lean-toolchain 2>/dev/null || true
ls lakefile.lean lakefile.toml lake-manifest.json 2>/dev/null || true
find . -maxdepth 3 -name '*.lean' | head
```

Then inspect the target file's imports, namespace, nearby theorems, existing tactics, and CI/build commands. Prefer the smallest command that checks the changed artifact:

```bash
lake env lean path/to/File.lean
lake build +Module.Name
lake build
```

Use `lake env lean --run path/to/File.lean` only for executable scripts or examples with `main`. Use plain `lean` only for toy files outside a Lake project. For mathlib-heavy projects with missing compiled dependencies, consider `lake exe cache get` before treating dependency build time as a proof failure.

## Verification boundary card

For verification tasks, keep this card current:

```text
Artifact under proof: Lean implementation | Lean spec/model | generated code | external adapter/tests | theorem library
Claim type: equality | refinement | soundness | completeness | invariant preservation | round trip | idempotence | case obligation | trace safety
Top-level theorem(s): ...
Trusted assumptions: Lean kernel, imported axioms, classical choice, native evaluation, compiler/runtime, external correspondence, IO/FFI/environment, adapters/tests
Not proved: ...
```

Allowed claim shapes:

- "Lean proved the pure Lean implementation equals the declarative specification."
- "Lean proved the executable Lean model is sound with respect to the relation."
- "Lean proved the transition model preserves the invariant."
- "Lean proved these concrete case obligations."
- "The external implementation was not itself formalized; correspondence to the Lean model remains an external assumption except for checked adapters/tests that were run."

Never write "the software is proved correct" unless the production implementation is itself in Lean, generated from verified Lean under stated assumptions, or connected to the Lean artifact by a checked refinement/semantics theorem.

## Proof workflow

1. Reproduce the first real failure on the smallest declaration or `example` that still fails.
2. Interrogate the environment:

   ```lean
   #check name
   #print name
   #print axioms theorem_name
   #eval expression
   ```

   `#eval` is exploration, not proof. Use it only for executable pure code or harmless diagnostics.
3. Normalize before searching for clever tactics:

   ```lean
   rfl
   simp
   simpa
   simp_all
   ```

4. Structure the proof explicitly:

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

5. Use deliberate rewrites when they are the proof idea:

   ```lean
   rw [h]
   rw [← h]
   nth_rewrite 1 [h]
   ```

6. Choose induction to match the theorem:
   - data induction when the theorem follows constructors;
   - functional induction when recursion drives the cases;
   - generalized accumulators, suffixes, environments, states, or continuations before induction when the public theorem is too weak.
7. Escalate to domain tactics only after simplifying the goal, and only when available under local imports:

   ```lean
   omega
   linarith
   nlinarith
   ring
   norm_num
   decide
   exact?
   apply?
   aesop?
   grind
   ```

8. Replace fragile broad automation with helper lemmas when the theorem supports a correctness claim.
9. Re-run the project-aware check command after each meaningful proof repair.

## Verified-program architecture

Use the spec/implementation/proof split aggressively:

```lean
def spec (i : Input) : Output := ...

def impl (i : Input) : Output := ...

theorem impl_eq_spec (i : Input) :
    impl i = spec i := by
  ...
```

For abstract or nondeterministic behavior, use a relation:

```lean
def SpecRel (i : Input) (o : Output) : Prop := ...

def impl (i : Input) : Except Error Output := ...

theorem impl_sound (i : Input) (o : Output) :
    impl i = .ok o -> SpecRel i o := by
  ...
```

Only prove completeness if the relation is functional enough and the implementation truly returns every admitted output. For optimized code, first prove a simple model, then prove the optimized helper/array/loop/accumulator implementation refines that model. Keep `IO` at the boundary and prove the pure core.

Use auditable theorem names:

- `_eq_spec`
- `_refines_spec`
- `_sound`
- `_complete`
- `_correct`
- `_preserves_inv` or `_preserves_invariant`
- `_roundtrip`
- `_idempotent`
- `_normalized`
- `_terminates`
- `case_...`

## External software and adapters

When implementation code is not Lean:

1. Identify the public behavior surface.
2. Make hidden inputs explicit: time, randomness, locale, ordering, filesystem, network, environment, concurrency, scheduler, permissions.
3. Formalize a pure model or relation in Lean.
4. Prove model obligations: concrete cases, error priority, normalization, round trip, invariant preservation, determinism, forbidden-event exclusion, resource/authorization preservation.
5. Optionally align generated fixtures or adapter tests to the model.
6. Report the boundary: Lean proved the model; tests/adapters are conformance evidence; external implementation correctness remains outside Lean unless linked by a checked refinement proof.

## Stateful, monadic, and trace verification

Default to pure transition modeling:

```lean
structure State where
  -- fields

structure StepResult where
  output : Output
  state' : State
  trace : List Event

def step (s : State) (i : Input) : Except Error StepResult := ...

def Inv (s : State) : Prop := ...

theorem step_preserves_inv
    (s : State) (i : Input) (r : StepResult) :
    Inv s ->
    step s i = .ok r ->
    Inv r.state' := by
  ...
```

For many-step properties, prove one-step preservation first, then lift over traces/input lists by induction.

## Termination policy

Prefer total definitions. Repair recursion in this order:

1. expose a structurally smaller argument;
2. introduce a helper with a stronger accumulator invariant;
3. split traversal/parsing into simpler phases;
4. use `termination_by` and `decreasing_by` with a clear measure;
5. use explicit fuel if the computation may fail to terminate externally.

Avoid `partial` for logic-facing definitions. If runtime partiality is intended, isolate it behind a total model and prove properties of the model.

## Theorem discovery and style

Search by head symbols, constructors, namespaces, and nearby naming conventions. Prefer local source and `.lake/packages` over web examples because they match the pinned version. Before relying on any theorem:

```lean
#check Theorem.name
#print Theorem.name
```

Use `simp` with intent:

```lean
simp [foo, bar]
simpa using h
simp at h
simp_all
simp only [lemma1, lemma2, theorem3]
```

Add `[simp]` only for canonical, directionally simplifying, terminating, broadly useful lemmas. Do not mark expansive, reversible, or one-off rewrites as `[simp]`.

## Trust audit lane

Run this lane for production verification, high assurance, proof certificates, external-code claims, generated-code claims, or any user request involving "audit", "prove correct", "sound", "no assumptions", or "trust".

Scan changed Lean files:

```bash
rg -n --glob '*.lean' --glob '!.lake/**' --glob '!lake-packages/**' \
  '\b(sorry|admit|axiom|unsafe|partial|noncomputable|native_decide)\b|@\[(implemented_by|csimp)\]|implemented_by|csimp|decide \+native' .
```

If this replacement skill's script is available, prefer:

```bash
scripts/lean_trust_audit.sh path/to/file-or-directory
```

For each theorem supporting the final claim, temporarily inspect:

```lean
#print axioms theorem_name
```

Classify the footprint:

- no axioms;
- only standard accepted axioms such as propositional extensionality, quotients, or classical choice;
- `sorryAx` / incomplete proof dependency;
- project-local/custom axioms;
- native-evaluation/compiler trust such as `Lean.trustCompiler` or native-computation assertion axioms;
- external correspondence/adapters/runtime assumptions.

For adversarial or high-risk proof artifacts, consider the stronger validation ladder: clean build, `#print axioms`, `lean4checker --fresh Module.Name` if available, and external checker/comparator workflows when the environment and risk justify them.

## Build and cache diagnosis

Do not treat a dependency download/build failure as a theorem failure. Separate:

- Lean elaboration/proof errors;
- missing imports;
- stale `.lake` build products;
- absent mathlib cache;
- mismatched `lean-toolchain`;
- changed `lake-manifest.json`;
- namespace/module naming mistakes;
- CI command differences.

Use `lake update` only when dependency resolution changes are intended. For proof repair and local correctness work, preserving the lock state is usually the right answer.

## If stuck

Use this order:

1. Restate the goal with `show` or `change`.
2. Expose definitions selectively with `simp [foo]` or `unfold foo`.
3. Inspect constructors and hypotheses.
4. Move the failing shape into a local `example`.
5. Prove the exact helper lemma the goal needs.
6. Strengthen the induction hypothesis.
7. Switch between data induction and functional induction.
8. Search local/imported theorem sources again.
9. Test whether the theorem is false with a concrete counterexample.
10. Use heavier automation only after normalization.

## Final response format

For ordinary Lean edits:

```text
Changed: ...
Checked with: ...
Result: ...
Theorems/definitions: ...
Placeholder status: ...
Notes: ...
```

For verification tasks:

```text
Verification boundary: ...
Formal artifacts: ...
Top theorem names: ...
Build/check command: ...
Result: ...
Placeholder status: ...
Axiom/trust status: ...
What Lean proved: ...
What Lean did not prove: ...
```

If a proof cannot be completed in the current response, still provide the strongest checked partial artifact, the exact remaining goal/error, and the next local lemma or theorem-shape change needed. Do not promise background work.

## Reference map

Read selectively:

- boundary and claim levels: `references/verification-boundaries.md`
- external/non-Lean software: `references/external-code-verification.md`
- trust audits and axiom reporting: `references/trust-audit.md`
- setup, Lake, caches, toolchains: `references/setup-and-workflow.md`
- tactic selection and proof debugging: `references/proof-playbook.md`
- program-correctness patterns: `references/program-correctness.md`
- theorem discovery and style: `references/mathlib-search-and-style.md`
- version-sensitive behavior: `references/version-sensitive-features.md`
- prompt patterns for humans invoking `$lean`: `references/start-prompts.md`

The pinned project, local imports, and actual Lean errors are authoritative over all references.
