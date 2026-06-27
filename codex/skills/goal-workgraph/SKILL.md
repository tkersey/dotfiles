---
name: goal-workgraph
description: "Unfold a GoalContract into a typed WorkGraph of inspect, edit, verify, review, branch, reuse, ask, and block nodes. Use when a goal, review campaign, migration, or debug loop is too large for one focused action."
metadata:
  version: "1.0.0"
  activation_cost: low
  default_depth: standard
---

# Goal WorkGraph

## Mission

Unfold a goal into an explicit work structure.

```text
GoalContract -> WorkGraph
```

This is the anamorphic side of the goal runtime: it produces the next shape of work without pretending a linear plan is always the right model.

## Work node schema

```yaml
work_node:
  version: WN-v1
  id: W001
  kind: inspect|edit|verify|review|branch|reuse|ask|block
  description:
  depends_on: []
  paths: []
  owner_boundary:
  invariant:
  expected_evidence: []
  verifier: []
  risk: low|medium|high
  memo_key:
  review_refs: []
  status: pending|running|passed|failed|blocked|skipped
```

## Graph schema

```yaml
work_graph:
  version: WG-v1
  goal_id:
  mode: direct|goal|review|debug|migration|hardening|st-governed
  persistence: update_plan|goal-workgraph|st-required
  nodes: []
  frontier_policy: highest-risk-first|verifier-first|dependency-order|representative-class-first|branch-race
  combine_policy: all-pass|best-branch|proof-sufficient|human-select
  escalation:
    use_st_when: []
    use_grill_me_when: []
    use_review_fold_when: []
```

## Procedure

1. Prefer verifier-first decomposition: each nontrivial node should know what evidence can close it.
2. Split by ownership boundary, failure class, package/module, invariant, or review equivalence class.
3. For repeated failures, make one representative node and attach a `memo_key`.
4. For reviews, group comments by liability and kernel rather than one node per comment.
5. For competing strategies, create `branch` nodes only when alternatives can be isolated and compared by the same verifier.
6. For high-risk mutation or overlapping resource claims, mark `persistence: st-required` and stop for `$st`.
7. Emit the graph and the next ready frontier.

## Reabstraction trigger

When review or failure nodes share any of the following, prefer a `refactor-kernel` node over local patches:

```text
same invariant violated in multiple places
same canonical owner missing
same adapter/projection hand-written repeatedly
same branch of state machine locally patched
same proof obligation repeated per call site
same review finding would create wound-specific helpers/tests
```

## Guardrails

- Do not expand work just to look comprehensive.
- Do not create separate nodes for comments that reduce to the same counterexample.
- Do not add refactor work unless it shrinks the proof surface or fixes a shared owner boundary.
- Do not use `$st` for ordinary in-memory planning; reserve it for durable coordination and fencing.
