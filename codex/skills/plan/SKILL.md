---
name: plan
description: "Compile accepted intent into an observable, proof-carrying Execution Policy Graph (EPG-v1). Use for `$plan`, implementation strategy, plan refinement, spec-to-execution lowering, adaptive experiment plans, stabilization plans, or preparing material work for `$st`/`$actuating`. The output is a source-bound policy over belief state, observations, guarded actions, safety constraints, progress potential, and terminal states—not a speculative full task list. Never mutate repository files."
metadata:
  version: "4.0.0"
  activation_cost: medium
  default_depth: balanced
---

# Plan

## Mission

`$plan` compiles strategy, not a frozen prediction of the future.

```text
authoritative intent
-> observable belief state
-> bounded guarded actions
-> evidence-conditioned policy
-> safety shield
-> progress potential
-> short commitment horizon
-> `$st` materialization
-> `$actuating` closed-loop execution
```

The authoritative artifact is:

```text
execution_policy_graph / EPG-v1
```

A plan is ready when every materially reachable state has a lawful next move:

```text
act
observe
block
rollback
return to authority
or terminate successfully
```

It is not ready merely because a document stopped changing.

## Authority boundary

```text
$grill-me
  resolves user judgment

$spec-pipeline
  owns goal, must/must-not behavior, scope, non-goals, architecture,
  compatibility, authority, proof bar, and terminal predicates

$plan
  compiles the execution policy over accepted semantics

$st
  stores durable work truth and materializes the current commitment horizon

$actuating
  interprets one policy tick at a time under GCR and frontier control

$fixed-point-driver
  realizes one selected bounded mutation action
```

When planning discovers a material semantic gap:

```text
return_to_spec
or
return_to_grill
```

Do not silently redesign accepted semantics.

## Source modes

Choose exactly one:

```text
spec_handoff
  governed SGR/spec input; semantic decisions are locked

direct_brief
  explicit user brief without governed spec; research first and record defaults

existing_policy_revision
  revision of a prior EPG; require parent ID/digest and computed delta
```

`spec_handoff` is the default when `$spec-pipeline` has passed its gate.

## System regimes

Classify the system before compiling actions:

```text
clear
  stable cause/effect; compile a precise procedure

complicated
  answer exists but requires analysis/specialist evidence

complex
  cause/effect emerges through execution; compile probes and adaptation

chaotic
  safety/observability are broken; stabilize before ordinary planning
```

See [system-regimes.md](references/system-regimes.md).

## Profiles

```text
fast
  narrow, low-risk policy; root-only audit

balanced
  default; one challenge and fresh-eyes pass

strict
  public API, migration, security, performance, compatibility, architecture;
  use `execution_policy_auditor`

campaign
  large or multi-session execution; strict audit plus durable checkpoints
```

Profiles change audit depth and projection density, not EPG semantics.

## Output contract

When emitting a plan, output exactly one `<proposed_plan>` block with these headings:

```text
# <title>
## Strategy Summary
## Source and Invariants
## Current Belief and Critical Unknowns
## Commitment Horizon
## Policy Branches
## Proof, Rollback, and Terminal States
## Policy Delta
## Execution Policy Graph
```

The final section contains exactly one fenced JSON object with `execution_policy_graph`.

The JSON is authoritative. Markdown is a human projection.

No text is allowed outside the block.

No `Iteration: N`, clean-round counters, self-declared rewrite ratios, synthetic signoff matrices, or mandatory innovation additions.

See [human-projection.md](references/human-projection.md).

## EPG-v1 contents

EPG-v1 contains:

```text
identity and parent lineage
source/spec/artifact binding
accepted obligations and terminal predicates
safety invariants and forbidden states
system regime
facts and critical unknowns
observable evidence vocabulary
guarded actions with predictions, proof, cost, risk, and rollback
policy rules mapping evidence to actions or terminal states
lexicographic progress potential
safety shield
commitment-horizon limits
initial runtime state
challenge disposition
handoff/readiness gates
```

See [execution-policy-graph.md](references/execution-policy-graph.md).

## Research and clarification

Research available code, docs, specs, tests, tickets, schemas, configuration, plans, and current tool surfaces first.

Ask at most one blocking judgment question.

A question is allowed only when the answer materially changes:

```text
scope
public behavior
authority
compatibility
architecture
data boundary
deployment target
irreversible migration
```

Include a recommended option and consequence.

When the user asks to be grilled or interrogated, route to `$grill-me` and emit no plan in that turn.

## Source-binding gate

Bind:

```text
source refs and digest
spec/governance receipt when present
repository/branch/base/head/dirty fingerprint when repo-bound
locked decision refs
created-at timestamp
```

A policy is stale when a declared invalidator fires.

Do not claim readiness for stale intent or artifact state.

See [source-binding.md](references/source-binding.md).

## Semantic-drift gate

In `spec_handoff` mode:

```text
semantic_drift = none
```

Changes to requirements, non-goals, public behavior, compatibility, authority, architecture, or proof bar require a new specification/governance revision.

`$plan` may add execution-only structure:

```text
belief facts and unknowns
observation predicates
probe and implementation actions
ownership
hard dependencies and lock roots
proof obligations
safety rules
policy branches
horizon limits
rollout/rollback ordering
```

## Belief and observation discipline

Keep separate:

```text
fact
hypothesis
unknown
observation
prediction
result
```

Every critical unknown must have at least one:

```text
observable evidence source
probe action
user decision action
explicit block/return route
```

Do not turn an assumption into invisible certainty.

## Action contract

Every action includes:

```text
stable action ID and kind
owner
preconditions
required prior actions
mutation boundary and lock roots
expected facts/unknowns/obligation effects
expected and failure observations
proof obligations
rollback
information value
execution cost
irreversible risk
semantic-surface growth
rework risk
repeatability
```

Mutation, deploy, or stabilization actions require bounded mutation scope and proof.

Inspect/probe actions must produce evidence that resolves or narrows a named unknown or obligation.

See [action-contract.md](references/action-contract.md).

## Policy rules

A rule maps current atoms to a next action or terminal state:

```text
when(all/any/none)
-> candidate actions or terminal
-> priority and rationale
-> replan conditions
```

Conditions reference only declared atoms:

```text
fact:<id>
obs:<id>=<outcome>
action:<id>=success|failure
unknown:<id>=resolved|blocked
terminal:<name>
```

The runtime chooses among eligible candidates using the declared lexicographic utility order.

## Dual-purpose action ranking

Prefer actions that jointly improve the system and reduce uncertainty.

Default utility order:

```text
maximize obligation reduction
maximize information gain
maximize downstream unlocks
maximize proof gain
minimize irreversible risk
minimize semantic-surface growth
minimize rework risk
minimize execution cost
stable action ID tie-break
```

This order is subordinate to the safety shield.

## Safety shield

The shield may block otherwise high-value actions.

Typical rules:

```text
no mutation without current GCR
no public/compatibility/authority change without source authority
no irreversible migration before its decision gate closes
no deployment without rollback
no stale proof reuse
no action outside its mutation boundary
```

Every runtime shield response is explicit:

```text
block
rollback
return_to_spec
```

A need for fresh user judgment is detected during policy compilation and routes through the planning handoff as `return_to_grill`; it is not a runtime shield terminal.

## Progress potential

Define a lexicographic potential over dimensions such as:

```text
safety violations
contract violations
critical unknowns
unsatisfied obligations
open counterexample classes
stale/missing proof
irreversible exposure
hard semantic surface
execution cost
```

Ordinary actions should predict no worsening in earlier dimensions and improvement in at least one dimension.

A probe may leave implementation progress unchanged when it materially reduces a critical unknown.

Execution records predicted versus observed potential.

## Commitment horizon

Distinguish:

```text
policy horizon
  all modeled conditional futures

commitment horizon
  only the next bounded action(s) granted durable execution authority
```

Default:

```text
mutation actions max = 1
non-mutating evidence actions max = 3
delivery transitions max = 1
```

Only the commitment horizon is materialized into active `$st` work.

Do not flatten every conditional future into speculative durable tasks.

## Challenge and fresh eyes

Run one strongest challenge:

```text
Could this policy satisfy the source contract while choosing a harmful,
unobservable, unsafe, or non-convergent route?
```

Disposition:

```text
adopt
defer
reject
none
return_to_spec
return_to_grill
```

No addition is mandatory.

Strict/campaign profiles should invoke `execution_policy_auditor`.

See [fresh-eyes-press-pass.md](references/fresh-eyes-press-pass.md).

## Revision and convergence

Revision identity is artifact-based:

```text
policy_id
revision
parent policy ID/digest
computed current digest
```

Internal thought passes are not revisions.

Use:

```bash
python3 codex/skills/plan/tools/policy_revision_diff.py \
  --parent parent-policy.json \
  --current current-policy.json
```

A policy is ready when the validator derives:

```text
source current
semantic drift acceptable
obligations covered
critical unknowns observable or explicitly blocked
all actions bounded
policy references valid
policy graph closed over modeled outcomes
safety shield complete
potential complete
terminal states reachable or explicitly blocked
runtime handoff valid
fresh-eyes blockers zero
```

## Validation and local runtime

Validate EPG or a proposed-plan Markdown file:

```bash
python3 codex/skills/plan/tools/execution_policy_gate.py policy.json

python3 codex/skills/plan/scripts/plan_contract_lint.py \
  --file proposed-plan.md
```

Select the next policy action from current state:

```bash
python3 codex/skills/plan/tools/policy_select.py \
  --policy policy.json \
  --state state.json \
  --out decision.json
```

Validate a transition receipt:

```bash
python3 codex/skills/plan/tools/transition_receipt_gate.py \
  --policy policy.json \
  --state state.json \
  --decision decision.json \
  --receipt receipt.json
```

Apply a validated receipt to the durable policy checkpoint:

```bash
python3 codex/skills/plan/tools/policy_checkpoint.py apply \
  --policy policy.json \
  --state state.json \
  --decision decision.json \
  --receipt receipt.json \
  --out next-state.json
```

These tools manage policy evidence only. They do not mutate source code or grant delivery authority.

## `$st` handoff

Current compatibility path:

```text
EPG/current state
-> EPD-v1 selected action
-> semantic intake for only the current commitment horizon
-> canonical .ledger/st/st-plan.jsonl
-> GCR-v1
```

Use exact policy/action/state refs in `$st` source and intent fields.

Do not claim critical path, parallel width, aperture, or execution permission in `$plan`; those are `$st`/GCR facts.

Native policy runtime work is specified in the package CLI spec.

See [st-handoff.md](references/st-handoff.md).

## Handoff states

```text
ready_for_runtime
  EPG valid; source current; initial/current state valid

return_to_spec
  source semantics incomplete, contradictory, or invalidated

return_to_grill
  unresolved user judgment blocks policy closure

stale
  source or artifact binding invalidated

blocked
  required evidence/tool/authority unavailable
```

`mutation_allowed` is always `no` in `$plan`.

## Readiness-only fast path

When the user asks only whether an existing policy is ready:

1. validate EPG;
2. verify source/artifact binding;
3. validate current state and any supplied runtime receipt;
4. if all pass and no revision is requested, reply exactly:

```text
Plan is ready.
```

Embedded self-declared flags alone are insufficient.

## Decision observability

Project material planning decisions into SDR-v1 when persistence is enabled:

```text
system regime
critical unknown classification
probe versus implementation action
policy branch and candidate rejection
safety-shield block
authority return
policy-ready/stale/blocked
```

Decision contract: [decision-contract.yaml](references/decision-contract.yaml).

## Hard rules

- Exactly one `<proposed_plan>` block when emitting a plan.
- EPG-v1 is authoritative; Markdown is projection.
- Never mutate repository files.
- Never redesign governed semantics during planning.
- Never claim readiness from document stasis or self-attestation.
- Never hide a critical unknown outside belief state.
- Never create an action without observable predicted effects.
- Never flatten the full conditional policy into speculative active tasks.
- Never bypass the safety shield for utility.
- Never grant source mutation or delivery authority.
- Never invent graph analytics reserved for `$st`.
