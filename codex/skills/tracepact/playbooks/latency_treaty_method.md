# Latency Treaty Method

## 1. Treat the trace as one observed execution, not the program

The observed run is a sample. The treaty is the program-level contract you infer from it.

Ask:

- Which spans were causal witnesses?
- Which spans merely happened before the answer?
- Which spans could have run earlier, later, in parallel, once per session, or never?
- Which spans are mutating and therefore require linearity/idempotency proof?
- Which spans are policy checks and therefore must be preserved but may move?

## 2. Build the dependency lattice

For every edge `A -> B`, label the edge:

- `data`: B consumes A output.
- `authority`: B is only allowed after A grants authority.
- `safety`: B is unsafe without A.
- `freshness`: B requires A's fresh result.
- `branch`: B depends on A's branch decision.
- `ui`: B should follow A for user experience.
- `resource`: B is serialized due to capacity/rate limit.
- `accidental`: no real requirement found.
- `unknown`: trace lacks evidence.

Only `data`, `authority`, `safety`, `freshness`, and real `branch` edges are hard semantic blockers.

## 3. Assign usage discipline

Borrowing the language of effect systems:

- `copyable`: can be duplicated freely; examples: pure formatting, static docs, deterministic transforms.
- `replayable`: can reuse previous output for the same request shape; examples: cached retrieval, deterministic classifiers, journaled tool reads.
- `affine`: may be used at most once; examples: one approval outcome, one fresh provider response.
- `linear`: must be used exactly once or explicitly cancelled; examples: payment capture, irreversible send, durable mutation with obligation.
- `ephemeral`: cannot be persisted/replayed; examples: secret-bearing data, single-use credentials, time-sensitive approval tokens.

Latency optimizations are easiest for copyable/replayable effects and dangerous for linear/ephemeral effects.

## 4. Identify provider offers

For each operation, list alternative providers:

- current LLM model
- smaller/faster LLM model
- deterministic code
- cached result
- retrieval answer-slice provider
- tool dispatcher
- policy engine
- human approval
- background worker
- WebSocket continuation
- structured-output one-shot call

Each offer gets latency, cost, quality, authority, cacheability, and failure semantics.

## 5. Generate morphism offers

A morphism offer is a legal adaptation from one effect surface to another:

- free-form LLM output -> structured JSON output
- raw retrieval docs -> compressed answer slice
- natural-language tool router -> deterministic function dispatcher
- multi-agent handoff -> typed provider call
- repeated planner call -> cached plan template
- model policy check -> deterministic policy table plus LLM fallback
- serial tool calls -> parallel batch call
- repeated function call loop -> Responses/WebSocket continuation

A morphism is not legal just because it is faster. It must preserve the answer, safety, authority, and freshness contract.

## 6. Produce the counterfactual schedule

For each proposed rewrite, describe:

- what starts earlier
- what starts later
- what runs in parallel
- what collapses into one call
- what becomes cached/replayed
- what becomes deterministic
- what streams to the user
- what stays linear and ordered
- what proof/eval is required

## 7. Turn the report into a patch

A strong latency report ends with implementation artifacts:

- feature flag name
- code path to change
- instrumentation fields to add
- eval set to run
- safety invariants
- rollback plan
- CI budget
- expected p50/p95/TTFU impact

## 8. Do not optimize the wrong path

Remove non-critical work only after you know whether it affects:

- TTFU
- final answer latency
- irreversible action latency
- throughput/rate limit saturation
- cost
- quality/safety

Many teams cut background tokens while leaving the critical path unchanged. This skill should not make that mistake.
