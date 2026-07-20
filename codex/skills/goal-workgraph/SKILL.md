---
name: goal-workgraph
description: "Project current source-bound work into the smallest verifier-first owner graph only when decomposition changes execution. Omit the graph for one bounded operation; compress repeated classes, derive the frontier from current evidence, and invalidate stale graphs."
---

# Goal WorkGraph

## Mission

Project current controlling obligations into the smallest verifier-first graph
that changes execution. The graph is an advisory, ephemeral view for
`$actuating`; it is not an authority source, event store, architecture
selector, or recursive executor.

## Admission

Do not create a WorkGraph for one bounded owner operation with one known
verifier. Let `$actuating` select that operation directly.

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
  version: work-node-view/v1
  node_id:
  construction_ref:
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
  counterexample_class_refs: []
  proof_obligation_refs: []
  retirement_refs: []
  parallel_safe: true | false
  isolation: read-only | file-disjoint | serial
  status: pending | selected | running | passed | failed | blocked # derived view
~~~

## Graph

~~~yaml
work_graph:
  version: work-graph-view/v1
  goal_id:
  goal_contract_ref:
  construction_ref:
  subject_digest:
  evidence_head:
  nodes: []
  frontier_policy: verifier-first | highest-risk-first | dependency-order
  combine_policy: all-pass | proof-sufficient
  next_ready_node_ids: [] # derived from current evidence
~~~

Node status and `next_ready_node_ids` are projections, never continuation
authority. Recompute them from the current Goal Contract, Construction
Contract, applicable Counterexample Sets, Evidence Ledger, and live subject.

## Compilation laws

1. **Current control basis.** Derive nodes only from the current Goal Contract,
   current Construction Contract, applicable Counterexample Sets, current
   Evidence Ledger, canonical applicable route-exclusion projection, subject
   identity, path scope, proof obligations, retirements, and verifier bindings.
   Raw findings and suggested patches are never nodes.
2. **Repeated-class compression.** When many instances share one governing law
   and one construction, create one canonical owner edit node. Instance
   application or verification may fan out; do not duplicate architecture
   nodes.
3. **Current-evidence frontier.** Recompute the ready frontier after every
   observation. Cached node state or an earlier ready frontier cannot authorize
   continuation.
4. **Whole-graph invalidation.** A change to the Goal Contract, current
   Construction Contract, applicable Counterexample Sets, canonical applicable
   route-exclusion projection, subject identity, paths, obligations, or
   verifier bindings invalidates the complete graph. Regenerate it rather than
   repairing stale graph state.
5. **Distinct stop meanings.** Keep failed execution, blocked progress, and
   invalid proof distinct. Stale, mismatched, fallback, or incomplete evidence
   does not become an implementation failure or a repair node.
6. **Selected architecture only.** Read-only experiments may compare candidate
   behavior, but architecture selection remains outside the graph. Only the
   exact current Construction Contract may inform edit nodes. Accepted
   Counterexample classes identify falsified laws; they never select a repair
   or edit node.
7. **Bounded parallelism.** Parallelize only resource-disjoint read-only scout,
   review, or proof nodes. Shared-owner mutation remains serial and every fanout
   returns through `$actuating`.

## Procedure

1. Apply the admission rule; omit the graph when one direct operation suffices.
2. Preserve the current Goal, Construction, owner, subject, Evidence Ledger
   head, path, obligation, and verifier bindings.
3. Split only by owner boundary, invariant, proof surface, or real dependency.
4. Compress repeated instances that share one law and construction.
5. Group applicable Counterexample classes by current Construction obligation
   and owner; never create one node per comment.
6. Create edit nodes only from the current Construction's selected architecture
   and execution boundary. If an accepted class is not referenced by the
   current Construction, return it to Actuating for successor selection; do not
   invent an edit node.
7. Make construction replacement one serial canonical-owner node with explicit
   retirement nodes or proof surfaces.
8. Consume current counterexamples and the canonical applicable
   `$negative-ledger` route-exclusion projection before proposing inspect work;
   never infer or perform reopening locally.
9. Return the currently ready node IDs to `$actuating` for lead selection.

## Guardrails

- The graph cannot grant mutation or complete the goal.
- The graph cannot select architecture or reinterpret the current Construction.
- Unknown review pressure routes back to classification or Actuating
  evaluation.
- Do not persist graph state as a second control plan.
- Do not parallelize a shared owner boundary.
- Do not add refactor work unless it removes a shared cause or proof surface.
