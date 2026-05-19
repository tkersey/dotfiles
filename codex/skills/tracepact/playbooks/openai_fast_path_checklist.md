# OpenAI fast-path checklist

Use this checklist whenever a trace uses OpenAI models, Responses API, function calling, Agents SDK, or OpenAI-compatible routing.

## Responses and tool-loop shape

- Are simple model/tool/model loops split into unnecessary external requests?
- Are function calls handled as a batch when multiple calls appear?
- Are independent function calls executed concurrently in the application?
- Are tool outputs appended compactly and with the correct `call_id`?
- Does the agent use structured outputs when the application needs JSON?
- Are repeated continuations using `previous_response_id` where appropriate?
- Would WebSocket mode reduce overhead for long tool-heavy chains?

## Streaming and user-perceived latency

- Is `stream=true` used for long generations?
- Is the first useful UI update emitted before all hidden work completes?
- Are function-call deltas surfaced when useful for progress?
- Is unsafe or unverified content withheld while safe progress is streamed?

## Prompt caching

- Are static instructions, examples, tool definitions, and schemas first?
- Are timestamps, random IDs, shuffled JSON, dynamic tool order, user data, and history kept after the static prefix?
- Is `usage.prompt_tokens_details.cached_tokens` logged?
- Is `cached_tokens / input_tokens` computed per request and by route?
- Is `prompt_cache_key` used consistently for shared prefixes?
- Are long prompts over 1024 tokens structured to maximize exact prefix reuse?

## Model routing

- Is a reasoning model used only where ambiguity, planning, or high-reliability synthesis demands it?
- Are classification, formatting, extraction, routing, and validation tasks handled by fast models or deterministic code?
- Is `reasoning_effort` logged and justified for each route?
- Is there a fast path for easy requests?
- Does a planner assign bounded tasks to faster executors instead of holding the whole workflow in a slow model?

## Tool surfaces

- Are rarely used tools deferred via tool search or a dispatcher?
- Are tool schemas concise, stable, and cache-friendly?
- Are tool outputs bounded by schema and token budget?
- Are retrieval tools returning answer slices instead of raw documents?
- Are mutating tools explicitly marked with authority, idempotency, branch, replay, and rollback policy?

## Tracing

- Does every model call have timing, usage, cache, model, reasoning, streaming, and route metadata?
- Does every tool call have timing, args hash, result bytes/tokens, mutability, cacheability, and consumed-by metadata?
- Are guardrails, handoffs, state loads, queue waits, DB calls, vector searches, render steps, and cache lookups traced as custom spans?
- Are first token, first useful UI update, final answer, and irreversible action timestamps logged?

## CI latency treaty gates

Add regression checks such as:

- No extra serial model request on the dominant route unless a treaty blocker is declared.
- p95 TTFU must not regress beyond threshold.
- Cached-token ratio must not drop for cacheable routes.
- Tool result bytes must stay under budget.
- Mutating tools must declare linearity/idempotency and rollback/cancel semantics.
