# Implementation patterns for OpenAI prompt caching

This file translates the official docs into engineering patterns that are easier to apply during a code review.

## Pattern 1: Stable prefix, dynamic suffix

**Goal:** maximize repeated prefix tokens.

**Stable prefix**
- instructions / developer prompt
- tools
- output schema
- repeated repo or environment context
- stable assistant / reasoning items
- compaction items

**Dynamic suffix**
- current user turn
- live retrieval results
- current tool outputs
- timestamps or per-request IDs

### Good
- Build instructions once.
- Keep tool ordering fixed.
- Append volatile context after the stable prefix.
- Reuse the same schema object.

### Bad
- Insert `Date.now()` or a trace ID in the first system/developer message.
- Sort tools differently every call.
- Inline only the currently allowed tools and rebuild the array every turn.
- Re-summarize prior context differently on every request.

## Pattern 2: Stable full toolset + per-turn restriction

When you need a subset of tools on a single turn:

**Prefer**
- one stable `tools` array
- per-turn restriction via `tool_choice.allowed_tools`

**Avoid**
- deleting or reordering tool definitions on every turn

Why this matters:
- changing the `tools` array changes early request tokens
- `allowed_tools` lets you constrain behavior without mutating the cacheable prefix

## Pattern 2b: Large tool surfaces

If the full tool surface is so large that keeping every tool in the prefix is itself expensive or unstable:

**Prefer**
- tool search or another deferred-tool loading mechanism
- stable namespace/group boundaries
- loading a subset once, then constraining that subset with `allowed_tools`

**Avoid**
- dynamically rebuilding hundreds of tool definitions every turn

The main objective is still the same: preserve a stable, repeated prefix.

## Pattern 3: Responses state choices

### Option A: `previous_response_id`
Use when:
- you want simple chained turns
- you want to send only new user/tool items
- you want OpenAI to carry forward prior state for the chain

Tradeoffs:
- easiest pattern for many agent loops
- if behavior depends on `instructions`, resend them because prior `instructions` are not implicitly preserved

### Option B: `conversation`
Use when:
- you want a durable conversation object
- state must live across sessions, devices, or jobs

Tradeoffs:
- convenient for longer-lived app workflows
- still requires deliberate prompt design for stable repeated prefixes

### Option C: manual replay
Use when:
- you need full client-side control
- you are operating in a stateless pattern intentionally

Tradeoffs:
- easiest to get wrong
- replay shape, assistant fields, and ordering all affect caching
- you must preserve assistant items faithfully in GPT-5.4 tool-heavy flows

## Pattern 4: `store=false` / ZDR with reasoning models

If you use reasoning models without durable server state:

- include `reasoning.encrypted_content`
- pass reasoning items forward between turns
- do not assume a missing response ID can always be recovered server-side

This is especially important if you are auditing a harness that expects Responses to “remember” prior work but also runs with `store=false`.

## Pattern 5: Compaction

Use compaction when:
- context size is becoming expensive
- latency is drifting because of transcript growth
- you need a controlled way to preserve key state but reduce replay size

Be careful:
- compaction changes the prompt history
- compaction can reduce caching if it changes the prefix frequently
- when using `previous_response_id`, follow the documented pattern and do not manually prune old items in the chain

### Good compaction review questions
- How often does compaction happen?
- Does compaction happen in large deliberate chunks or constant tiny shifts?
- What metric matters more here: recall/intelligence or cache stability?
- Is compaction actually cheaper once the lost cache reuse is considered?

## Pattern 6: Logging and observability

A prompt-caching-aware harness should log at least:

- model
- response ID
- prompt/input token count
- cached token count
- reasoning effort
- prompt cache key
- retention policy
- latency
- whether the request reused prior state (`previous_response_id`, `conversation`, manual replay)

Useful derived metrics:
- cached tokens / input tokens
- percent of eligible requests with any cache hit
- p50 / p95 latency for cached vs uncached requests
- zero-hit rate for requests above 1024 tokens
- hit rate by model
- hit rate by cache key
- hit rate before and after compaction or tool changes

## Pattern 7: WebSocket continuation and warmup

For long tool-call-heavy workflows:

**Prefer**
- WebSocket mode if continuation latency matters
- incremental input + `previous_response_id`
- optional `generate: false` warmup when you already know the tools/instructions/messages you will use soon

Why this matters:
- the active socket retains one recent response in connection-local memory
- incremental continuation lowers per-turn overhead
- warmup can prepare request state before a later generated turn

Be careful:
- with `store=false`, there is no persisted fallback if a previous response falls out of the in-memory cache
- handle `previous_response_not_found`
- this is an advanced optimization on top of good prompt design, not a substitute for it

## Common anti-patterns

### Anti-pattern: tool-array churn
Symptom:
- `cached_tokens` drop after every turn
Cause:
- tool definitions are rebuilt or reordered
Fix:
- freeze the full toolset and gate per turn with `allowed_tools`

### Anti-pattern: top-of-prompt volatility
Symptom:
- almost no repeated prefix even though the harness looks “similar”
Cause:
- timestamps, UUIDs, run IDs, or user-specific headers are placed near the top
Fix:
- move volatile data later or out of the model input

### Anti-pattern: Chat Completions for complex reasoning loop
Symptom:
- higher latency and weaker cache reuse in tool-heavy multi-turn reasoning flows
Cause:
- reasoning state is not preserved the same way
Fix:
- migrate to Responses and use `previous_response_id` or `conversation`

### Anti-pattern: overgrown replay history
Symptom:
- cost and latency climb over time, then cache stability collapses once truncation begins
Cause:
- no compaction / no context management plan
Fix:
- add compaction and evaluate the balance between context retention and cache stability

### Anti-pattern: cache key misuse
Symptom:
- misses remain high even with stable-looking prompts
Cause:
- key is absent, random, too broad, or too narrow
Fix:
- choose a routing-friendly stable key that matches the long repeated prefix

### Anti-pattern: stateless reasoning without encrypted carryover
Symptom:
- tool-heavy reasoning chains get slower or less coherent in `store=false` / ZDR mode
Cause:
- reasoning items are not being carried forward
Fix:
- request and replay `reasoning.encrypted_content`

## Practical review checklist

When reading a harness, answer these questions in order:

1. Which API is being used?
2. How is state carried forward?
3. What exactly is repeated between turns?
4. Is the repeated region at least ~1024 tokens?
5. Which early tokens vary unexpectedly?
6. Is the toolset stable?
7. Is the schema stable?
8. Is the cache key stable?
9. Is retention chosen intentionally?
10. Are `cached_tokens` and latency logged?
11. Is truncation/compaction changing the prefix?
12. Is stateless reasoning carrying encrypted reasoning items?
13. Would WebSocket continuation help this tool-heavy loop?
14. What single code change yields the largest improvement first?
