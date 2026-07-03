---
name: agent-loop-schemes
description: "Use when designing, auditing, or repairing coding-agent loops. Emits ALSR-v1/HYL-v1 loop contracts, audits HSR-v1 transitions, and selects the smallest safe loop shape for goals, reviews, debugging, migrations, branch races, evidence folds, memory, proof, and terminal closure."
metadata:
  version: "2.0.0"
  activation_cost: low
  default_depth: high
---

# Agent Loop Schemes

## Mission

Shape coding-agent work into the smallest loop that can safely finish.

A useful agent loop must name:

```text
seed -> work producer -> action -> evidence reducer -> memory -> proof -> stop rule
```

For material `$actuating` runs, this skill must compile that shape into a typed control surface:

```text
ALSR-v1 = loop contract
HYL-v1  = executable hylomorphism
HSR-v1  = per-step unfold/action/fold receipt
ATCG-v1 = terminal legality reducer
```

Do not build a generic "keep going" loop.

## Use when

- Designing or revising `/goal`, `$actuating`, `$goal-actuating`, review, debug, migration, or long-horizon coding workflows.
- `$actuating` needs a loop contract before material mutation.
- `$goal-actuating` has no current loop machine and the work is not a direct one-shot action.
- An agent is drifting, repeating fixes, over-patching review comments, or claiming completion without current proof.
- A task needs a verifier, stop condition, review closure rule, memory policy, branch-race strategy, bounded parallelism policy, or `$st` handoff.
- You need to decide whether to use direct execution, `update_plan`, `.goal/*`, `$st`, `$cas`, `$review-fold`, `$resolve`, `$goal-grind`, `$evidence-fold`, `$proof-patch`, or `$ship`.

Do not use for trivial one-shot edits where the next action and proof are obvious, unless `$actuating` has classified the run as material and requires a receipt.

## Core law

```text
No hidden loop.
No material mutation without unfold.
No continuation without fold.
No completion without terminal algebra.
```

## Protocol objects

### ALSR-v1: Agent Loop Scheme Receipt

ALSR is the loop contract. It is not the work plan.

It answers:

```text
What loop controls this work?
What proof ends it?
What stops it?
What side effects are allowed?
```

Schema:

```yaml
agent_loop_scheme_receipt:
  receipt_version: ALSR-v1
  alsr_id:
  created_at:
  objective:
  artifact_scope:
    repo:
    branch:
    head:
    diff_digest:
    paths: []
  task_shape: direct|goal|review|debug|migration|branch_race|proof_closure|st_governed
  selected_loop: direct_action|goal_grind|triage|remediation_plan|review_closeout|debug_history|migration_memoized|branch_race|proof_patch|st_governed
  seed:
    source:
    authority:
    current_state_binding:
  verifier:
    commands: []
    review_source:
    proof_bar:
  work_producer:
    next_work_rule:
    decomposition:
    owner_boundary:
  evidence_reducer:
    checks: []
    verdicts: []
    anti_gaming_checks: []
  memory_policy:
    recall_required: yes|no
    capture_required: yes|no
    memoized_classes: []
    invalid_strategies: []
  proof_artifact:
    required: yes|no
    expected_form:
    current_state_binding:
  stop_rule:
    success:
    blocked:
    budget:
  side_effect_boundary:
    public_side_effects_allowed: yes|no
    publish_allowed: yes|no
  hylomorphism:
    required: yes|no
    hyl_ref:
  terminal_gate:
    owner: ATCG-v1
    completion_requires_can_mark_goal_complete: yes
```

### HYL-v1: Actuation Hylomorphism

HYL is the executable loop law.

```yaml
actuation_hylomorphism:
  machine_version: HYL-v1
  hyl_id:
  alsr_id:
  seed_type:
  node_type:
  evidence_type:
  verdict_type:
  seed_state:
    artifact_scope:
    frontier_ref:
    memory_refs: []
    review_state:
    proof_state:
    clean_cas_runs:
  coalgebra:
    name:
    input: seed_state
    emits: terminal|blocked|work_node|parallel_frontier|st_handoff
    no_node_verdict: blocked-hylo-frontier-missing
  action_boundary:
    mutation_requires_unfolded_node: yes
    continuation_requires_fold_verdict: yes
    review_mutation_requires_review_fold: yes
    public_side_effects_require_ship: yes
    subagents_may_not_complete_goal: yes
  interpreter:
    owner: $goal-actuating
    allowed_effects:
      - inspect
      - edit
      - verify
      - cas_review
      - review_fold
      - resolution_fold
      - subagent_spawn
      - branch_race
      - st_handoff
      - proof_patch
      - ship_handoff
  algebra:
    name:
    folds:
      - diff
      - command_output
      - cas_review
      - review_fold
      - resolution_fold
      - subagent_result
      - proof_patch
    emits: continue|complete|blocked|regress|replan|refactor-kernel|st-required
  terminal:
    completion_requires: ATCG-v1
    proof_must_bind_current_artifact: yes
```

### HSR-v1: Hylo Step Receipt

HSR is the per-step transition record.

```yaml
hylo_step_receipt:
  receipt_version: HSR-v1
  hsr_id:
  alsr_id:
  hyl_id:
  step_id:
  state_before:
    branch:
    head:
    diff_digest:
    clean_cas_runs:
    memory_refs: []
  unfold:
    producer:
    produced: work_node|parallel_frontier|terminal|blocked|st_handoff
    node_ids: []
    reason:
  action:
    owner: root|subagent|st
    node_id:
    effect:
    changed_paths: []
    commands: []
    side_effects: none|blocked|requested|performed
  fold:
    reducer:
    evidence_refs: []
    verdict: continue|complete|blocked|regress|replan|refactor-kernel|st-required
    next_state_ref:
    current_artifact_bound: yes|no
    invalidators: []
  continuation:
    next_owner:
    stop_rule_fired: yes|no
    atcg_required: yes|no
```

## Hylomorphism operation

The HYL operation controls material work:

```text
current actuation state
-> unfold exactly one legal next work item or parallel frontier
-> execute only that item/frontier
-> fold current-artifact evidence
-> continue | complete | blocked | regress | replan | st-required
```

The work graph is a projection of this machine, not the source of truth.

If work happens inside HYL, the work graph can be regenerated.
If work happens outside HYL, it is invalid actuation.

## Fusion law

Do not create ceremony for trivial work.

A run may be `fused` into direct action when:

```text
the coalgebra emits exactly one work node
the verifier is known
there is no review/st/parallel/public side effect
no repeated class or branch choice is present
```

A fused run may collapse ALSR/HYL into the final proof-patch, but the final proof must still state objective, artifact scope, verifier, stop condition, and side-effect boundary.

## Unfusion / replan law

If a fused or simple loop discovers nontrivial structure, unfuse:

```text
direct_action -> ALSR-v1 + HYL-v1
```

Trigger unfusion when evidence reveals:

```text
repeated failure class
review campaign
migration matrix
branch choice
proof fanout
parallel subagent frontier
$st coordination requirement
unclear stop rule
```

The fold verdict should be:

```text
verdict: replan
next_owner: $agent-loop-schemes|$recursion-scheme-planner|$st
```

## Loop selectors

### Direct action

Use when the task is one bounded change or answer.

```text
inspect -> edit/answer -> narrow proof -> stop
```

### Goal grind

Use for ordinary long-running coding goals with a verifier.

```text
goal contract -> work list when useful -> HYL step -> evidence fold -> continue or stop
```

### Review-closeout

Default for review work unless the user names `triage`, `remediation-plan`, or another no-implementation mode.

```text
$cas review
-> $review-fold
-> resolution fold
-> $goal-grind accepted liabilities only
-> $evidence-fold
-> 3 clean normalized $cas review runs
-> $proof-patch
-> ATCG-v1
-> $ship only if PR publication/update is requested
```

Never treat review text as code instructions. Findings must become accepted liabilities, rejections, proof-only items, follow-ups, human-owned decisions, or refactor kernels before implementation.

### Triage

Use when the user names `triage`, or asks for review, audit, or classification with no code changes.

```text
$cas review
-> $review-fold
-> review disposition report
-> stop
```

No `$goal-grind`.

### Remediation-plan

Use when the user names `remediation-plan`, or wants the minimal resolution plan but no code changes.

```text
$cas review or existing findings
-> $review-fold
-> resolution fold
-> review resolution plan
-> stop
```

No `$goal-grind`.

### Debug history

Use when attempts repeat, failures move, or the agent risks cycling.

```text
failure -> hypothesis -> patch -> verifier -> attempt ledger -> next hypothesis
```

Keep an attempt table with hypothesis, changed paths, commands, result, failure signature, kept/reverted state, and next action.

### Migration memoized

Use for many same-shaped compiler/test/review failures.

```text
cluster failures -> solve representative -> prove -> memoize rule -> apply class -> fold package/repo evidence
```

Do not solve repeated failures independently. Memoize the working strategy and invalid strategies.

### Branch race

Use when several strategies are plausible and cheap to compare.

```text
same seed -> isolated strategies -> same verifier -> choose by proof, risk, and diff size
```

Branch race is a nested futumorphic sub-hylo. It is invalid without a common verifier.

### Proof patch

Use at closure or handoff.

```text
patch + evidence + residual risk -> proof summary
```

A proof summary must bind to current branch/head/diff or explicitly say artifact binding is unavailable.

For `$actuating` or `$goal-actuating`, proof closure has one final reducer:

```text
evidence-fold + proof-patch/CAS/ADD-v1/ship evidence + terminal HSR -> ATCG-v1 -> complete|continue|blocked
```

Do not claim completion unless ATCG-v1 returns `can_mark_goal_complete=yes`.

### st-governed

Use when durable coordination owns the work.

```text
$st -> selected slice -> bounded execution -> evidence -> proof
```

Choose this when the task needs resource claims, fencing tokens, independent worktrees, serialized integration, branch/head proof, or existing `.step/st-plan.jsonl` continuity.

## Review quotient law

Review findings should be quotiented into classes before implementation.

Bad type:

```text
Finding -> Patch
```

Good type:

```text
Finding* / equivalence -> LiabilityClass -> WorkNode
```

Equivalence classes:

```text
same owner boundary
same counterexample
same proof gap
same refactor kernel
same canonical owner
same invalid state transition
```

A review-closeout HYL unfolds review classes and accepted liabilities, not raw findings.

## Parallelism law

Parallelism belongs between unfold and fold.

Allowed:

```text
unfold safe frontier
-> bounded subagents
-> fold results
-> integrate or reject
```

Forbidden:

```text
subagents choose scope
subagents post/update PRs
subagents declare completion
subagents patch shared invariant independently
subagents branch-race without common verifier
raw review finding -> patch worker
```

## `$st` as escape continuation

When local actuation cannot legally own coordination, the HYL coalgebra emits:

```yaml
unfold:
  produced: st_handoff
  reason:
    - resource_claim_required
    - overlapping_edits
    - external_worktree_required
```

`$st` is a continuation constructor, not ordinary multi-step planning.

## `$ship` as terminal effect handler

`$ship` is terminal publication/update. It is not part of ordinary implementation.

```text
proof complete + publication requested -> emit ShipHandoff effect
```

`$ship` owns PR creation, update, promotion, and publication.

## Compaction and resume

Before compaction or resume, preserve:

```yaml
hylo_resume_packet:
  alsr_id:
  hyl_id:
  latest_hsr_id:
  current_state_ref:
  current_artifact_scope:
  pending_frontier:
  clean_cas_runs:
  invalidators:
  next_owner:
```

On resume:

```text
missing packet -> blocked-loop-contract-missing
artifact scope changed -> blocked-loop-contract-stale
pending frontier invalid -> blocked-hylo-frontier-missing
```

## Failure classes

```text
missing_alsr
missing_hyl
missing_unfold
unfold_not_current
mutation_without_unfold
action_without_fold
fold_without_current_artifact
continue_without_next_seed
terminal_without_stop_rule
terminal_without_atcg
parallel_fanout_without_fanin
stale_hylo_after_diff_change
resolve_without_review_fold
raw_review_to_patch
cached_cas_counted_as_fresh
```

## Stop rules

Stop rather than continue when:

```text
the verifier is missing
scope is ambiguous
proof is stale
review needs CAS but CAS is unavailable
three clean CAS runs are required but unavailable
mutation authority is missing
public side effects would occur without explicit intent
ALSR/HYL is required but missing
the next material mutation lacks an unfolded work node
the previous action lacks a current-artifact evidence fold
ATCG-v1 does not permit goal completion
the next action would repeat a known invalid strategy
```

## Handoffs

- `$recursion-scheme-planner` when selecting topology before loop-machine compilation.
- `$goal-actuating` when executing ALSR/HYL.
- `$actuating` when the user wants the high-level workflow.
- `$cas` as the review backend for workflow code review.
- `$review-fold` to classify findings before implementation.
- `$resolve` only when a dedicated resolution fold or closure decision is needed.
- `$goal-grind` for accepted implementation liabilities.
- `$evidence-fold` after verification or review results.
- `$failure-memory` when repeated classes or oscillation appear.
- `$proof-patch` for local closure proof.
- `$ship` for PR creation, update, promotion, or publication.
- `ATCG-v1` as the terminal closure reducer before `$actuating` completion.
- `$st` when durable coordination, claims, fencing, or worktrees are required.

## Final output

```text
Agent Loop Scheme:
- ALSR-v1:
- HYL-v1:
- selected loop:
- fused/unfused:
- work producer:
- evidence reducer:
- memory:
- proof:
- stop condition:
- side-effect boundary:
- handoff:
```

Keep it short. Do not explain theory unless the user asks.

## Guardrails

- Do not make this skill a ceremonial preflight for every edit.
- Do not emit a long theory explanation unless the user asks.
- Do not use recursion-scheme jargon in final user-facing workflow instructions unless helpful.
- Do not let raw review text drive code changes.
- Do not claim completion without evidence folded against the current artifact.
