# Hylo released contracts

This reference describes the released Hylo CRF/HCTP boundary used by `$hylo`.
Installed CLI help, capabilities, validators, and executable schemas remain the
authority when this document and a binary differ.

## Contents

- [Contract layers](#contract-layers)
- [Canonical identity](#canonical-identity)
- [CRF extraction graph](#crf-extraction-graph)
- [HCTP source governance](#hctp-source-governance)
- [Campaign–trial relationship](#campaigntrial-relationship)
- [HCTP trial protocol](#hctp-trial-protocol)
- [Compatibility campaign fold](#compatibility-campaign-fold)
- [Typed causal frontier](#typed-causal-frontier)
- [Native observation commands](#native-observation-commands)
- [Availability and threat model](#availability-and-threat-model)

## Contract layers

Hylo currently has four additive layers:

```text
CRF episode graph      counterfactual cut, target bundle, world, runtime, custody
HCTP trial protocol    public trial, private custody, lane claims, grades, reveal, proof
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
delivered only through the declared custodian FD and is not persisted in the
runner root, custody manifest, event store, stdout, or proof bundle.

Every secret-bearing descriptor is already-open, unlinked, anonymous,
directional, distinct, and `>=3`, and is supplied under the admitted
custodian's custody. The CLI verifies descriptor shape, direction, and
non-aliasing required by its contract; it does not authenticate the peer
process or establish hostile same-user isolation. Regular-file redirection, a
named FIFO, stdin/stdout/stderr, argv, and environment variables are not
protected secret transport.

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
ledger validate hylo-trial --input FILE
```

These validators are platform-neutral, read no Hylo store, mutate nothing, and
grant no authority.

## HCTP source governance

`seq hctp-source` owns source-side HCTP selection and materialization:

```text
compile      derive the complete denominator, independence clusters, split
             integrity, sanitization, source commitments, route admissions
             from supplied replay-episode evidence, and sealed cases
validate     prove the exact signed source-selection receipt matches one
             completed trial
govern       derive source-governance evidence from admitted inputs
materialize release one registered visible case and source profile by FD,
             then emit a lane-scoped role attestation
```

```bash
seq hctp-source compile \
  --manifest source.json --output selection.json \
  --source-signing-seed-fd <source-owner-seed-fd>
```

Compilation precedes campaign admission and trial construction. Validation
does not: run it only after `trial.json` exists and passes `validate-trial`, and
before `register-trial`:

```bash
ledger --source hylo validate-trial --repo REPO --trial trial.json
seq hctp-source validate --receipt selection.json --trial trial.json
ledger --source hylo register-trial \
  --repo REPO \
  --trial trial.json \
  --custody-input-fd <custodian-registration-source-fd>
```

Do not attempt registration after source validation fails.

Case-blind compilation additionally uses a sealed directory and owner-only
seal-key output FD. Materialization accepts the exact sealed case, registered
trial, and lane ID; it receives the seal key and signing seed by FD and writes
visible input and the optional historical source profile only to protected
output FDs.

The primary artifacts are:

```text
hylo-source-selection-receipt/v1
hylo-source-route-admission/v1
hylo-sealed-case/v1
hylo-case-materializer-contract/v1
hylo-materialization-receipt/v1
```

The source-selection receipt must cover the registered units exactly, preserve
scenario/split/cluster/source commitments, carry the compiler-derived route
admission where required, and reject exact cross-split duplicates. The
source-owner attestation on the exact receipt covers the admission. Validation
compares the exact canonical signed-receipt value and its fingerprint, not a
caller-rebuilt semantic equivalent.

The route admission binds campaign, unit, scenario, episode, CRF fidelity,
`replay_eligible`, source episode projection, source profile, effective
reconstruction, limitations, required lineage/FIR, comparison eligibility, and
one execution route:

```text
direct + replay_eligible:true             -> direct, comparison eligible
direct + replay_eligible:false            -> diagnostic_only, ineligible
historical_decision + valid governance    -> historical_replay,
                                             capped by retained CRF fidelity
absent or invalid historical governance   -> compilation failure;
                                             diagnostic evidence only
```

Seq derives this admission from the validated CRF episode and source profile;
the caller must not supply it. A replay-ineligible historical source retains
the CRF reconstruction ceiling and limitations. It may not be relabeled
`direct`. Historical `practice_repair` and `promotion` require authoritative
governance with workflow effects allowed.

The materialization receipt binds one lane, one opaque arm, one visible-input
fingerprint, the frozen producer, and the controller/materializer trust domain
without disclosing semantic arm identity, hidden reference, or a private
historical-profile body.

## Campaign–trial relationship

An HCTP trial is additive to an immutable admitted campaign; it is not a
campaign substitute. Before trial compilation or registration, the campaign
fold must contain:

```text
campaign_created
every required target_bundle_admitted
every scenario_admitted in the complete manifest
the exact owner-applied change and current target identity when evaluating a candidate
```

The private-v2 route opts into `protocol_profiles:["hylo-trial/v2"]` and MAY
also retain `"hylo-trial/v1"` for compatibility,
`canonical_json_profile:"hylo-canonical-json/v1"`, and
`trial_policy.source_route_admission:"required"`. It also freezes proof
authority/trust when applicable and the complete scenario manifest.

This opt-in does not rewrite legacy campaign bytes. Existing campaigns without
HCTP profiles remain valid under the compatibility fold, and legacy profiles
must not acquire HCTP-only fields where the current validator rejects them.

Registration derives campaign, scenario, target, split, and promotion-coverage
authority from the event fold. It rejects an unknown campaign, incomplete
scenario admission, missing target bindings, and a promotion trial that omits
an applicable protected scenario. Low-level `append` admits ordinary campaign
events only; high-level trial commands exclusively own HCTP lifecycle events.

## HCTP trial protocol

### `hylo-trial/v2` and `hylo-trial-custody/v1`

A trial freezes the complete paired experiment before registration and
execution:

```text
trial and campaign identity
purpose: practice_repair | promotion | mechanism_probe | environment_probe |
         calibration_null | calibration_positive | reliability_probe
canonical JSON profile
assurance and trust policy
allocation and order balancing
units, scenarios, splits, and independence clusters
pairs, repeats, lanes, and opaque arms
source profiles and source-selection receipt commitment
target treatment, epoch, witness, and common-projection commitments
execution, model, runtime, tool, and effect projections
rubric, oracle, judge, and producer authorities
case, arm, and grade visibility
reveal and publication policy
```

The public/private carrier split is normative:

| Carrier | Public `hylo-trial/v2` | Private `hylo-trial-custody/v1` |
| --- | --- | --- |
| arms | opaque `arm_id` and `treatment_commitment` | semantic roles, value/materialization identities, nonces, and materialization bodies |
| target epoch | before/after/change commitments | target fingerprints and change ID openings |
| factor | intervention-witness and target-common-projection commitments | witness and target-common-projection bodies |
| source selection | portable `artifact:sha256:<64 lowercase hex>` ref, matching fingerprint, and commitment | exact signed receipt and nonce |
| unit source profile | exact validator-defined safe projection | full profile body and semantic material |
| arm map | commitment | semantic mapping and nonce |

Two private sub-openings have distinct consumers. Seq receives only
`hylo-source-selection-opening/v1` from `custody.source_selection` through
`--source-selection-opening-fd` when materializing a v2 case. CAS receives
`hylo-target-common-projection-opening/v1` inside the lease-bound treatment
claim and validates it before execution. Neither consumer receives the whole
custody record through those narrower carriers.

Before reveal, the public trial MUST NOT contain `value_fingerprint`,
`materialization_ref`, or `materialization_fingerprint` in its arms; raw target
fingerprints or change ID; intervention-witness or target-common-projection
bodies; the caller's local source-receipt path; or the full source-selection
receipt. `hylo-trial/v1` retains its exact
legacy semantics and does not satisfy the private-v2 execution route.

Each v2 `units[*].source_profile` MUST match the native safe projection exactly.
Unknown or semantic extra keys are invalid; the projection cannot carry a full
historical profile body, source target text, rationale, rejected routes, or
hidden references. V1 retains its established source-profile contract.

### Trial compiler

The native compiler maps an admitted campaign, exact source receipt, current
owner-applied target change, and `hylo-trial-build-request/v1` into public
commitment-only `hylo-trial/v2` plus private `hylo-trial-custody/v1`:

```bash
ledger --source hylo compile-trial \
  --repo REPO \
  --request trial-build-request.json \
  --source-receipt selection.json \
  --output trial.json \
  --custody-output-fd <custodian-custody-sink-fd>
```

The build request binds:

```text
trial ID, campaign ID, and expected campaign head
purpose, selected units, and exact source-receipt fingerprint
before/after target bundles and snapshots, applied change, allowed roots
hypothesis, estimand, execution, grading, assurance, and sealing
allocation, stop, and calibration policy
```

The factor verifier fingerprint must equal the running Ledger executable's
observed fingerprint. The request's `sealing` object may contain only
`reveal_scope` and the case-materializer reference, fingerprint, and optional
contract. Case, arm, and grade visibility plus visible/hidden commitment sets
are derived from the signed source receipt and compiler law; supplying those
generated fields is a conflict, not an override.

The current compiler admits `practice_repair` and `promotion` target-snapshot
routes with `balanced_ab_ba` and a positive even fixed pair count. It rejects
sealed assurance as `SealedBrokerUnavailable`; a future product route may add
broker admission. It also rejects unsupported non-null proof/publication
request bodies rather than ignoring them.

It validates campaign, scenario, target, change, and source state before
generating entropy. It creates opaque IDs, freezes the balanced allocation,
derives the target common projection and intervention witness, commits every
private treatment and semantic opening, validates the public/custody join, and
returns only public commitments in `hylo-trial-build-receipt/v2`.

Public and private sinks cannot be crash-atomic. The compiler links a
create-new `0600` public trial, delivers private custody material, and attempts
to remove the public artifact if private delivery reports failure.
`TrialOutputRollbackFailed` means the path may remain as an uncommitted recovery
artifact. A partial custody byte stream is not an admitted custody record. The
compiler emits its build receipt with `custody_material_delivered:true` only
after both sinks complete. That stdout receipt is the completion observation;
transient public-file visibility is neither completion nor authority. Custody
bytes never enter normal stdout or the event store.

### Validation and registration

Use the exact order below after complete campaign admission:

```bash
ledger --source hylo validate-trial --repo REPO --trial trial.json
seq hctp-source validate --receipt selection.json --trial trial.json
ledger --source hylo register-trial \
  --repo REPO \
  --trial trial.json \
  --custody-input-fd <custodian-registration-source-fd>
```

Registration validates and appends the complete manifest atomically. Changing
any frozen field requires a new trial identity. For v2, the custodian supplies
the exact custody record through a fresh protected pipe. The event persists the
public trial and only a validated nonsemantic custody observation containing
the custody commitment, `validated:true`, and
`semantic_material_persisted:false`.

Private-v2 registration has two validation times. The command-level preflight
validates the public/custody join and the current semantic campaign view, but it
does not authorize append. After acquiring exclusive store ownership, the
append owner reloads the exact snapshot and reruns the full semantic
trial-against-campaign validator on the custody-backed trial before event
application. Any stale campaign, scenario, source, target, grading, assurance,
coverage, or policy binding fails before append and leaves the store unchanged.
Legacy v1 registration retains its established public-trial path.

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
label alone is not evidence. Sealed execution additionally requires an
explicitly admitted broker and never infers that product boundary from a test
driver.

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
full source-selection receipt or sealed-case locator
raw before/after target fingerprints or change ID
target common projection or intervention witness body
treatment opening or materialization body
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
compile-trial
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

Private trial custody uses `--custody-output-fd` at compilation,
`--custody-input-fd` at registration, each new v2 `start-lane` or
`commit-lane-start`, and lane materialization, and `--reveal-material-fd` at
reveal. The custodian retains one exact
`hylo-trial-custody/v1` record outside public artifacts and re-delivers it over
a fresh protected pipe for each operation. Lane materialization additionally
receives the exact retained lease through `--lease-input-fd` and writes one
lease-bound private claim through `--materialization-output-fd`. Each endpoint
is a distinct unlinked anonymous directional pipe. The CLI verifies descriptor
shape, direction, and non-aliasing required by its contract; it does not
authenticate the peer process or establish hostile same-user isolation. No
endpoint is a regular input or output file.

For case-blind v2 input release, the custodian separately projects the exact
`hylo-source-selection-opening/v1` value onto
`--source-selection-opening-fd`. Seq requires the opening, verifies its whole
commitment against the public trial, and joins its nested signed receipt before
materializing the visible input or optional historical profile. V1 retains its
embedded source receipt and rejects this v2-only carrier.

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
uses a clean workspace, invokes the declared executor exactly once, and hashes
evidence. A legacy v1 trial emits `hylo-run-receipt/v1`. A private-v2 trial
requires `--materialization-fd` and emits commitment-only
`hylo-run-receipt/v2`. An existing claim makes retry a hard error; use
status/recovery rather than executing again.

For v2, `ledger --source hylo lane-materialization` consumes the exact custody
record and retained lease and sends `hylo-lane-materialization-claim/v2` only
over the protected materialization FD. Normal stdout contains only
`hylo-lane-materialization-receipt/v2`, which binds trial, lane, and claim
fingerprint, records `delivered_by_fd:true`, and records
`semantic_role_disclosed:false`. Retain that safe receipt for reveal; never
persist the private claim. The private claim contains the exact
`hylo-target-common-projection-opening/v1`; CAS verifies its whole-opening
commitment and the nested projection fingerprint against the public trial and
rejects a raw projection alias.

CAS publishes the same claim identity as
`hylo-run-receipt/v2.materialization.materialization_claim_fingerprint`.
Before reveal, every lane must satisfy the exact join:

```text
hylo-lane-materialization-receipt/v2.claim_fingerprint
  == hylo-run-receipt/v2.materialization.materialization_claim_fingerprint
```

The reveal fold accepts exactly one v2 materialization receipt for every lane.
A changed fingerprint, missing lane, duplicate lane, unknown lane, wrong trial,
non-v2 safe receipt, or mixed version in the per-lane safe-receipt set is
invalid and must fail before `trial_revealed` appends. Separate private
materializer evidence, when required, follows its existing contract and cannot
satisfy or replace this join. The v2 join does not change the legacy v1
materialization/reveal contract.

`preflight --json` projects the frozen route without granting authority:

```text
source_profile_kind
compile_replay_required
replay_preparation_mode
source_profile_body_delivery
execution_route
required_lineage
```

Lane preparation branches on the frozen source profile:

```text
source_profile.kind == "direct"
  -> compile_replay_required:false
  -> replay_preparation_mode:"none"
  -> source_profile_body_delivery:"none"
  -> run without a source-profile FD

source_profile.kind == "historical_decision"
  -> compile_replay_required:false
  -> replay_preparation_mode:"integrated_run"
  -> source_profile_body_delivery:"source_profile_fd" for every v2 lane
  -> run validates the profile and prepares one DCP/RIP internally before claim
  -> claim, executor request, native receipt, and FIR bind those fingerprints
```

For every v2 historical lane, connect the materializer's protected source
profile output directly to `cas trial run --source-profile-fd`. Embedded
historical delivery is legacy v1 or standalone diagnostic compatibility. No
standalone replay-plan receipt or DCP/RIP file is an execution input.

Direct lanes skip and reject standalone `compile-replay`. Historical execution
also does not call it: the accountable preparation lives inside `run` before
the irreversible claim. The standalone command is an open, embedded historical
diagnostic. It rejects case-blind, `role_separated`, and `sealed` use; its
receipt records `execution_authority:false`. `run` consumes neither that receipt
nor its DCP/RIP files. Diagnostic named outputs require a caller-owned
no-symlink `0700` root and create-new `0600` files, but they are not execution
inputs.

The executor receives one request path and one result path. It does not receive
the lane lease, semantic arm mapping, historical answer, or hidden reference.
The public v2 run receipt exposes only the treatment commitment, visible-input
lineage, permitted historical fingerprints, non-disclosure booleans, and the
exact `hylo-fir-public-projection/v1`. It MUST NOT expose raw
target/factor/archive identifiers, treatment material, or the full FIR. The v1
run-receipt path retains its compatible full-FIR carrier.

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

For a v2 trial, the native consumers treat
`hylo-grade-presentation-receipt/v1`, `hylo-grade-receipt/v1`, and
`hylo-pair-grade-receipt/v1` as closed and exact shapes. Unknown top-level keys,
undeclared nested keys, or fields outside the applicable optional branch are
invalid. Every consumed public `evidence_refs` item, pair-dimension
`rationale_ref`, `grade_receipt_ref`, `pair_grade_receipt_ref`, and
`grade_presentation_receipt_ref` must be exactly
`artifact:sha256:<64 lowercase hex>`. When a carrier also declares a
fingerprint, the reference digest must equal it. Local paths, bare
fingerprints, other algorithms, uppercase hex, and malformed lengths are not
portable evidence. Legacy v1 trial carriers retain their established receipt
compatibility.

Grade commitments may be public before reveal; plaintext outcomes and openings
may not. Reveal must match the precommitted semantic arm map and all required
terminal/grade conditions. `--reveal FILE` is the legacy v1 carrier and accepts
only `hylo-trial-reveal/v1`; a caller-authored `hylo-trial-reveal/v2` file is
rejected. For v2, the custodian supplies the exact
`hylo-trial-custody/v1` record through `--reveal-material-fd` plus one exact
safe `hylo-lane-materialization-receipt/v2` per lane. Ledger validates custody
provenance, derives `hylo-trial-reveal/v2`, exact-joins each receipt to its
lane's authenticated run-receipt claim fingerprint, and fails changed,
missing, duplicate, or version-mixed per-lane safe-receipt sets before append.
The validated v2 reveal is the first public semantic opening: it opens the arm
map, treatments, target epoch, intervention witness, and target common
projection. The full source-selection receipt remains custody-only. A reveal
does not retroactively authorize target mutation. After reveal, `trial-result`
reports diagnostic position balance and per-dimension order-effect records.
`mean_second_minus_first` is non-null only when both baseline-first and
candidate-first orientations contribute. These observations are noncausal and
do not alter claim eligibility.

### Proof bundles

`hylo-proof-artifact-set/v1` enumerates the exact post-reveal artifact set that
a trusted source owner may sign as
`hylo-proof-sanitization-receipt/v1`. Export produces a deterministic
`hylo-proof-bundle/v1`; verification checks internal closure and may bind
explicit external anchors.

Proof bundles MUST exclude `hylo-trial-custody/v1`, private lane claims,
treatment materializations, retained leases, and custody keys. V2 proof
projection derives semantic target, witness, and common-projection evidence
only from the validated public `hylo-trial-reveal/v2`, never directly from
private custody. The public-proof sanitizer recursively rejects private
semantic keys, including `chain_of_thought`, `future_outcome`, `hidden_oracle`,
`hidden_oracle_text`, `hidden_reasoning`, `historical_response`,
`private_reasoning`, and `source_target_text`, while allowing schema-declared
boolean non-disclosure observations such as `hidden_reference:false`. The
boolean is a public disclosure observation, not hidden-reference content.

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

That chronology belongs only to the compatibility campaign fold. HCTP freezes
balanced A/B-B/A allocation before execution, permits either semantic arm to
run first, and joins the two matching frozen lanes after reveal. Do not impose
baseline-first chronology on an HCTP B/A pair.

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
Sealed execution also requires a caller-provided admitted broker whose binary
and contract fingerprints satisfy the native role, FD, checkpoint, recovery,
and non-disclosure contracts. The repository-owned
`hctp-sealed-role-driver` is conformance/test infrastructure, not an installed
product command or capability. Without an admitted broker, fail before secret
generation or trial mutation. The route intentionally records
`os_confinement:false`.

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
