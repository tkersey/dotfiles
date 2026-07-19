---
name: ledger
description: "Ensure a `ledger` command is available on PATH, validate and derive Actuating Artifact Kernel contracts without taking semantic authority, coordinate post-closure Learnings/Synesthesia/Negative Ledger evaluation and repo-local source-memory reconciliation, address Universalist plans and receipts, and route Hylo campaign/trial operations. Use before a workflow's first Ledger command, for artifact-kernel validation, fold/state/closure projection, source-memory lifecycle work, Ledger status or migration, Universalist plan addressing or receipt emission, or Hylo CRF/HCTP lifecycle work."
---

# Ledger

## Mission

Own the shared Ledger bootstrap and lifecycle-coordination boundaries,
coordinate repo-local source-memory stores through native source APIs, and
route pure validation and deterministic derivation of governance, review, and
Actuating Artifact Kernel artifacts.

Use `$ledger` for source-memory migration, cross-store doctor, harvest planning, and memory admission coordination. Do not use it to bypass source-specific authority.

## Bootstrap boundary

Every procedural Ledger consumer must declare this prerequisite: before the
first native Ledger command in a workflow, load this skill and complete
`$ledger ensure` once. That readiness applies to every consumer in the workflow;
do not repeat the bootstrap per skill or per command. `$ledger` is skill syntax,
not a shell command.

Use [scripts/ensure-ledger](scripts/ensure-ledger) as the deterministic bootstrap
handler:

```bash
codex/skills/ledger/scripts/ensure-ledger
```

After the handler emits `ledger-bootstrap-ready/v1`, invoke the native CLI
directly:

```bash
ledger <native-ledger-arguments...>
```

The bootstrap handler checks only that `ledger` resolves on `PATH` and,
when installation authority exists, can install the canonical Homebrew formula.
It does not inspect the CLI version, duplicate CLI integrity checks, or proxy
native commands. A source owner that depends on a minimum version must probe
`ledger --version` after readiness and before mutation; the bootstrap receipt
does not satisfy that compatibility check. Afterward, the native CLI owns
integrity, stdout, stderr, exit status, and failure reporting.

If `ledger` does not resolve on `PATH`:

1. install only when the current user request or standing
   environment policy authorizes user-level CLI provisioning;
2. pass `--install` to the bootstrap handler when that authority exists;
3. otherwise stop with the handler's exact remediation;
4. never use `curl | sh`, an unpinned download, or an alternate Ledger
   implementation.

On supported Homebrew environments the canonical formula is
`tkersey/tap/ledger`. Bootstrap before opening an actuation generation; do not
install during an open generation.

~~~yaml
ledger_bootstrap_ready:
  schema: ledger-bootstrap-ready/v1
  status: ready
  path:
  action: none | installed
~~~

Bootstrap readiness grants no source authority. The calling skill still owns
the semantic operation and every requested write or effect.

Canonical source APIs:

- `ledger --source learnings`
- `ledger --source negative-ledger` for negative evidence; source-less commands
  remain a compatibility surface
- `ledger --source synesthesia` when present
- `ledger --source actuation`
- `ledger --source hylo`

Current source-memory persistent-adapter locations, retained for path
compatibility and explicit migration:

- `.ledger/learnings/events.jsonl`
- `.ledger/negative-ledger/events.jsonl`
- `.ledger/synesthesia/events.jsonl` when present

Operational, non-memory stores:

- `.ledger/actuation/events.jsonl` is the current actuation persistent adapter,
  owned exclusively by `ledger --source actuation`; do not harvest it into
  memory or route its writes through source-memory coordination.
- `.ledger/hylo/events.jsonl` is the current Hylo persistent adapter, owned
  exclusively by `ledger --source hylo`; do not harvest it into memory or
  route its writes through source-memory coordination.

Operational, non-memory artifacts:

- `.ledger/universalist/plan-{plan-id}.md`, addressed exclusively by
  `ledger --source universalist`; do not harvest these plans into memory.

## Actuating Artifact Kernel v1 boundary

After `$ledger ensure`, use the root validators for immutable documents, the
static Review Contract, individual Evidence Ledger events, and derived closure
receipts:

```bash
ledger validate goal-contract-v3 --input FILE|-
ledger validate counterexample-set --input FILE|-
ledger validate construction-contract --input FILE|-
ledger validate actuating-review-contract --input FILE|-
ledger validate actuating-evidence-event --input FILE|-
ledger validate actuating-closure-receipt --input FILE|-
ledger validate ship-v1 --input FILE|-
```

Together, these commands accept only canonical instances of:

```text
goal-contract/v3
counterexample-set/v1
construction-contract/v1
actuating-review-contract/v1
actuating-evidence-event/v1
```

An explicit `--goal` selects the Artifact Kernel Actuation source. Inspect that
surface, replay the current Evidence Ledger, and derive closure with:

```bash
ledger --source actuation --goal GOAL_ID --help
ledger --source actuation --goal GOAL_ID state
ledger --source actuation --goal GOAL_ID decide
```

The static Review Contract is not mutable per-goal state. `state` is a
discardable view. `decide` deterministically binds the Goal Contract, current
Construction Contract, current subject digest, goal-local Evidence Ledger
material and full heads, and Review Contract into an
`actuating-closure-receipt/v1`. A serialized receipt is a cache, not an
independently authored completion decision; discard and recompute it whenever
any bound input changes.

Ledger owns canonical envelopes, content identities, append integrity, replay,
folds, and projections. It does not author Goal semantics, classify
Counterexamples, select a Construction, grant mutation, choose review repairs,
or perform public effects. Validation establishes only the claims named in the
validator response. See
[Actuating's Artifact Kernel owner map](../actuating/references/artifact-kernel.md)
for ownership and protocol routing; Ledger does not duplicate that contract.

## Hylo CRF/HCTP authority

After `$ledger ensure`, use the portable validator when only artifact structure
is in scope:

```bash
ledger validate hylo-trial --input trial.json
```

This root artifact validator is platform-neutral, reads no Hylo store, and
grants no campaign, execution, reveal, proof, or mutation authority. Only root
`ledger validate ...` artifact validators are portable. Operational commands
under `ledger --source hylo`, including `doctor`, remain gated by the shared
macOS product-admission law. On an admitted macOS build, probe:

```bash
ledger --source hylo capabilities
ledger --source hylo --help
```

The capabilities response is `hylo-capabilities/v1`; `features` is an array of
exact strings rather than a map of Boolean aliases. The private-v2 route
requires:

```text
hylo_trial_v2
hylo_lane_leases_v1
hylo_trial_compiler_v1
hylo_reveal_material_fd_v1
hylo_private_trial_custody_v1
hylo_lane_materialization_v1
hylo_signed_attestations_v1
hylo_trial_custody_fd_v1
hylo_private_lane_start_custody_fd_v1
hylo_trial_build_receipt_v2
hylo_lane_materialization_receipt_v2
hylo_run_receipt_v2
hylo_trial_reveal_v2
```

`hylo_trial_v1` remains an explicit legacy compatibility feature; it does not
satisfy private-v2 custody.

Proof export additionally requires:

```text
hylo_proof_bundle_v1
hylo_external_proof_anchor_v1
```

### Campaign admission before trial registration

An HCTP trial is additive to an admitted parent campaign, not a campaign
substitute. Preserve this order:

```text
ledger --source hylo validate-campaign
-> append campaign_created
-> append every required target_bundle_admitted
-> append every scenario_admitted in the complete manifest
-> append the owner-applied change_recorded intent
-> ledger --source hylo doctor
-> ledger --source hylo compile-trial (or construct a validator-backed trial)
-> ledger --source hylo validate-trial
-> seq hctp-source validate
-> ledger --source hylo register-trial with --custody-input-fd for v2
```

The private-v2 campaign must opt into `hylo-trial/v2` (and MAY also retain
`hylo-trial/v1` compatibility) and set
`trial_policy.source_route_admission:"required"`. Registration derives campaign,
scenario, target, and promotion-coverage authority from immutable campaign
events. It fails without complete admission; low-level `append` never owns
trial lifecycle events.

`compile-trial` consumes the current admitted campaign, one exact signed source
receipt, frozen before/after target identities, and an already owner-applied
candidate:

```bash
ledger --source hylo compile-trial \
  --repo <repo> \
  --request trial-build-request.json \
  --source-receipt selection.json \
  --output trial.json \
  --custody-output-fd <anonymous-private-write-fd>
```

The custody endpoint must be an unlinked anonymous directional pipe supplied
under the admitted custodian's custody. The CLI verifies descriptor shape and
direction, not peer-process identity, and a regular file is invalid. The
compiler atomically creates the opaque public `trial.json` path before
delivering private `hylo-trial-custody/v1`. It attempts to remove the public
output when private delivery fails; `TrialOutputRollbackFailed` means that path
may remain as an uncommitted recovery artifact. The public-file and private-pipe
sinks are not crash-atomic. Artifact presence or a partial custody stream is not
completion: require the emitted
`hylo-trial-build-receipt/v2` with `custody_material_delivered:true` before
proceeding to source validation or registration. The public trial, normal
stdout, and event store never contain semantic arm mappings, treatment
materializations, target openings, witness/common-projection bodies, or the
full source receipt.

The compiler emits each public v2 `units[*].source_profile` as the exact native
safe projection. Exact-key validation rejects semantic extras; full historical
profile material remains outside the public trial. For v2 run evidence, Ledger
accepts and persists only the exact `hylo-fir-public-projection/v1`; the full
FIR remains private. The v1 path retains its established full-FIR carrier.

The custodian retains the exact custody record outside public artifacts and
re-delivers it over fresh protected pipes for registration, each new v2 lane
start or caller-retained start commit, each lane materialization, and reveal.
Register v2 with:

```bash
ledger --source hylo register-trial \
  --repo <repo> \
  --trial trial.json \
  --custody-input-fd <anonymous-private-read-fd>
```

The event persists only the public `hylo-trial/v2` and a validated nonsemantic
custody-commitment observation. Later reveal consumes the same exact custody
record through `--reveal-material-fd <anonymous-private-read-fd>`. Do not
demonstrate any protected FD with shell regular-file redirection.

The earlier `validate-trial`, source validation, and registration preflight are
necessary but are not append authority. For private v2, Ledger reacquires
exclusive store ownership, reloads the exact append snapshot, and reruns the
full semantic trial-against-campaign validation on the custody-backed trial
before applying or appending `trial_registered`. Any stale semantic binding
fails without append. V1 retains its established public-trial registration
path.

A new v2 lane start also consumes custody while Ledger holds the repository
observation locks and validates the private target treatment:

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

`commit-lane-start` requires the same custody input when committing a new v2
start from a caller-retained lease. Exact already-started recovery uses the
retained lease and re-emits existing state without rereading custody.

For each started v2 lane, `lane-materialization` consumes a fresh custody FD
and the exact retained lease and emits the selected treatment only to a private
output FD:

```bash
ledger --source hylo lane-materialization \
  --repo <repo> \
  --trial-id <trial-id> \
  --lane-id <lane-id> \
  --registration-event-digest <registration-digest> \
  --lane-started-event-digest <start-digest> \
  --lane-lease-digest <lease-digest> \
  --custody-input-fd <custodian-source-fd> \
  --lease-input-fd <retained-lease-source-fd> \
  --materialization-output-fd <cas-sink-fd>
```

Normal stdout contains only `hylo-lane-materialization-receipt/v2`; retain it
for reveal. The FD-delivered claim is lease-bound, contains no semantic role,
and must not enter public artifacts or proof bundles. The claim includes the
exact `hylo-target-common-projection-opening/v1`; CAS validates its public
commitment and nested projection fingerprint before execution.

For every v2 lane, the safe receipt's `claim_fingerprint` must exact-join
`hylo-run-receipt/v2.materialization.materialization_claim_fingerprint`.
Reveal accepts exactly one matching
`hylo-lane-materialization-receipt/v2` per lane; changed, missing, duplicate,
wrong-lane, wrong-trial, or version-mixed per-lane safe receipts fail before
append.

`ledger --source hylo reveal-trial --reveal FILE` is legacy v1-only and
accepts only `hylo-trial-reveal/v1`. It cannot import a caller-authored v2
reveal. V2 requires validated `hylo-trial-custody/v1` provenance over
`--reveal-material-fd` plus every joined lane-materialization receipt; Ledger
derives `hylo-trial-reveal/v2` before the high-level append.

For v2 grading, `hylo-grade-presentation-receipt/v1`,
`hylo-grade-receipt/v1`, and `hylo-pair-grade-receipt/v1` are closed and exact
native shapes. All consumed public evidence, rationale, grade-receipt,
pair-grade-receipt, and presentation-receipt references use exactly
`artifact:sha256:<64 lowercase hex>` and exact-join companion fingerprints.
Public proof rejects private semantic keys but permits schema-declared boolean
non-disclosure observations such as `hidden_reference:false`. V1 grade
carriers retain their established compatibility behavior; proof sanitization
applies across versions without changing v1 trial semantics.

`compile-trial` validates live campaign head, complete scenario and target
admission, source-route bindings, authoritative historical governance for
`practice_repair` and `promotion`, target snapshots, and the applied change
before generating opaque arm IDs and balanced A/B-B/A allocation. Native
`compile-trial` currently rejects every sealed request as
`SealedBrokerUnavailable`; a separately validator-backed sealed trial still
requires an admitted external broker.

The request's `factor.verifier.fingerprint` must equal the SHA-256 content
fingerprint of the executing Ledger binary. Its `sealing` object must contain
`reveal_scope` (`trial` or `campaign_holdout`), `case_materializer_ref`, and
`case_materializer_fingerprint`; `case_materializer_contract` may be omitted.
For `open` and `result_blind`, the materializer values must be null. For
`case_blind`, the ref and fingerprint must be strings and the contract must be
an object. Visibility and commitment fields are compiler-generated and
rejected if caller-supplied.

HCTP lane execution follows its frozen balanced order; either semantic arm may
run first. The rule that a `replay_baseline` attempt must predate its candidate
belongs only to the legacy compatibility campaign fold. `RUN` selects a bounded
next experiment but grants no target mutation authority; a new owner-applied
candidate requires a new evaluation trial.

CAS preflight reports `compile_replay_required:false` for both direct and
historical lanes. Direct uses `replay_preparation_mode:"none"`; historical uses
`replay_preparation_mode:"integrated_run"`. Historical case-blind source
profiles travel through a protected FD directly into
`cas trial run --source-profile-fd`. Standalone `compile-replay` is
non-authorizing diagnostic infrastructure and contributes no input to an
accountable lane run.

Stateless, non-authorizing observations:

- the Artifact Kernel validators listed in
  [Actuating Artifact Kernel v1 boundary](#actuating-artifact-kernel-v1-boundary);
- `ledger validate plan-source-contract --input FILE`
- `ledger validate policy-synthesis-receipt --input FILE`
- `ledger validate review-fold --input FILE`
- `ledger validate source-memory-checkpoint --input FILE`

Legacy read compatibility only:

- `ledger validate actuation-review-policy --phase PHASE --input FILE`
- `ledger validate review-resolution --phase PHASE --input FILE`

These commands accept canonical JSON and never read or write `.ledger`. General
governance contracts emit `ledger-validate-decision/v1`; Actuating contracts
emit their domain validation-decision schemas. Ledger 0.7.0 and newer preserve
v1 same-tuple review-policy validation and enforce the v2 certified
cross-tuple standard-clean chain for historical goals. Artifact Kernel goals
must not write either legacy artifact. Source-memory checkpoint coordination
requires Ledger 0.10.0 or newer; probe `ledger --version` before opening that
checkpoint.

Source-store state model:

```text
missing -> legacy-only -> migrated/current
             \                 /
              +---- invalid ---+
```

`legacy-only` is an actionable preflight state. It means reads may use
compatibility fallback, but writes and commit closeout must first run the owning
source migration. For learnings, that owner is
`ledger migrate --source learnings --mode copy`; for negative evidence, that
owner is `ledger migrate --source negative-ledger --mode copy`. Synesthesia can report `notes-only`
during transition; copy import is explicit through
`ledger migrate --source synesthesia --mode copy`.

For learnings, Ledger `>= 0.5.2` validates the selected canonical or legacy
store and reports `records`, bounded repairs, and invalid physical line spans.
An `invalid` doctor result exits nonzero. Default migration rejects every
remaining invalid record. `--invalid-policy skip` is an explicit partial
projection: it is copy-only, preserves the immutable legacy source, and lists
every skipped span. The learnings skill, not `$ledger`, decides whether the
task authorizes that omission.

Compiled Codex memory is still owned by Phase 2. Memory-source notes are admission snapshots, not canonical stores.

## Source-memory lifecycle checkpoint

At a decision-shaping validation transition, material strategy pivot, delivery
boundary after implementation, pre-commit boundary, PR handoff, terminal
implementation/review closeout, or explicit checkpoint request, use the
repository's governing lifecycle. For `artifact-kernel-v1`, defer this
checkpoint until a current `ready-to-ship` or `complete` closure projection and
delivery handoff so source-memory processing remains outside code closure:

1. Complete `$ledger ensure` once for the workflow and require Ledger 0.10.0 or
   newer. Participants consume that readiness; they do not bootstrap again.
2. Construct one bounded immutable `source-memory-checkpoint-input/v1` packet
   containing current subject identity, literal decision and validation
   evidence, attempted routes, user-authority events, changed paths, and the
   final handoff. Compute subject and evidence SHA-256 fingerprints.
3. Invoke exactly `$learnings`, `$synesthesia`, and `$negative-ledger` with
   `checkpoint_context=source-memory-checkpoint/v1`. Each participant evaluates
   only its source contract, returns exactly one canonical disposition plus one
   admission disposition, and does not invoke Ledger as coordinator or call a
   sibling source.
4. Continue collecting all three results when one participant fails. Canonical
   source writes are independent and append-only; never roll one back because a
   sibling or derived admission stage failed.
5. Assemble `source-memory-checkpoint/v1`, validate it with
   `ledger validate source-memory-checkpoint --input FILE|-`, and retain one
   current receipt. Recompute both fingerprints before reuse; changed code,
   evidence, route, or authority makes the prior receipt stale and requires a
   fresh fan-out.

Aggregate `complete` when every participant evaluated and neither a canonical
nor derived operation is blocked; use `degraded` when semantic evaluation and
canonical writes completed but a note or digest stage failed; use `blocked` for
a missing participant, stale/invalid evidence, or a required canonical failure.
This status proves source-memory closeout only. It does not grant delivery
authority, and the separate exact current Negative Ledger pre-route map remains
the only source-memory route gate.

Evaluation is mandatory; writes and admissions are conditional. Keep ordinary
all-no-op receipts internal. Report source writes, actionable Synesthesia
candidates, derived-stage degradation, and exact blockers. See
[source-memory-checkpoint.md](references/source-memory-checkpoint.md) for the
packet, participant, receipt, freshness, idempotence, and reporting contracts.

## Reconciliation boundary

Lifecycle checkpointing prevents new gaps; it does not scan or admit historical
rows. Run the read-only reconciliation workflow explicitly to compare canonical
records, immutable notes, derived digests, and compiled-memory mentions. The
report may identify `admitted`, `eligible-unadmitted`, `not-eligible`,
`needs-source-review`, `incomplete-projection`, `stale-note`, and
`phase2-lag`; it must not synthesize source eligibility or write notes.

```bash
uv run python \
  codex/skills/ledger/scripts/source-memory-reconcile.py \
  --repo "$(git rev-parse --show-toplevel)" \
  --format text
```

When source owners have reviewed specific historical rows, pass an explicit
`source-memory-eligibility/v1` JSON file via `--eligibility`. Each decision must
name one canonical ID, `eligible|not-eligible`, and a non-empty source-owned
reason. The reconciler uses that input only to distinguish a real admission gap
from an ineligible or unreviewed record; it remains read-only and non-authorizing.

After an owning source explicitly accepts a candidate, use its documented
adapter or native export plus `memory-note`. Keep backfill bounded and auditable;
never bulk-admit every learning or incomplete Negative Ledger projection.

## Trigger Cues

- `$ledger`;
- `$ledger ensure`;
- a skill's first native Ledger command;
- ensure, install, or verify the native Ledger CLI is available;
- ledger status;
- source memory stores;
- migrate learnings;
- memory harvesting;
- source-memory lifecycle checkpoint;
- reconcile canonical source records with memory notes;
- harvest stores for memories;
- why memories are not being captured;
- doctor `.ledger`;
- cross-store memory digest.
- validate legacy PSC-v1, PSR-v1, or RF-v2;
- `ledger validate`.
- `goal-contract/v3`, `counterexample-set/v1`, or
  `construction-contract/v1` validation;
- Artifact Kernel fold, state, closure, Review Contract, or Evidence Ledger.
- create or resolve a Universalist plan;
- find the newest Universalist plan without overwriting an earlier run.
- emit or atomically append a Universalist SDR-v1 decision receipt.

## Authority

`$ledger` may provision and verify the native CLI, then coordinate, inspect, and
recommend. It does not proxy ordinary native commands. Writes remain delegated
to source-specific skills and native source APIs:

- `$learnings` / `ledger --source learnings`; the current compatibility adapter is `.ledger/learnings/events.jsonl`;
- `$negative-ledger` / `ledger --source negative-ledger`; source-less commands
  remain compatible, and the current persistent adapter is
  `.ledger/negative-ledger/events.jsonl`;
- `$synesthesia` / `ledger --source synesthesia`; the current compatibility adapter is `.ledger/synesthesia/events.jsonl`, and current Synesthesia notes remain transition evidence;
- `$memory-source-notes` / `memory-note` for immutable admission snapshots.
- `$actuating` / `ledger --source actuation` for the operational actuation
  event chain; this is not a memory-admission source.
- `$hylo` / `ledger --source hylo` for operational replay-campaign evidence;
  the current compatibility adapter is `.ledger/hylo/events.jsonl`, and this is
  not a memory-admission source.
- `$universalist` owns decision policy, its SKDC-v1 contract, plan templates,
  and ordinary Markdown field updates; `ledger --source universalist` owns plan
  identity, atomic creation, address resolution, SDR-v1 receipt construction,
  Seq validation, and single-receipt atomic append.

Never write `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*`.

`ledger validate` checks structure and invariants only. A pass verdict never
grants execution or mutation authority; the artifact's domain owner retains
that authority boundary.

## Universalist Plan Workflow

Create a fresh plan from the Universalist-owned template:

```bash
ledger create --source universalist \
  --repo PROJECT_ROOT \
  --template /path/to/universalist/templates/universalist-plan.md
```

Retain the returned `plan_id`; resolve the exact run address with:

```bash
ledger path --source universalist --repo PROJECT_ROOT --id PLAN_ID
```

Recover the newest valid address only when the run id was lost:

```bash
ledger latest --source universalist --repo PROJECT_ROOT
```

Plan ids use `YYYYMMDDTHHMMSSnnnnnnnnnZ-NNNN`. Timestamp order makes the
newest address visible, while atomic ordinal retries prevent overwrite. Treat
`latest` as recovery, not identity: verify the plan's task fields before
resuming because another run may be newer.

New plans use `.ledger/universalist/plan-{plan-id}.md`. Exact-id and `latest`
lookup preserve read access to legacy `.ledger/universalist-plan-{plan-id}.md`
files without rewriting them; the namespaced path is canonical when both
layouts contain the same id.

Ledger 0.10.6 or newer, paired with Skills Seq 0.3.52 or newer, emits the
consequential root receipt selected by Universalist:

```bash
ledger emit --source universalist \
  --plan .ledger/universalist/plan-PLAN_ID.md \
  --contract /path/to/universalist/references/decision-contract.yaml \
  --question "Which construction owns this seam?" \
  --selected-route UNI-ORDINARY \
  --rejected-route UNI-CANONICAL \
  --expected-outcome "One owner enforces the observable law." \
  --disposition changed \
  --construction "checked owner-boundary adapter" \
  --law "required observations are preserved" \
  --falsifier "a mismatched source is accepted" \
  --advanced-mechanics none \
  --evidence-ref "code:path" \
  --write-plan
```

The native command preserves the Universalist contract as policy authority,
accepts YAML and JSON SKDC-v1, and consumes Seq's fingerprint, decision-capable
skill kind, parsed identities, and clause-route bindings from one validation of
one immutable contract snapshot. It validates the generated SDR-v1 with that
capability-compatible Skills Seq companion and fails before plan mutation on an
unknown reference, noncanonical write target, invalid receipt, concurrent
writer, or duplicate JSON or YAML receipt. Ledger checks a sibling `seq` before
searching `PATH` and skips same-name binaries that do not advertise the required
receipt-binding projection and receipt-validation capabilities. Without
`--write-plan`, receipt projection leaves the plan unchanged.

## Read-Only Workflow

1. Resolve the git root.
2. Run each native source doctor and path command. Inspect only explicit legacy
   import locations and current Synesthesia notes when migration evidence is
   needed; do not open a current persistent adapter for ordinary reads.
3. Classify each source as `migrated`, `legacy-only`, `current`, `legacy-path`, `notes-only`, `missing`, or `invalid`.
4. Retain source-doctor record counts, repair
   receipts, invalid line spans, and exit status.
5. If any required source is `legacy-only` or `invalid`, or Synesthesia is
   `notes-only` and import is requested, report the exact owning migration or
   blocking command before any harvest or append recommendation. Never convert
   an invalid learnings store with skip unless `$learnings` has established
   that authority.
6. Report harvest candidates and recommended source-specific commands.

See [source-store-layout.md](references/source-store-layout.md), [migration-workflow.md](references/migration-workflow.md), and [harvest-workflow.md](references/harvest-workflow.md).

## Output Shape

```md
## Ledger status

- learnings: migrated | legacy-only | missing | invalid
- negative-ledger: current | legacy-path | missing | invalid
- synesthesia: notes-only | ledger-present | missing | invalid

## Harvest candidates

- learnings:
- negative-ledger:
- synesthesia:

## Recommended actions

1. ...

## Proof

- commands run:
- source stores read:
- writes attempted:
- memory-note admissions:
```

## Guardrails

- Bootstrap once before the first Ledger command in a workflow; do not repeat
  it per skill or per command.
- After readiness, invoke `ledger` directly and let the CLI own compatibility,
  integrity, and failures.
- Do not install without current installation authority.
- Do not install during an open actuation generation.
- Do not mutate a source store except through its owning CLI.
- Do not treat memory-source notes as the canonical store.
- Do not persist checkpoint receipts or turn Ledger into a semantic source
  decision engine without evidence that the stateless protocol is insufficient.
- For `artifact-kernel-v1`, do not run source-memory processing before closure
  or make its outcome a code-closure prerequisite.
- Do not reuse a checkpoint receipt after its subject or evidence fingerprint
  changes.
- Do not admit every source-store event to memory.
- Do not block a route from Negative Ledger memory without current ledger verification.
- Do not turn Synesthesia decorative language into memory.
- Do not migrate, compact, hand-edit, or harvest actuation events as source
  memory; use the actuation source's `state` and transition commands.
- Do not invent Universalist plan ids, write a replacement latest pointer, or
  reuse an existing plan path; use the Universalist source commands.
- Do not route stateless validation through `--source`; sources own state, while
  `validate` is a pure observation.
