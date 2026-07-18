---
name: hylo
description: "Compile historical Codex sessions into governed counterfactual evidence, evaluate an existing owner-applied candidate through blinded paired HCTP trials, and fold observable evidence into RUN, OBSERVE, or STOP. Use for `$hylo`, CRF extraction, counterfactual replay, source-governed direct or historical trials, sealed evidence, paired baseline/candidate evaluation, causal frontiers, or evidence-governed improvement."
---

# Hylo

## Mission

Coordinate the released CRF/HCTP owners into one custody-safe experiment:

```text
CRF evidence
  -> governed source selection
  -> admitted campaign, scenarios, and target bundles
  -> existing owner-applied candidate
  -> validated and source-bound paired trial
  -> route-correct one-claim lanes
  -> blind grades -> reveal -> observe result -> close -> proof
  -> causal frontier -> owner-routed action or STOP
```

Hylo does not recover private reasoning, treat a historical answer as a replay
baseline, create a candidate, or grant edit, reveal, commit, push, spend, or
external-effect authority. `STOP: no_obvious_next_step` is a successful result.

## Current product boundary

```text
Seq 0.3.52+     CRF extraction, source governance, route admission, materialization
Ledger 0.10.6+  campaign/trial validation, compilation, lifecycle, folds, proof
CAS 0.2.81+     route projection, internal historical preparation, one-claim execution
```

`seq hylo-extract`, `seq hctp-source`, `ledger --source hylo`, and `cas trial`
are macOS product surfaces. Root `ledger validate hylo-*` artifact validators
are platform-neutral. The macOS route establishes commitments, role separation,
one-shot descriptor delivery, public non-disclosure, and exactly-once claims
while reporting
`os_confinement:false`; it does not establish hostile same-user isolation.

Sealed assurance requires a caller-provided admitted broker whose binary and
contract fingerprints satisfy the native role, FD, checkpoint, recovery, and
non-disclosure contracts. Native `compile-trial` currently rejects every sealed
build request as `SealedBrokerUnavailable`; a sealed trial therefore requires a
separately validator-backed trial and an admitted external broker. The
repository's `hctp-sealed-role-driver` is conformance infrastructure, not an
installed product command. Fail closed before secret generation or trial
mutation when either prerequisite is absent.

## Ownership

```text
$seq       historical parsing, cut, redaction, source selection, route admission
$ledger    validation, immutable admission, trial compilation/lifecycle, folds, proof
$cas       route projection, private historical replay preparation, one-claim run
adapters   frozen model/tool execution and observable grading
owner      target changes, staging, commit, push, and publication
$hylo      coordination only; authority_granted:false
```

The historical response is sealed diagnostic evidence. It is never the fresh
baseline or a golden answer.

## Source-of-truth order

When surfaces disagree, use:

1. installed CLI help and capabilities;
2. released validators, schemas, and executable fixtures;
3. implementation documentation;
4. this skill and its references;
5. historical or proposed specifications.

Do not invent standalone `hylo replay`, `hylo grade`, or `hylo compare`
commands.

## Mode-sensitive capability gate

Before the first native Ledger command, load `$ledger` and complete
`$ledger ensure` once. Probe only the requested operation:

| Operation | Required surface |
| --- | --- |
| `validate` (pure artifact validation) | Root `ledger validate hylo-*`; no Seq or CAS requirement |
| repo-aware `doctor`, report, or frontier | macOS `ledger --source hylo` product surface and selected command |
| `extract` | pure validation plus Seq `hylo_extract_v1`, `seq hylo-extract` |
| source selection | Seq `hctp_source_selection_v1`, `hctp_source_route_admission_v1`, `hctp_independence_clusters_v1`, `seq hctp-source` |
| open/direct trial | Ledger `hylo_trial_v2`, `hylo_private_trial_custody_v1`, `hylo_trial_custody_fd_v1`, `hylo_private_lane_start_custody_fd_v1`, `hylo_lane_materialization_v1`, `hylo_lane_materialization_receipt_v2`, `hylo_lane_leases_v1`, `hylo_signed_attestations_v1`, `hylo_trial_compiler_v1`, `hylo_trial_build_receipt_v2`, `hylo_run_receipt_v2`, `hylo_trial_reveal_v2`, `hylo_reveal_material_fd_v1`; CAS `hylo_trial_runner_v2`, `hylo_fd_lane_lease_v1`, `hylo_signed_run_receipt_v2`, `hylo_private_lane_materialization_fd_v1`, `hylo_private_receipt_redaction_v1`, `hylo_target_common_projection_opening_v1`, `hylo_trial_route_projection_v1` |
| historical trial | direct requirements plus CAS `hylo_internal_historical_replay_v1`, `dcp_v2`, `rip_v1`, `fir_v1` |
| case-blind trial | source-selection plus selected direct/historical requirements and Seq `hctp_sealed_case_v1`, `hctp_materializer_v1`, `hctp_source_materialization_v1`, `hctp_source_selection_opening_fd_v1`; historical case-blind additionally requires `hctp_historical_profile_v1` and `hctp_case_blind_source_profile_fd_v1` |
| sealed trial | Native `compile-trial` is unavailable (`SealedBrokerUnavailable`); require a separately validator-backed trial, the selected trial capabilities, and an explicitly admitted external broker |
| proof export | Ledger v2 trial/custody requirements plus `hylo_proof_bundle_v1`, `hylo_external_proof_anchor_v1`, and proof commands; no Seq or CAS requirement after close |

`hylo_trial_v1`, `hylo_trial_runner_v1`, and `hylo_signed_run_receipt_v1`
remain legacy compatibility features. They do not satisfy the private-v2 happy
path.

Use the installed capabilities shape:

```bash
ledger --version
ledger --source hylo capabilities
seq --version
seq capabilities --format json
cas --version
cas capabilities --json
```

Probe command help only for commands selected by the mode. If a required
feature or broker is absent, stop before evidence creation or mutation; do not
emulate it or hand-edit `.ledger/hylo/events.jsonl`.

## Candidate lifecycle

Choose one lifecycle before building a trial:

```text
evaluate_existing_candidate
  owner-applied candidate already exists
  -> admit before/after identities and bounded change
  -> freeze and evaluate it in a new trial

derive_next_candidate
  prior evidence exists
  -> fold failures, hypotheses, experiments, and frontier
  -> RUN | OBSERVE | STOP
  -> owner may apply RUN only under separate authority
  -> return after a new candidate identity exists
```

`RUN` selects an eligible experiment. It neither mutates the target nor creates
the candidate. Report candidate state independently as `absent`,
`owner_applied`, `frozen_for_trial`, `evaluated`, `promoted`, or `rejected`.

## Workflow

Read [orchestration.md](references/orchestration.md) before executing a trial;
it owns the complete state machine and protected-FD rules. Read
[contracts.md](references/contracts.md) before authoring artifacts or event
intents. Read
[grading-and-progression.md](references/grading-and-progression.md) before
grading, comparing, promoting, or selecting an experiment.

### 1. Extract and apply the fidelity gate

Run `seq hylo-extract` with the complete target root. Deliver the seal key only
through an already-open, unlinked anonymous protected descriptor supplied by
the admitted custodian; every sensitive FD is distinct and `>=3`.

```bash
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
  --seal-key-output-fd <custodian-key-sink-fd>
```

Never replace a protected-FD placeholder with regular-file redirection, a
named FIFO, stdin/stdout/stderr, argv, or an environment variable.

Validate the complete extraction graph with Ledger's pure validators. Then
record the episode fingerprint, cut, target bundle, world availability,
runtime, fidelity, `replay_eligible`, and limitations. Schema validity alone
does not admit execution.

### 2. Select and compile the source route

Apply this non-upgrading gate:

| CRF evidence | Source profile | Native result |
| --- | --- | --- |
| `replay_eligible:true` | genuinely `direct` | direct comparison admission |
| `replay_eligible:false` | `direct` | `diagnostic_only` source admission; trial compilation, registration, and comparison execution forbidden |
| `replay_eligible:true` | valid governed `historical_decision` | historical replay admission |
| `replay_eligible:false` | valid governed `historical_decision` | historical replay admission at the retained reconstruction ceiling |
| any | absent or invalid `historical_decision` governance | compilation fails; the source remains diagnostic evidence only |

A historical source must never be relabeled `direct`. Historical
`practice_repair` and `promotion` require authoritative SGG/DCP target-text
witness governance and the required RIP/FIR lineage.

Compile the source-selection receipt before trial construction. The signing
seed and any seal key use admitted protected descriptors:

```bash
seq hctp-source compile \
  --manifest source.json \
  --output selection.json \
  --source-signing-seed-fd <source-owner-seed-fd>
```

Do not run `hctp-source validate` yet; it requires the completed trial.

### 3. Admit the parent campaign

Construct `campaign.json` and its complete scenarios JSONL. An HCTP campaign
opts into `hylo-trial/v2` (and MAY also retain `hylo-trial/v1` compatibility),
`hylo-canonical-json/v1`, its trial policy,
`source_route_admission:"required"`, proof authority/trust where required, and
the complete scenario manifest.

```bash
ledger --source hylo validate-campaign --campaign campaign.json
ledger --source hylo append --repo <repo> --json campaign-created.json
ledger --source hylo append --repo <repo> --json baseline-target-bundle-admitted.json
ledger --source hylo append --repo <repo> --json candidate-target-bundle-admitted.json
ledger --source hylo append --repo <repo> --json scenario-admitted-001.json
ledger --source hylo append --repo <repo> --json change-recorded.json
ledger --source hylo doctor --repo <repo>
```

Append every remaining `scenario_admitted` intent in the frozen manifest before
the change intent and doctor pass.

A trial is additive to an admitted campaign, not a campaign substitute. Do not
compile or register it until the campaign, every required scenario, and both
required target identities are admitted. Promotion must cover the complete
applicable protected set fixed by the campaign.

### 4. Bind the existing candidate

Require the owner-applied candidate, exact before/after bundle and snapshot
identities, bounded path set, and applied change event. If no concrete candidate
exists, stop trial construction and use the causal frontier first.

### 5. Compile, validate, source-validate, and register

Use the native compiler and deliver `hylo-trial-custody/v1` to an admitted
custodian over an unlinked anonymous protected descriptor. The public output is
commitment-only `hylo-trial/v2`:

```bash
ledger --source hylo compile-trial \
  --repo <repo> \
  --request trial-build-request.json \
  --source-receipt selection.json \
  --output trial.json \
  --custody-output-fd <custodian-custody-sink-fd>

ledger --source hylo validate-trial --repo <repo> --trial trial.json
seq hctp-source validate --receipt selection.json --trial trial.json
ledger --source hylo register-trial \
  --repo <repo> \
  --trial trial.json \
  --custody-input-fd <custodian-registration-source-fd>
```

Stop if any command fails. The `hylo-trial-build-receipt/v2` on stdout with
`custody_material_delivered:true` is the compiler's completion observation. The
compiler attempts to remove the public trial when private delivery reports
failure; `TrialOutputRollbackFailed` identifies an uncommitted recovery path.
Transient file visibility or a partial custody stream is not completion or
authority. Source
validation joins the external signed receipt to the public portable
`artifact:sha256:<64 lowercase hex>` reference, fingerprint, and commitment;
the reference digest equals the receipt fingerprint. The public trial never
embeds the full receipt or a caller-local path.

Every public v2 `units[*].source_profile` is the exact native safe projection.
Exact-key validation rejects semantic extras; a full historical profile body,
source target text, rationale, rejected routes, and hidden references remain
outside the public trial and use the admitted private carrier when required.

The custodian retains the exact custody record outside public artifacts and
re-delivers it through a fresh protected pipe for registration, each new v2
lane start or caller-retained start commit, each lane materialization, and
reveal. The public registration event persists only the v2 trial and a
validated nonsemantic custody-commitment observation. Exact recovery of an
already-started lane uses the retained lease and does not create changed work.

For private-v2 registration, the earlier validators and command preflight are
necessary but do not own the append decision. Ledger reacquires exclusive
store ownership, loads the exact append snapshot, and reruns the full semantic
trial-against-campaign validation on the custody-backed trial before applying
or appending `trial_registered`. A stale or mismatched semantic view fails
without append. The legacy v1 registration path retains its established public
trial contract.

### 6. Execute each lane by its frozen route

Run `cas trial preflight --trial trial.json --lane-id <lane> --json` and obey
its exact `source_profile_kind`, `compile_replay_required`,
`replay_preparation_mode`, `source_profile_body_delivery`, `execution_route`,
and `required_lineage`. Direct lanes report
`compile_replay_required:false` and `replay_preparation_mode:"none"`;
historical lanes report `compile_replay_required:false` and
`replay_preparation_mode:"integrated_run"`.

```text
source_profile.kind == "direct"
  -> materialize visible input
  -> start or commit the lease
  -> privately materialize the selected treatment from custody under that lease
  -> cas trial run once with --materialization-fd and no source-profile FD
  -> finish or recover the terminal acknowledgement

source_profile.kind == "historical_decision"
  -> materialize visible input
  -> privately materialize the source profile through the required v2 FD
  -> start or commit the lease
  -> privately materialize the selected treatment from custody under that lease
  -> cas trial run receives --materialization-fd and --source-profile-fd,
     then prepares one DCP/RIP internally before claim
  -> validate FIR/native receipt lineage
  -> finish or recover the terminal acknowledgement
```

For every v2 lane, bind the public start event to `treatment_commitment`, retain
the exact lease, and supply custody while the new start validates the private
target treatment under the repository locks:

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

For a caller-retained start, `commit-lane-start` likewise receives the exact
custody through `--custody-input-fd` alongside its lease input. Then invoke the
private treatment bridge:

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

Ledger emits only `hylo-lane-materialization-receipt/v2` on stdout; retain that
safe receipt for reveal. The FD carries the lease-bound claim and selected
treatment without semantic role. It also carries the exact
`hylo-target-common-projection-opening/v1`; CAS verifies the committed opening
and nested projection before execution. CAS emits commitment-only
`hylo-run-receipt/v2`; raw target, factor, archive, and treatment fields remain
private. Its only public FIR carrier is the exact
`hylo-fir-public-projection/v1`; the full FIR remains private. A v1 run receipt
retains its compatible full-FIR carrier.

For each v2 lane, retain and exact-join the safe receipt's `claim_fingerprint`
to
`hylo-run-receipt/v2.materialization.materialization_claim_fingerprint`.
Reveal admits one matching `hylo-lane-materialization-receipt/v2` per lane;
changed, missing, duplicate, or version-mixed per-lane safe receipts fail
before append.

For case-blind input materialization, the custodian projects only the exact
`hylo-source-selection-opening/v1` from trial custody onto a separate protected
FD:

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

For every v2 historical lane, preflight freezes
`source_profile_body_delivery:"source_profile_fd"`. Add
`--source-profile-output-fd <runner-source-profile-sink-fd>` and connect that
protected source directly to the historical `cas trial run
--source-profile-fd` input. Embedded historical delivery is legacy v1 or
standalone diagnostic compatibility, not the v2 execution route.

Direct lanes skip and forbid `compile-replay`. Historical execution also does
not use the standalone command: CAS performs private replay preparation inside
`run` before the irreversible claim. The standalone `compile-replay` surface is
diagnostic-only, rejects direct/case-blind/role-separated/sealed use, grants no
execution authority, reports `execution_authority:false`, and is not part of
the trial happy path. `run` does not consume its receipt or DCP/RIP files.

Follow the frozen balanced A/B-B/A lane order exactly; either semantic arm may
execute first. Never retry a claimed lane as new work. Use native status and
recovery to re-emit or finish only the exact admitted work.

### 7. Grade, reveal, and prove

Record hard gates before scores, then blind absolute and pair grades under the
frozen authorities. Pre-reveal public output contains only commitments,
fingerprints, opaque acknowledgements, and permitted terminal metadata.

When consumed by a v2 trial, `hylo-grade-receipt/v1`,
`hylo-pair-grade-receipt/v1`, and
`hylo-grade-presentation-receipt/v1` are closed and exact native shapes:
unknown keys or undeclared nested fields are invalid. Every consumed public
evidence, rationale, grade-receipt, pair-grade-receipt, and
presentation-receipt reference uses exactly
`artifact:sha256:<64 lowercase hex>` and exact-joins any companion fingerprint.
V1 trial carriers retain their established compatibility behavior.

Reveal only after every required lane and grade is terminal and policy permits
it. Supply the exact custody record plus every required safe lane-materialization
receipt:

```bash
ledger --source hylo reveal-trial \
  --repo <repo> \
  --reveal-material-fd <custodian-reveal-source-fd> \
  --materialization-receipt lane-001-materialization-receipt.json
```

Repeat `--materialization-receipt` for every lane.

`--reveal FILE` is legacy v1-only and accepts only
`hylo-trial-reveal/v1`. A caller-authored `hylo-trial-reveal/v2` file has no
admitted provenance. V2 reveal requires the validated `hylo-trial-custody/v1`
record through `--reveal-material-fd`; Ledger derives and validates the v2
reveal, exact-joins every lane receipt to its run receipt, and only then may
append `trial_revealed`.

Validated `hylo-trial-reveal/v2` is the first public semantic opening. It opens
the arm map, treatments, target epoch, intervention witness, and target common
projection; the full source-selection receipt remains custody-only. Derive
paired deltas, hard-gate changes, critical regressions, dispersion,
uncertainty, independence-cluster coverage, null/calibration results, and
post-reveal diagnostic position/order effects. Observe the derived result, then
close the trial; proof occurs only after close:

```bash
ledger --source hylo trial-result --repo <repo> --trial-id <trial-id> --format json
ledger --source hylo close-trial --repo <repo> --trial-id <trial-id>
```

Proof export grants no mutation or publication authority. Proof bundles exclude
`hylo-trial-custody/v1` and private lane claims/materializations and derive
semantic evidence only from the validated public reveal. Public proof
sanitization rejects private semantic keys such as `private_reasoning`,
`historical_response`, and `source_target_text`, while retaining
schema-declared boolean non-disclosure observations such as
`hidden_reference:false`.

### 8. Fold the frontier and route owner action

Derive failure signatures, hypotheses, bounded experiments, and the native
frontier decision:

```text
RUN      owner may apply the selected intervention only under separate authority
OBSERVE  execute only the bounded read-only probe
STOP     stop the current campaign scope
```

A newly applied candidate requires a new evaluation trial. Keep the HCTP
allocation law separate from the compatibility campaign law: HCTP accepts A/B
or B/A frozen pairs, while the legacy fold still requires a `replay_baseline`
attempt to predate its matching `candidate` attempt.

## Output

```text
Hylo:
- requested operation, assurance, versions, and capability result
- campaign ID/head and admission completeness
- episode/cut, CRF fidelity, replay_eligible, route, and retained limitations
- source-selection receipt fingerprint/commitment and independence-cluster coverage
- trial ID/fingerprint, purpose, allocation, pair/repeat/lane counts
- direct/historical preparation and terminal/recovered lane counts
- hard gates, grades, pair deltas, position effects, and uncertainty
- reveal/proof state and scoped claim class
- active failures, hypotheses, experiments, and frontier decision
- candidate_state
- authority_granted_by_hylo:false
- owner_authority: none | propose | apply | commit | push
- event-chain or proof identity
```

Never print private reasoning, pre-reveal semantic arm mapping, historical
answer, hidden reference, full source-selection receipt, raw target epoch,
target common projection, intervention witness, treatment materialization,
lease material, openings, signing seeds, custody record, or custody keys.

## Hard rules

- No cut after the first causally relevant target influence.
- No dropped or deduplicated fixed-prefix occurrence.
- No replay-ineligible CRF source relabeled as direct.
- No source receipt validation before a complete trial exists.
- No trial compilation or registration before complete campaign admission.
- No private-v2 registration without the exact custody record on a protected FD.
- No private-v2 registration append without full semantic revalidation against
  the exact exclusive append snapshot.
- No new private-v2 lane start or caller-retained start commit without the
  exact custody record on `--custody-input-fd`.
- No private-v2 case materialization without the exact custody-projected
  `hylo-source-selection-opening/v1` on `--source-selection-opening-fd`.
- No private-v2 CAS run without the exact lease-bound lane materialization FD.
- No v2 reveal without one exact per-lane join from
  `hylo-lane-materialization-receipt/v2.claim_fingerprint` to
  `hylo-run-receipt/v2.materialization.materialization_claim_fingerprint`.
- No caller-authored v2 reveal through legacy `--reveal FILE`.
- No full FIR or source-profile semantic extras on a v2 public trial, run
  receipt, event, or proof surface.
- No unknown keys in v2-consumed grade, pair-grade, or presentation receipts;
  no nonportable public evidence, rationale, or receipt reference.
- No trial mutation after registration; changed contracts require a new trial.
- No protected-FD value carried through argv, environment variables,
  regular-file redirection, named FIFOs, normal stdout, the event store, or
  proof bundles; native private DCP/RIP files remain governed by their explicit
  `0700`/`0600` custody contract.
- No standalone `compile-replay` in an execution path.
- No custody record or private lane claim included in a public event or proof.
- No baseline-first requirement imposed on frozen HCTP B/A allocation.
- No historical answer used as a baseline or golden answer.
- No claimed lane retried as new execution.
- No low-level `append` used for trial lifecycle events.
- No hard-gate failure averaged away.
- No comparison across source, world, runtime, model, tool/effect, oracle,
  grader, visibility, or split drift.
- No repair motivated by exposed holdout or challenge evidence.
- No `RUN` represented as target mutation or candidate creation.
- No uninstalled sealed driver represented as product infrastructure.
- No OS-confinement, generalized-causality, or authority overclaim.
- No hand-editing `.ledger/hylo/events.jsonl`.
