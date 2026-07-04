# Goal-Focus HYL Driver Spec

## Purpose

Use one stable parent `/goal` and many parent-owned goal-focus frames. Do not redesign `$actuating` around repeatedly changing the primary Codex `/goal`.

```text
stable parent /goal
-> active goal-focus frame
-> HYL unfold/action/fold
-> parent state update
-> next focus | blocked | terminal ATCG
```

The parent goal remains the authority. Goal-focus frames are local execution objectives that must fold back into the parent state.

## Why

The audit failure mode was not missing skill availability; it was missing governance. True `$actuating` runs could proceed without a durable loop-shaping object, yielding graph bypass, stale proof ambiguity, and weak review compression. A goal-focus HYL driver makes every material local objective explicit without replacing the parent goal.

## Definitions

### Parent goal

The stable user-facing objective for the thread.

Examples:

```text
/goal $actuating implement the accepted spec
/goal $actuating review-closeout this PR
/goal $actuating close out review for this branch
```

The parent goal owns:

```text
objective
artifact scope
accepted authority
terminal proof bar
review closure bar
public side-effect boundary
ATCG completion
```

### Goal-focus frame

A local objective selected by the HYL coalgebra.

```yaml
goal_focus_frame:
  version: GFF-v1
  parent_goal_id:
  frame_id:
  focus_kind: inspect|review-intake|review-quotient|abstraction-decision|implementation|proof|ship|st-handoff|blocked|terminal
  local_objective:
  contribution_to_parent:
  seed_ref:
  authority:
    mutation_allowed: yes|no
    public_side_effects_allowed: no|ship-only
  unfold:
    producer:
    expected_node_or_frontier:
  action:
    allowed_effects: []
  fold:
    reducer:
    expected_parent_state_update:
  stop:
    child_success:
    child_blocked:
    parent_continuation:
```

### Hylo effect goal

A goal-focus frame whose local objective is one hylomorphic transition:

```text
seed -> anamorphic work generation -> action -> catamorphic evidence fold -> parent state delta
```

Schema:

```yaml
hylo_effect_goal:
  version: HEG-v1
  parent_goal_id:
  hyl_id:
  hsr_id:
  local_goal:
    summary:
    contribution_to_parent:
  anamorphism:
    seed:
    generated_work:
    frontier:
  action:
    owner: root|subagent|st
    allowed_effects: []
    mutation_allowed: yes|no
  catamorphism:
    evidence: []
    fold_verdict: continue|complete|blocked|regress|replan|refactor-kernel|st-required
    parent_state_delta:
  continuation:
    next_focus:
```

## Core rule

```text
The primary /goal is stable.
The active goal focus is mutable.
Every focus must unfold, act, fold, and return to the parent.
Only the parent may complete.
```

Do not treat child frames as literal nested `/goal` commands. They are HYL frames under the parent goal.

## `$actuating` responsibility

`$actuating` drives the stable parent goal. It may change the active focus, but it must not repeatedly rewrite the primary `/goal` as a substitute for HYL state.

Before each material action, `$actuating` must know:

```text
parent goal
active goal-focus frame
unfolded node or frontier
allowed effects
expected fold reducer
parent state update
```

A material action without a goal-focus frame is equivalent to `mutation_without_unfold`.

## `$recursion-scheme-planner` responsibility

The planner should emit a subgoal ladder when the parent goal has staged structure.

```yaml
scheme_plan:
  parent_goal:
    objective:
    artifact_scope:
    terminal_gate: ATCG-v1
  subgoal_ladder:
    enabled: yes|no
    reason:
    subgoals:
      - id:
        name:
        scheme:
        depends_on: []
        objective:
        seed:
        producer:
        reducer:
        output:
        verifier:
        abstraction_checkpoint:
          required: yes|no
          question:
          local_fix_allowed_when: []
        parallelism:
          mode: none|review-class-fanout|branch-race|proof-fanout|patch-fanout
          fan_in:
        stop:
  terminal_gate: ATCG-v1
```

A Scheme Plan is not a list of implementation steps. It is a topology for producing goal-focus frames.

## Review-closeout subgoal ladder

For review closeout, prefer this ladder:

```text
Parent: review-closeout this PR

SG1 review-intake
  output: raw review findings bound to current PR/diff

SG2 review-quotient
  output: finding classes by counterexample, owner boundary, invariant, proof gap, canonical owner, or refactor kernel

SG3 abstraction-decision
  output: resolution plan with local-fix vs refactor-kernel vs branch-race vs proof-only vs reject vs follow-up vs ask-human

SG4 implementation
  output: patch candidates for accepted code-change liabilities only

SG5 closure
  output: evidence-fold, proof-patch, three clean normalized standard CAS attempts, ATCG verdict
```

Implementation may not begin until SG3 has folded. This is the abstraction checkpoint.

## Abstraction checkpoint

Before patching a review class, the active goal-focus frame must decide:

```yaml
abstraction_decision:
  finding_class:
  owner_boundary:
  shared_invariant:
  missing_canonical_owner: yes|no
  local_fix_allowed: yes|no
  refactor_kernel_candidate: yes|no
  branch_race_required: yes|no
  proof_only: yes|no
  follow_up: yes|no
  ask_human: yes|no
  reason:
```

Local fixes are allowed only when:

```text
exactly one accepted liability has one owner-correct repair
no repeated finding class exists
no shared invariant is implicated
no missing canonical owner is implicated
no branch-race alternative is plausible under the same verifier
```

If several findings share one owner boundary, invariant, state transition, proof surface, or missing canonical owner, emit a refactor-kernel frame instead of one patch frame per comment.

## Parallelism

Parallelism is legal only inside a goal-focus frame whose unfold produced a safe frontier.

Allowed:

```text
review-class-fanout after review quotient
branch-race after abstraction decision
patch-fanout only after resolution fold and only for disjoint accepted liabilities
proof-fanout during closure
```

Forbidden:

```text
raw review finding -> patch worker
subagent chooses parent scope
subagent declares parent completion
subagent updates or publishes PRs
patch fanout over shared owner boundary or invariant
branch race without common verifier
```

Subagents return typed results. The parent folds them.

## HSR integration

Extend HSR-v1 with focus metadata:

```yaml
hylo_step_receipt:
  goal_focus:
    parent_goal_id:
    active_focus_id:
    focus_kind:
    local_objective:
    contribution_to_parent:
  unfold:
  action:
  fold:
  continuation:
```

ATCG must verify:

```text
primary_goal_stable = yes
all child focus frames folded or blocked = yes
terminal focus matches parent stop rule = yes
no child frame claimed parent completion = yes
```

## Failure classes

Add or recognize:

```text
primary_goal_swapped_without_user_authority
child_goal_claimed_parent_completion
focus_without_parent_goal
focus_without_fold
focus_fold_not_parent_bound
abstraction_checkpoint_missing
raw_finding_to_focus_patch
subgoal_ladder_bypassed
parallel_child_without_parent_fanin
```

## Final law

```text
One stable parent /goal.
Many parent-owned goal-focus frames.
Each frame is an anamorphism plus action plus catamorphism.
Only the parent fold and ATCG can close the goal.
```
