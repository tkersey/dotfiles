---
name: goal-workgraph
description: "Project current source-bound work into the smallest verifier-first owner graph only when decomposition changes execution. Omit the graph for one bounded operation; compress repeated classes, derive the frontier from current evidence, and invalidate stale graphs."
---

# Goal WorkGraph

## Mission

Project current controlling obligations into the smallest verifier-first graph
that changes execution. The graph is an advisory, ephemeral view for
`$goal-actuating`; it is not an authority source, event store, architecture
selector, or recursive executor.

## Admission

Do not create a WorkGraph for one bounded owner operation with one known
verifier. Let `$goal-actuating` select that operation directly.

Use a graph only when decomposition changes at least one of:

- dependency order;
- repeated-class realization;
- proof fanout;
- safe read-only parallelism; or
- stopping behavior.

A graph that merely wraps one selected operation is ceremony.

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
  status: pending | selected | running | passed | failed | blocked # derived view
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
  next_ready_node_ids: [] # derived from current evidence
~~~

Node status and `next_ready_node_ids` are projections, never continuation
authority. Recompute them from the current controlling artifacts, kernel state,
and evidence.

## Compilation laws

1. **Current control basis.** Derive nodes only from the current GoalContract,
   selected review resolution or construction, subject identity, path scope,
   obligations, and verifier bindings. Raw findings and suggested patches are
   never nodes.
2. **Repeated-class compression.** When many instances share one governing law
   and one construction, create one canonical owner edit node. Instance
   application or verification may fan out; do not duplicate architecture
   nodes.
3. **Current-evidence frontier.** Recompute the ready frontier after every
   observation. Cached node state or an earlier ready frontier cannot authorize
   continuation.
4. **Whole-graph invalidation.** A change to the source, selected construction,
   subject identity, paths, obligations, or verifier bindings invalidates the
   complete graph. Regenerate it rather than repairing stale graph state.
5. **Distinct stop meanings.** Keep failed execution, blocked progress, and
   invalid proof distinct. Stale, mismatched, fallback, or incomplete evidence
   does not become an implementation failure or a repair node.
6. **Selected architecture only.** Read-only experiments may compare candidate
   behavior, but architecture selection remains outside the graph. Only the
   already-selected construction may produce edit nodes.
7. **Bounded parallelism.** Parallelize only resource-disjoint read-only scout,
   review, or proof nodes. Shared-owner mutation remains serial and every fanout
   returns through `$goal-actuating`.

## Procedure

1. Apply the admission rule; omit the graph when one direct operation suffices.
2. Preserve the current source, run, owner, subject, path, obligation, and
   verifier bindings.
3. Split only by owner boundary, invariant, proof surface, or real dependency.
4. Compress repeated instances that share one law and construction.
5. Group already-quotiented review findings into one resolution decision; never
   create one node per comment.
6. Create edit nodes only for an already-selected `local-repair` or
   `replacement-kernel` construction.
7. Make replacement-kernel work one serial canonical-owner node with explicit
   retirements.
8. Consume current counterexamples and route exclusions before proposing inspect
   work; reopen an excluded route only when its recorded criterion changes.
9. Return the currently ready node IDs to `$goal-actuating` for lead selection.

## Guardrails

- The graph cannot grant mutation or complete the goal.
- The graph cannot select architecture or reinterpret a selected strategy.
- Unknown review pressure routes back to classification or resolution.
- Do not persist graph state as a second control plan.
- Do not parallelize a shared owner boundary.
- Do not add refactor work unless it removes a shared cause or proof surface.
