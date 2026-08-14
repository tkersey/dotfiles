---
name: emulator
description: "Define, generate, run, mutate, compare, and export executable emulator environments for agents. Use for `$emulator`, synthetic worlds, agent learning environments, scenario contracts, deterministic/noisy/adversarial environments, counterexamples, trajectory datasets, implementation divergence, trace reports, or EER-v1. Not for generic library reimplementation specs, material scope clarification, target-skill edits, or treating synthetic outcomes as production truth."
---

# Emulator

## Mission

`$emulator` owns the complete path from evidence or explicit design intent to executable synthetic experience.

```text
source evidence + explicit user decisions
                  |
                  v
          emulator-spec.yaml
                  |
                  v
environments -> agent episodes -> traces, counterexamples, datasets, EER-v1
```

Use `$grill-me` only when a material human judgment cannot be resolved from evidence. No separate contract-generation skill is required.

## Activation boundary

Use `$emulator` to:

```text
author an emulator contract from a repo, spec, tests, traces, or user design
generate an executable environment for an agent
instantiate deterministic, noisy, adversarial, or mutable worlds
run agents and collect replayable episodes
mutate or shrink scenarios to find counterexamples
compare agents or implementations against one contract
export traces, trajectories, divergences, or EER-v1
```

Do not use it for:

```text
material human choices -> $grill-me
generic portable library reimplementation contracts -> direct specification work
historical session mining -> $seq
one live watched session -> $shadow
skill diagnosis -> $tune only when explicitly requested
skill edits -> $refine only after explicit apply authority
```

## Request

Prefer:

```yaml
emulator_request:
  mode: design | implement | run | mutate | compare | export
  source:
    kind: repository | specification | tests | traces | user_design | existing_contract | mixed
    path:
    revision:
    fingerprint:
    evidence_refs: []
  contract_path: codex/emulators/<target>/emulator-spec.yaml
  target:
    name:
    kind: skill | agent_loop | tool_loop | workflow | library_protocol
  emulator_root: codex/emulators
  implementation_kinds: [deterministic, noisy, adversarial, mutation]
  seed:
  scenario_budget:
  authorized_files:
    allowed: []
    forbidden: []
  output:
    report: EER-v1
    trajectories: true
```

An existing contract is optional. Fail closed only when neither a valid contract nor enough evidence and explicit user decisions exist to author one.

## Modes

Choose exactly one mode.

### design

Author or repair `emulator-spec.yaml`. Do not generate runtime files.

### implement

Validate an existing contract or author the missing contract first, then generate or update the executable environment inside the authorized emulator directory.

Do not edit source repositories or target skills without explicit authority.

### run

Execute seeded scenarios against one or more implementations or agents. Capture observations, actions, tool interactions, state transitions, rewards, oracle results, termination, and skips.

### mutate

Generate contract-admissible variants and shrink failures. An invariant-breaking mutation must be explicitly labeled as a negative or boundary case.

### compare

Compare implementations or agents against the same contract. Classify differences as contract ambiguity, emulator bug, oracle gap, nondeterminism, behavior gap, or source-contract gap.

### export

Emit EER-v1 and requested trajectory, counterexample, or curriculum datasets.

`$tune` and `$refine` are optional downstream consumers, never implicit parts of this lifecycle.

## Contract ownership

`emulator-spec.yaml` is the single normative contract. Its contract fingerprint is the SHA-256 digest of the finalized file's exact UTF-8 bytes.

A contract declares one origin:

```text
source_faithful  source behavior is being reproduced
designed         explicit user intent defines the world
mixed            source behavior is the baseline with explicit deviations
```

Rules about source behavior must be grounded in executable tests, captured traces, public interfaces, schemas, source behavior, or non-contradicted normative documentation. Designed behavior must be grounded in explicit user decisions.

Every normative scenario rule, permission, side-effect boundary, terminal condition, oracle, reward, and mutation dimension must cite its authority. Assumptions may fill non-critical description only; never infer safety, security, authority, hidden truth, side effects, reward, or termination.

Normalize nondeterminism into explicit inputs:

```text
seed, time, timezone, locale, latency, failure schedule,
actor stochasticity, message ordering, collection normalization
```

Read `references/emulator-contract-profile.md` when authoring or validating the contract.

## Workflow

1. Bind the target, authority source or user design, revision when applicable, origin, and output path.
2. Inspect discoverable tests, traces, interfaces, schemas, behavior, and normative docs.
3. Use `$grill-me` only for unresolved material choices.
4. Author or validate `emulator-spec.yaml`.
5. Generate the requested environment implementations.
6. Run, mutate, compare, or export as requested.
7. Report exact contract gaps instead of inventing missing normative behavior.

## Environment laws

Every generated environment must expose semantic equivalents of:

```text
reset(scenario_id, seed) -> initial observation
observe() -> current agent-visible observation
step(action) -> observation, reward, done, termination reason, oracle results
score() -> deterministic score and invariant summary
trace() -> replayable execution trace
```

Hidden ground truth belongs to the environment and oracles. It reaches the agent only through contracted observations or tool results.

The same deterministic implementation, contract fingerprint, scenario, seed, recorded action sequence, and oracle version must reproduce the same environment observations, state transitions, and terminal result.

A failed hard oracle or trace invariant cannot be overridden by reward or model judgment.

## Implementations and traces

Implementations may be:

```text
deterministic  exact state-machine execution
noisy          seeded latency, failures, retries, and actor noise
adversarial    hostile inputs, injection, misleading outputs, hidden-state traps
mutation       declared perturbations and counterexample shrinking
```

Each declares its id, kind, contract fingerprint, supported scenarios, seed policy, oracle surface, nondeterminism, and limitations.

Each episode records:

```text
episode/scenario/case/agent/implementation ids and agent fingerprint
contract fingerprint, seed, recorded actions, and oracle version
visible observations and hidden-state fingerprint
actions, tool calls/results, state mutations, and rewards
oracle and invariant results
final state, termination, failure labels, and counterexample data
```

Read `references/synthetic-implementations.md` when generating environments.

## Oracle and learning policy

Prefer deterministic state, trace, tool, side-effect, schema, budget, and terminal assertions. Model judgment may support criteria that deterministic checks cannot express, but it is never sole authority for safety-critical behavior.

EER-v1 is the run-level evidence record. When requested, also emit:

```text
trajectories.jsonl
counterexamples.jsonl
curriculum.jsonl
```

Every dataset row binds the contract fingerprint, episode identities, agent fingerprint, implementation, seed, recorded actions, trace, terminal status, and oracle result.

A counterexample becomes a binding regression only after adoption into `emulator-spec.yaml`.

## Output

```text
Emulated:
- Source and origin:
- Contract and fingerprint:
- Target and mode:
- Implementations and agents:
- Seed and scenario budget:

Run summary:
- Executed / passed / failed / skipped:

Findings:
- Divergences:
- Counterexamples:
- Oracle gaps:
- Contract ambiguities:
- Candidate regressions:

Artifacts:
- Environment:
- Traces:
- Datasets:
- EER-v1:

Next route:
- none | repair-contract | build-more-implementations | export-eval-dataset | optional-handoff-tune
```

Use `optional-handoff-tune` only after explicit skill-improvement intent.

## Hard rules

- `$emulator` owns emulator contract authoring and environment generation.
- `$grill-me` owns unresolved material human judgments.
- Keep one normative `emulator-spec.yaml`.
- Attribute every normative rule; do not silently invent behavior.
- Preserve contract, scenario, case, implementation, agent, seed, and oracle identities.
- Keep hidden truth out of uncontracted agent observations.
- Every exported failure has a trace, fixture, or skip reason.
- Prefer contract-faithful behavior and deterministic checks.
- Do not edit target skills or infer skill defects from emulator failures.
- Do not invoke `$tune` or `$refine` without explicit skill-improvement intent.
