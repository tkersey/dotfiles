---
name: retrace
description: "Reconstruct and experimentally challenge decisions from prior Codex sessions. Use for `$retrace`, historical decision replay, counterfactual forks, alternative-route challenges, hindsight-separated retrospectives, workflow-governance audits, skill decision attribution, or 'why did that session choose this?'. `$seq` owns deterministic history and source-governance evidence; `$cas` owns safe thread/rollout replay and FIR lifecycle; `$retrace` owns bounded experiments and DRR synthesis. Never present fork output as the source model's hidden chain of thought."
metadata:
  version: "1.3.0"
  activation_cost: high
  default_depth: standard
---
# Retrace

## Mission
Use a historical Codex session as an experimental branch point.
```text
$seq      freezes visible historical evidence
$cas      creates controlled historical-context replays
$retrace  compares bounded witnesses and synthesizes conclusions
```
Determine:
```text
what was historically explicit
what the visible trace supports
whether the claimed workflow really governed the source
whether the route is stable under replay
which alternative is strongest
which fact flips the route
what hindsight changes
what remains unknowable
```
A replay is a new model execution, not access to the source model's private chain of thought.

## Evidence classes
Keep separate:
```text
historically_explicit
trace_inferred
fork_consistent
counterfactual_stable
outcome_informed
unsupported
unknown
```
Allowed:
```text
The source explicitly said...
Two pre-decision replays selected...
The route flipped when evidence E was withheld...
```
Forbidden:
```text
The original model secretly thought...
The replay recovered the original chain of thought...
```
See [epistemic-boundary.md](references/epistemic-boundary.md).

## Ownership
### `$seq`
Owns:
- source session/rollout identity;
- bounded source-governance observations;
- bounded decision-candidate observations;
- turn ordering and temporal anchors;
- explicit rationale/routes;
- artifact-state reconstructability;
- contamination and limitations.

Seq returns observations and provenance. It does not author or validate Retrace
artifacts.

### `$ledger`

Owns passive-definition compilation, structural validation, canonicalization,
and identity derivation for SGG-v1, DCP-v2, RIP-v1, and DRR-v1. A pass grants
neither replay authority nor a Retrace verdict.

### `$cas`
Owns:
- app-server compatibility;
- source verification;
- `thread_fork` or `rollout_transcript` lineage;
- rollback or retained-transcript anchoring;
- read-only/no-network policy;
- turn lifecycle;
- FIR persistence;
- cleanup.
Artifact:
```text
fork_inquiry_receipt / FIR-v1
```
### `$retrace`
Owns:
- source-governance decision;
- SGG-v1 and DCP-v2 authorship and meaning;
- inquiry objective and lanes;
- question framing;
- experiment staging and budgets;
- comparison and adjudication;
- final reconstruction.
Artifacts:
```text
source_governance_gate / SGG-v1
decision_context_packet / DCP-v2
retrace_inquiry_plan / RIP-v1
decision_reconstruction_record / DRR-v1
```

Canonical passive definitions live under `definitions/`; the reference pages
state interpretation laws and do not duplicate the machine schemas.

## Modes
```text
explain        contemporaneous rationale reconstruction
replay         pre-decision independent route selection
challenge      strongest supported non-selected route
retrospective  outcome-aware learning
compare        staged baseline/intervention experiment
audit          validate source and artifacts without replay
```

## Staged experiment policy
Do not begin with a large fork portfolio.
### Stage 0 — source governance
Prove the claimed workflow governed the source.
### Stage 1 — replay positive control
Run one outcome-blind lane and require one valid FIR.
### Stage 2 — minimal A/B
Run:
```text
historical-context baseline
policy/instruction intervention
```
### Stage 3 — conditional expansion
Only when Stage 2 yields a material difference or unresolved ambiguity:
```text
strongest-alternative challenge
one evidence/instruction ablation
one outcome-aware retrospective
```
Default maximum:
```text
4 forks
1 turn per fork
read-only
ephemeral
network off
```

## Inputs
Resolve source, question, claimed workflow/skill, mode, lane portfolio, model policy, workspace policy, budgets, and persistence.
Defaults:
```text
mode = compare
workspace = transcript_only unless exact reconstruction is needed
permissions = read-only, network-off
persistence = receipts
```

## Workflow
### 0. Source-governance gate
Run this phase when:
- a workflow-specific audit selected the source;
- the question asks whether a workflow/skill governed the decision;
- an intervention will apply a current workflow contract;
- source inclusion depends on a workflow-specific observation.
Obtain the exact session-level row, not only aggregate counts.
For controller-backed review-closure workflows:
```bash
seq observe \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/seq/source-governance.json" \
  --root ~/.codex/sessions \
  --repo <repo> \
  --since <time> \
  --until <time> \
  --param "workflow=<workflow>" \
  --projection events \
  --format json

seq observe \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/seq/source-governance.json" \
  --root ~/.codex/sessions \
  --repo <repo> \
  --since <time> \
  --until <time> \
  --param "workflow=<workflow>" \
  --projection tools \
  --format json
```
Set `--until` before the current audit when current-session contamination would
change inclusion. Select the exact session evidence and preserve:
```text
true workflow signal
required
entered
closed
closure compression
```
Classify workflow provenance:
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
ambiguous
absent
```
Classify closure provenance separately:
```text
controller_close
controller_receipt
campaign_bound_terminal
generic_delivery_closure
tool_success_only
ambiguous
absent
```
Create `SGG-v1`.

Validate the authored gate structurally:

```bash
ledger validate \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/ledger/source-governance-gate.json" \
  --input gate=source-governance-gate.json \
  --format json
```

Verdicts:
```text
authoritative
  controller-grade governance evidence; replay allowed
declared_uncontrolled
  explicit workflow declaration but controller governance unproven;
  replay allowed with limitation
incidental
  artifact/path/history mention only; stop before replay
ambiguous
  deterministic investigation only
absent
  stop before replay
```
A filename such as `.step/review-workflow-plan.jsonl` is not a workflow activation.
A generic merge/land/complete signal is not controller closure.
See [source-governance.md](references/source-governance.md).
### 1. Find the decision
Use Retrace's candidate observation first:

```bash
seq observe \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/seq/decision-candidates.json" \
  --root ~/.codex/sessions \
  --repo <repo> \
  --since <time> \
  --until <time> \
  --projection rows \
  --format json
```

Then freeze the selected session's ordered source evidence:

```bash
seq observe \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/seq/decision-capsule.json" \
  --session-id <id> \
  --projection events \
  --format json
```

Locate the visible route decision and bind its exact one-based turn index while
authoring DCP-v2. Seq does not choose the decision episode or author the packet.
Do not let replay models select the historical source episode.
### 2. Bind DCP-v2
The capsule must distinguish:
```text
pre_decision
post_decision_pre_outcome
outcome_aware
```
Outcome blindness must be structural.
Do not use a full-history replay plus an instruction to ignore later outcomes.

Materialize the content identity from a null `packet_id`, or verify an existing
claimed identity:

```bash
ledger materialize \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/ledger/decision-context-packet.json" \
  --input packet=decision-context-packet.json \
  --format json
```

Consume the returned canonical packet and `DCP-…` identity. A validation or
materialization pass establishes structure only.
See [decision-capsule.md](references/decision-capsule.md).
### 3. Select lineage and workspace mode
CAS supports two lineage modes.
#### `thread_fork`
Use when source thread identity is available.
```text
thread/fork
-> exact rollback
-> retained-anchor verification
```
Workspace may be exact, head-only, or transcript-only according to DCP evidence.
#### `rollout_transcript`
Use when the DCP has a verified rollout path but no source thread ID.
```text
verify source rollout digest
-> verify retained anchor digest
-> fresh thread/start
-> bounded transcript-context turn/start
```
Requirements:
```text
workspace_policy = transcript_only
no current-checkout tools
no live historical workspace claim
lineage_mode recorded in FIR
```
Rollout transcript replay is structurally anchored transcript replay, not live thread forking or workspace reconstruction.
See [workspace-reconstruction.md](references/workspace-reconstruction.md).
### 4. Capability requirements

Require:
```text
Seq observation ABI and all three Retrace observation definitions
Ledger artifact ABI and all four Retrace artifact definitions
cas session_inquiry and FIR support
at least one supported lineage mode
read-only inquiry
no-network policy
receipt persistence
```
When only deterministic analysis is available, fork-based claims are forbidden.
### 5. Compile RIP-v1
Use different lane contracts; do not manufacture consensus through repeated leading prompts.

Validate the exact plan CAS will consume:

```bash
ledger validate \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/ledger/retrace-inquiry-plan.json" \
  --input plan=plan.json \
  --format json
```

See [inquiry-lanes.md](references/inquiry-lanes.md).
### 6. Run CAS
```bash
cas session_inquiry run \
  --capsule capsule.json \
  --plan plan.json \
  --receipt-dir .ledger/retrace/<inquiry-id> \
  --json
```
CAS must prove source lineage, retained anchor, model/provider, permission policy, workspace mode, turn state, and cleanup.
Detached lifecycle remains available through `start`, `status`, `wait`, `interrupt`, and `cleanup`.
### 7. Consume FIR-v1

Only complete, source-bound FIRs contribute to:
```text
route distribution
consensus
stability
instruction effect
```
For rollout transcript receipts require:
```text
lineage_mode = rollout_transcript
workspace_reconstruction.mode = transcript_only
verified source and anchor digests
```
See [fork-inquiry.md](references/fork-inquiry.md).
### 8. Adjudicate
Use `decision_interrogation_adjudicator` when:
```text
source governance is declared_uncontrolled
forks disagree
hindsight leakage is plausible
lineage/workspace/model differs
skill effect is material
route stability will drive tuning or doctrine
```
The adjudicator is read-only.
### 9. Synthesize DRR-v1
DRR must preserve:
```text
source-governance verdict
historical explicit facts
trace inference
valid/invalid receipts
baseline/intervention routes
strongest alternative
route-flip conditions
hindsight lessons
skill/instruction effects
contradictions
limitations
confidence
```
Consensus is never historical fact.

Validate the authored record:

```bash
ledger validate \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/retrace/definitions/ledger/decision-reconstruction-record.json" \
  --input record=decision-reconstruction-record.json \
  --format json
```

See [synthesis.md](references/synthesis.md).

## Inquiry contracts
```text
rationale:
  post-decision/pre-outcome; reconstruct visible support and assumptions
counterfactual:
  pre-decision; choose independently without predicting history
alternative challenge:
  pre-decision; strongest evidence-consistent non-historical route
evidence ablation:
  pre-decision; withhold/change one named item and re-decide
retrospective:
  outcome-aware; label every lesson as hindsight-informed
```

## Skill/workflow effect
Ask:
```text
Did the source actually contain the skill/workflow?
Was governance authoritative, declared, incidental, or absent?
Did baseline and intervention choose different routes?
Did controlled ablation change the route?
Did the source explicitly attribute the decision?
```
Strongest evidence:
```text
historical explicit attribution
+ authoritative source governance
+ exact pre-decision anchor
+ controlled intervention/ablation
+ route change
```
Fork self-report alone is weak.
DRR may inform `$tune`; it does not authorize edits.

## Security, persistence, and failure
Defaults:
```text
ephemeral
read-only
network disabled
approvals denied
dynamic tools denied
one bounded turn
bounded excerpts and refs
```
Do not use `thread/shellCommand`.
Do not persist private reasoning.
Use `.ledger/retrace/<inquiry-id>/` only when receipts are required, and local-exclude it by default.
A blocked replay does not erase deterministic source evidence.

## Output
Report:
```text
source / decision / question
source-governance provenance and verdict
lineage and workspace mode
historical explicit / trace-inferred evidence
valid and invalid FIRs
baseline/intervention route distribution
strongest alternative and flip conditions
hindsight-separated lessons
skill/workflow effect
confidence and unsupported claims
cleanup and CLI gaps
```

## Hard rules
- `$seq` owns history and workflow provenance.
- `$cas` owns replay lifecycle.
- `$retrace` owns experiments and synthesis.
- Prove workflow governance before workflow-specific replay.
- Artifact/path mentions are not activations.
- Generic delivery completion is not controller closure.
- Fork output is not hidden historical chain of thought.
- No outcome-blind claim without exact structural anchoring.
- No historical workspace claim from the current checkout.
- No causal skill claim from self-report or consensus alone.
- Hindsight stays separate.
- Default read-only, ephemeral, network-off, bounded.
- No mutation, commit, push, approval escalation, or uncontrolled fanout.
- Preserve uncertainty.
