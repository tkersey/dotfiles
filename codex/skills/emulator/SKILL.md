---
name: emulator
description: "Instantiate Ghost-style behavior contracts as executable, replayable, mutatable synthetic implementations. Use for `$emulator`, emulator runs, generated worlds from Ghost packages, synthetic implementations, scenario mutation, counterexamples, implementation divergence, trace reports, or EER-v1 execution reports. Not for deciding what to specify, producing Ghost contracts, editing target skills, or assuming emulator failures imply skill defects."
---

# Emulator

## Mission

`$emulator` turns portable behavior contracts into executable synthetic experience.

```text
$grill-me learns what is worth specifying
$ghost    captures the behavior contract
$emulator instantiates, runs, mutates, and compares implementations
```

`$emulator` does not decide what matters, produce the Ghost contract, diagnose skill deltas, or edit target skills.

## Activation boundary

Use `$emulator` when the user asks to:

```text
generate executable worlds from a Ghost package
instantiate a scenario spec as a runnable environment
create deterministic, noisy, adversarial, or mutation implementations
run or compare synthetic implementations
mutate scenarios to find counterexamples
produce traces, divergence reports, or EER-v1
```

Do not use `$emulator` for:

```text
material scope clarification -> $grill-me
portable behavior contract/spec extraction -> $ghost
historical session mining -> $seq
one live watched session -> $shadow
skill change diagnosis -> $tune only if explicitly requested
skill package edits -> $refine only after explicit apply authority
```

`$tune` and `$refine` are optional downstream consumers, not part of the core emulator lifecycle.

## Inputs

Prefer:

```yaml
emulator_request:
  mode: design | implement | run | mutate | compare | export
  source_contract:
    kind: ghost_package | ghost_scenario_tests | emulator_contract
    path:
    fingerprint:
  target:
    name:
    kind: skill | agent_loop | tool_loop | workflow | library_protocol
  emulator_root: codex/emulators
  implementation_kinds:
    - deterministic
    - noisy
    - adversarial
    - mutation
  seed:
  scenario_budget:
  authorized_files:
    allowed: []
    forbidden: []
  output:
    report: EER-v1
```

Fail closed when the source contract is absent or the target is unknown.

## Modes

Choose exactly one mode.

### design

Inspect a Ghost-style contract and produce an emulator design plan.

No files are changed unless the user explicitly requests implementation.

### implement

Create or update emulator implementation files inside the authorized emulator directory.

Do not edit the source Ghost package unless the user explicitly asks for contract repair.

Do not edit target skills.

### run

Execute seeded scenarios against one or more emulator implementations.

Capture traces, state transitions, oracle results, and skipped-case reasons.

### mutate

Generate scenario variants from the contract while preserving declared invariants.

Use mutations to find smaller counterexamples, wider boundary coverage, and oracle gaps.

### compare

Compare multiple synthetic implementations against the same contract.

Classify differences as contract ambiguity, emulator bug, oracle gap, nondeterminism, or behavior gap.

### export

Emit an `emulator_execution_report / EER-v1`.

Only produce `$tune`-compatible evidence when the user explicitly asks to use emulator findings to improve a skill.

## Source contract rules

The preferred source is a Ghost scenario-layout package:

```text
SPEC.md
tests.yaml
TESTS_SCHEMA.md
VERIFY.md
verification/evidence/*
```

Treat `tests.yaml` as the behavior contract.

Treat `SPEC.md` as explanatory and normative only where the Ghost package marks it as binding.

Treat `VERIFY.md` and `verification/evidence/*` as provenance and confidence evidence.

If the Ghost package is incomplete, report the missing contract surface instead of inventing it.

## Synthetic implementations

Generate implementations from the same contract, such as:

```text
deterministic  exact, reproducible state-machine execution
noisy          latency, partial failure, retries, stochastic user behavior
adversarial    hostile inputs, prompt injection, misleading tool output
mutation       systematic perturbation and counterexample shrinking
```

Each implementation must declare:

```yaml
implementation:
  id:
  kind:
  source_contract_fingerprint:
  seed_policy:
  supported_scenarios: []
  oracle_surface:
  nondeterminism:
  limitations: []
```

## Runtime traces

Capture enough evidence to reproduce and explain behavior:

```text
scenario id
case id
implementation id
seed
initial visible state
hidden ground truth fingerprint
tool surface
user/actor events
tool calls and responses
state mutations
trace invariants checked
oracle results
final state
failure labels
counterexample data
```

Do not rely on final text matching when state or trace assertions can express the outcome.

## Oracle policy

Prefer deterministic oracles:

```text
state assertions
trace invariants
forbidden tool checks
side-effect checks
budget and step limits
schema assertions
```

Use model judgment only when deterministic checks cannot express the criterion.

Never let a model judge be the sole authority for safety-critical behavior.

When an oracle fails, classify whether the likely problem is:

```text
contract_ambiguity
emulator_bug
oracle_gap
nondeterminism
behavior_gap
source_contract_gap
```

## Output

Default report:

```text
Emulated:
- Source contract:
- Target:
- Mode:
- Implementations:
- Seed:
- Scenario budget:

Run summary:
- Executed:
- Passed:
- Failed:
- Skipped:

Findings:
- Divergences:
- Counterexamples:
- Oracle gaps:
- Contract ambiguities:
- Candidate regressions:

Artifacts:
- Traces:
- Report:
- EER-v1:

Next route:
- none | repair-contract | build-more-implementations | export-eval-dataset | optional-handoff-tune
```

Use `optional-handoff-tune` only when the user explicitly asks to improve a skill from emulator evidence.

## Hard rules

- `$grill-me` decides material user judgments; `$emulator` does not.
- `$ghost` owns portable contract generation; `$emulator` consumes the contract.
- Do not edit target skills.
- Do not assume emulator failures imply skill defects.
- Do not route to `$tune` or `$refine` unless skill improvement is explicit.
- Preserve seeds, fingerprints, implementation IDs, and oracle versions.
- Every exported failure must have a trace, fixture, or skipped-case reason.
- Prefer contract-faithful implementation over creative scenario invention.
- Prefer deterministic checks over model-judged checks.
- Report source-contract gaps instead of filling them silently.
