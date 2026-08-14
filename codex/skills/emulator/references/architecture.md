# Emulator Architecture

`$emulator` owns both the behavior contract and the executable synthetic world.

```text
source evidence + explicit user decisions
                  |
                  v
          emulator-spec.yaml
                  |
                  v
 environments + episodes + traces + EER-v1
```

Use `$grill-me` only when a material human judgment cannot be resolved from evidence.

## Responsibility split

| Skill | Owns | Does not own |
|---|---|---|
| `$grill-me` | Material user judgments, scope, proof bar, failure priorities | Contracts or environments |
| `$emulator` | Contract authoring, environments, runs, mutation, traces, datasets, divergence reports | Undiscoverable user priorities or target-skill edits |
| `$tune` | Optional downstream skill-change diagnosis | Core emulator lifecycle |
| `$refine` | Optional downstream authorized edits | Core emulator lifecycle |

## Boundary

`emulator-spec.yaml` is the single normative boundary between authority and runtime.

Each rule identifies its authority:

```text
source evidence
explicit user decision
non-critical assumption
```

Source-faithful claims require source evidence. Designed deviations require explicit user decisions. Assumptions cannot define critical behavior.

Every implementation interprets one contract fingerprint.

Laws:

```text
same deterministic implementation + contract + scenario + seed + action sequence + oracle version
  -> same environment observations, state transitions, and terminal result

hidden ground truth
  -> environment/oracle-visible
  -> agent-visible only through contracted observations or tool results

hard oracle failure
  -> not overridable by reward or model judgment
```

## Canonical flow

1. Resolve source, target, revision, origin, and requested environment.
2. Inspect discoverable evidence.
3. Use `$grill-me` only for unresolved material choices.
4. Author or validate `emulator-spec.yaml`.
5. Generate and run one or more implementations.
6. Mutate, shrink, compare, and export only as requested.

Missing normative evidence is `source_contract_gap`, not permission to invent behavior. Conflicting authority is `contract_ambiguity`.

## Optional downstream route

```text
EER-v1 -> $tune -> $refine
```

Use it only after explicit skill-improvement intent.
