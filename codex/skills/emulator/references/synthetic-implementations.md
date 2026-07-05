# Synthetic Implementation Patterns

`$emulator` may generate multiple executable implementations from the same Ghost contract.

## Deterministic implementation

Use for debugging and reproducible counterexamples.

Properties:

```text
fixed seed
explicit state machine
stable tool responses
exact oracle checks
no unmodeled time or randomness
```

## Noisy implementation

Use for production-like reliability testing.

Possible perturbations:

```text
tool latency
transient errors
partial failures
retryable failures
actor hesitation
message ordering noise
irrelevant context
```

All noise must be seed-controlled and trace-recorded.

## Adversarial implementation

Use to test security, safety, and robustness boundaries.

Possible perturbations:

```text
prompt injection in tool output
misleading user claims
conflicting instructions
forbidden tool temptations
malformed tool responses
stale policy snippets
hidden-state traps
```

The implementation must preserve the contract's declared invariants.

## Mutation implementation

Use to explore nearby cases and shrink failures.

Mutation dimensions may include:

```text
remove a visible fact
swap tool response order
rename an entity
change a threshold
add irrelevant noise
delay a tool
make hidden ground truth contradict the user's claim
```

Do not mutate a scenario in a way that invalidates the source contract unless the mutation is explicitly marked as a negative/boundary case.

## Artifact layout

Recommended output:

```text
codex/emulators/<target>/
  emulator-spec.yaml
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
  evidence/
```

Each implementation should be reproducible from source contract fingerprint, implementation id, seed, and oracle version.
