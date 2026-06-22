---
name: retrace
description: "Reconstruct and experimentally challenge decisions from prior Codex sessions. Use for `$retrace`, historical decision replay, counterfactual forks, alternative-route challenges, hindsight-separated retrospectives, workflow-governance audits, skill decision attribution, or 'why did that session choose this?'. `$seq` owns deterministic history and source-governance evidence; `$cas` owns safe thread/rollout replay and FIR lifecycle; `$retrace` owns bounded experiments and DRR synthesis. Never present fork output as the source model's hidden chain of thought."
metadata:
  version: "1.2.0"
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
- included-run and workflow-provenance evidence;
- decision candidates;
- turn ordering and temporal anchors;
- explicit rationale/routes;
- artifact-state reconstructability;
- contamination and limitations.
Artifacts:
```text
source_governance_gate / SGG-v1
decision_context_packet / DCP-v2
```
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
- inquiry objective and lanes;
- question framing;
- experiment staging and budgets;
- comparison and adjudication;
- final reconstruction.
Artifacts:
```text
retrace_inquiry_plan / RIP-v1
decision_reconstruction_record / DRR-v1
```

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
- source inclusion depends on classifier output such as `review-compiler-audit`.
Obtain the exact session-level row, not only aggregate counts.
For `$resolve`/C3:
```bash
seq review-compiler-audit \
  --root ~/.codex/sessions \
  --protocol c3-mrpc \
  --repo <repo> \
  --since <time> \
  --until <time> \
  --exclude-current \
  --format json
```
Select the exact `denominator.included_sessions` row and preserve evidence for:
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
Create `SGG-v1` and validate:
```bash
python3 codex/skills/retrace/tools/source_governance_gate.py governance.json
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
A filename such as `.step/resolve-c3-st-plan.jsonl` is not a C3 activation.
A generic merge/land/complete signal is not a C3 close.
See [source-governance.md](references/source-governance.md).
### 1. Find the decision
Use the narrowest `$seq` surface:
```text
skill-decision-audit
decision-capsule --mode candidates
turns
session-detail
artifact-search
```
When automatic candidates are absent, locate the visible route decision and use an exact one-based `--turn-index`.
```bash
seq decision-capsule \
  --session-id <id> \
  --turn-index <n> \
  --anchor all \
  --outcome-policy conservative \
  --format json
```
Do not let replay models select the historical source episode.
### 2. Validate DCP-v2
```bash
python3 codex/skills/retrace/tools/dcp_gate.py capsule.json
```
The capsule must distinguish:
```text
pre_decision
post_decision_pre_outcome
outcome_aware
```
Outcome blindness must be structural.
Do not use a full-history replay plus an instruction to ignore later outcomes.
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
### 4. Preflight
```bash
python3 codex/skills/retrace/tools/retrace_preflight.py
```
Require:
```text
seq decision-capsule and DCP validation
cas session_inquiry and FIR support
at least one supported lineage mode
read-only inquiry
no-network policy
receipt persistence
```
When only deterministic analysis is available, fork-based claims are forbidden.
### 5. Compile RIP-v1
```yaml
retrace_inquiry_plan:
  plan_version: RIP-v1
  inquiry_id:
  source_capsule:
  objective:
  lanes:
    - lane_id:
      temporal_horizon:
      inquiry_mode:
      fork_count:
      prompt_template:
      evidence_allowed: []
      evidence_withheld: []
  model_policy:
  workspace_policy:
  permission_policy:
  budgets:
  cleanup:
```
Validate:
```bash
python3 codex/skills/retrace/tools/rip_gate.py plan.json
```
Use different lane contracts; do not manufacture consensus through repeated leading prompts.
See [inquiry-lanes.md](references/inquiry-lanes.md).
### 6. Run CAS
```bash
cas session_inquiry run \
  --capsule capsule.json \
  --plan plan.json \
  --receipt-dir .retrace/<inquiry-id> \
  --json
```
CAS must prove source lineage, retained anchor, model/provider, permission policy, workspace mode, turn state, and cleanup.
Detached lifecycle remains available through `start`, `status`, `wait`, `interrupt`, and `cleanup`.
### 7. Validate FIR-v1
```bash
python3 codex/skills/retrace/tools/fir_gate.py receipt.json
```
Only valid FIRs contribute to:
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
```bash
python3 codex/skills/retrace/tools/drr_gate.py reconstruction.json
```
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
Use `.retrace/<inquiry-id>/` only when receipts are required, and local-exclude it by default.
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
