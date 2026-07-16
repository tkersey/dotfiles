# Hylo released contracts

This reference describes the released Hylo CRF/HCTP boundary used by `$hylo`.
Installed CLI help, capabilities, validators, and executable schemas remain the
authority when this document and a binary differ.

## Contract layers

Hylo currently has four additive layers:

```text
CRF episode graph      counterfactual cut, target bundle, world, runtime, custody
HCTP trial protocol    blinded paired lanes, grades, reveal, proof
campaign event fold    compatibility campaigns, attempts, grades, progress
causal frontier fold   failures, hypotheses, experiments, RUN | OBSERVE | STOP
```

Do not collapse them:

- a replay episode is not a whole campaign;
- a registered trial is not an authorization to reveal or edit;
- a historical diagnostic is not a replay baseline;
- a scalar grade is not a mechanism hypothesis;
- `RUN` is not mutation authority.

## Canonical identity

New CRF/HCTP identity uses:

```text
canonical JSON profile: hylo-canonical-json/v1
digest algorithm label: sha256-hylo-canonical-json-v1
fingerprint spelling:   sha256:<64 lowercase hexadecimal characters>
```

Important profile rules:

- signed 64-bit integers retain their exact value;
- arbitrary `number_string` and non-finite values are rejected;
- finite binary64 values use the pinned shortest-round-trip spelling;
- negative zero canonicalizes to `0`;
- strings and keys must be valid UTF-8;
- code points are preserved without Unicode normalization;
- object keys sort by raw UTF-8 bytes;
- array order remains significant.

This is not an unrestricted RFC 8785 claim. Identity code must use the shared
Hylo codec and its published vectors, not a language-default JSON writer.

## CRF extraction graph

### Command receipt

Successful `seq hylo-extract` prints one:

```text
hylo-extract-receipt/v1
```

It binds the episode identity and fingerprint, exact cut lines, runner
blindness, and absence of persisted custody plaintext. A receipt authorizes use
only of the artifacts produced by that successful invocation.

### Runner root

The runner root contains:

| File | Contract | Purpose |
| --- | --- | --- |
| `runner-input.json` | `hylo-runner-input/v1` | Pure manifest of runner-visible causal artifacts |
| `stimulus.json` | `hylo-stimulus/v1` | Ordered visible messages, fixed instructions, target slot |
| `baseline-bundle.json` | `hylo-target-bundle/v1` | Complete historical target treatment manifest |
| captured target paths | bundle file carriers | Verified bytes referenced by the bundle |
| `world.json` | `hylo-world-snapshot/v1` | Reconstructed observable world |
| `world-availability.json` | `hylo-world-availability-receipt/v1` | Fidelity and replay eligibility |
| `runtime.json` | `hylo-runtime-contract/v1` | Runtime identity and reconstruction label |

The runner input MUST NOT contain custody locators that disclose sealed bytes,
the historical response, future outcomes, grader references, or grade
openings.

### Custody root

The private custody root contains:

| File | Contract | Purpose |
| --- | --- | --- |
| `episode.json` | `hylo-replay-episode/v1` | Complete controller/custody episode |
| `cut.json` | `hylo-counterfactual-cut-receipt/v1` | Exact activation and causal-cut proof |
| `redaction.json` | `hylo-redaction-receipt/v1` | Source/output binding and substitutions |
| `historical-response.sealed.json` | `hylo-sealed-historical-response/v1` | XChaCha20-Poly1305 envelope |
| `manifest.json` | `hylo-custody-manifest/v1` | Sealed-entry fingerprint and owner-only key delivery |

The custody root is caller-owned `0700`. Runner, custody, source, and target
roots must not overlap by native filesystem identity or ancestry.

### `hylo-stimulus/v1`

The stimulus preserves:

```text
ordered message occurrences
duplicate message occurrences
roles and source-line provenance
fixed pre-cut instructions
one replaceable target instruction slot
attachments and initial goal state when present
requested and applied context policy
stimulus fingerprint
```

Instruction classes are:

```text
fixed
replaceable_target
runtime_owned
unknown
```

Extraction rejects an unknown state-bearing carrier that cannot safely cross
the cut. The target's historical body is represented by the replaceable slot;
it is not retained as fixed runner text.

### `hylo-counterfactual-cut-receipt/v1`

The current extractor admits an exact structured skill-activation cut. It
binds:

```text
activation reference
last fixed turn and event
first regenerated event
rationale
excluded-future digest
historical target-content fingerprint
cut fingerprint
```

An evaluated answer that precedes same-turn target activation is invalid. A
generic target mention is not exact activation authority.

### `hylo-target-bundle/v1`

Bundle identity covers:

```text
target kind and ID
entrypoint
ordered path, mode, and content fingerprints
target-content fingerprint
loader contract
dependency bundle fingerprints
bundle-fingerprint basis
```

Artifact location is provenance, not semantic treatment identity. Moving the
same verified bytes must not manufacture a new target. Sensitive bytes in a
captured target fail extraction; redacting them would mutate the treatment.

### World and runtime

`hylo-world-snapshot/v1` and `hylo-world-availability-receipt/v1` distinguish
observable reconstruction from unavailable history. Relevant identity may
include repository state, tool registry, clock, locale, environment
substitutions, fixtures, network/effect policy, and limitations.

Allowed fidelity language includes:

```text
exact_reconstruction
controlled_replay
workspace_snapshot
tool_tape_replay
transcript_only
diagnostic_only
unusable
```

Slice 1 reserves `exact_reconstruction`; admitted Slice 1 artifacts do not
claim it. Missing repository or historical runtime bytes remain explicit
missingness. `hylo-runtime-contract/v1` may label a compatible frozen current
runtime as `paired_contemporary_counterfactual`; that is not an exact historical
reconstruction.

### Redaction and sealing

Portable stimulus redaction uses stable per-value placeholders, including:

```text
<CREDENTIAL_1>
<EMAIL_1>
<HOME_1>
```

Repeated values reuse their placeholder. Redaction preserves surrounding
authorization, assignment, flag, and URI syntax. The receipt binds source and
output fingerprints, classes, counts, namespaces, semantic impact, and local
unredacted availability.

The historical response payload is sealed with XChaCha20-Poly1305. The key is
delivered only through the declared owner FD and is not persisted in the
runner root, custody manifest, event store, stdout, or proof bundle.

### Pure validators

```bash
ledger validate hylo-replay-episode --input FILE
ledger validate hylo-runner-input --input FILE
ledger validate hylo-stimulus --input FILE
ledger validate hylo-target-bundle --input FILE
ledger validate hylo-world-snapshot --input FILE
ledger validate hylo-world-availability-receipt --input FILE
ledger validate hylo-runtime-contract --input FILE
ledger validate hylo-counterfactual-cut-receipt --input FILE
ledger validate hylo-redaction-receipt --input FILE
ledger validate hylo-custody-manifest --input FILE
```

These validators are platform-neutral, read no Hylo store, mutate nothing, and
grant no authority.

## HCTP source governance

`seq hctp-source` owns source-side HCTP selection and materialization:

```text
compile      derive the complete denominator, independence clusters, split
             integrity, sanitization, source commitments, and sealed cases
validate     prove one source-selection receipt matches one trial
govern       derive source-governance evidence from admitted inputs
materialize release one registered visible case and source profile by FD,
             then emit a lane-scoped role attestation
```

```bash
seq hctp-source compile \
  --manifest source.json --output selection.json \
  --source-signing-seed-fd 3

seq hctp-source validate --receipt selection.json --trial trial.json
```

Case-blind compilation additionally uses a sealed directory and owner-only
seal-key output FD. Materialization accepts the exact sealed case, registered
trial, and lane ID; it receives the seal key and signing seed by FD and writes
visible input and the optional historical source profile only to protected
output FDs.

The primary artifacts are:

```text
hylo-source-selection-receipt/v1
hylo-sealed-case/v1
hylo-case-materializer-contract/v1
hylo-materialization-receipt/v1
```

The source-selection receipt must cover the registered units exactly, preserve
scenario/split/cluster/source commitments, and reject exact cross-split
duplicates. The materialization receipt binds one lane, one opaque arm, one
visible-input fingerprint, the frozen producer, and the controller/materializer
trust domain without disclosing semantic arm identity or hidden reference.

## HCTP trial protocol

### `hylo-trial/v1`

A trial freezes the complete paired experiment before execution:

```text
trial and campaign identity
purpose: practice_repair | promotion | mechanism_probe | environment_probe |
         calibration_null | calibration_positive | reliability_probe
canonical JSON profile
assurance and trust policy
allocation and order balancing
units, scenarios, splits, and independence clusters
pairs, repeats, lanes, and opaque arms
source profiles and source-selection receipt
target arm values and common projection
execution, model, runtime, tool, and effect projections
rubric, oracle, judge, and producer authorities
case, arm, and grade visibility
reveal and publication policy
```

Registration validates and appends the complete manifest atomically:

```bash
ledger --source hylo validate-trial --repo REPO --trial trial.json
ledger --source hylo register-trial --repo REPO --trial trial.json
```

Changing any frozen field requires a new trial identity.

Purpose constrains factor kind:

```text
practice_repair       target_snapshot | null
promotion             target_snapshot
mechanism_probe       instruction_bundle | evidence_set
environment_probe     environment_variant | tool_policy
calibration_null      null
calibration_positive  instruction_bundle | evidence_set | environment_variant |
                      model_configuration | tool_policy
reliability_probe     null
```

Assurance levels are `precommitted`, `receipt_bound`, `role_separated`, and
`sealed`. Every label must satisfy its declared trust and role contract; the
label alone is not evidence.

### Blinding

Before reveal, public/controller-visible material may include:

```text
opaque arm and lane IDs
commitments and fingerprints
public producer metadata
opaque acceptance acknowledgements
terminal status without semantic outcome
```

It must not include:

```text
semantic arm map
hidden reference
historical response plaintext
plaintext grade or pair winner
private grade opening
lease nonce or signing seed
```

### Lane lifecycle

HCTP lifecycle events are:

```text
trial_registered
lane_started
lane_finished
grade_committed
pair_grade_committed
pair_grade_recorded
trial_revealed
trial_closed
```

Only the high-level trial commands may create them. Low-level campaign
`append` rejects trial lifecycle events.

The public commands are:

```text
validate-trial
register-trial
start-lane
commit-lane-start
recover-lane-start
lane-materialization
finish-lane
recover-lane-finish
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

`start-lane` delivers a fresh lease through a protected FD before the public
start event commits. `commit-lane-start` accepts a caller-retained lease and is
the sealed-assurance route. Recovery requires the exact retained lease and
lineage; it re-emits an existing receipt and does not append changed work.

### CAS lane runner

`cas trial` exposes:

```text
preflight
compile-replay
run
status
cleanup
key-info
```

CAS owns the persistent one-claim boundary. `run` claims before executing,
uses a clean workspace, invokes the declared executor exactly once, hashes
evidence, and emits `hylo-run-receipt/v1`. An existing claim makes retry a hard
error; use status/recovery rather than executing again.

The executor receives one request path and one result path. It does not receive
the lane lease or hidden reference.

### Grades and reveal

Absolute and pair grades bind the registered:

```text
trial, unit, pair, lane, and attempt identity
rubric and oracle contracts
producer identity, version, binary fingerprint, key, and role
run-receipt fingerprints
grade commitments and private openings
critical-policy derivation
```

Grade commitments may be public before reveal; plaintext outcomes and openings
may not. Reveal must match the precommitted semantic arm map and all required
terminal/grade conditions. A reveal does not retroactively authorize target
mutation.

### Proof bundles

`hylo-proof-artifact-set/v1` enumerates the exact post-reveal artifact set that
a trusted source owner may sign as
`hylo-proof-sanitization-receipt/v1`. Export produces a deterministic
`hylo-proof-bundle/v1`; verification checks internal closure and may bind
explicit external anchors.

Live verification accepts the declared global event range as an immutable
prefix and validates the current suffix. An offline expected campaign head and
trust-policy fingerprint are exact-value anchors, not claims about the current
live head.

## Compatibility campaign fold

The pre-HCTP campaign API remains supported:

```text
hylo-campaign/v1
hylo-scenario/v1
hylo-event-intent/v1
hylo-event/v1
hylo-progress/v1
hylo-target-snapshot-request/v1
hylo-target-snapshot/v1
```

The portable campaign freezes target, source corpus, privacy receipt, rubric,
replay policy, stop policy, change/publication authority, scenario file, and
scenario manifest. Each scenario freezes visible request, hidden reference
locator, environment/effect policy, oracles, split, and optional synthetic
parent.

Compatibility event kinds are:

```text
campaign_created
target_bundle_admitted
scenario_admitted
attempt_recorded
grade_recorded
feedback_recorded
change_recorded
publication_recorded
campaign_closed
```

The native store adds global and campaign sequences, predecessor digests,
canonical body digests, event digests, and timestamps. Only this command may
append ordinary campaign intents:

```bash
ledger --source hylo append --repo REPO --json intent.json
```

The current adapter is:

```text
<repo>/.ledger/hylo/events.jsonl
```

Do not read its line layout as an API or write it directly.

### Attempts and baselines

Attempt roles include:

```text
historical_baseline  diagnostic historical evidence only
replay_baseline      fresh blind compatible baseline execution
candidate            controlled candidate execution
mutation             admitted synthetic execution
```

Historical attempts omit comparable world/replay identity unless genuinely
known and remain comparison-ineligible. A candidate grade requires an earlier
compatible replay-baseline attempt for the same scenario. The historical
response never supplies the comparison denominator.

### Target snapshots and changes

For Git-backed targets:

```bash
ledger --source hylo snapshot-target \
  --repo REPO --revision HEAD --input target-roots.json

ledger --source hylo snapshot-target \
  --repo REPO --revision INDEX --input target-roots.json
```

`HEAD` resolves to the immutable commit SHA. `INDEX` observes staged candidate
content. Applied changes bind the exact staged binary diff, exact path set,
before/after identities, owner authority, motivating practice grades, and
validation. One target fingerprint cannot name two physical snapshots.

Publication requires the exact current applied change, explicit commit
authority, exact changed paths, the exact promoted candidate projection, and
the latest complete passing repeat cohort.

## Typed causal frontier

Typed causal event kinds are:

```text
failure_signature_recorded
hypothesis_recorded
experiment_recorded
next_step_recorded
```

### Failure signature

`hylo-failure-signature/v1` binds an observable predicate, affected families,
dimensions or hard gates, and evidence references. It must be reusable and
must not depend on private reasoning.

### Hypothesis

`hylo-causal-hypothesis/v1` binds:

```text
applicability context
mechanism claim
failure signatures and observable evidence
causal cut points
predicted affected and protected scope
candidate intervention
falsifiers
status
```

A scalar score change alone cannot support a mechanism.

### Experiment

`hylo-experiment/v1` binds:

```text
kind and hypothesis IDs
bounded intervention and allowed paths
semantic change budget and reversibility
measurable predictions
protected controls
explicit falsifiers
practice and reserved holdout budget
selection-basis certificate
```

Read-only probes must not mutate the target. Target interventions must change
content-addressed treatment identity.

### Dominance and next step

Eligibility rejects unreproducible failures, unsupported hypotheses,
unmeasurable predictions, missing controls/falsifiers, unchanged targets,
out-of-scope edits, infeasible promotion budgets, equivalent refuted routes,
holdout-motivated repairs, insufficient reconstruction, and nondeterministic
bundle construction.

Pareto comparison is ordinal over evidence, discriminability, coverage,
semantic scope, reversibility, risk, and cost.

```text
one non-dominated eligible intervention          -> RUN
several alternatives + bounded separating probe -> OBSERVE
no eligible intervention                         -> STOP
several alternatives + no bounded probe         -> STOP
```

`hylo-dominance-certificate/v1` records the eligible, dominated, and
undominated set. `hylo-next-step-decision/v1` always records
`authority_granted:false` and `target_mutated:false`.

## Native observation commands

```bash
ledger --source hylo capabilities
ledger --source hylo doctor --repo REPO
ledger --source hylo progress --repo REPO --campaign-id ID --format json
ledger --source hylo frontier --repo REPO --campaign-id ID --format json
ledger --source hylo next-experiment --repo REPO --campaign-id ID
ledger --source hylo trial-result --repo REPO --trial-id ID --format json
ledger --source hylo inspect --repo REPO --trial-id ID --kind KIND
ledger --source hylo path --repo REPO
```

Malformed identity, invalid transitions, false Git claims, chain corruption,
authority mismatch, fixture drift, or storage failure must exit nonzero and
leave the store unchanged.

## Availability and threat model

The released CRF/HCTP product commands are admitted on macOS. Their sealing
route uses Zig, macOS/POSIX process primitives, cryptographic commitments,
separate roles, anonymous descriptors, and an encrypted recovery checkpoint.
It intentionally records `os_confinement:false`.

Therefore the proof does establish:

```text
content and lineage commitments
one-shot capability delivery
role and producer separation
pre-reveal public non-disclosure
exactly-once lane claims
deterministic fold and proof verification
```

It does not establish:

```text
hostile same-user process isolation
removal of all compiler/register/allocator secret remnants
arbitrary remote artifact-store security
generalized causal truth outside the admitted episodes
```

Do not add an undocumented platform-specific isolation substitute. A stronger
same-user threat model requires a separately authorized artifact store or
custody boundary with its own contract and evidence.
