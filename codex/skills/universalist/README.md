# universalist

`$universalist` is a boundary-triggered, proof-carrying architecture compiler. It preserves the full Universal Architecture and category-theory corpus while changing how that knowledge is used:

```text
repository facts
  -> one boring repository-native candidate
  -> one hidden universal-problem pass
  -> effective universal completion or obstruction
  -> material-delta comparison
  -> repository-native artifact and executable proof
```

Category theory is the optimizer, not the default user interface.

## Activation

`$universalist` is implicitly invoked whenever implementation, refactoring, review, migration, or resolution considers a code boundary. **Boundary consideration itself is the activation signal**, including ordinary feature work and PR/review resolution.

**Activation is broad; escalation is proportional.** The boundary pass may preserve an already exact seam and return to ordinary delivery. Stronger constructions are retained only when they materially change ownership, possible states, legal composition, information flow, interpretation, proof, resources, compatibility, or existence.

## Core discipline

```text
one signal
one seam
one boring candidate
one universal shadow pass
one smallest honest construction
one executable proof
```

The shadow pass asks:

```text
What are the admissible alternatives?
Which observations and equations define correctness?
What artifact or map mediates every admissible competitor?
What is unique up to the intended equivalence?
Can the construction be represented and executed within budget?
What nearby weaker route fails?
```

If the categorical result changes nothing architectural, the boring candidate wins.

## Install and validate

From the repository checkout:

```bash
cd codex/skills/universalist
chmod +x scripts/*.sh scripts/*.py
./scripts/check_universalist.sh
```

Run the package-wide compatibility sweep with:

```bash
./scripts/check_universalist_replacement.sh
```

## Universal Problem Compiler

The primary specification is:

- `references/universal-problem-kernel.md`
- `references/universal-construction-registry.yaml`
- `templates/universal-problem-certificate.md`

The registry contains theorem cards for the current concept inventory: products and sums, pullbacks and pushouts, free constructions, adjunction-shaped builders, Kan transport and lifts, observations and representations, effects and coalgebras, composition geometry, Day/promonoidal products, Tambara/context actions, comonadic locality, sheafification, categorical data, Exact Context, and presentation strategies.

Each card records:

```text
preconditions
admissible competitors
mediator direction
canonicality / uniqueness up to
plain repository-native lowerings
positive witnesses
falsifiers
effectivity hazards
boring fallback
material architectural dimensions
claim boundary and expert references
```

Validate the registry:

```bash
uv run --with pyyaml python3 scripts/validate_universal_registry.py \
  --check-references
```

Generate a plain-language certificate:

```bash
uv run --with pyyaml python3 scripts/emit_universal_problem.py pullback
```

Request the expert derivation only when needed:

```bash
uv run --with pyyaml python3 scripts/emit_universal_problem.py day-convolution --expert
```

List cards:

```bash
uv run --with pyyaml python3 scripts/emit_universal_problem.py --list
```

## Universal bytecode

The theorem cards compile through a small internal instruction set:

```text
DECLARE     define worlds, maps, observations, equivalence, effects, resources
CONSTRAIN   retain exactly simultaneous equations and agreements
GLUE        integrate contributors along declared overlap
GENERATE    create the least structure closed under operations or frames
OBSERVE     characterize behavior through sanctioned probes or traces
TRANSPORT   extend, restrict, migrate, or lower semantics coherently
REALIZE     construct an implementation behind a fixed projection
COMPOSE     make sequencing, wiring, decomposition, or feedback explicit
FRAME       preserve a generalized capability under context action
LOCALIZE    represent coherent neighborhoods and restrictions
NORMALIZE   quotient equivalent presentations safely
OBSTRUCT    explain why no exact, canonical, representable, or effective solution follows
```

The concept name is not the decision. The universal problem and its material delta are the decision.

## Proof contract

A consequential universal claim needs:

1. existence;
2. commutation or observation preservation;
3. mediation/factorization for admissible competitors;
4. canonicality or uniqueness up to a declared equivalence/normal form;
5. effective implementation and resource bounds;
6. a targeted falsifier.

A commuting square or passing happy-path fixture alone is insufficient.

## Plain-language output

Normal output should describe consequences:

- one authoritative constructor;
- explicit legal cases;
- canonical integration over declared overlap;
- complete legal decomposition;
- preserved observations and provenance;
- coherent context framing;
- locality-preserving transport;
- one interpreter/projection path;
- an obstruction when implementation is underdetermined.

The plan or expert certificate may retain the category-theory derivation. User-facing prose does not need to expose it unless requested.

## Ordinary-first lowering

Try the repository's ordinary forms first:

| Pressure | Repository-native candidate |
| --- | --- |
| independent data | record / struct |
| exclusive state | tagged union / enum with payload |
| stable predicate | checked value object |
| shared observation | compatibility witness |
| declared overlap | canonical merge with provenance/conflict policy |
| supplied behavior | strategy / function seam |
| inspectable behavior | AST / explicit IR |
| ongoing behavior | transition plus observer |
| several runtimes | operation signature plus handlers |
| ordinary environment | context parameter / adapter |
| local dependency | labelled graph / bounded index |

The universal shadow may keep the same surface artifact while strengthening ownership, mediation, normalization, completeness, or falsifiers.

## Existing categorical corpus

The existing doctrines and mechanics remain intact and are loaded lazily after the universal problem is stated:

- Domain Algebra Discovery and law/non-law discovery;
- products, coproducts, refinements, pullbacks, pushouts, and DPO rewrites;
- free syntax, adjunctions, Kan extensions/lifts, free-builder diagnostics, and obstruction reports;
- Yoneda/Coyoneda, codensity/density, and defunctionalization;
- effect signatures, handlers, behavioral coalgebras, Freyd/premonoidal effect geometry;
- operads, PROPs/properads, traces, and resource-sensitive composition;
- pointwise, Day, promonoidal, substitutional, monadic, resource, and spatial description products;
- Tambara modules, mixed/dependent context actions, optics, free/cofree contextual closure, and representability;
- comonadic spatiality, density bases, halos, germs, and continuous boundaries;
- Possibility Sheafification and Abstraction Normal Form;
- Exact Context, Verified Context Plane, CQL/categorical data, mappings, constraints, and provenance;
- Category Pivot / Syntax-Semantics transfer;
- Effective Universal Software Synthesis.

Use `scripts/emit_mechanics_report.sh index` to inspect mechanics routes. Do not invoke a mechanics family before the seam, comparison universe, boring candidate, material delta, law, falsifier, and resource boundary are known.

## Boundary adapters

`emit_boundary_adapter.py` now emits fail-closed scaffolds. It never casts an external value directly into the core model and never emits an `Any -> Any` identity decoder.

```bash
python3 scripts/emit_boundary_adapter.py decoder typescript
python3 scripts/emit_boundary_adapter.py decoder python
```

The generated decoder intentionally fails until repository-specific validation and normalization rules are supplied.

## Scaffolds

Scaffolds are rendered from the canonical templates so field contracts cannot drift:

```bash
python3 scripts/emit_scaffold.py report
python3 scripts/emit_scaffold.py plan
python3 scripts/emit_scaffold.py universal-problem
```

## Ledger-addressed plans

Consequential implementation routes allocate a fresh plan through the Ledger-owned initializer:

```bash
./scripts/init_universalist_plan.sh [PROJECT_ROOT]
```

Plans live under:

```text
.ledger/universalist/plan-YYYYMMDDTHHMMSSnnnnnnnnnZ-NNNN.md
```

One plan and one root decision receipt belong to one changed seam. The plan now records the boring candidate, comparison universe, theorem card, mediation, canonicality, effectivity, and material delta.

## Exact Context

The context rule remains:

```text
Allow arbitrary sources.
Forbid uncertified semantic consumption.

Operational stores own mutation.
Verified context planes own semantic publication.
```

Retrieval produces candidate material, not semantic context. The prepared artifact is task-indexed, schema-shaped, constraint-closed, provenance-preserving, freshness-valid, and minimal relative to required observations.

## Composition, descriptions, context, and execution are separate

```text
Base composition geometry
  how values, components, resources, contexts, or patches compose

Description composition
  pointwise / Day / promonoidal / substitutional / monadic

Context action
  ordinary / Tambara / mixed / residual / free-cofree / dependent

Runtime semantics
  how effects actually execute and which operations may commute
```

Static or contextual structure never grants effect commutativity, parallelism, duplication, or discard for free.

## Spatial Day correction

A spatial Day claim must name either:

- one shared ambient monoidal index world; or
- an explicit product index world with tensor, unit, variance, external-product patches, density comparison map, and continuous projections.

Do not write a Day product between density constructions over unrelated bases without specifying that common/product index and comparison theorem or engineering approximation.

## Team mode

Custom subagents remain explicit-request only. The root produces the boring candidate and universal problem; read-only specialists supply evidence and countercases; one writer implements one root-selected witness; an independent verifier checks the proof.

## Package stance

The former standalone `kan` material remains folded into `$universalist`. This package is self-contained with respect to Universal Architecture doctrine, but operational plan/receipt workflows still depend on the repository's Ledger and Seq tooling.
