# Synthetic Implementation Patterns

`$emulator` may generate total designed worlds and partial session-derived
charts inside one EC-v1 atlas.

Variation belongs in implementation behavior or contract-declared mutations.
It cannot silently widen transition support, evaluator authority, world
fidelity, or claim strength.

## Common surface

Every chart provides semantic equivalents of:

```text
reset(chart_id, subject_id, repeat_id)
observe()
support(action)
evaluate(output_or_trace)
trace()
```

`step(action)` is provided only for actions classified `executable`.
Synthetic worlds may declare `transition_model: total`; session-derived worlds
are commonly partial or have no transition model.

## Deterministic

Use for debugging, exact reset, hard oracles, and reproducible counterexamples.

```text
fixed seed
explicit state machine
stable tool responses
exact state and trace assertions
no unmodeled time or randomness
```

The same closure, implementation, chart, reset, seed, action sequence, and
evaluator version must reproduce the same observations, transitions, and
terminal result.

## Noisy

Use for contract-admissible reliability testing:

```text
tool latency and transient failures
retries
actor hesitation
message ordering
irrelevant context
```

All noise is seeded where possible and trace-recorded. If the actor runtime
offers no deterministic seed, declare `environment_seed_control: unavailable`, use repeats,
and lower the supported claim.

## Adversarial

Use for declared robustness boundaries:

```text
injection in tool output
misleading user claims
forbidden-tool temptations
malformed responses
stale information
hidden-state traps
```

Adversarial observations preserve the chart's laws and effect policy. They do
not expose hidden evaluator material.

## Mutation

Use only declared mutation dimensions. Each declares its domain, preserved laws,
intentional negative cases, and shrink strategy.

An invariant-breaking mutation is a negative or boundary case. A mutation
outside a session chart's declared support creates a new `designed` or `mixed`
chart with its own authority and fingerprint. It cannot be called a
source-faithful counterfactual.

Deterministic, noisy, adversarial, and mutation implementations never upgrade:

```text
ambiguous attribution -> direct
transcript_only -> exact
observed_only or unsupported -> executable
diagnostic -> harness_selection or promotion
```

## Storage

Shareable, sanitized designed worlds may live under:

```text
codex/emulators/<target>/
```

Session-derived material defaults to:

```text
${CODEX_HOME:-$HOME/.codex}/emulators/<atlas-id>/
```

Use private directory and file modes where supported. Do not commit raw
sessions, corrections, evaluator-only material, secrets, or private tool
outputs. Create only requested artifacts; empty scaffolding has no value.

## Reproducibility

Bind every implementation and run to:

```text
root and ordered chart fingerprints
recursive closure inventory
implementation plus the declared subject fingerprint; harness fingerprint only for a harness subject
chart and split identity
actor input and actor-readable inventory fingerprints
world/reset and evaluator fingerprints
runtime configuration, seed control, repeat id, and effect policy
fresh action sequence and trace
```

Reproducibility does not mean historical trace imitation. Executable charts may
reach the same valid state through a different trajectory unless sequence
identity is itself a contracted law.

## Rollback

Generated implementations and candidate worktrees are disposable. On invalid
closure, leakage, drift, or failed proof, stop actors and discard the isolated
candidate/reset workspace. Preserve private source and evaluation evidence by
default for diagnosis; remove it only with explicit authorization. No emulator
result edits or rolls back the live harness.
