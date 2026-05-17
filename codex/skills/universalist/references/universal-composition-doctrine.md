# Universal Composition Doctrine

## Maxim

```text
Allow arbitrary primitives. Forbid arbitrary composition.
```

Universal architecture is not the claim that every primitive operation must be categorical. It is the discipline that meaningful cross-world composition must be mediated by explicit canonical boundary artifacts with executable witnesses.

## Doctrine

A system is universally architected when every meaningful composition boundary between worlds factors through a canonical artifact, and every artifact has an interpreter, projection, lowering, handler, or law-test witness.

```text
Program = primitives + certified composition boundaries + witnesses
```

Primitives compute. Boundaries compose. Witnesses certify.

## Axioms

1. **Primitive admission** — arbitrary domain primitives are allowed: I/O, clocks, randomness, vendor APIs, CPU, database drivers, parser kernels, model calls, and human input.
2. **World stratification** — every meaningful subsystem is treated as a world only if it has objects, transformations, invariants, observations, primitive effects, and composition rules.
3. **Boundary explicitness** — every meaningful interaction between worlds names its boundary: embedding, projection, forgetful map, interpreter, compiler, serializer, view, handler, observer, migration, tool call, memory retrieval, or policy gate.
4. **Canonical artifact factorization** — every nontrivial boundary factors through free syntax, coherent observations, transported semantics, lifted implementation, residual obligations, behavioral coalgebras, effect signatures, Yoneda/Coyoneda vocabularies, defunctionalized IR, or another named canonical artifact.
5. **Witness obligation** — every artifact has a law witness and a falsifier.

## Engineering laws

```text
No boundary without an artifact.
No artifact without an interpreter.
No interpreter without a law.
No law without a falsifier.
```

## Expressivity thesis

Any computable software system can be implemented in universal-architecture style, provided it admits a computationally universal primitive substrate and treats domain primitives as external effects. The discipline requires that every meaningful cross-world composition boundary be certified.

This is an architecture thesis, not a theorem about every line of source code. Ordinary code may live inside boundaries; universal composition governs how worlds communicate.

## Agentic corollary

Agentic systems should be built as certified networks of planning, tool, memory, policy, execution, and observation boundaries. Plans are free syntax, tools are effects, traces are coalgebras, policies are residual obligations, callbacks become defunctionalized IR, and public guarantees are certified by observations/lifts/law tests.
