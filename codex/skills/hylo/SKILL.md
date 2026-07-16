---
name: hylo
description: "Compile historical Codex sessions into blinded counterfactual replay episodes, govern sealed paired HCTP trials, grade comparable observable outcomes, and fold typed evidence into RUN, OBSERVE, or STOP. Use for `$hylo`, counterfactual replay, causal frontiers, paired baseline/candidate trials, sealed evidence, or evidence-governed improvement."
---

# Hylo

## Mission

Turn historical execution evidence into controlled counterfactual experiments
and a reusable causal frontier.

```text
historical session
  -> counterfactual cut + blinded replay episode
  -> baseline and candidate executions under one frozen contract
  -> observable traces + frozen grades + paired comparison
  -> failure signatures + hypotheses + bounded experiments
  -> RUN | OBSERVE | STOP
```

Hylo does not imitate a transcript, recover private reasoning, train model
weights, or invent a sequence of edits. It freezes the causal prefix before a
target first influences the session and regenerates everything downstream.

`STOP: no_obvious_next_step` is a successful result when the evidence does not
justify one intervention.

## Current product boundary

The released CRF/HCTP product route is:

```text
Seq 0.3.50+     episode compilation and source governance
Ledger 0.10.3+  artifact validation, trial custody, event folds, causal frontier
CAS 0.2.80+     one-claim lane execution and run-receipt normalization
```

The `seq hylo-extract`, `ledger --source hylo`, and `cas trial` product
surfaces are currently admitted on macOS. Stateless `ledger validate hylo-*`
schema checks remain platform-neutral. Do not invent an unadmitted
platform-specific isolation route.

The supported macOS proof establishes commitments, role separation, one-shot
descriptor delivery, and public non-disclosure. It records
`os_confinement:false`; it does not claim hostile same-user isolation.

## Ownership

```text
$seq / seq hylo-extract
    owns historical parsing, target activation, the causal cut, redaction,
    episode construction, target capture, and runner/custody separation

$ledger / ledger --source hylo
    owns validation, trial registration and lifecycle, immutable campaign
    events, deterministic folds, proof export, and causal-frontier decisions

$cas / cas trial
    owns one-claim lane execution, clean workspaces, observable evidence hashes,
    and hylo-run-receipt/v1 production

runner and grader adapters
    own model/tool execution and frozen observations; they do not edit targets

target owner workflow
    owns any authorized edit, staging, commit, or publication

$hylo
    coordinates those owners without borrowing their authority
```

The historical response is sealed source evidence. It MAY support diagnostic
failure mining after authorized custody access, but it MUST NOT satisfy a replay
baseline or act as a golden answer.

## Source-of-truth order

When surfaces disagree, use this order:

1. installed CLI help and capabilities;
2. released validators and schemas;
3. implementation documentation and executable fixtures;
4. this skill;
5. proposed specifications or historical campaign prose.

Do not invoke a proposed `hylo replay`, `hylo grade`, or `hylo compare` binary.
Those standalone commands are not the released product surface.

## Bootstrap and capability gate

Before the first native Ledger command, load `$ledger` and complete
`$ledger ensure` once. Then probe all three released owners:

```bash
ledger --version
ledger --source hylo capabilities
ledger --source hylo --help

seq --version
seq capabilities --format json
seq hylo-extract --help
seq hctp-source --help

cas --version
cas capabilities --json
cas trial --help
```

For the complete route, require the version floor in **Current product
boundary** and these capabilities or commands:

```text
Seq:    hylo_extract_v1, hctp_source_selection_v1, hctp_sealed_case_v1
Ledger: hylo_trial_v1, hylo_lane_leases_v1, hylo_pair_grade_v1,
        hylo_trial_reveal_v1, hylo_proof_bundle_v1,
        hylo_grade_commit_open_v1
CAS:    trial preflight, compile-replay, run, status, cleanup
```

If a required surface is absent, stop before creating evidence. Do not emulate
the source with a fallback writer or hand-edit `.ledger/hylo/events.jsonl`.

Read [contracts.md](references/contracts.md) before authoring artifacts or
trial events. Read
[grading-and-progression.md](references/grading-and-progression.md) before
grading, comparing, selecting an experiment, or claiming improvement.

## Modes

Choose one primary mode per invocation:

```text
extract   compile one historical response into a blinded CRF episode
trial     register or advance one paired HCTP trial
measure   grade observable attempts and derive paired evidence
frontier  compile typed hypotheses, experiments, and RUN | OBSERVE | STOP
report    inspect progress, trial state, proof state, or limitations
doctor    validate artifacts, campaign state, or event-chain integrity
```

A persistent request may repeat a verified mode transition. It does not grant
target-edit, external-effect, reveal, publication, or spend authority.

## Workflow

### 1. Compile the counterfactual episode

Select one historical response and the target whose influence is being
replaced. Use the canonical trace compiler, not an analytics projection that
deduplicates messages or drops context.

```bash
umask 077
: >./owner.key
chmod 600 ./owner.key

seq hylo-extract \
  --root ~/.codex/sessions \
  --session-id <session-id> \
  --turn-index <one-based-turn-or-zero-for-first> \
  --target-skill <skill-name> \
  --target-root /absolute/path/to/complete/target \
  --context-policy dependency-closed \
  --capture-world \
  --output-root ./runner \
  --sealed-root ./custody \
  --seal-key-output-fd 3 3>./owner.key
```

The key sink must be a caller-owned `0600` single-link regular file outside
the source, target, runner, and custody roots, or an anonymous pipe. Never use
stdin, stdout, stderr, an environment variable, a named FIFO, or a file inside
an artifact root.

`--target-root` names the complete historical bundle, including referenced
files, scripts, templates, and assets. Extraction fails closed on target drift,
root overlap, symlinks, malformed trace data, ambiguous activation, unknown
state-bearing pre-cut carriers, sensitive target bytes, or answer-before-
activation ordering.

The cut MUST precede the earliest structured target influence. Preserve
ordered and duplicate message occurrences, fixed pre-cut observations, and the
replaceable target slot. Regenerate post-cut target behavior, workers, tools,
files, responses, and outcomes.

### 2. Keep runner and custody artifacts separate

The runner root receives only causal inputs:

```text
runner-input.json
stimulus.json
baseline-bundle.json
captured target files
world.json
world-availability.json
runtime.json
```

The private `0700` custody root receives controller/grader evidence:

```text
episode.json
cut.json
redaction.json
historical-response.sealed.json
manifest.json
```

The runner consumes `runner-input.json`, not custody `episode.json`. Never
copy the sealed response, excluded-future digest material, future outcomes, or
grader-only references into the runner root.

Treat `world-availability.json` as authoritative for fidelity. Slice 1
reserves `exact_reconstruction`; it does not claim it. If historical repository
or runtime bytes are unavailable, retain the explicit limitation and do not
upgrade a `transcript_only` or `replay_eligible:false` episode by assertion.

Validate the generated graph before trial construction:

```bash
ledger validate hylo-runner-input --input ./runner/runner-input.json
ledger validate hylo-stimulus --input ./runner/stimulus.json
ledger validate hylo-target-bundle --input ./runner/baseline-bundle.json
ledger validate hylo-world-snapshot --input ./runner/world.json
ledger validate hylo-world-availability-receipt --input ./runner/world-availability.json
ledger validate hylo-runtime-contract --input ./runner/runtime.json
ledger validate hylo-replay-episode --input ./custody/episode.json
ledger validate hylo-counterfactual-cut-receipt --input ./custody/cut.json
ledger validate hylo-redaction-receipt --input ./custody/redaction.json
ledger validate hylo-custody-manifest --input ./custody/manifest.json
```

These are pure schema/invariant checks. A pass grants no replay, reveal, edit,
or publication authority.

### 3. Freeze source selection

Use `seq hctp-source` to compile the complete denominator, dependency-aware
independence clusters, split integrity, sanitized source commitments, and any
case-blind sealed payloads:

```bash
seq hctp-source compile \
  --manifest source.json --output selection.json \
  --source-signing-seed-fd <fd>
seq hctp-source validate --receipt selection.json --trial trial.json
```

`govern` derives source-governance evidence. `materialize` releases one exact
registered visible case through a protected FD and emits a lane-scoped signed
receipt; it must not release the hidden reference. Consult
`seq hctp-source --help` for sealed-case arguments and descriptor ownership.

### 4. Freeze a paired HCTP trial

Build `hylo-trial/v1` before candidate execution. Freeze:

- campaign, purpose, split, units, independence clusters, pairs, and repeats;
- opaque arms and balanced A/B-B/A execution order;
- baseline and candidate target identities and common projection;
- source-selection and visible/hidden commitments;
- runtime, tool/effect policy, runner, model, and environment projections;
- rubric, oracle, judge, producer, trust, and assurance authorities;
- reveal, stop, publication, and proof policies.

Use `practice_repair` trials to select repairs. Reserve untouched `promotion` units for
holdout evidence. A null trial is a real control: its two semantic arms have an
identical common target projection and a declared null intervention witness.

```bash
ledger --source hylo validate-trial --repo <repo> --trial trial.json
ledger --source hylo register-trial --repo <repo> --trial trial.json
```

Registration is atomic over the complete manifest. Trial lifecycle events are
owned by high-level Hylo commands; low-level `append` must not author them.

### 5. Execute lanes without unblinding

Use `cas trial` for each registered lane:

```bash
cas trial preflight --trial trial.json --lane-id <lane> --json
cas trial compile-replay \
  --trial trial.json --lane-id <lane> --output-dir <compiled-dir> --json
```

For an admitted run, the controller obtains or commits the lane lease through
Ledger, delivers the lease and visible input through protected file
descriptors, and calls `cas trial run` with the exact registration and start
digests. CAS claims the lane before execution, creates a fresh workspace,
invokes the executor exactly once, hashes every evidence file, and emits one
`hylo-run-receipt/v1`.

The executor receives only:

```text
EXECUTOR --request REQUEST.json --result RESULT.json
```

It must not receive the lane lease, semantic arm identity, sealed historical
response, hidden reference, future outcome, grade opening, or pair result.

For `assurance.required_level:sealed`, use the supported broker/driver route
with `commit-lane-start`; output-style `start-lane` is invalid. Preserve the
encrypted pending checkpoint and use exact recovery commands after an
acknowledgement loss. Recovery may finish already-admitted work; it must not
create changed or additional work.

Public lifecycle primitives include:

```text
register-trial
start-lane | commit-lane-start | recover-lane-start
lane-materialization
finish-lane | recover-lane-finish
grade-lane
grade-pair
reveal-trial
trial-result
close-trial
inspect
proof-artifact-set
export-proof
verify-proof
```

Consult `ledger --source hylo --help` for the exact current arguments. Never
put leases, signing seeds, grade openings, hidden references, or custody keys
in command-line arguments, environment variables, normal stdout, the event
store, or proof bundles.

### 6. Grade observable consequences

Grade hard gates before scored dimensions. Use visible messages, tool events,
file effects, worker events, tests, runtime metadata, signed receipts, and
human attestations. Never request or persist private chain-of-thought.

Record blind absolute lane grades and blind pair grades against the frozen
producer and grader authorities. Pre-reveal controller output may contain only
public metadata, commitments, fingerprints, and opaque acknowledgements. It
must not disclose plaintext grades, pair winners, or semantic arm labels.

The historical response may be inspected only by an authorized custody/grader
route and remains diagnostic. The comparison denominator is a fresh compatible
`replay_baseline` executed before the candidate for the same episode.

### 7. Reveal, compare, and prove

Reveal only after every required lane and grade is terminal and the frozen
reveal policy is satisfied:

```bash
ledger --source hylo reveal-trial --repo <repo> --reveal reveal.json
ledger --source hylo trial-result \
  --repo <repo> --trial-id <trial-id> --format markdown
```

After reveal, derive paired dimension deltas, hard-gate changes, dispersion,
critical violations, observable behavior deltas, and calibration/null-trial
results. Keep association, comparison-valid delta, supported mechanism, and
causal claim distinct.

For portable proof, obtain the exact artifact set, have the trusted source
owner sign that set, then export and verify:

```bash
ledger --source hylo proof-artifact-set \
  --repo <repo> --trial-id <trial-id> --output proof-artifacts.json

ledger --source hylo export-proof \
  --repo <repo> --trial-id <trial-id> --output proof.tar \
  --sanitization-receipt proof-sanitization.json

ledger --source hylo verify-proof --repo <repo> --input proof.tar
```

Proof verification establishes the declared closure and anchors. It does not
grant target-edit, commit, push, or generalized-improvement authority.

### 8. Fold campaign evidence and the causal frontier

The compatible campaign fold remains available for
`hylo-campaign/v1`, `hylo-scenario/v1`, target snapshots, attempts, grades,
changes, publications, and progress:

```bash
ledger --source hylo validate-campaign --campaign campaign.json
ledger --source hylo snapshot-target \
  --repo <repo> --revision INDEX --input target-roots.json
ledger --source hylo append --repo <repo> --json event-intent.json
ledger --source hylo doctor --repo <repo>
ledger --source hylo progress \
  --repo <repo> --campaign-id <campaign-id> --format json
```

Do not confuse compatibility with authority. A `historical_baseline` event is
diagnostic only; candidate comparison still requires a compatible prior
`replay_baseline`.

Typed causal events are:

```text
failure_signature_recorded
hypothesis_recorded
experiment_recorded
next_step_recorded
```

Every target-changing experiment must bind observable evidence, one mechanism,
a bounded intervention, measurable predictions, protected controls, explicit
falsifiers, a changed content-addressed target, and sufficient reserved
promotion budget.

Derive, do not guess, the next step:

```bash
ledger --source hylo frontier \
  --repo <repo> --campaign-id <campaign-id> --format json

ledger --source hylo next-experiment \
  --repo <repo> --campaign-id <campaign-id>
```

Interpret the result literally:

```text
RUN      exactly one eligible intervention is non-dominated
OBSERVE  one bounded read-only probe can discriminate among alternatives
STOP     no eligible intervention, or unresolved alternatives have no bounded probe
```

Every projection reports `authority_granted:false` and
`target_mutated:false`. A `RUN` decision selects an experiment; it does not
authorize or apply the edit.

### 9. Route an authorized repair through the owner

Only practice evidence may motivate a change in the active campaign. Route the
selected experiment through the target's owner workflow and preserve:

```text
experiment_id
hypothesis_ids
before and after bundle fingerprints
before and after target snapshots
prediction-contract fingerprint
authorized paths and semantic change budget
```

After eligible holdout or challenge evidence is exposed for the candidate,
reject further target changes in that campaign. A miss means reject the
candidate or begin a new campaign with untouched cases.

Publication requires explicit authority, the exact evaluated bundle and
snapshot, the latest complete required repeat cohort, no forbidden critical
violations, exact changed paths, and equality between the committed target
projection and the promoted projection. Push authority remains separate.

## Output

```text
Hylo:
- mode / campaign / trial / target bundle
- episode / cut / world / runtime / fidelity limitations
- runner-custody separation and blindness status
- pairs / repeats / terminal lanes / eligible grades
- hard gates / dimension deltas / behavior deltas / uncertainty
- active failure signatures / hypotheses / experiments
- decision: RUN | OBSERVE | STOP
- Hylo authority_granted: false; report any owner authority separately
- event-chain or proof identity
```

## Hard rules

- No cut after the first causally relevant target influence.
- No dropped or deduplicated fixed-prefix message occurrence.
- No historical answer, future outcome, hidden oracle, or grade opening in runner input.
- No historical response as a replay baseline or golden answer.
- No invented world, exact-reconstruction claim, fixture response, or missing observation.
- No target label change without a target-content change.
- No trial change after registration; changed contracts require a new trial.
- No lane execution without registration, lease lineage, and one-claim custody.
- No trial lifecycle event through low-level `append`.
- No private reasoning in attempts, grades, portable artifacts, or proofs.
- No hard-gate failure averaged away by a scalar score.
- No comparison across episode, world, runtime, tool/effect, oracle, grader, or visibility drift.
- No repair motivated by exposed holdout or challenge evidence.
- No intervention without predictions, controls, falsifiers, scope, and budget.
- No `RUN` decision treated as mutation authority.
- No publication from cherry-picked repeats or mismatched committed bytes.
- No unadmitted platform-specific isolation claim or hidden OS-confinement assumption.
- No hand-editing `.ledger/hylo/events.jsonl`.
- No endless edit loop when the derived answer is `STOP`.
