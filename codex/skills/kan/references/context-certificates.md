# Context Certificates for Kan

A Context Certificate is the witness object for a semantic-consumption boundary.

## Kan data

```text
Raw source worlds --M_q--> Task context schema T_q --render--> Consumer input
```

or lift-shaped:

```text
B = data-processing/source-selection plans
C = inference-ready context observables
P : B -> C = context projection/rendering/observable extraction
F : Task -> C = required context behavior
```

The lift question:

```text
Which data-preparation plan b in B projects to the required context observables F(q)?
```

## Certificate law shapes

```text
schema(Context(q)) = T_q
Obs_q(Context(q)) = required observables
provenance(Context(q)) is total for evidence-bearing claims
freshness(Context(q), consumption_time) holds
render(Context(q)) preserves Obs_q
```

## Falsifiers

- missing required observable;
- stale source;
- unsupported claim enters rendered packet;
- contradiction collapsed silently;
- irrelevant retained item changes no observable and should have been removed;
- rendering omits provenance or uncertainty required by the task.
