# Operads as Architecture Composition Grammars

An operad is the syntax of typed hierarchical assembly. A category composes one arrow after another; a colored operad specifies operations with many typed input slots and one typed output, plus substitution of whole composites into those slots.

## Structure

```text
colors         = interface / port / subsystem types
operations     = legal many-input -> one-output assemblies
unit           = identity wiring
substitution   = plug composites into input slots
symmetry/order = which input permutations are meaningful
algebra        = concrete semantic interpretation
```

Software example:

```text
buildUserService : (Database, Cache, Policy) -> UserService
buildApi         : (UserService, AuthService) -> HttpApi
```

Substitution produces:

```text
(Database, Cache, Policy, AuthService) -> HttpApi
```

## Use when

- components have typed ports;
- hierarchical assembly is domain meaning, not incidental call order;
- a composite subsystem should itself be a reusable component;
- the same wiring needs production, test, simulation, cost, security, documentation, or deployment interpretations;
- illegal wiring should be rejected before execution.

Use a nonsymmetric/planar operad for ordered pipelines. Use a PROP/properad when multiple outputs are fundamental. Use traced/temporal wiring or coalgebraic structure for feedback loops.

## Algebra / semantics

An algebra assigns concrete objects to colors and concrete maps/processes to operations, preserving units and substitution. This separates:

```text
operad = architecture syntax
algebra = architecture semantics
```

One wiring grammar may have several algebras:

```text
production
unit/integration test
simulation
cost
security
trace
explanation/documentation
```

## Required report

```text
Colors / port types:
Primitive operations:
Composite operation:
Substitution rules:
Symmetric / nonsymmetric / partially commutative:
Multiple-output / feedback requirements:
Forbidden wiring:
Semantic algebras:
First witness composition:
```

## Law

```text
interpret(substitute(f,g1,...,gn))
  ==
compose(interpret(f), interpret(g1), ..., interpret(gn))
```

Also require type/port correctness and explicit rejection of forbidden wiring.

## Falsifiers

- the operad admits a wiring the domain forbids;
- a required composite cannot be expressed;
- two algebras disagree on a supposedly preserved observation;
- order-sensitive effects are placed in a symmetric grammar without proof;
- feedback or multiple outputs are hidden by artificial bundling that loses semantics.

Sources: `[SPIVAK-WIRING-OPERAD]`, `[FONG-SPIVAK-COMPOSITIONALITY]`.
