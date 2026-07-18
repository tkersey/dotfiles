# Universal Composition Doctrine

## Maxim

```text
Allow arbitrary primitives. Forbid arbitrary composition.
```

Universal architecture is not the claim that every primitive operation must be categorical. It is the discipline that meaningful cross-world composition must be mediated by explicit canonical boundary artifacts with executable witnesses.

When software manipulates artifacts indexed by a world, apply the companion maxim:

```text
Do not invent composition for descriptions.
Derive it from composition of their indices.
```

## Doctrine

A system is universally architected when every meaningful composition boundary between worlds factors through a canonical artifact, every artifact has an interpreter, projection, lowering, handler, or law-test witness, and every consequential indexed-description product is selected from the composition law of its index world rather than from ad hoc implementation convenience.

```text
Program = primitives + certified composition boundaries + witnessed description products + laws
```

```text
Primitives compute.
Indices compose.
Descriptions convolve when decomposition is semantic.
Boundaries compose.
Presentations compress.
Witnesses certify.
```

## Axioms

1. **Primitive admission** — arbitrary domain primitives are allowed: I/O, clocks, randomness, vendor APIs, CPU, database drivers, parser kernels, model calls, and human input.
2. **World stratification** — every meaningful subsystem is treated as a world only if it has objects, transformations, invariants, observations, primitive effects, and composition rules.
3. **Boundary explicitness** — every meaningful interaction between worlds names its boundary: embedding, projection, forgetful map, interpreter, compiler, serializer, view, handler, observer, migration, tool call, memory retrieval, or policy gate.
4. **Canonical artifact factorization** — every nontrivial boundary factors through free syntax, coherent observations, transported semantics, lifted implementation, residual obligations, behavioral coalgebras, effect signatures, Yoneda/Coyoneda vocabularies, defunctionalized IR, or another named canonical artifact.
5. **Description-product derivation** — when `F,G` are descriptions indexed by a composed world, choose pointwise, Day, promonoidal, substitutional, or monadic composition from the intended index and dependency semantics. Do not use a generic binary merge as an unnamed product.
6. **Witness obligation** — every artifact and consequential description product has a law witness and a falsifier.
7. **Effectivity obligation** — every decomposition, quotient, residual, halo, or reconstruction used by the architecture has a finite/effective presentation, bounded approximation, or obstruction report.

## Engineering laws

```text
No boundary without an artifact.
No artifact without an interpreter.
No interpreter without a law.
No law without a falsifier.
```

For indexed descriptions:

```text
No description convolution without an index tensor or kernel.
No composite without a legal decomposition witness.
No quotient without a collision/provenance policy.
No static structure without a separate effect-order decision.
No convolution without an effective implementation or obstruction.
```

## Description-Composition Addendum

Use two selectors:

```text
Base composition geometry:
  category / monoidal / Freyd / operad / PROP / traced / resource-sensitive

Description product:
  pointwise / Day / promonoidal / substitution / endofunctor composition
```

Day convolution is the canonical left-Kan extension of a base tensor to indexed descriptions:

```text
F star G = Lan_tensor(F external-product G)
```

Its central generator law is:

```text
represent(a) star represent(b)
  ~=
represent(a tensor b)
```

Use promonoidal convolution when composition is partial, relation-valued, or multi-witnessed. Use pointwise product for same-index combination, substitution for recursive typed insertion, and monadic/endofunctor composition for value-dependent sequencing.

A static/applicative description shape may support inspection, dependency extraction, batching, cost analysis, documentation, and several interpreters. It never by itself proves that runtime effects commute or may execute in parallel; Freyd/resource mechanics own that claim.

## Expressivity thesis

Any computable software system can be implemented in universal-architecture style, provided it admits a computationally universal primitive substrate and treats domain primitives as external effects. The discipline requires that every meaningful cross-world composition boundary and every architecture-significant description product be certified.

This is an architecture thesis, not a theorem about every line of source code. Ordinary code may live inside boundaries; universal composition governs how worlds communicate and how indexed descriptions inherit their composition laws.

## Agentic corollary

Agentic systems should be built as certified networks of planning, tool, memory, policy, execution, and observation boundaries. Plans are explicit syntax, tools are effects, traces are coalgebras, policies are residual obligations, callbacks become defunctionalized IR, and public guarantees are certified by observations/lifts/law tests.

When a plan's complete operation/dependency shape is known before results, a free-applicative/Day-style description may support analysis and several interpreters. When later structure depends on earlier results, use monadic syntax. Actual tool execution remains order-sensitive unless a Freyd/resource witness proves otherwise.

## Presentation Strategy Addendum

Every complex canonical artifact needs a presentation strategy. The main modes are algebraic presentation, codensity/dense-dual presentation, density-comonadic spatial presentation, mixed presentation, and primitive containment.

```text
No boundary without an artifact.
No artifact without a presentation.
No presentation without reconstruction.
No reconstruction without a law.
No law without a falsifier.
```

Description composition is separate from presentation. An algebraic, codense, spatial, mixed, or primitive description family may still use pointwise, Day, promonoidal, substitutional, or sequential composition.

## Dense-Dual Presentation Principle

When a semantic artifact is too large, infinitary, observational, probabilistic, or completion-like for a clean generators/equations presentation, present it by a small dense world of probes plus a dual or observational bridge.

## Semantic compression

Semantic compression presents a large behavioral world by a smaller dense world of probes, observations, traces, expectations, or finite approximants.
