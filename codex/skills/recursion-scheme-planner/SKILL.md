---
name: recursion-scheme-planner
description: "Use after an implementation spec or direct goal is accepted when deciding how to break it into planning, implementation, review, proof, memory, and parallel subagent loops. Selects the recursion-scheme topology that $agent-loop-schemes compiles into ALSR/HYL."
metadata:
  version: "1.1.0"
  activation_cost: low
  default_depth: high
---

# Recursion Scheme Planner

## Mission

Choose the right recursive control structure before execution.

```text
accepted spec or direct goal
-> Scheme Plan
-> ALSR/HYL compilation by $agent-loop-schemes
-> correct execution loop
```

This skill is for cases where `$goal-actuating` alone would be too flat. It decides whether the work should be handled as a simple goal grind, a memoized migration, a history-aware debug loop, a branch race, a proof-carrying patch, a review compression loop, a parallel traversal, or `$st`-governed execution.

It does **not** implement code. It selects topology.

## Use when

- A spec is accepted but the implementation shape is unclear.
- The work contains repeated classes, migrations, review campaigns, branch choices, or proof obligations.
- A direct goal is too complex for one linear plan.
- `$goal-actuating` risks becoming a generic while-loop.
- You need to decide between `update_plan`, `.goal/*`, `$st`, subagents, branch race, or memoized class work.
- Review or CAS findings may require compression before implementation.
- Parallel subagents might help, but only after safe frontier selection.
- `$agent-loop-schemes` needs topology input before emitting ALSR/HYL.

Do not use for trivial one-shot edits.

## Output: Scheme Plan

Emit a compact plan:

```yaml
scheme_plan:
  version: SP-v1
  source:
    kind: accepted-spec|direct-goal|review|debug|migration|plan-handoff
    ref:
    artifact_scope:
    authority:
  selected:
    primary_scheme: direct|cata|ana|hylo|para|apo|histo|futu|zygo|dyna|chrono|meta|mutu|parallel-traverse|st-governed
    composition: []
    reason:
  work_shape:
    structure: line|tree|dag|graph|mutual-graph|review-classes|migration-matrix|branch-race|proof-fanout
    decomposition_basis:
      - verifier
      - owner-boundary
      - invariant
      - failure-class
      - review-class
      - package
      - proof-surface
  loops:
    - id:
      scheme:
      seed:
      producer:
      reducer:
      memory:
      proof:
      stop:
      parallelism:
        mode: none|scout-fanout|review-class-fanout|patch-fanout|proof-fanout|branch-race
        safe_frontier: []
        forbidden_frontier: []
      hylomorphism:
        required: yes|no
        suggested_coalgebra:
        suggested_algebra:
        terminal_gate: ATCG-v1
  handoff:
    next_owner: $agent-loop-schemes|$goal-actuating|$goal-workgraph|$goal-grind|$review-fold|$resolve|$plan|$st|$ship|blocked
    mode:
    required_checks: []
    blocked_on: []
```

## Procedure

1. Read the accepted spec, direct goal, review target, or failure.
2. Identify the dominant work shape: line, tree, graph, repeated class set, review class set, branch race, proof fanout, or durable coordination.
3. Select the smallest recursion scheme composition that fits the work.
4. Name the producer: how work is unfolded or selected.
5. Name the reducer: how evidence, findings, proofs, or subagent results are folded into a verdict.
6. Decide whether memory is needed: attempt history, failure classes, review classes, or reusable transformations.
7. Decide whether lookahead or parallelism is safe.
8. Decide whether `$st` owns execution because of resource claims, fencing, worktrees, or serialized integration.
9. Emit the Scheme Plan and hand off to `$agent-loop-schemes` when ALSR/HYL must be compiled. Do not mutate code.

## Scheme selector

### Direct

Use when no recursive structure is needed.

```text
inspect -> act -> verify -> stop
```

### Catamorphism: fold evidence

Use when the main problem is reducing a structure into a verdict.

Examples:

```text
test logs -> pass/fail/block
CAS findings -> dispositions
diff + proof -> readiness claim
AST/files -> risk summary
```

Owners: `$evidence-fold`, `$review-fold`, `$proof-patch`.

### Anamorphism: unfold work

Use when the main problem is generating the work structure.

Examples:

```text
spec -> work graph
migration target -> package matrix
review target -> finding classes
bug report -> reproduction search tree
```

Owners: `$goal-workgraph`, `repo_scout` fanout.

### Hylomorphism: unfold work and fold evidence

Use for ordinary goal execution.

```text
state -> next work -> action -> evidence -> new state
```

Owners: `$agent-loop-schemes` for HYL definition, `$goal-actuating` for HYL interpretation.

### Paramorphism: fold while keeping original structure

Use when edits require both summarized meaning and original spans/files.

Examples:

```text
AST-aware refactor
API migration with original call-site preservation
review disposition that still needs exact diff context
```

Route: produce work nodes with file/span anchors; avoid summary-only patches.

### Apomorphism: unfold while reusing solved pieces

Use when known patterns, codemods, templates, or previous fixes can be plugged in.

Examples:

```text
known migration script
previous package solution
existing adapter/helper
reused test harness
```

Route: add `reuse` nodes and cite proof surface.

### Histomorphism: history-aware fold

Use when prior attempts matter.

Examples:

```text
debugging that oscillates
review findings that reappear
failed strategies that should not repeat
```

Owners: `$failure-memory`, attempt ledger, `$seq` if historical forensics are needed.

### Futumorphism: lookahead / future expansion

Use when multiple futures should be explored before choosing.

Examples:

```text
local fix vs refactor kernel
adapter layer vs producer-boundary fix
rollback vs forward migration
```

Owners: `branch_racer`, `$goal-workgraph` branch nodes.

### Zygomorphism: artifact plus proof sidecar

Use when every implementation result must carry proof/risk.

Examples:

```text
security-sensitive patch
PR handoff
migration with rollback proof
review closure proof
```

Owners: `$proof-patch`, `$evidence-fold`, `$ship` for PR publication.

### Dynamorphism: memoized repeated subproblems

Use when repeated classes appear.

Examples:

```text
many compiler errors of same shape
many review comments sharing one cause
migration across packages
same test fixture failure across modules
```

Owners: `$failure-memory`; solve representative class before bulk application.

### Chronomorphism: history plus lookahead

Use for long-horizon work that needs both attempt memory and branch choices.

Examples:

```text
hard bug with competing theories
multi-round review/fix campaign
performance tuning with repeated benchmark classes
```

Route: combine `$failure-memory`, branch-race, and evidence folds.

### Metamorphism: transform old representation to new representation

Use when the core work is a structured migration.

Examples:

```text
old API -> new API
old config format -> new config format
old state machine -> normalized state owner
```

Route: fold old structure into an intermediate model, then unfold new implementation. Prefer proof over local patching.

### Mutumorphism: mutually recursive decomposition

Use when subproblems are interdependent and must be solved as a system.

Examples:

```text
client/server protocol changes
type/schema/test fixture co-evolution
multi-package dependency cycles
```

Route: do not patch in parallel unless the dependency cycle is broken. Consider `$st`.

### Parallel traversal

Use when the work unfolds into independent leaves.

Examples:

```text
repo_scout fanout
review-class fanout
proof fanout
disjoint patch fanout
```

Route: subagents can work on leaves, but the lead owns fan-in, integration, proof, CAS clean-run counting, and `$ship`.

## Handoff to `$agent-loop-schemes`

When a Scheme Plan selects any material recursive loop, hand off to `$agent-loop-schemes` to compile:

```text
Scheme Plan -> ALSR-v1 -> HYL-v1
```

Skip ALSR/HYL compilation only when the work is direct-action fused or `$st` owns execution.

## Final answer shape

```text
Scheme Plan:
- selected scheme(s):
- why:
- work shape:
- decomposition:
- parallelism:
- memory:
- proof:
- HYL required: yes|no
- stop condition:
- handoff:
```

Keep it short. Do not explain theory unless the user asks.
