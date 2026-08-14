# Synthetic Implementation Patterns

`$emulator` may generate multiple executable environments from one `emulator-spec.yaml`.

Variation belongs in implementation behavior or contract-declared mutations, not silent changes to normative semantics.

## Common surface

Each implementation provides equivalents of:

```text
reset(scenario_id, seed)
observe()
step(action)
score()
trace()
```

## Deterministic

Use for debugging and reproducible counterexamples.

```text
fixed seed
explicit state machine
stable tool responses
exact oracle checks
no unmodeled time or randomness
```

The same contract fingerprint, implementation id, scenario, seed, recorded action sequence, and oracle version must reproduce the same environment observations, state transitions, and terminal result.

## Noisy

Use for production-like reliability testing.

```text
tool latency
transient or partial failures
retries
actor hesitation
message-order noise
irrelevant context
```

All noise must be contract-admissible, seed-controlled, and trace-recorded.

## Adversarial

Use for security, safety, and robustness boundaries.

```text
injection in tool output
misleading user claims
conflicting instructions
forbidden-tool temptations
malformed responses
stale information
hidden-state traps
```

The world must preserve its contracted laws while presenting adversarial observations.

## Mutation

Use declared mutation dimensions to explore nearby cases and shrink failures.

An invariant-breaking mutation must be labeled as a negative or boundary case. Do not mutate outside the contract and claim conformance.

## Artifact layout

```text
codex/emulators/<target>/
  emulator-spec.yaml
  env-manifest.yaml
  implementations/
    deterministic/
    noisy/
    adversarial/
    mutation/
  scenarios/
    generated/
    mutations/
  traces/
  reports/
    EER-v1.yaml
  datasets/
    trajectories.jsonl
    counterexamples.jsonl
    curriculum.jsonl
  evidence/
```

Create only requested artifacts; empty scaffolding has no value.

## Reproducibility

Each implementation declares its id, kind, contract fingerprint, supported scenarios, seed policy, oracle version, nondeterminism, and limitations.

Each episode is reproducible from:

```text
contract fingerprint
implementation id
scenario id
case id
seed
oracle version
recorded action sequence
agent id and configuration fingerprint when regenerating actions
```
