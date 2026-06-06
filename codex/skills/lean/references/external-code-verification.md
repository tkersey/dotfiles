# Verifying external software with Lean

When implementation code is not Lean, use Lean as a formal contract and model workbench. The usual output is a verified model plus a precise statement of what remains unproved about the external implementation.

## Workflow

1. Identify the public behavior surface:
   - function inputs and outputs;
   - command-line arguments;
   - API request/response behavior;
   - parser and serializer behavior;
   - state transitions;
   - validation and error-priority behavior;
   - authorization decisions;
   - emitted events or traces.
2. Make hidden inputs explicit:
   - time;
   - randomness;
   - locale;
   - input ordering;
   - filesystem contents;
   - network responses;
   - environment variables;
   - permissions;
   - concurrency and scheduling.
3. Write a portable pure specification or relation.
4. Model state explicitly when behavior is stateful.
5. Prove obligations: concrete cases, soundness, completeness if true, normalization laws, idempotence, round trips, invariant preservation, forbidden output/event exclusion, error priority, and determinism under explicit environment inputs.
6. Align tests or adapters to the specification if useful.
7. Report the boundary without conflating model correctness, Lean implementation correctness, conformance evidence, and end-to-end external implementation correctness.

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

## Adapter discipline

Adapters and generated fixtures are evidence, not proof of the external implementation, unless the adapter itself is part of a checked refinement chain. Report:

```text
Lean proved the formal model satisfies the invariant. The non-Lean implementation was not itself formalized; its correspondence to the model remains an external assumption except for adapter tests that were run.
```
