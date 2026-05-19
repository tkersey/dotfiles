# TracePact Report

## 1. Verdict

Highest-leverage observed issue: Consecutive model calls may be collapsible or routable (ROUND_TRIP_AMPLIFICATION). Rewrite: Combine steps into one structured call, or split once into planner plus deterministic/fast executor only when the first call produces a consumed plan.

## 2. Metrics

- **span_count**: 7
- **end_to_end_ms**: 7650ms
- **critical_path_duration_ms**: 5880ms
- **time_to_first_useful_output_ms**: 7350ms
- **model_request_count**: 3
- **tool_call_count**: 3
- **guardrail_count**: 1
- **handoff_count**: 0
- **retry_count**: 0
- **input_tokens**: 28500
- **cached_tokens**: 1200
- **cache_hit_ratio**: 4.21%
- **output_tokens**: 1270
- **reasoning_tokens**: 180
- **tool_result_bytes**: 97700

## 3. Critical path approximation

- **duration**: 5880ms
- **path**:
  - `m1` — planner (o4-mini)
  - `t1` — retrieval:web_search
  - `m2` — synthesize_tool_results (gpt-5.5)
  - `m3` — format_final_answer (gpt-5.5)
  - `g1` — guardrail:posthoc_policy_check

## 4. Latency Treaty IR

| id | op | usage | freshness | authority | branch | critical role | proof needed |
|---|---|---|---|---|---|---|---|
| m1 | planner (o4-mini) | replayable | unknown | unknown | unrestricted | causal_witness | freshness_policy |
| t1 | retrieval:web_search | replayable | cache_ok | unknown | unrestricted | causal_witness | — |
| t2 | tool:customer_db_lookup | replayable | cache_ok | unknown | unrestricted | movable_witness | — |
| t3 | retrieval:web_search | replayable | cache_ok | unknown | unrestricted | movable_witness | — |
| m2 | synthesize_tool_results (gpt-5.5) | replayable | unknown | unknown | unrestricted | causal_witness | freshness_policy |
| m3 | format_final_answer (gpt-5.5) | replayable | unknown | unknown | unrestricted | causal_witness | freshness_policy |
| g1 | guardrail:posthoc_policy_check | replayable | unknown | unknown | unrestricted | treaty_blocker | freshness_policy |

## 5. Findings

### F01: Consecutive model calls may be collapsible or routable

- **Category**: `ROUND_TRIP_AMPLIFICATION`
- **Severity**: high
- **Impact**: final
- **Expected savings**: one or more model round trips if semantic dependencies are accidental
- **Confidence**: medium
- **Effort**: M
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - m2: synthesize_tool_results (gpt-5.5), duration=2580.0ms
  - m3: format_final_answer (gpt-5.5), duration=850.0ms
- **Rewrite**: Combine steps into one structured call, or split once into planner plus deterministic/fast executor only when the first call produces a consumed plan.
- **Proof needed**: verify second call consumes unique output from first, quality eval for collapsed prompt
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F02: Repeated equivalent tool call: web_search

- **Category**: `DUPLICATE_TOOL_CALL`
- **Severity**: high
- **Impact**: final
- **Expected savings**: up to 720ms observed duplicate tool time
- **Confidence**: high
- **Effort**: S
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - t1: args_hash=search-retention-v1, duration=800.0ms
  - t3: args_hash=search-retention-v1, duration=720.0ms
- **Rewrite**: Memoize/journal the first result inside the run; for durable routes, add freshness and replay policy before reusing across runs.
- **Proof needed**: freshness_policy, result equivalence, result was consumed identically
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F03: Read-only tools appear serialized

- **Category**: `SERIAL_READ_ONLY_TOOLS`
- **Severity**: high
- **Impact**: final
- **Expected savings**: up to 1490ms if independent
- **Confidence**: medium
- **Effort**: S
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - t1: retrieval:web_search, duration=800.0ms, usage=replayable
  - t2: tool:customer_db_lookup, duration=770.0ms, usage=replayable
  - t3: retrieval:web_search, duration=720.0ms, usage=replayable
- **Rewrite**: Execute independent read-only tool calls concurrently, or issue them as a batch provider offer; preserve ordering only for data/authority/freshness edges.
- **Proof needed**: no data dependency between tools, read-only/idempotent proof, rate-limit budget
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F04: Large tool result sent through agent loop: retrieval:web_search

- **Category**: `TOOL_RESULT_BLOAT`
- **Severity**: high
- **Impact**: final
- **Expected savings**: input-token/prefill reduction and often fewer downstream summarization calls
- **Confidence**: high
- **Effort**: M
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - t1: result_bytes=46000, result_tokens=None
- **Rewrite**: Change the provider contract to return a bounded answer slice: facts, citations/ids, confidence, and omitted-result count. Keep raw payload outside the model path.
- **Proof needed**: consumer only needs answer slice, answer-slice eval
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F05: Large tool result sent through agent loop: retrieval:web_search

- **Category**: `TOOL_RESULT_BLOAT`
- **Severity**: high
- **Impact**: final
- **Expected savings**: input-token/prefill reduction and often fewer downstream summarization calls
- **Confidence**: high
- **Effort**: M
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - t3: result_bytes=45500, result_tokens=None
- **Rewrite**: Change the provider contract to return a bounded answer slice: facts, citations/ids, confidence, and omitted-result count. Keep raw payload outside the model path.
- **Proof needed**: consumer only needs answer slice, answer-slice eval
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F06: Long model prompt has poor cache reuse: planner (o4-mini)

- **Category**: `LOW_CACHED_TOKEN_RATIO`
- **Severity**: medium
- **Impact**: throughput
- **Expected savings**: lower prefill latency/cost for repeated long-prefix routes
- **Confidence**: high
- **Effort**: S
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - m1: input_tokens=5200, cached_tokens=0, ratio=0.00, prompt_cache_key=None
- **Rewrite**: Move static instructions/examples/tools/schemas to the exact prefix, move dynamic history/RAG/user data later, stabilize JSON/tool ordering, and set a route-appropriate prompt_cache_key.
- **Proof needed**: stable prefix hash, cache hit ratio dashboard
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F07: Long model prompt has poor cache reuse: synthesize_tool_results (gpt-5.5)

- **Category**: `LOW_CACHED_TOKEN_RATIO`
- **Severity**: medium
- **Impact**: throughput
- **Expected savings**: lower prefill latency/cost for repeated long-prefix routes
- **Confidence**: high
- **Effort**: S
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - m2: input_tokens=17200, cached_tokens=1200, ratio=0.07, prompt_cache_key=None
- **Rewrite**: Move static instructions/examples/tools/schemas to the exact prefix, move dynamic history/RAG/user data later, stabilize JSON/tool ordering, and set a route-appropriate prompt_cache_key.
- **Proof needed**: stable prefix hash, cache hit ratio dashboard
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F08: Long model prompt has poor cache reuse: format_final_answer (gpt-5.5)

- **Category**: `LOW_CACHED_TOKEN_RATIO`
- **Severity**: medium
- **Impact**: throughput
- **Expected savings**: lower prefill latency/cost for repeated long-prefix routes
- **Confidence**: high
- **Effort**: S
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - m3: input_tokens=6100, cached_tokens=0, ratio=0.00, prompt_cache_key=None
- **Rewrite**: Move static instructions/examples/tools/schemas to the exact prefix, move dynamic history/RAG/user data later, stabilize JSON/tool ordering, and set a route-appropriate prompt_cache_key.
- **Proof needed**: stable prefix hash, cache hit ratio dashboard
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

### F09: Large model output likely dominates decode latency: synthesize_tool_results (gpt-5.5)

- **Category**: `EXCESSIVE_OUTPUT_TOKENS`
- **Severity**: medium
- **Impact**: ttfu
- **Expected savings**: decode latency roughly scales with generated tokens; TTFU improves with streaming
- **Confidence**: high
- **Effort**: S
- **Quality risk**: low
- **Safety risk**: low
- **Evidence**:
  - m2: output_tokens=640, streaming_used=False
- **Rewrite**: Use a shorter answer contract, structured fields, max output budget, or progressive rendering. If the long output is necessary, stream safe partial content.
- **Proof needed**: quality eval for shorter output, streaming safety gate
- **Rollback**: Feature flag or route fallback
- **Validation**: Replay traces and compare quality/latency

## 6. Counterfactual schedules

### parallel_read_only_effects
- **Rewrite**: Group independent read-only tool/retrieval calls after the planning boundary and execute them concurrently; return compact answer slices to the final model call.
- **Legality**: Legal only for read-only/idempotent effects with no data dependency between them and acceptable freshness/cache policy.
- **Risk**: May increase provider load or rate-limit pressure; cap concurrency and preserve cancellation.
- **Validation**: Trace dependency reasons, compare final quality, monitor rate limits and tool failure fanout.

### collapse_serial_model_round_trips
- **Rewrite**: Replace serial planner/executor/formatter model calls with one structured response or a planner once plus deterministic/fast executor steps.
- **Legality**: Legal if intermediate natural language is not a required user-visible artifact and downstream calls consume only structured decisions.
- **Risk**: Prompt complexity may rise; validate accuracy and parse stability.
- **Validation**: Golden eval tasks, parse-failure rate, model-request count per task, p95 final latency.

### stable_prefix_cache_treaty
- **Rewrite**: Freeze instructions, examples, tool schemas, and structured output schema at the prompt prefix; move dynamic content later; set prompt_cache_key by route/prefix family.
- **Legality**: Semantics unchanged if only prompt ordering changes and the final prompt content remains equivalent.
- **Risk**: Accidental prompt behavior change from ordering; eval before rollout.
- **Validation**: cached_tokens/input_tokens by route, answer quality eval, p95 prefill latency.

### provider_answer_slice
- **Rewrite**: Change tools/retrievers to return bounded answer slices with ids/citations/confidence instead of raw documents or full payloads in the model path.
- **Legality**: Legal if the downstream model only requires the slice; raw payload can remain available outside the model path for audit/drilldown.
- **Risk**: Could omit relevant context; use retrieval eval and fallback expansion.
- **Validation**: Answer quality, omitted-context error rate, tool result token budget, fallback expansion rate.

## 7. Patch plan

- Add per-run tool-result memoization keyed by tool name, normalized args hash, freshness policy, and authority scope.
- Introduce an async tool batch executor for read-only/idempotent effects; require dependency reasons for serial edges.
- Refactor planner/executor sequence into one structured model response or a planner-once plus deterministic executor path.
- Refactor prompt builder into static_prefix + dynamic_suffix; sort JSON/tool schemas deterministically; set prompt_cache_key by prefix family.
- Modify providers to return compact answer slices and keep raw payloads in external storage by id.
- Enable streaming on long-generation routes and add a safe progress/partial-output UI path.
- Ship behind a feature flag; compare old/new routes on golden traces and production canary.

## 8. Validation plan

- Replay golden traces and compare final outputs, tool outputs, and safety decisions.
- Track p50/p95/p99 end-to-end latency, TTFU, model request count, tool call count, serial depth, and idle gaps.
- Track input, cached, output, reasoning, retrieval, and tool-result tokens by route.
- Add a CI gate: no new serial model round trip on the dominant route without an explicit treaty blocker.
- Add cache-hit dashboard: cached_tokens / input_tokens by prompt prefix and prompt_cache_key.
- Add answer-slice retrieval eval: compact tool output must preserve answer quality and citations/ids.
- A/B concurrency limits and monitor rate limits, provider errors, and tail latency.
