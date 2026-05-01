# Verification boundaries and claim discipline

Formal verification is only as strong as the boundary being verified.

Before claiming correctness, identify the artifact, the theorem, the trust assumptions, and the gap between the formal model and the real system.

## Claim levels

### Level 1: Model sanity

Lean checks that a formal model is well-typed and internally coherent.

Allowed claim:

> Lean checked the formal model.

Not allowed:

> The implementation is correct.

### Level 2: Case obligations

Lean proves selected concrete cases satisfy the formal definitions.

Allowed claim:

> Lean proved the modeled cases conform to the formal specification.

Not allowed:

> The full behavior is proved correct.

### Level 3: Invariants and laws

Lean proves general properties of a model or specification.

Examples:

- determinism
- idempotence
- parser/serializer round trip
- invariant preservation
- forbidden trace exclusion
- error-priority law
- monotonicity or resource-bound law

Allowed claim:

> Lean proved property P for the formal model.

### Level 4: Lean implementation refinement

Lean proves that an executable Lean implementation equals, refines, or satisfies a specification.

Allowed claim:

> Lean proved the Lean implementation correct relative to the formal specification.

### Level 5: External implementation conformance evidence

A non-Lean implementation is tested against cases generated from or aligned with the proved spec.

Allowed claim:

> The external implementation passed conformance tests derived from the formal specification.

Not allowed unless a checked semantics/refinement link exists:

> Lean proved the external implementation correct.

### Level 6: End-to-end verified implementation

The production implementation is written in Lean, generated from verified Lean, or connected to the specification by a checked semantics/refinement proof.

Allowed claim:

> Lean proved the implementation correct relative to the formal specification, under the documented compiler/runtime trust assumptions.

## Boundary checklist

For verification tasks, record:

- Artifact under proof
- Formal specification
- Implementation or model
- Top theorem names
- Build/check command
- Placeholder status
- Axiom footprint
- Trusted runtime/compiler/adapter assumptions
- What was proved
- What was not proved

## Wording rules

Use precise wording.

Good:

- “The pure Lean implementation equals `spec` for all inputs.”
- “The transition model preserves `StateInvariant` for every successful step.”
- “The model excludes `Event.forbidden` from every generated trace.”
- “The external implementation was not itself formalized.”

Avoid:

- “The software is verified” when only the model is verified.
- “The tests prove correctness” unless the domain is finite and coverage is proved.
- “Lean proved the runtime behavior” when IO, FFI, compiler, or environment behavior is outside the formal model.
