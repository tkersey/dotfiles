# Ability / Effect Treaties bridge

This playbook adapts the latency skill to an Ability-style defunctionalized execution substrate.

## PR #109 lens

Effect Treaties introduced these concepts into `tkersey/ability`:

- provider offers
- morphism offers
- treaty requests
- treaty policies
- structured treaty blockers
- treaty certificates
- treaty authorization
- deterministic resolver behavior
- least-authority attenuation
- replay/usage/branch constraints

For latency work, this is the right abstraction. The agent loop should not be an opaque series of prompts. It should be a typed exchange where every effect boundary has enough metadata to decide whether a faster route is legal.

## Mapping from agent traces to Ability concepts

| Agent trace concept | Ability/treaty concept | Latency use |
|---|---|---|
| Model call | provider offer | choose model by task, latency, quality, context, authority |
| Tool call | provider offer | declare mutability, byte limits, replayability, idempotency |
| Tool adapter | morphism offer | adapt a source request to a target provider/tool/protocol |
| Guardrail | treaty policy | enforce safety before/after/parallel, not accidentally late |
| Cache hit | replay route | avoid fresh work when replay is legal |
| User approval | linear/affine obligation | prevent duplicate irreversible actions |
| Trace replay | journal/certificate | prove rewrite equivalence |
| Branch exploration | capsule/branch policy | speculate safely or reject unsafe fresh branches |
| Tool result summary | response authorization | bound what crosses back into model context |

## The radical architecture

```text
User task
  -> typed Program/Protocol request
  -> treaty resolver chooses route:
       direct deterministic handler
       cached replay
       fast model
       reasoning planner
       retrieval answer-slice provider
       mutating provider with linear obligation
       human approval provider
       rejected with structured blocker
  -> provider harness validates and executes
  -> response envelope with authorization sidecar
  -> journal event for replay and eval
  -> model sees only the minimum authorized answer slice
```

## What this buys you

- Latency decisions become deterministic pre-model routing where possible.
- Mutating actions stay safe because linear/affine obligations block unsafe parallelism.
- Read-only/replayable effects can parallelize or move earlier.
- Model context shrinks because providers return typed answer slices.
- Trace replay becomes a first-class eval harness.
- Prompt engineering stops carrying policy, authority, and routing burden that belongs in typed exchange metadata.

## Review questions

Ask these questions against any Ability-like agent trace:

1. Which yielded sites are entropy-bearing and need an LLM?
2. Which sites can be handled by deterministic providers?
3. Which provider offers have byte budgets and response schemas?
4. Which effects are replayable and journaled?
5. Which effects are linear/affine and therefore must not be speculated or duplicated?
6. Which morphism offers could compile a slow source protocol into a faster target protocol?
7. Which treaty blockers appear because metadata is missing rather than because a real dependency exists?
8. Which spans are not causal witnesses for the final answer?

## Implementation pattern

1. Add effect metadata to every agent operation.
2. Define provider offers with max latency, byte limits, cache policy, replay policy, and mutability.
3. Define morphism offers for common adaptations.
4. Resolve route before model invocation.
5. Use model only for unresolved entropy-bearing decisions.
6. Journal request, route, response, authorization, and final answer.
7. Replay old journals under the new treaty resolver in CI.
