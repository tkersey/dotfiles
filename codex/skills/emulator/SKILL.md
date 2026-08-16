---
name: emulator
description: "Define, compile, run, mutate, compare, and export total synthetic or partial session-derived agent environments. Use for `$emulator`, session-derived environments, existing session corpora, correction windows, environment atlases, harness optimization, preference extraction, fresh baseline/candidate comparisons, synthetic worlds, counterexamples, trajectories, or EER-v1. Not for treating historical actions as expert labels, inventing unsupported transitions, or mutating a live harness without separate authority."
---

# Emulator

## Mission

`$emulator` owns one content-addressed contract closure containing total synthetic
worlds and partial session-derived charts.

```text
source evidence or explicit design
  -> emulator-spec.yaml closure
  -> environment charts
  -> fresh actor runs
  -> hard oracles, state diffs, traces, and eligible datasets
```

A historical session is a partial transition witness, not a complete simulator,
expert demonstration, or baseline arm. Historical evidence discovers what to
challenge; fresh executions decide whether a harness candidate wins.

Use `$grill-me` only when a material human judgment cannot be resolved from
evidence. Do not introduce a native CLI, protocol service, database, or global
event store. The private file-backed exposure claims, locks, and retirement
index required by the atlas contract are permitted evidence assets, not a new
product or service.

## Activation boundary

Use `$emulator` to:

```text
author a contract from a repository, spec, tests, traces, sessions, or design
compile correction windows into normative decision charts
reconstruct resettable tasks as executable episode charts
preserve useful but non-selecting evidence as observational charts
run total synthetic or honest partial environments
compare fresh baseline and factor-local candidate harnesses
export EER-v1, preference rows, fresh trajectories, or curriculum rows
```

Do not use it for:

```text
physical session facts -> Seq owns discovery, identity, order, and tool facts
material user choices -> $grill-me
automatic target-skill or live-harness edits
historical-trace imitation or private chain-of-thought reconstruction
model-generated transitions presented as source-faithful history
```

## Request

Prefer:

```yaml
emulator_request:
  mode: design | implement | run | mutate | compare | export
  source:
    kind: session | session_corpus | repository | specification | tests | traces | user_design | existing_contract | mixed
    session_id:
    session_path:
    root:
    repo:
    since:
    until:
    revision:
    fingerprint:
    evidence_refs: []
  contract_path:
  target:
    name:
    kind: agentic_harness | skill | agent_loop | tool_loop | workflow | library_protocol
  atlas:
    atlas_id:
    storage_domain_root:
    root:
    chart_kinds: [normative_decision, executable_episode, observational]
    partitions:
      discovery:
      development:
      holdout:
  experiment:
    subject: harness
    factor:
    baseline_harness:
    candidates: []
    max_candidates: 3
  authorized_files:
    allowed: []
    forbidden: []
  output:
    report: EER-v1
    preferences: true | false
    trajectories: true | false
    curriculum: true | false
    counterexamples: true | false
```

Session-derived atlases default to
`${CODEX_HOME:-$HOME/.codex}/emulators/<atlas-id>/`; shareable designed
environments may use `codex/emulators/<target>/`. Do not create empty
scaffolding or commit session artifacts without explicit sanitization and
authority. Verify the selected private root is writable before authoring; when
the default is not writable, require a caller-supplied writable private
`storage_domain_root` and derive the atlas root as
`<storage_domain_root>/emulators/<atlas-id>` rather than silently writing into
the repository. Freeze one caller-supplied domain for the complete source
corpus and comparison cycle. Its location does not determine selection
eligibility: a private fallback root may support holdout only when the single
user-global exposure registry required by `session-derived-atlas.md` is
writable and prior exposure outside that registry can be excluded. Otherwise
the atlas is diagnostic/development-only.

## Modes

Choose exactly one mode.

### design

Compile or repair the root contract and its charts. Do not generate runtime
files unless the requested artifact is itself an actor packet or evaluator.

### implement

Author or validate the contract closure when needed, then materialize its
executable world, reset, tool, fixture, and evaluator assets. Do not edit source
repositories or target skills without separate authority.

### run

Execute one frozen harness against selected charts. Capture only fresh runtime
observations, actions, effects, terminal state, cost, and trace.

### mutate

Apply only chart-declared mutations. A mutation outside declared support creates
a new designed chart; it never becomes a source-faithful transition. Each
declared dimension binds its domain, preserved laws, shrink strategy, and any
generator bytes through the chart closure. Mutation execution uses one frozen
harness subject; compare mutated results only in a separate `compare` request.

### compare

Run fresh baseline and candidate arms against the same chart boundary and emit a
chart-aware comparison. Both arms are frozen harness bundles. The historical
trajectory is never an arm.

### export

Emit EER-v1 and only datasets whose fresh evidence, authority, partition, and
visibility rules make them eligible. Export reads an existing contract closure;
it does not rewrite the root, its sealed EER, or change the root's originating
`operation_mode`. A deferred export emits a content-addressed export manifest
that binds the original EER/runs and every emitted dataset.

## Contract ownership

One normative content-addressed contract closure is rooted at
`emulator-spec.yaml`. The root fingerprint is SHA-256 of its exact UTF-8 bytes.
Each chart is bound by exact bytes, and each chart recursively binds every
execution-relevant external source map, actor input, world/reset recipe, fixture,
tool manifest, and evaluator asset by exact SHA-256. A referenced artifact that
is missing or mismatched makes the environment invalid.

The contract declares `source_faithful`, `designed`, or `mixed` origin. Every
normative rule, permission, side-effect boundary, evaluator, terminal condition,
reward, and mutation dimension cites its authority. Assumptions cannot define
safety, authority, hidden truth, side effects, selection, or termination.

Read `references/emulator-contract-profile.md` when authoring or validating a
contract. Read `references/session-derived-atlas.md` whenever a session source
is selected or any source will participate in holdout selection or a selecting
comparison.

## Environment laws

Every chart exposes semantic equivalents of:

```text
reset(chart_id, subject_id, repeat_id) -> observation
observe() -> current actor-visible observation
support(action) -> executable | judgeable | denied | observed_only | unsupported
evaluate(output_or_trace) -> oracle vector + state diff + reward + residual judgment
trace() -> fresh observable trace
```

Validate actor output against `actor.output_schema` and the action schema before
support routing; malformed actor output is `hard_fail`, not an unsupported
counterfactual. `step(action)` exists only when
`support(action) == executable`. Support classes
are mutually exclusive. An overlap or unverifiable classification is
`invalid_environment`; an attempted `observed_only` or `unsupported` transition
is `unsupported_counterfactual`; a `denied` action is `hard_fail`. Never guess a
next state.

Actor-visible and evaluator-only projections are separate. Selection and
training additionally require an actor-readable inventory and fingerprint plus
tool-access evidence proving hidden roots were inaccessible. A combined file is
not proof of separation.

A failed hard oracle, required state assertion, or trace invariant cannot be
overridden by reward, cost, preference, prose quality, or model judgment.
Executable charts judge required state and trace laws, not historical tool-
sequence imitation.

## Session-derived execution

Seq owns physical session discovery and exact source-event facts. `$emulator`
owns source bundles, cuts, chart classification, support, evaluator authority,
fresh comparison, claims, exports, and STOP decisions. CAS or the selected
existing runner owns fresh actor execution facts; Git and task tools own reset
and state assertions.

For correction charts, cut immediately before the disputed historical action.
Give the actor only facts legitimately available at that cut. Hide the action,
later correction, recovery, tests, review, final answer, labels, and holdout
evaluator details. Whole-harness executable comparisons cut before the first
assistant action unless earlier influence is proved absent.

All charts may support discovery. Only environment-valid fresh paired charts
with sufficient attribution, valid action support, evaluator authority, and
untouched holdout status may select a candidate. Group all charts from the same
root session, task, issue, PR, or worker lineage into one partition.

Read `references/session-derived-atlas.md` for source extraction, correction and
executable compilation, leakage checks, harness manifests, partitions, fresh
execution, evaluation, exports, and stop reasons.

## Comparison and learning policy

Freeze the baseline and each candidate as complete harness manifests. A candidate
changes exactly one semantic owner and cannot change charts, source bundles,
reset recipes, evaluators, comparison code, actor runner, or holdout
partitioning. Candidate generation cannot inspect active holdout material.

Evaluate in this order:

```text
environment validity -> actor schema -> support -> hard oracles -> state diff
-> trace laws -> protected dimensions -> reward -> cost/latency -> residual judgment
```

In `compare` mode, recommendations are `adopt`, `reject`, or
`insufficient_evidence`, but they grant no mutation authority. Other modes omit
the recommendation. Export preference rows only from direct authority
and a fresh passing chosen action. Export trajectories only from fresh valid
executable runs. Active holdouts never enter training exports.

Read `references/eer-v1.md` for run accounting and comparison artifacts. Read
`references/synthetic-implementations.md` when generating designed worlds.

## Output

```text
Emulated:
- Source, origin, and limitations:
- Contract closure and fingerprints:
- Charts, groups, partitions, and support:
- Baseline, candidate, factor, and fresh runs:

Run summary:
- Valid / passed / hard-failed / ambiguous:
- Invalid environment / unsupported / runtime error / skipped:

Findings:
- Hard-oracle and state deltas:
- Protected regressions:
- Residual preference:
- Recommendation (compare mode only): adopt | reject | insufficient_evidence

Artifacts:
- Source bundles, actors, worlds, traces, reports, and eligible datasets:

Next route:
- none | repair-contract | reconstruct-world | choose-factor | separately-authorize-adoption
```

## Hard rules

- Historical sessions are sources, never baseline arms or expert labels.
- Preserve exact source provenance, content-addressed closure, and source order.
- Keep actor and evaluator projections separate and prove actor-readable roots.
- Keep support classes exclusive; never totalize an unknown transition.
- `reset`, `observe`, `support`, `evaluate`, and `trace` are universal; `step` is not.
- All charts may discover; only eligible fresh charts may select.
- Use one semantic factor per candidate and freeze it before holdout execution.
- Keep active holdouts out of candidate generation and training exports.
- Hard oracles and protected dimensions dominate preferences and scalar scores.
- Stop on leakage, drift, missing authority, unsupported transitions, or irreconstructable state.
- Never mutate the live harness or publish private data without separate authority.
- Do not add a native subsystem before repeated real charts prove a general capability gap.
