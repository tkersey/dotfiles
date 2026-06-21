---
name: retrace
description: "Reconstruct and experimentally challenge decisions from prior Codex sessions. Use for `$retrace`, 'why did that session choose this?', historical decision replay, counterfactual forks, alternative-route challenges, hindsight-separated retrospectives, skill decision attribution, or session interrogation. `$seq` freezes the source episode; `$cas` owns ephemeral read-only fork/rollback/turn lifecycle; `$retrace` compares receipts and emits a bounded decision reconstruction. Never present fork output as the original model's hidden chain of thought."
metadata:
  version: "1.0.0"
  activation_cost: high
  default_depth: standard
---

# Retrace

## Mission

Use a historical Codex session as an experimental branch point.

```text
$seq      freezes visible historical evidence
$cas      creates controlled historical-context forks
$retrace  asks bounded questions and synthesizes conclusions
```

Determine:

```text
what was historically explicit
what the visible trace supports
whether the route is stable under replay
which alternative is strongest
which fact flips the route
what hindsight changes
what remains unknowable
```

A fork is a new model execution, not access to the source model's private chain of thought.

## Evidence classes

Keep these separate:

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
Two of three pre-decision replays selected...
The route flipped when evidence E was withheld...
```

Forbidden:

```text
The original model secretly thought...
The fork recovered the original chain of thought...
```

See [epistemic-boundary.md](references/epistemic-boundary.md).

## Ownership

### `$seq`

Owns deterministic source evidence and emits:

```text
decision_context_packet / DCP-v1
```

It identifies the source decision, explicit rationale, selected/rejected routes, artifact state, turn ordering, temporal anchors, contamination, and limitations.

### `$cas`

Owns model-runtime lifecycle and emits:

```text
fork_inquiry_receipt / FIR-v1
```

It forks, rolls back to the exact horizon, applies read-only permissions, starts/waits/interrupts turns, records events, and cleans up.

### `$retrace`

Owns the inquiry portfolio and emits:

```text
decision_reconstruction_record / DRR-v1
```

It compares historical evidence, fork witnesses, counterfactual routes, hindsight, contradictions, and confidence.

## Modes

```text
explain        post-decision/pre-outcome rationale reconstruction
replay         pre-decision independent route selection
challenge      strongest supported non-selected route
retrospective  outcome-aware learning
compare        bounded multi-lane experiment
audit          validate existing artifacts without forks
```

Default `compare` portfolio:

```text
1 rationale witness
2 pre-decision replays
1 alternative challenger
0 hindsight fork unless requested or useful
```

Default bounds:

```text
maximum 4 forks
maximum 1 turn per fork
read-only
ephemeral
network off
```

## Inputs

Resolve source session/rollout/decision, question, mode, lane portfolio, model policy, workspace policy, fork/token/timeout budgets, and persistence.

Defaults:

```text
mode = compare
workspace = exact when reconstructable, otherwise transcript-only
max forks = 4
turns per fork = 1
permissions = read-only, network-off
persistence = receipts
```

Use explicit model and workspace overrides only when the experiment requires them.

## Workflow

### 1. Find the decision

Use the narrowest `$seq` evidence first:

```text
skill-decision-audit
session-prompts
turns
session-detail
artifact-search
```

Then produce:

```bash
seq decision-capsule \
  --session-id <id> \
  --decision-id <id> \
  --anchor all \
  --format json
```

Do not let model forks select the source episode.

### 2. Validate the source capsule

```bash
python3 codex/skills/retrace/tools/dcp_gate.py capsule.json
```

DCP must distinguish:

```text
pre-decision
post-decision/pre-outcome
outcome-aware
```

Outcome-blind replay is unavailable when exact truncation cannot be proven.

Never fork full history and merely prompt the model to ignore later outcomes.

See [decision-capsule.md](references/decision-capsule.md).

### 3. Classify workspace reconstruction

```text
exact            historical head + dirty/generated/dependency state
head_only        historical commit only
transcript_only  no repository tools
unavailable
```

Never point a historical fork at today's checkout and call it historical context.

Prefer transcript-only unless code inspection is necessary.

See [workspace-reconstruction.md](references/workspace-reconstruction.md).

### 4. Preflight native support

```bash
python3 codex/skills/retrace/tools/retrace_preflight.py
```

Required:

```text
seq decision-capsule
cas session_inquiry
thread/fork
exact rollback/prefix anchoring
turn/start and interrupt
ephemeral read-only forks
receipt persistence
```

If unavailable:

```text
deterministic source analysis remains allowed
fork-based claims are forbidden
```

Use the included CLI specifications as the implementation owner.

### 5. Compile an inquiry plan

Create `retrace_inquiry_plan / RIP-v1`:

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

Use distinct lane questions; do not manufacture consensus through identical leading prompts.

See [inquiry-lanes.md](references/inquiry-lanes.md).

### 6. Run CAS forks

```bash
cas session_inquiry run \
  --capsule capsule.json \
  --plan plan.json \
  --receipt-dir .retrace/<inquiry-id> \
  --json
```

Detached lifecycle:

```bash
cas session_inquiry start ...
cas session_inquiry status --inquiry-id <id> --json
cas session_inquiry wait --inquiry-id <id> --json
cas session_inquiry interrupt --inquiry-id <id> --json
cas session_inquiry cleanup --inquiry-id <id> --confirm --json
```

CAS must prove source/fork lineage, anchor, model/provider, permissions, workspace, turn IDs, terminal state, and cleanup.

### 7. Validate receipts

```bash
python3 codex/skills/retrace/tools/fir_gate.py receipt.json
```

Only valid FIRs contribute to route distributions or consensus.

See [fork-inquiry.md](references/fork-inquiry.md).

### 8. Adjudicate when necessary

Use `decision_interrogation_adjudicator` when:

```text
forks disagree
hindsight leakage is plausible
model/workspace state differs
skill effect is material
route stability will drive doctrine or tuning
```

The adjudicator is read-only.

### 9. Synthesize DRR-v1

```bash
python3 codex/skills/retrace/tools/drr_gate.py reconstruction.json
```

DRR must preserve:

```text
historical facts
trace inference
fork rationale consensus
pre-decision route distribution
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
  post-decision/pre-outcome; reconstruct visible evidence, assumptions,
  alternatives, and route-flip conditions

counterfactual:
  pre-decision; choose independently without predicting history

alternative challenge:
  pre-decision; strongest evidence-consistent non-historical route and falsifier

evidence ablation:
  pre-decision; withhold or change one named evidence item and re-decide

retrospective:
  outcome-aware; label every lesson as hindsight-informed
```

Do not claim an alternative was historically considered unless the source proves it.

## Skill-effect analysis

Ask:

```text
Was the skill present?
Was it explicitly cited?
Did a pre-decision replay select another route?
Did controlled instruction/evidence ablation change the route?
Did the source explicitly attribute the decision?
```

Strongest evidence:

```text
historical explicit attribution
+ exact pre-decision context
+ controlled ablation
+ route change
```

Fork self-report alone is weak.

DRR evidence may inform `$tune`; it does not authorize edits.

## Security and privacy

Default:

```text
ephemeral forks
read-only permission profile
network disabled
approval requests denied
dynamic tools denied
one bounded turn
no current-checkout access without exact reconstruction
bounded excerpts and refs
```

Do not use `thread/shellCommand`.

Do not persist private reasoning.

See [security-and-budget.md](references/security-and-budget.md).

## Persistence and failure

When required, use:

```text
.retrace/<inquiry-id>/
  capsule.json
  plan.json
  forks/*.json
  events/*.jsonl
  adjudication.yaml
  reconstruction.json
```

Local-exclude by default. Do not version model outputs without explicit intent.

Fail deterministically on source/decision/anchor ambiguity, unavailable exact anchoring, workspace mismatch, unsupported fork/rollback/permissions, model unavailability, timeout/interruption, invalid receipt, hindsight contamination, cleanup failure, or exhausted budget.

A blocked fork does not erase deterministic source evidence.

## Output

Report source/decision/question, modes and horizons, workspace/model policy, historical explicit and trace-inferred evidence, valid/invalid fork receipts, route distribution, strongest alternative, route-flip conditions, contradictions, hindsight lessons, reconstruction, skill effect, confidence, unsupported claims, cleanup, and CLI gaps.

## Hard rules

- `$seq` owns history; `$cas` owns forks; `$retrace` owns synthesis.
- Fork output is not hidden historical chain of thought.
- No outcome-blind claim without exact temporal anchoring.
- No historical workspace claim from the current checkout.
- No causal skill claim from self-report or consensus alone.
- Hindsight stays separate.
- Default read-only, ephemeral, network-off, bounded.
- No mutation, commit, push, approval escalation, or uncontrolled fanout.
- Preserve uncertainty.
