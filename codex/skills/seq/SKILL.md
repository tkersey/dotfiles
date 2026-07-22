---
name: seq
description: "Mine Codex session JSONL and memory artifacts with the Zig `seq` CLI. Use for explicit `$seq`, artifact/session/tool/memory/plan forensics, Hylo CRF extraction and governed HCTP source selection, skill activation and outcome audits, decision provenance, `$tune` evidence, `$retrace` source capsules, review-compiler provenance, watched-session deltas, worker attribution, or reproducible historical reports. Prefer the narrowest lifted command and preserve denominators, provenance, contamination, and uncertainty."
metadata:
  version: "1.2.1"
---
# seq

## Mission
Use deterministic local session and memory evidence to answer:
```text
what happened
where it happened
what evidence supports it
what remains unknown
```
For skill/workflow analysis distinguish:
```text
presence
decision influence
downstream outcome
workflow governance
```
These are not interchangeable.

## Source boundary
Primary local sources:
```text
~/.codex/sessions
~/.codex/memories
```
`seq` is local-corpus forensics, not product-wide telemetry.
State the denominator and exclusion policy before counts.

## Capability-first rule

For current or post-change audits, run:
```bash
seq --version
seq capabilities --format json
<target-command> --help
```
Use the installed lifted surface as source of truth.
Do not recreate a newer native classifier with broad transcript searches when the installed binary is old.

For session JSONL forensics, require:
```text
streaming_session_scanner_v1
```
This capability means aggregate session or corpus size is not a scanner limit;
the shared scanner retains one protocol record at a time and each command owns
its semantic fold. The per-record fail-closed guard remains separate. If the
capability is absent, upgrade Seq rather than substituting broad `jq`, `rg`, or
ad hoc whole-file scans. A genuinely bounded native query is acceptable only
when that narrower denominator fully answers the question.

## Hylo CRF/HCTP product surface

`seq hylo-extract` and `seq hctp-source` are admitted macOS product commands.
Portable trial validation belongs to Ledger and must not fail merely because
these Seq commands are unavailable. On an admitted macOS build, require the
exact `seq_capabilities.features` keys needed by the selected route:

```text
hylo_extract_v1
hctp_source_selection_v1
hctp_source_route_admission_v1
hctp_independence_clusters_v1
hctp_sealed_case_v1
hctp_materializer_v1
hctp_source_materialization_v1
hctp_source_selection_opening_fd_v1
hctp_historical_profile_v1
hctp_case_blind_source_profile_fd_v1
```

Use `hylo_extract_v1` for CRF extraction. Use
`hctp_source_selection_v1`, `hctp_source_route_admission_v1`, and
`hctp_independence_clusters_v1` for governed source compilation and validation.
Case-blind execution additionally requires `hctp_sealed_case_v1`,
`hctp_materializer_v1`, `hctp_source_materialization_v1`, and
`hctp_source_selection_opening_fd_v1`. Historical case-blind delivery also
requires `hctp_historical_profile_v1` and
`hctp_case_blind_source_profile_fd_v1`. These are exact emitted keys; do not
infer them from command presence. On non-macOS builds, the product commands and
their feature keys are absent.

### Source compile and trial validation order

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure` once. Reuse that readiness for the remaining Ledger
commands.

Compile source selection before constructing the trial, but validate the
receipt against the completed trial only after campaign admission and trial
construction:

```text
seq hctp-source compile
-> admit campaign, target bundles, and complete scenario manifest
-> ledger --source hylo compile-trial (or construct the validator-backed trial)
-> ledger --source hylo validate-trial
-> seq hctp-source validate
-> ledger --source hylo register-trial with private custody
```

Representative commands, with sensitive descriptors supplied by an admitted
caller or custodian, are:

```bash
seq hctp-source compile \
  --manifest source.json \
  --output selection.json \
  --source-signing-seed-fd <protected-source-seed-fd>

ledger --source hylo validate-trial --repo <repo> --trial trial.json
seq hctp-source validate --receipt selection.json --trial trial.json
ledger --source hylo register-trial \
  --repo <repo> \
  --trial trial.json \
  --custody-input-fd <custodian-registration-source-fd>
```

`hctp-source compile` derives each required
`hylo-source-route-admission/v1` from the CRF episode and source profile, then
binds it into the selection core covered by the source-owner attestation in
`hylo-source-selection-receipt/v1`; callers do not supply or relabel that
projection. A direct profile is comparison-eligible only when the CRF episode
has `fidelity.replay_eligible:true`. Otherwise its route is `diagnostic_only`.
A governed `historical_decision` profile may independently admit
`historical_replay`, while retaining the CRF reconstruction ceiling and
limitations. For `practice_repair` and `promotion`, historical governance must
be authoritative at the effective Ledger/CAS gate.

For `hylo-trial/v2`, the exact signed receipt is a private compiler/custody
input. The public trial carries only its normalized
`artifact:sha256:<64 lowercase hex>` reference, matching fingerprint, and
salted commitment; it never preserves the caller's local receipt path.
`hctp-source validate` joins the external receipt to those public
bindings and the completed unit/scenario/source projections; registration then
requires the compiler-produced `hylo-trial-custody/v1` through a protected FD.
The public trial and event store never embed the full receipt or its sealed-case
locator.

For v2, each public `units[*].source_profile` is the exact native safe
projection. `hctp-source validate` rejects unknown or semantic extra keys while
joining the projection to the signed source receipt. A full historical profile
body, source target text, rationale, rejected routes, and hidden references do
not enter the public trial.

For case-blind materialization, deliver visible input through
`--visible-output-fd` and the historical profile, when required, through
`--source-profile-output-fd`. Both are protected anonymous directional pipes
supplied under the admitted receiver's custody. The CLIs verify descriptor
shape and direction, not peer-process identity. Never replace them with regular
files, argv, environment variables, or normal stdout. Receipt output contains
commitments and fingerprints, not plaintext hidden references or source-profile
bodies.

For `hylo-trial/v2`, Seq also requires the exact private
`hylo-source-selection-opening/v1` on
`--source-selection-opening-fd`. The custodian projects only
`custody.source_selection` onto that protected pipe; the full
`hylo-trial-custody/v1` is not a Seq input. Seq validates the whole opening
commitment against the public trial, then validates and joins its nested exact
signed source receipt before releasing case material. A v2 trial rejects an
embedded full receipt or a missing opening FD; v1 retains its embedded receipt
carrier and rejects the v2-only FD.

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

Add `--source-profile-output-fd <runner-source-profile-sink-fd>` only for a
historical lane whose preflight projection freezes FD delivery. Connect that
protected output directly to `cas trial run --source-profile-fd`; it is not an
input to standalone `compile-replay` or a controller-visible intermediate.

Seq source materialization and Ledger treatment materialization are distinct.
Seq releases one visible case and, when required, one historical source profile.
Ledger later releases the selected treatment under the retained lane lease via
`ledger --source hylo lane-materialization`; CAS receives that claim through
its separate `--materialization-fd`.

## Routing ladder
### Skill decisions and tuning
```text
skill-decision-audit
skill-evidence
skill-success-rank
skill-audit
skill-cohort
workflow-audit
workflow-overlap
```
### Historical decisions and replay
```text
decision-capsule
historical_decisions dataset
turns
session-detail
artifact-search
```
### Review/workflow audits
```text
review-compiler-audit
adjudication-audit
goal-audit
routing-gap
```
### Session/artifact forensics
```text
artifact-search
plan-search
find-session
session-prompts
sessions
turns
session-detail
tail
```
### Tools and orchestration
```text
tool-lifecycle
tool-audit
tool-search
session-tooling
session-graph
orchestration-concurrency
```
### Memory
```text
memory-inventory
memory-provenance
memory-map
memory-history
memory-extension-audit
```
### Generic
```text
message-search
message-audit
token-usage
token-window
token-cost
query-diagnose
query
```
Use generic `query` when no lifted surface owns the relation.
See [command-routing.md](references/command-routing.md).

## Skill-decision audit
Use when asking:
```text
How did a skill affect decisions?
Was its decision contract followed?
Was activation missed?
What should $tune change?
```
```bash
seq skill-decision-audit \
  --root ~/.codex/sessions \
  --skill <skill> \
  --skill-root codex/skills \
  --repo <repo> \
  --last 30d \
  --exclude-current \
  --mode tune-packet \
  --format json
```
Modes:
```text
summary
episodes
misses
clauses
outcomes
matched-cohort
tune-packet
delta
```
Evidence levels:
```text
structured SDR-v1 receipt
explicit assistant attribution
contract-aligned action
associated outcome
co-occurrence only
```
Do not collapse these into one “used” count.
A receipt proves attribution structure, not a good outcome.
`skill-decision-audit` uses the shared streaming scanner and retains only
activation, decision, and outcome evidence needed by its output contract.

## Skill presence
Use `skill-evidence` for one watched session and `skill-audit --mode activation` for cohorts.
Preserve:
```text
explicit user call
implicit assistant declaration
injected skill block
manual skill-file read
target-skill lens use
outcome evidence
raw mention
```
Presence does not prove influence.
`skill-evidence` uses the same scanner in a single pass for normalized messages,
skill mentions, tool reads, outcomes, and session identity.

## Decision contracts and receipts
Decision-oriented skills may carry:
```text
references/decision-contract.yaml
skill_decision_contract / SKDC-v1
```
Authority order:
1. explicit `--contract`;
2. target skill contract under `--skill-root`;
3. no clause-level judgment.
Do not invent contract semantics in the CLI.
Strongest decision attribution:
```yaml
skill_decision_receipt:
  receipt_version: SDR-v1
  decision_id:
  skill:
  skill_contract_fingerprint:
  trigger_refs: []
  clause_refs: []
  question:
  alternatives_considered: []
  selected_route:
  rejected_routes: []
  expected_outcome:
  artifact_state:
```

## Decision capsules
Use `decision-capsule` to freeze one visible decision for `$retrace`.
```bash
seq decision-capsule \
  --root ~/.codex/sessions \
  --session-id <id> \
  --turn-index <n> \
  --anchor all \
  --outcome-policy conservative \
  --format json
```
Prefer `--decision-id` when candidate normalization produced one.
When candidates are empty:
```text
inspect turns/session-detail
locate the visible route boundary
use exact one-based turn index
```
DCP owns visible historical context and structural temporal anchors.
It does not infer hidden rationale.

## Review-compiler provenance
Aggregate counts are discovery only.
Before a session-level claim:
1. select the exact `denominator.included_sessions` row;
2. preserve the row’s session ID/path/protocol/classification;
3. cite evidence for true workflow, required, entered, closed, and compression;
4. distinguish present signals from absence-derived evidence;
5. classify workflow and closure provenance;
6. only then use the row as a `$retrace` source.
For controller-backed review-closure workflows, evidence roles are:
```text
controller_invocation
controller_event
controller_state
controller_receipt
explicit_workflow_declaration
artifact_under_repair
filename_or_path_mention
historical_reference
generic_prose
```
Only controller-grade evidence proves authoritative governance.
A path containing only a workflow name is not activation.
Generic completion, merge, or land evidence is not controller closure.
When evidence is incidental, exclude the row from the true workflow denominator rather than deriving required/entered/closed state.
Use ordered lifecycle evidence when available:
```text
begin
basis
candidate
ablation
proof
permit
realization
apply
commit
push
close/abort
```
See [review-compiler-provenance.md](references/review-compiler-provenance.md).

## `$retrace` source selection
When `$retrace` investigates a workflow:
```text
aggregate audit
-> included session row
-> provenance classification
-> SGG-v1
-> DCP-v2
```
Do not select a replay source from aggregate counts or fallback transcript similarity.
Allowed source-governance states:
```text
authoritative
declared_uncontrolled
incidental
ambiguous
absent
```
Only the first two permit workflow-specific replay, with limitations preserved.
See [retrace-decision-capsules.md](references/retrace-decision-capsules.md).

## Protocol separation
Do not evaluate one protocol with another protocol’s vocabulary.
For review-closure workflow audits, distinguish:
```text
legacy-cleanroom
controller-backed
kernel-compression
mixed
none
```
Report:
```text
expected protocol
detected protocol
mismatch
```
Keep controller lifecycle evidence separate from kernel/compression/recomposition evidence.

## Churn, Git delta, and semantic surface
Never collapse:
```text
mutation churn
final Git delta
semantic surface
```
Mutation churn:
```text
patch operations
gross insertions/deletions
rewrites
```
Final Git delta:
```text
base/head
path classes
production/test/docs/generated/config
```
Semantic surface:
```text
metric name/version/unit
dimensions
baseline/head
value
```
Unknown units must be labeled `UNIT_UNRESOLVED`.

## Corpus reproducibility
For comparative audits preserve:
```text
sessions root
seq version
scanner/index version
candidate files
files opened
session-id/path digest
time window
worker inclusion
current-session exclusion
```
A fixed time window is not an immutable corpus snapshot.

## Worker attribution
Use linked workers only when requested or when the relevant decision occurred there.
Preserve:
```text
root session
worker session
parent edge
lane/receipt ID
declared skills
decision receipt
outcome
```
Do not merge unlinked worker sessions into the root denominator.

## Causality discipline
Report:
```text
explicit decision delta
contract-consistent but causality unproven
associated outcome only
co-occurrence only
```
Matched cohorts are observational.
Fork/retrace evidence is experimental but remains separate from historical source fact.

## Privacy and contamination
Default to sanitized refs and bounded excerpts.
Detect:
```text
injected skill blocks
current audit prompts
generated reports
quoted transcripts
memory summaries
examples
```
A schema example inside a skill body is not a historical decision.
Private reasoning must not be exposed as report evidence.

## Current patterns
```bash
seq artifact-search --contains "<term>" --surface messages --format jsonl
seq plan-search --repo <repo> --include-body --format jsonl
seq skill-audit --skill <skill> --mode activation --last 30d --exclude-current
seq tool-lifecycle --session-id <id> --format json
seq session-detail --session-id <id> --format markdown
seq review-compiler-audit --protocol auto --repo <repo> --format json
seq decision-capsule --session-id <id> --mode candidates --format table
```

## Hard rules
- Use the narrowest lifted command.
- Prove the installed CLI surface first for post-change questions.
- Require `streaming_session_scanner_v1` for session JSONL forensics; do not fall back to broad whole-file scans when it is absent.
- State denominators and exclusions.
- Preserve protocol and evidence provenance.
- Aggregate counts do not authorize session-level claims.
- Artifact/path mentions are not workflow activations.
- Generic delivery completion is not controller closure.
- Presence is not influence.
- Outcome association is not causality.
- Historical source fact is not replay consensus.
- Use generic query only for relations not owned by lifted commands.
- Report unresolved units, identities, and evidence gaps honestly.
