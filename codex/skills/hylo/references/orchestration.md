# Hylo executable orchestration

This reference owns the ordered CRF/HCTP operator state machine. Installed CLI
help, capabilities, validators, and executable fixtures remain authoritative.

## Contents

- [Execution graph](#execution-graph)
- [Native operator-recipe binding](#native-operator-recipe-binding)
- [Phase 0 — Resolve intent and authority](#phase-0--resolve-intent-and-authority)
- [Phase 1 — Extract and validate CRF evidence](#phase-1--extract-and-validate-crf-evidence)
- [Phase 2 — Select a source route](#phase-2--select-a-source-route)
- [Phase 3 — Compile source selection](#phase-3--compile-source-selection)
- [Phase 4 — Admit the campaign](#phase-4--admit-the-campaign)
- [Phase 5 — Establish a candidate](#phase-5--establish-a-candidate)
- [Phase 6 — Compile and register the trial](#phase-6--compile-and-register-the-trial)
- [Phase 7 — Materialize and execute lanes](#phase-7--materialize-and-execute-lanes)
- [Phase 8 — Grade, reveal, and prove](#phase-8--grade-reveal-and-prove)
- [Phase 9 — Fold the causal frontier](#phase-9--fold-the-causal-frontier)
- [Protected descriptor contract](#protected-descriptor-contract)
- [Allocation and chronology](#allocation-and-chronology)
- [Sealed assurance](#sealed-assurance)
- [Recovery](#recovery)

## Execution graph

```text
resolve mode and authority
  -> probe only required capabilities
  -> extract and validate CRF graph
  -> apply fidelity gate
  -> compile governed source selection
  -> construct and admit campaign, scenarios, target bundles
  -> require an existing owner-applied candidate
  -> compile public v2 trial and private custody
  -> validate trial
  -> validate exact source receipt against completed trial
  -> register trial with private custody
  -> preflight each lane
  -> materialize each selected treatment under its retained lease
  -> execute each lane by frozen source route
  -> blind grade
  -> reveal and observe the derived result
  -> close trial
  -> prove when requested and authorized
  -> fold causal frontier
  -> route owner action or stop
```

Each arrow is fail-closed. Do not skip a predecessor because a later schema
validator might also detect the omission.

## Native operator-recipe binding

The pinned native `expected-route.json` owns the exact executable recipe step
order. This table is its documentation projection. Repeated owner commands are
intentional: they represent distinct immutable transitions or frozen lanes.
The cross-repository contract requires exact step order and requires every
command identity below to belong to the pinned native surface manifest.

| Native step | Owner command |
| --- | --- |
| `source_compile` | `seq hctp-source compile` |
| `campaign_validate` | `ledger --source hylo validate-campaign` |
| `campaign_created` | `ledger --source hylo append` |
| `target_bundle_admitted` | `ledger --source hylo append` |
| `scenario_manifest_complete` | `ledger --source hylo append` |
| `owner_applied_candidate_precondition` | `ledger --source hylo append` |
| `campaign_doctor` | `ledger --source hylo doctor` |
| `trial_compile` | `ledger --source hylo compile-trial` |
| `trial_validate` | `ledger --source hylo validate-trial` |
| `source_validate` | `seq hctp-source validate` |
| `trial_register` | `ledger --source hylo register-trial` |
| `direct_lane_preflight` | `cas trial preflight` |
| `direct_lane_source_materialize` | `seq hctp-source materialize` |
| `direct_lane_start` | `ledger --source hylo start-lane` |
| `direct_lane_recover_start` | `ledger --source hylo recover-lane-start` |
| `direct_lane_materialization` | `ledger --source hylo lane-materialization` |
| `direct_lane_run` | `cas trial run` |
| `direct_lane_finish` | `ledger --source hylo finish-lane` |
| `direct_lane_recover_finish` | `ledger --source hylo recover-lane-finish` |
| `direct_lane_grade` | `ledger --source hylo grade-lane` |
| `historical_lane_preflight` | `cas trial preflight` |
| `historical_lane_source_materialize` | `seq hctp-source materialize` |
| `historical_lane_start` | `ledger --source hylo start-lane` |
| `historical_lane_recover_start` | `ledger --source hylo recover-lane-start` |
| `historical_lane_materialization` | `ledger --source hylo lane-materialization` |
| `historical_lane_run` | `cas trial run` |
| `historical_lane_finish` | `ledger --source hylo finish-lane` |
| `historical_lane_recover_finish` | `ledger --source hylo recover-lane-finish` |
| `historical_lane_grade` | `ledger --source hylo grade-lane` |
| `pair_grade` | `ledger --source hylo grade-pair` |
| `custody_reveal` | `ledger --source hylo reveal-trial` |
| `trial_result` | `ledger --source hylo trial-result` |
| `trial_close` | `ledger --source hylo close-trial` |
| `proof_artifact_set` | `ledger --source hylo proof-artifact-set` |
| `proof_export` | `ledger --source hylo export-proof` |
| `proof_verify` | `ledger --source hylo verify-proof` |

### Native semantic binding

The following JSON is the machine-checked documentation projection of every
semantic object in the pinned native `expected-route.json`. It is intentionally
literal: any native change to these route, authority, allocation, custody,
broker, or candidate-lifecycle laws must update the operator prose and this
projection together.

```json
{
  "trial_boundary": {
    "public_schema": "hylo-trial/v2",
    "private_schema": "hylo-trial-custody/v1",
    "registration_requires_custody_fd": true,
    "lane_materialization_requires_custody_and_lease_fds": true,
    "cas_run_requires_lease_input_and_materialization_fds": true
  },
  "execution_authorities": {
    "runner_contract_schema": "cas-hylo-runner/v1",
    "runtime_rebinding_required": true,
    "runner": {
      "producer_id": "cas-trial",
      "key_id": "runner-key",
      "binary_binding": "cas_trial_path",
      "version_binding": "cas_version"
    },
    "executor": {
      "producer_id": "cas-trial-executor",
      "key_id": "executor-authority-key",
      "binary_binding": "fixture_executor_path"
    },
    "ledger": {
      "producer_id": "hylo-ledger",
      "key_id": "executor-authority-key",
      "binary_binding": "ledger_path"
    }
  },
  "routes": {
    "direct": {
      "comparison_eligible": true,
      "crf_replay_eligible_required": true,
      "compile_replay_required": false,
      "source_profile_body_delivery": "none",
      "replay_preparation_mode": "none",
      "execution_route": "direct",
      "required_lineage": null,
      "compile_replay_owner": null
    },
    "historical_decision": {
      "comparison_eligible": true,
      "crf_replay_eligible_required": false,
      "compile_replay_required": false,
      "source_profile_body_delivery": "source_profile_fd",
      "case_blind_source_profile_body_delivery": "source_profile_fd",
      "replay_preparation_mode": "integrated_run",
      "execution_route": "historical_replay",
      "required_lineage": "either",
      "compile_replay_owner": "cas_trial_run"
    },
    "diagnostic_only": {
      "comparison_eligible": false,
      "compile_replay_required": false,
      "execution_route": "diagnostic_only",
      "registration_allowed": false
    }
  },
  "allocation": {
    "method": "balanced_ab_ba",
    "semantic_baseline_must_run_first": false,
    "compatibility_fold_requires_prior_baseline": true
  },
  "sealed_product_boundary": {
    "admitted_broker_required": true,
    "repository_driver_installed": false,
    "fail_before": [
      "secret_generation",
      "campaign_mutation",
      "trial_mutation"
    ],
    "os_confinement": false
  },
  "candidate_lifecycle": {
    "evaluate_requires_existing_candidate": true,
    "run_grants_mutation_authority": false,
    "new_candidate_requires_new_trial": true
  }
}
```

## Phase 0 — Resolve intent and authority

Record:

```text
operation:
  validate | extract | evaluate_existing_candidate | derive_next_candidate |
  report | doctor

assurance:
  precommitted | receipt_bound | role_separated | sealed

source route:
  direct | historical_decision | unresolved

owner authority:
  none | propose | apply | commit | push
```

Default every authority to `none`. A persistent request is persistence toward
the outcome, not broader authority.

Probe only the selected mode. Root `ledger validate hylo-*` artifact checks do
not require the macOS product surfaces. Repo-aware `ledger --source hylo`
doctor, report, campaign, and trial operations do. Source selection adds Seq;
execution adds CAS; a historical route adds DCP/RIP/FIR and internal historical
replay; case-blind adds source sealing, materialization, and protected
source-selection opening delivery; sealed adds a separately admitted broker.
Post-close proof export probes only Ledger's v2 trial/custody and proof surfaces;
it does not require an installed Seq or CAS binary.

## Phase 1 — Extract and validate CRF evidence

Invoke `seq hylo-extract` with the complete target bundle root and an admitted
custodian's protected seal-key output descriptor. Preserve separate runner and
`0700` custody roots.

Validate:

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

Report before routing:

```text
episode ID and fingerprint
counterfactual cut and confidence
target bundle fingerprint
world availability and runtime fingerprint
CRF fidelity class
replay_eligible
limitations
runner and custody root identities
```

A pure validator pass establishes structure and invariants only. It grants no
execution, reveal, edit, or publication authority.

## Phase 2 — Select a source route

### Source route table

| CRF evidence | Source profile | Native result |
| --- | --- | --- |
| `replay_eligible:true` | genuinely `direct` | direct comparison admission |
| `replay_eligible:false` | `direct` | `diagnostic_only` source admission; trial compilation, registration, and comparison execution forbidden |
| `replay_eligible:true` | valid governed `historical_decision` | historical replay admission |
| `replay_eligible:false` | valid governed `historical_decision` | historical replay admission at the retained reconstruction ceiling |
| any | absent or invalid `historical_decision` governance | compilation fails; the source remains diagnostic evidence only |

For source-profile literals:

```text
source_profile.kind == "direct"
source_profile.kind == "historical_decision"
```

Seq derives `source_route_admission` during source compilation; the caller does
not supply it. The source-owner attestation on the exact source-selection
receipt covers that admission. The admission binds campaign, unit, scenario,
split, source episode projection, source profile, effective reconstruction,
limitations, and execution route.

A historical source is never upgraded by changing its label. A historical
route requires SGG-v1, DCP-v2 at a `pre_decision` anchor, a source-target-text
witness, `retrace_mode:"replay"`, required lineage and FIR version, and an
honest reconstructability label. Historical `practice_repair` and `promotion`
require authoritative governance with workflow effects allowed.

## Phase 3 — Compile source selection

Run source compilation before trial construction:

```bash
seq hctp-source compile \
  --manifest source.json \
  --output selection.json \
  --source-signing-seed-fd <source-owner-seed-fd>
```

Retain:

```text
complete denominator and split membership
independence clusters and duplicate analysis
source episode and source profile fingerprints
source route admissions
visible and hidden commitments
sealed-case references when case-blind
source-owner attestation and receipt fingerprint
```

Do not run `seq hctp-source validate` yet. That command compares the receipt to
a complete trial and therefore has no valid pre-trial invocation.

## Phase 4 — Admit the campaign

Construct `campaign.json` and the complete scenarios JSONL. The new operator
route requires:

```text
protocol_profiles: ["hylo-trial/v2"]
canonical_json_profile: "hylo-canonical-json/v1"
trial_policy.source_route_admission: "required"
complete scenario_manifest
proof authority and proof trust policy when proof is required
```

The campaign MAY also include `hylo-trial/v1` for legacy trial compatibility.

### Registration order

```text
validate campaign
  -> append campaign_created
  -> append every required target_bundle_admitted
  -> append every scenario_admitted in the complete manifest
  -> append the owner-applied change when evaluating a changed target
  -> doctor and inspect admission state
  -> compile trial
  -> validate trial
  -> source-validate completed trial
  -> register trial
```

Representative commands:

```bash
ledger --source hylo validate-campaign --campaign campaign.json
ledger --source hylo append --repo <repo> --json campaign-created.json
ledger --source hylo append --repo <repo> --json baseline-target-bundle-admitted.json
ledger --source hylo append --repo <repo> --json candidate-target-bundle-admitted.json
ledger --source hylo append --repo <repo> --json scenario-admitted-001.json
ledger --source hylo append --repo <repo> --json change-recorded.json
ledger --source hylo doctor --repo <repo>
```

Append every remaining scenario intent in the complete manifest before the
change intent and final doctor pass.

Use only native `hylo-event-intent/v1` bodies and fingerprints. Low-level
`append` owns compatibility campaign events; it must not author HCTP trial
lifecycle events.

The parent campaign fixes promotion coverage. Registration must reject an
unknown campaign, an unadmitted or partially admitted scenario manifest,
missing target bindings, and a promotion trial that omits an applicable
protected unit.

## Phase 5 — Establish a candidate

### Candidate lifecycle

```text
evaluate existing candidate
  owner-applied candidate identity exists
  -> before and after target bundles admitted
  -> before and after snapshots admitted
  -> exact bounded change recorded as applied
  -> candidate can be frozen for a trial

derive next candidate
  prior evidence folds to RUN | OBSERVE | STOP
  -> RUN grants no mutation authority
  -> target owner may apply the bounded intervention if separately authorized
  -> a new content-addressed candidate identity exists
  -> begin a new evaluation trial
```

If the candidate is absent, stop trial construction. Do not create a circular
trial whose candidate depends on the evidence that the same trial has not yet
produced.

## Phase 6 — Compile and register the trial

The current compiler accepts `hylo-trial-build-request/v1`, the exact
`hylo-source-selection-receipt/v1`, a create-new public output path, and an
admitted custodian's protected custody output descriptor:

```bash
ledger --source hylo compile-trial \
  --repo <repo> \
  --request trial-build-request.json \
  --source-receipt selection.json \
  --output trial.json \
  --custody-output-fd <custodian-custody-sink-fd>
```

The request binds the current campaign head, purpose, unit IDs, source receipt,
before/after target bundles and snapshots, applied change, allowed difference
roots, hypothesis, estimand, execution, grading, assurance, sealing, allocation,
stop, and calibration policies. The current compiler supports the admitted
`practice_repair`/`promotion` target-snapshot route, balanced A/B-B/A allocation,
and a positive even fixed pair count. It rejects unsupported non-null proof or
publication request bodies rather than ignoring them.

The factor verifier fingerprint must match the observed Ledger executable.
The sealing request carries only reveal scope and admitted materializer fields;
case/arm/grade visibility and commitment sets are source/compiler-derived, and
the compiler rejects a request that tries to supply them.

Compilation validates campaign/scenario/target/change/source state before
entropy. It generates opaque arm IDs, allocation, arm-map commitment, canonical
public `hylo-trial/v2`, and private `hylo-trial-custody/v1`.

Within the public trial, every `units[*].source_profile` is the exact native
safe projection. Exact-key validation rejects semantic extras. A full
historical profile body, source target text, rationale, rejected routes, and
hidden references remain private and use the admitted FD carrier when required.

The two sinks cannot be crash-atomic. The compiler links a create-new `0600`
public trial, delivers private custody, and attempts to remove the public trial
when delivery reports failure. `TrialOutputRollbackFailed` identifies a path
that may remain as an uncommitted recovery artifact; a partial custody byte
stream is not an admitted custody record. The compiler emits
`hylo-trial-build-receipt/v2` with `custody_material_delivered:true` only after
both sinks complete. Treat that stdout receipt—not transient file visibility—as
the commit observation. The receipt grants no authority.

The public v2 trial carries only opaque arm/treatment commitments, committed
target epoch, committed intervention witness and common projection, and the
portable `artifact:sha256:<64 lowercase hex>` source-receipt reference,
matching fingerprint, and commitment. The exact signed source receipt,
treatment openings and materializations, semantic arm map, target openings,
witness, and common projection remain in custody.

Then use this exact sequence:

```bash
ledger --source hylo validate-trial --repo <repo> --trial trial.json
seq hctp-source validate --receipt selection.json --trial trial.json
ledger --source hylo register-trial \
  --repo <repo> \
  --trial trial.json \
  --custody-input-fd <custodian-registration-source-fd>
```

Source validation checks the exact canonical signed-receipt value and its
fingerprint plus every unit, scenario, split, cluster, visible commitment,
hidden commitment, source episode projection, source profile, and route
admission. Never attempt registration after source validation fails. For v2,
the custodian re-delivers the exact custody record through a fresh protected
pipe. The registration event persists only the public trial and a validated
nonsemantic custody-commitment observation. Retain custody for every new v2
lane start or caller-retained start commit, treatment materialization, and
reveal; each use receives a fresh protected input pipe.

For private-v2 registration, treat the preceding validation as necessary
preflight, not append authority. Ledger reacquires exclusive store ownership,
loads the exact append snapshot, and reruns the full semantic
trial-against-campaign validation on the custody-backed trial before applying
or appending `trial_registered`. Any stale binding fails without append. The
legacy v1 registration route retains its established public-trial behavior.

## Phase 7 — Materialize and execute lanes

### Lane execution

For each lane, run:

```bash
cas trial preflight --trial trial.json --lane-id <lane> --json
```

Consume its exact projection:

```text
source_profile_kind
compile_replay_required
replay_preparation_mode
source_profile_body_delivery
execution_route
required_lineage
```

#### Direct lane

```text
preflight reports:
  source_profile_kind:"direct"
  compile_replay_required:false
  replay_preparation_mode:"none"
  source_profile_body_delivery:"none"
  execution_route:"direct"
  required_lineage:null
  -> materialize the exact visible input
  -> start-lane or commit-lane-start under the frozen assurance route
  -> materialize the selected treatment from custody under the retained lease
  -> call cas trial run exactly once with --materialization-fd and without
     --source-profile-fd
  -> finish-lane, or recover the exact terminal acknowledgement
```

`compile-replay` is forbidden for direct lanes.

#### Historical lane

```text
preflight reports:
  source_profile_kind:"historical_decision"
  compile_replay_required:false
  replay_preparation_mode:"integrated_run"
  source_profile_body_delivery:"source_profile_fd"
  execution_route:"historical_replay"
  required_lineage:<frozen-lineage>
  -> materialize the exact visible input
  -> materialize the private profile to the runner FD
  -> start-lane or commit-lane-start under the frozen assurance route
  -> materialize the selected treatment from custody under the retained lease
  -> call cas trial run exactly once with --materialization-fd and the
     protected --source-profile-fd
  -> CAS validates the profile and prepares one DCP/RIP internally before claim
  -> CAS binds preparation fingerprints into claim, executor request, and receipt
  -> finish-lane after FIR/native lineage validation, or exact recovery
```

Embedded historical delivery is legacy v1 or standalone diagnostic
compatibility. It is not the v2 execution route.

#### Private treatment bridge

Every new `hylo-trial/v2` lane start validates its private target treatment
from custody while the repository observation locks are held:

```bash
ledger --source hylo start-lane \
  --repo <repo> \
  --campaign-id <campaign-id> \
  --trial-id <trial-id> \
  --lane-id <lane-id> \
  --runner-id <runner-id> \
  --custody-input-fd <custodian-start-source-fd> \
  --lease-output-fd <runner-lease-sink-fd>
```

`commit-lane-start` also requires `--custody-input-fd` when it commits a new
v2 start from a caller-retained lease. Exact already-started recovery uses the
retained lease and re-emits existing state without rereading custody. After the
start event, every v2 lane uses the same lease-bound treatment bridge:

```bash
ledger --source hylo lane-materialization \
  --repo <repo> \
  --trial-id <trial-id> \
  --lane-id <lane-id> \
  --registration-event-digest <registration-digest> \
  --lane-started-event-digest <start-digest> \
  --lane-lease-digest <lease-digest> \
  --custody-input-fd <custodian-lane-source-fd> \
  --lease-input-fd <retained-lease-source-fd> \
  --materialization-output-fd <cas-materialization-sink-fd>

cas trial run \
  --trial trial.json \
  --lane-id <lane-id> \
  ... \
  --materialization-fd <ledger-materialization-source-fd>
```

The v2 lane-start event binds `treatment_commitment`, not a raw target snapshot
fingerprint. The materialization FD carries
`hylo-lane-materialization-claim/v2`, including the selected treatment but no
semantic role. The claim contains the exact private
`hylo-target-common-projection-opening/v1`; CAS validates its whole-opening
commitment and the nested `hylo-target-common-projection/v1` fingerprint before
execution. Normal Ledger stdout contains only the safe
`hylo-lane-materialization-receipt/v2`; retain one receipt per lane for reveal.
CAS emits commitment-only `hylo-run-receipt/v2` and rejects raw target, factor,
archive, or treatment fields in its public projection. Its FIR value is exactly
`hylo-fir-public-projection/v1`; the full FIR stays private. The v1 receipt
keeps its compatible full-FIR carrier.

After each v2 run, verify the exact public join:

```text
hylo-lane-materialization-receipt/v2.claim_fingerprint
  == hylo-run-receipt/v2.materialization.materialization_claim_fingerprint
```

Retain the joined receipt for reveal. Do not substitute a changed receipt,
another lane's receipt, a duplicate, or a v1 materialization receipt.

The public standalone `cas trial compile-replay` command is diagnostic-only.
It rejects direct lanes, private case-blind source delivery, and
`role_separated`/`sealed` assurance; its receipt says
`execution_authority:false`. `cas trial run` consumes neither that receipt nor
its DCP/RIP files; do not call it in an execution recipe.

For case-blind materialization, the custodian projects the exact
`hylo-source-selection-opening/v1` stored at `custody.source_selection` onto its
own protected pipe; it does not deliver the full custody record to Seq:

```bash
seq hctp-source materialize \
  --sealed-case <sealed-case> \
  --trial trial.json \
  --lane-id <lane-id> \
  --seal-key-fd <custodian-seal-key-source-fd> \
  --visible-output-fd <runner-visible-input-sink-fd> \
  --source-selection-opening-fd <custodian-source-selection-opening-source-fd> \
  --signing-seed-fd <materializer-signing-seed-source-fd> \
  --output <safe-materialization-receipt>
```

When preflight freezes `source_profile_body_delivery:"source_profile_fd"`, add
`--source-profile-output-fd <runner-source-profile-sink-fd>` and connect that
protected output directly to `cas trial run --source-profile-fd`. Seq validates
the opening commitment against the public trial and joins its nested exact
signed receipt before releasing the visible input or historical profile. The
public receipt contains commitments and fingerprints, not the opening or
private bodies.

## Phase 8 — Grade, reveal, and prove

Record hard gates first, then absolute and pair grades under frozen producer,
rubric, oracle, and judge contracts. Before reveal, public material contains no
plaintext grade, pair winner, rationale, semantic arm map, full source receipt,
raw target epoch, target common projection, intervention witness, treatment
opening, or materialization body.

For v2 trials, the native `hylo-grade-presentation-receipt/v1`,
`hylo-grade-receipt/v1`, and `hylo-pair-grade-receipt/v1` shapes are closed and
exact: unknown keys and undeclared nested fields are invalid. Every consumed
public evidence, rationale, grade-receipt, pair-grade-receipt, and
presentation-receipt reference must be exactly
`artifact:sha256:<64 lowercase hex>` and exact-join its companion fingerprint.
V1 trial carriers retain their established compatibility behavior.

Reveal only when every required lane and grade is terminal and policy permits.
The compiler's exact custody record is supplied through the admitted
custodian's protected input descriptor via `--reveal-material-fd`, together
with one safe lane-materialization receipt per lane:

```bash
ledger --source hylo reveal-trial \
  --repo <repo> \
  --reveal-material-fd <custodian-reveal-source-fd> \
  --materialization-receipt lane-001-materialization-receipt.json
```

Repeat `--materialization-receipt` for every lane.

`--reveal FILE` is legacy v1-only and accepts only
`hylo-trial-reveal/v1`. A caller-authored v2 reveal is rejected. The v2 route
must derive `hylo-trial-reveal/v2` from validated
`hylo-trial-custody/v1` bytes delivered through `--reveal-material-fd`.
Before append, Ledger exact-joins every supplied
`hylo-lane-materialization-receipt/v2.claim_fingerprint` to the lane's
`hylo-run-receipt/v2.materialization.materialization_claim_fingerprint`.
Changed, missing, duplicate, and version-mixed per-lane safe-receipt sets fail
without appending `trial_revealed`.

Validated `hylo-trial-reveal/v2` is the first public semantic opening. It opens
the arm map, treatments, target epoch, intervention witness, and target common
projection; the full source-selection receipt remains custody-only. Custody
bytes never enter argv, stdout, the event store, or a proof bundle.

After reveal, derive:

```text
paired dimension deltas and hard-gate changes
critical regressions
dispersion and uncertainty
independence-cluster coverage
null/calibration result
observable behavior delta
diagnostic position/order effects
qualification, noninferiority, or improvement claim class
```

Observe the derived result before closing the trial, then close it:

```bash
ledger --source hylo trial-result --repo <repo> --trial-id <trial-id> --format json
ledger --source hylo close-trial --repo <repo> --trial-id <trial-id>
```

Proof occurs only after `close-trial`. When requested and authorized:

```bash
ledger --source hylo proof-artifact-set \
  --repo <repo> --trial-id <trial-id> --output proof-artifacts.json
ledger --source hylo export-proof \
  --repo <repo> --trial-id <trial-id> --output proof.tar \
  --sanitization-receipt proof-sanitization.json
ledger --source hylo verify-proof --repo <repo> --input proof.tar
```

Proof verifies declared closure and anchors. It excludes private custody and
lane claims/materializations and derives v2 semantic evidence only from the
validated public reveal. It grants no edit, commit, push, or generalized causal
authority. Public proof rejects private semantic keys while preserving
schema-declared boolean non-disclosure observations such as
`hidden_reference:false`.

## Phase 9 — Fold the causal frontier

Append or derive observable failure signatures, hypotheses, and bounded
experiments. Use native `frontier` and `next-experiment` commands.

```text
RUN      one eligible intervention is non-dominated
OBSERVE  one bounded read-only probe can distinguish alternatives
STOP     no eligible intervention, or no bounded distinguishing probe exists
```

Every projection reports `authority_granted:false` and
`target_mutated:false`. An owner-applied RUN intervention creates a new
candidate identity, which must be evaluated by a new trial.

## Protected descriptor contract

Every secret-bearing or private semantic carrier uses a descriptor that is:

```text
already open before the product command starts
unlinked and anonymous
directional for the declared producer/consumer
supplied under the admitted custodian, runner, source owner, or broker's custody
distinct from every other sensitive descriptor
numbered >=3
bounded and one-shot where the native contract requires it
```

The CLI verifies descriptor shape, direction, and non-aliasing required by its
contract. It does not authenticate the peer process or establish hostile
same-user isolation.

Never place a lease, seal key, signing seed, FD-delivered source-profile body,
source-selection opening, target-common-projection opening, trial custody
record, private lane claim, or grade opening in argv, an environment variable,
stdin, stdout/stderr, a named FIFO, normal event storage, or a regular file.
Shell regular-file redirection is not a protected-FD example. Open embedded
lanes may carry the admitted source-profile body in the public trial projection,
but never a prohibited historical response or source target text.

## Allocation and chronology

HCTP and the compatibility fold have different order laws:

```text
HCTP paired trial
  semantic arms freeze before execution
  lanes follow the frozen balanced A/B-B/A allocation
  either semantic arm may execute first
  comparison joins the two matching frozen lanes

compatibility campaign fold
  replay_baseline attempt must predate candidate attempt for one scenario
```

Do not impose the compatibility chronology on HCTP. Post-reveal
`order_effects` is diagnostic: always report baseline-first and candidate-first
counts and per-dimension records; `mean_second_minus_first` is non-null only
when both orientations contribute. These observations are noncausal and do not
alter claim eligibility.

## Sealed assurance

Sealed assurance requires an admitted broker with an authenticated binary and
contract fingerprint. The broker owns role separation, anonymous descriptor
custody, `commit-lane-start`, encrypted pending checkpoints, exact recovery,
and non-disclosure. It must preserve `os_confinement:false`.

The repository-owned `hctp-sealed-role-driver` lives in conformance/test
infrastructure and is not installed product capability. The current native
trial compiler returns `SealedBrokerUnavailable` for a sealed build request.
Do not substitute the test driver, downgrade the label, or proceed through an
open route. A caller integration may use a separately admitted broker only
through the validator-backed native sealed contracts.
Configured binary and contract hashes prove only commitment equality; they do
not establish broker admission. No released native broker-admission validator
or capability currently exists, so the surface checker keeps sealed mode
blocked even when both configured hashes match.

## Recovery

Recovery never creates changed work:

```text
lost lane-start acknowledgement
  -> present exact retained lease and lineage
  -> recover existing start without append

lost lane-finish acknowledgement
  -> present exact retained receipt, lease, and lineage
  -> recover existing terminal state without append

changed input, lineage, lease, trial, or lane
  -> fail
```

If executor liveness is unproved, do not declare a terminal receipt whose
workspace could still change. A one-claim lane is never retried as a new
execution.
