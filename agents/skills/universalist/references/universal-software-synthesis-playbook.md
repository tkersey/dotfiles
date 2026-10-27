# Universal Software Synthesis Playbook

## Phase 1: Specify observations

Start from externally meaningful behavior, not category names.

- inputs and outputs;
- traces and state transitions;
- safety/liveness/policy properties;
- failure and recovery;
- performance/resource commitments.

## Phase 2: Establish the effective substrate

Choose representations, evaluator/compiler, recursion/partiality, primitive effects, state/interaction, and resource model.

## Phase 3: Map worlds and boundaries

Name domain, syntax, semantics, runtime, storage, interface, context, policy, and observation worlds. Record what boundaries preserve, forget, generate, or observe.

## Phase 4: Choose canonical constructions

Use the smallest construction that closes the exact obligation. Compare nearby alternatives and include obstruction reports.

## Phase 5: Present effectively

Choose algebraic syntax, dense probes, schema instances, defunctionalized IR, abstract domains, or another executable presentation.

## Phase 6: Prove one witness

The witness must cross the whole path:

```text
input -> syntax -> interpretation/effects/state -> observable behavior -> law
```

## Phase 7: Accrete

Only generalize after the witness is verified. Add one certified seam at a time.
