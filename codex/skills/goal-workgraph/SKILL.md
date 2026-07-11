---
name: goal-workgraph
description: "Project a source-bound GoalContract, actuation run, or review resolution into explicit inspect, edit, verify, review, ask, and block nodes. Use when decomposition changes execution; consume selected owner-boundary strategies rather than raw review findings."
---

# Goal WorkGraph

## Mission

Project accepted work into a verifier-first graph. The graph is advisory input
to `actuation-open/v1` obligations and operations; it is not an authority
source, event store, or recursive executor.

## Node

~~~yaml
work_node:
  version: WN-v2
  node_id:
  run_id:
  kind: inspect | edit | verify | review | ask | block
  description:
  depends_on: []
  paths: []
  resource_keys: []
  owner_boundary:
  invariant:
  proof_surface: []
  verifier: []
  expected_evidence: []
  review_resolution_ref:
  resolution_decision_id:
  strategy: none | local-repair | replacement-kernel
  parallel_safe: true | false
  isolation: read-only | file-disjoint | serial
  status: pending | selected | running | passed | failed | blocked
~~~

## Graph

~~~yaml
work_graph:
  version: WG-v2
  goal_id:
  run_id:
  source_digest:
  nodes: []
  frontier_policy: verifier-first | highest-risk-first | dependency-order
  combine_policy: all-pass | proof-sufficient
  next_ready_node_ids: []
~~~

## Procedure

1. Preserve the source, run, owner, and verifier bindings.
2. Split by owner boundary, invariant, proof surface, or accepted resolution
   class.
3. Group review findings already quotiented into one resolution decision; never
   create one node per comment.
4. Create edit nodes only for `local-repair` or `replacement-kernel` decisions
   that already contain a selected work node.
5. Make replacement-kernel work one serial owner node with explicit
   retirements.
6. Mark only read-only nodes parallel-safe. File-disjoint mutation nodes remain
   serial alternatives for lead selection.
7. Return the ready node IDs to `$goal-actuating` for lead selection.

## Guardrails

- The graph cannot grant mutation or complete the goal.
- Unknown review pressure routes back to classification or resolution.
- Do not parallelize a shared owner boundary.
- Do not add refactor work unless it removes a shared cause or proof surface.
