# Verification boundaries and claim discipline

Formal verification is only as strong as the boundary being verified. Before claiming correctness, identify the artifact, theorem, trusted assumptions, and the gap between the formal model and the real system.

## Claim levels

### Level 0: Parse/build sanity

Lean accepted the file or module. This means declarations elaborated, but it does not itself say the theorem statements express the intended requirement.

Allowed claim: "The Lean file/module checked."

### Level 1: Model sanity

Lean checked a formal model or definitions.

Allowed claim: "Lean checked the formal model."

Not allowed: "The implementation is correct."

### Level 2: Case obligations

Lean proved selected concrete cases.

Allowed claim: "Lean proved these modeled cases conform to the formal specification."

Not allowed: "The full behavior is proved correct" unless the domain is finite and coverage is proved.

### Level 3: Invariants and laws

Lean proved general properties of a model or specification, such as determinism, idempotence, parser/serializer round trip, invariant preservation, forbidden trace exclusion, error-priority law, monotonicity, or resource-bound law.

Allowed claim: "Lean proved property `P` for the formal model."

### Level 4: Lean implementation refinement

Lean proved that an executable Lean implementation equals, refines, or satisfies a specification.

Allowed claim: "Lean proved the Lean implementation correct relative to the formal specification."

### Level 5: External implementation conformance evidence

A non-Lean implementation is tested against cases generated from, or aligned with, the proved specification.

Allowed claim: "The external implementation passed conformance tests derived from the formal specification."

Not allowed unless a checked semantics/refinement link exists: "Lean proved the external implementation correct."

### Level 6: End-to-end verified implementation

The production implementation is written in Lean, generated from verified Lean, or connected to the specification by a checked semantics/refinement proof.

Allowed claim: "Lean proved the implementation correct relative to the formal specification, under the documented compiler/runtime trust assumptions."

## Boundary checklist

For verification tasks, record:

- Artifact under proof
- Formal specification
- Implementation, model, adapter, or generated-code path
- Top theorem names
- Build/check command
- Placeholder status
- Axiom footprint
- Native/compiler/runtime assumptions
- External correspondence assumptions
- What was proved
- What was not proved

## Wording rules

Good:

- "The pure Lean implementation equals `spec` for all inputs."
- "The transition model preserves `StateInvariant` for every successful step."
- "The model excludes `Event.forbidden` from every generated trace."
- "The external implementation was not itself formalized."

Avoid:

- "The software is verified" when only the model is verified.
- "The tests prove correctness" unless the domain is finite and coverage is proved.
- "Lean proved runtime behavior" when IO, FFI, compiler, filesystem, network, clock, or environment behavior is outside the model.
