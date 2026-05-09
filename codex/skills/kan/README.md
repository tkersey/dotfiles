# Kan skill bundle

`kan` is a Codex/Agent Skills bundle for implementing Kan extensions, implementing Kan lifts, and using both as a coequal architecture calculus.

It covers left and right Kan extensions, left and right Kan lifts, precomposition/postcomposition adjunctions, pointwise formulas, ends/coends, density/codensity, finite-category and finite-poset algorithms, Haskell/TypeScript/Rust/Python implementation patterns, functorial data migration, DSL/interpreter and plugin architecture, implementation synthesis behind boundaries, residual requirements, outside-in contract-first refactors, Freyd/AFT projection diagnostics, free-builder checks, no-exact-lift reports, law tests, failure modes, and source ledgers.

## Installation

For repo-local Codex use, copy this folder to:

```text
.agents/skills/kan
```

For user-level use, copy it to:

```text
$HOME/.agents/skills/kan
```

For API upload, zip the top-level folder:

```bash
cd /path/to/parent
zip -r kan.zip kan
```

## Validation

```bash
cd kan
./scripts/check_skill.sh
```

## Useful entry points

```bash
./scripts/emit_kan_stub.sh plugin-api typescript
./scripts/emit_kan_stub.sh finite-lan python
./scripts/emit_kan_stub.sh lift-realization agnostic
./scripts/emit_kan_stub.sh lift-obligation agnostic
./scripts/emit_witness_pack.sh codensity haskell
./scripts/emit_witness_pack.sh left-kan-lift python
./scripts/emit_law_test_plan.sh lan agnostic
./scripts/emit_law_test_plan.sh right-lift agnostic
./scripts/emit_source_pack.sh foundations pointwise
./scripts/emit_defun_pass.sh boundary-ir typescript
./scripts/emit_yoneda_pass.sh lift agnostic
./scripts/emit_source_pack.sh yoneda representation
./scripts/emit_source_pack.sh lifts residual
./scripts/emit_lift_playbook.sh contract-refactor typescript
./scripts/emit_lift_playbook.sh obligation-discovery agnostic
./scripts/emit_lift_playbook.sh no-exact-lift agnostic
./scripts/emit_freyd_pass.sh boundary-diagnostic agnostic
./scripts/emit_freyd_pass.sh free-builder typescript
```

## Design stance

The skill treats Kan extensions and Kan lifts as architecture-changing tools, not as decoration.

- Kan extensions use precomposition: `Lan_K ⊣ K* ⊣ Ran_K`.
- Kan lifts use postcomposition: `Lft_P ⊣ P_* ⊣ Rft_P` when the relevant adjoints exist.

The skill asks for:

- extension data: `C`, `D`, `K`, `F`, `Lan`/`Ran`/`Δ`, unit/counit, and a witness object; or
- lift data: `A`, `B`, `C`, `P`, `F`, `Lft`/`Rft`/`P_*`, comparison cell, and a witness object.

The practical goal is to replace ad hoc glue with explicit boundaries, generated or synthesized artifacts, and law tests.


## Defunctionalization layer

This bundle also treats Yoneda/Coyoneda as local representation passes and defunctionalization as the implementation move that makes Kan-shaped architecture concrete. After choosing `Lan`, `Ran`, `Δ`, `Lft`, or `Rft`, the skill asks whether callbacks, continuations, paths, observers, handler clauses, requirements, or implementation realizers should be turned into a first-order boundary IR plus an interpreter/apply/project function.

Useful entry points:

```bash
./scripts/emit_defun_pass.sh boundary-ir typescript
./scripts/emit_witness_pack.sh defunctionalization agnostic
./scripts/emit_law_test_plan.sh defunctionalization agnostic
./scripts/emit_source_pack.sh defunctionalization boundary-ir
```


## Yoneda/Coyoneda representation layer

Yoneda/Coyoneda are used as boundary-normalization tools, not as replacements for `Lan`, `Ran`, `Lft`, or `Rft`.

- Yoneda: use for observation-heavy boundaries. It centralizes sanctioned observations behind `Observation` plus `runObservation`/`observe` and supports `Ran`, `Rft`, facades, read models, policies, and public contract views.
- Coyoneda: use for generation-heavy boundaries. It packages raw payloads with deferred maps/paths behind `Generated`/`Path` plus `lower`/`interpretPath` and supports `Lan`, `Lft`, plugin APIs, migrations, generated clients, and candidate implementation realizers.
- Kan lifts often use both: public observations are Yoneda-like; candidate internal realizers plus projection paths are Coyoneda-like.

Useful entry points:

```bash
./scripts/emit_yoneda_pass.sh observation-boundary typescript
./scripts/emit_yoneda_pass.sh generation-boundary typescript
./scripts/emit_yoneda_pass.sh lift agnostic
./scripts/emit_witness_pack.sh yoneda-observation agnostic
./scripts/emit_witness_pack.sh coyoneda-generation agnostic
./scripts/emit_law_test_plan.sh yoneda-coyoneda agnostic
./scripts/emit_source_pack.sh yoneda representation
```


## Kan lift architecture playbook

The bundle now treats Kan lifts as the main tool for outside-in architecture changes: refactors where public commitments are fixed and internals must be rebuilt behind a projection.

Use lift mode when the shape is:

```text
A --?--> B
|        |
F        P
v        v
C
```

- `A`: contract cases, tests, policies, reports, workflows, or use cases.
- `B`: internal architecture choices, modules, workflows, resources, handlers, or obligations.
- `C`: observable behavior: API responses, events, traces, views, reports, policy results.
- `P : B -> C`: the concrete projection from internals to observable behavior.
- `F : A -> C`: required behavior.

The skill should produce an obligation ledger before broad refactors and classify each witness as exact, covering, sound, approximate, or no-exact-lift.

Useful entry points:

```bash
./scripts/emit_lift_playbook.sh contract-refactor typescript
./scripts/emit_lift_playbook.sh obligation-discovery agnostic
./scripts/emit_lift_playbook.sh no-exact-lift agnostic
./scripts/emit_freyd_pass.sh boundary-diagnostic agnostic
./scripts/emit_freyd_pass.sh free-builder typescript
./scripts/emit_witness_pack.sh lift-contract-refactor agnostic
./scripts/emit_witness_pack.sh lift-obligation-discovery agnostic
./scripts/emit_law_test_plan.sh contract-lift agnostic
./scripts/emit_law_test_plan.sh obligation-lift agnostic
./scripts/emit_source_pack.sh lift-playbook outside-in
```


## Freyd/AFT boundary diagnostic layer

Freyd's adjoint functor theorem is used as a practice for lift-shaped refactors, not as decoration. After a Kan lift identifies a projection `P : B -> C`, the skill asks whether that projection is disciplined enough to support a canonical free builder `Free : C -> B`.

The diagnostic asks for:

- the concrete projection `P`;
- constraints available in `B`;
- preservation tests showing `P` does not lie about those constraints;
- a solution-set-like menu of implementation templates;
- a candidate `Free : C -> B`;
- the lift candidate `L = Free · F`;
- an exact / embedding / covering / sound / approximate / no-exact-lift classification;
- a projection law `P(Free(F(a))) ~= F(a)`.

Useful entry points:

```bash
./scripts/emit_freyd_pass.sh boundary-diagnostic agnostic
./scripts/emit_freyd_pass.sh free-builder typescript
./scripts/emit_freyd_pass.sh solution-set agnostic
./scripts/emit_witness_pack.sh freyd-aft agnostic
./scripts/emit_law_test_plan.sh freyd-aft agnostic
./scripts/emit_source_pack.sh freyd boundary
```
