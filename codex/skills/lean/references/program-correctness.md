# Program-correctness patterns

Use this when proving correctness of executable Lean code or formal models.

## Core pattern

Separate specification, implementation, and proof.

```lean
def spec (i : Input) : Output := ...

def impl (i : Input) : Output := ...

theorem impl_eq_spec (i : Input) :
    impl i = spec i := by
  ...
```

## Relational specifications

Use a relation when the behavior is abstract, nondeterministic, or easier to state as a property.

```lean
def SpecRel (i : Input) (o : Output) : Prop := ...

def impl (i : Input) : Except Error Output := ...

theorem impl_sound (i : Input) (o : Output) :
    impl i = .ok o -> SpecRel i o := by
  ...
```

Completeness is stronger and should be proved only when true.

```lean
theorem impl_complete (i : Input) (o : Output) :
    Preconditions i ->
    SpecRel i o ->
    impl i = .ok o := by
  ...
```

## Boolean decision procedures

For boolean recognizers, prove a bidirectional theorem.

```lean
def Good (x : α) : Prop := ...

def isGood (x : α) : Bool := ...

theorem isGood_correct (x : α) :
    isGood x = true ↔ Good x := by
  constructor
  · intro h
    ...
  · intro h
    ...
```

## Error models

Use explicit error types.

```lean
inductive Error where
  | invalidInput
  | outOfRange
  | unsupported
  deriving DecidableEq, Repr
```

For error-priority behavior, prove exact results:

```lean
theorem invalid_input_takes_priority (i : Input) :
    invalid i -> impl i = .error .invalidInput := by
  ...
```

## State machines

Model state transitions purely.

```lean
structure State where
  -- fields

inductive Event where
  -- events

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

For many-step properties, define an execution relation or recursive runner and prove preservation by induction over the trace or input list.

## Parser/serializer laws

Be precise about direction.

```lean
theorem parse_serialize_roundtrip (x : α) :
    parse (serialize x) = .ok x := by
  ...
```

The reverse direction usually requires normalization.

```lean
theorem serialize_parse_normalizes (s : String) (x : α) :
    parse s = .ok x ->
    serialize x = normalize s := by
  ...
```

## Normalizers

For normalization functions, the common theorem pair is:

```lean
theorem normalize_normalized (x : α) :
    Normalized (normalize x) := by
  ...

theorem normalize_idempotent (x : α) :
    normalize (normalize x) = normalize x := by
  ...
```

## Arrays and optimized code

For optimized code:

1. Define a simple list or mathematical spec.
2. Implement the optimized version.
3. Prove a representation relation.
4. Prove each loop or helper preserves the relation.
5. Conclude equivalence to the spec.

Avoid proving the optimized code directly against a vague English requirement.

## IO boundary

Keep IO out of the core theorem when possible.

Good architecture:

- pure parser
- pure validator
- pure planner
- pure state transition
- small IO wrapper

Prove correctness of the pure core. State that the IO wrapper, filesystem, network, clock, and process environment are outside the Lean proof unless modeled explicitly.
