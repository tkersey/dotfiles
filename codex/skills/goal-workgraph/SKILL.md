---
name: goal-workgraph
description: "Unfold a goal contract or Scheme Plan into inspect, edit, verify, review, branch, reuse, ask, and block nodes. Use when a goal, review campaign, migration, debug loop, or parallel frontier is too large for one focused action."
metadata:
  version: "1.1.0"
  activation_cost: low
  default_depth: standard
---

# Goal WorkGraph

## Mission

Unfold a goal into an explicit work structure.

```text
goal contract or Scheme Plan -> WorkGraph
```

This produces the next shape of work without pretending a linear plan is always the right model.

## Work node schema

```yaml
work_node:
  version: WN-v1
  id: W001
  kind: inspect|edit|verify|review|branch|reuse|ask|block
  description:
  depends_on: []
  paths: []
  resource_keys: []
  proof_surface: []
  owner_boundary:
  invariant:
  expected_evidence: []
  verifier: []
  risk: low|medium|high
  parallel_safe: yes|no
  parallel_group:
  isolation: read-only|file-disjoint|worktree|blocked-external-coordination
  merge_policy: evidence-only|serial-integrate|winner-take-all
  conflict_with: []
  reviewer_class:
  memo_key:
  review_refs: []
  status: pending|running|passed|failed|blocked|skipped
```

## Graph schema

```yaml
work_graph:
  version: WG-v1
  goal_id:
  scheme_plan_ref:
  mode: direct|goal|review|debug|migration|hardening|blocked-external-coordination
  persistence: update_plan|goal-artifacts
  nodes: []
  frontier_policy: highest-risk-first|verifier-first|dependency-order|representative-class-first|branch-race
  combine_policy: all-pass|best-branch|proof-sufficient|human-select
  parallelism:
    mode: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
    max_agents:
    allowed_roles: []
    fan_in: evidence-fold|review-fold|resolution-fold|lead-integration
    stop_on_blocker: yes|no
    stop_on_winner: yes|no
  escalation:
    block_external_coordination_when: []
    use_grill_me_when: []
    use_review_fold_when: []
```

## Procedure

1. Prefer verifier-first decomposition: each nontrivial node should know what evidence can close it.
2. Respect the Scheme Plan when present.
3. Split by ownership boundary, failure class, package/module, invariant, proof surface, or review equivalence class.
4. For repeated failures, make one representative node and attach a `memo_key`.
5. For reviews, group comments by liability and kernel rather than one node per comment.
6. For competing strategies, create `branch` nodes only when alternatives can be isolated and compared by the same verifier.
7. For high-risk mutation or overlapping resource claims, mark the node blocked unless an existing supported controller owns it.
8. Emit the graph and the next ready frontier.

## Parallelism rules

1. Emit `parallel_safe: yes` only when dependencies are satisfied, paths/resources do not conflict, and the proof surface is known.
2. Use `scout-fanout` only for read-only fact finding.
3. Use `review-class-fanout` only after CAS findings have been grouped.
4. Use `patch-fanout` only after the resolution fold accepts refactor-kernel work nodes.
5. Use `branch-race` only when all strategies share the same verifier.
6. Mark shared invariants, shared files, or shared owner-boundary fixes as `parallel_safe: no`.
7. Consume `$review-fold` `kernel_fold.status`: `refactor-kernel` may become one owner-level work node, `none` cannot produce edit work, and `unknown` must inspect, ask, block, branch-race, or reclassify before mutation.
8. Do not let subagents update public tracker state, resolve threads, or declare completion.

## Reabstraction trigger

When review or failure nodes share any of the following, prefer a refactor-kernel node over local patches:

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
- Do not invent a durable controller for ordinary in-memory planning.
- Do not mark patch nodes parallel-safe when they touch the same owner boundary or invariant.
