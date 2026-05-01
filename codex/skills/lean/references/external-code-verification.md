# Verifying external software with Lean

When the implementation is not Lean code, use Lean as a formal contract and model workbench.

The correct output is usually a verified model plus a precise statement of what remains unproved about the external implementation.

## Workflow

1. Identify the public behavior surface.

   Examples:

   - function inputs and outputs
   - command-line arguments
   - API request/response behavior
   - state transitions
   - validation and error-priority behavior
   - parser and serializer behavior
   - authorization decisions

2. Make hidden inputs explicit.

   External systems often depend on:

   - time
   - randomness
   - locale
   - ordering
   - filesystem contents
   - network responses
   - environment variables
   - concurrency and scheduling

   Model these as explicit parameters rather than implicit effects.

3. Write a portable specification.

   Prefer a clear mathematical definition or relation.

   ```lean
   def spec (env : Env) (input : Input) : Except Error Output := ...
   ```

4. Model state explicitly.

   ```lean
   structure State where
     -- fields

   def stepSpec (env : Env) (s : State) (i : Input) : Except Error (Output × State) := ...
   ```

5. Prove obligations.

   Typical obligations:

   - concrete cases
   - soundness
   - completeness, if true
   - normalization laws
   - idempotence
   - parser/serializer round trips
   - invariant preservation
   - forbidden output or forbidden event exclusion
   - error-priority ordering
   - determinism under explicit environment inputs

6. Align tests or adapters to the specification.

   Tests are useful evidence about external implementation conformance, but they are not the same thing as a Lean proof of the external implementation.

## Recommended theorem shapes

### Concrete behavior cases

```lean
/-- case_id: rejects_empty_name -/
theorem case_rejects_empty_name :
    spec env emptyNameInput = .error .invalidName := by
  rfl
```

### Soundness of an executable model

```lean
def SpecRel (env : Env) (i : Input) (o : Output) : Prop := ...

def modelImpl (env : Env) (i : Input) : Except Error Output := ...

theorem modelImpl_sound (env : Env) (i : Input) (o : Output) :
    modelImpl env i = .ok o -> SpecRel env i o := by
  ...
```

### State invariant preservation

```lean
def Inv (s : State) : Prop := ...

theorem stepSpec_preserves_inv
    (env : Env) (s s' : State) (i : Input) (o : Output) :
    Inv s ->
    stepSpec env s i = .ok (o, s') ->
    Inv s' := by
  ...
```

## Reporting discipline

Always distinguish:

- formal model correctness
- Lean implementation correctness
- conformance tests for external code
- end-to-end external implementation correctness

Use final wording such as:

> Lean proved the formal model satisfies the invariant. The non-Lean implementation was not itself formalized; its correspondence to the model remains an external assumption except for any adapter tests that were run.
