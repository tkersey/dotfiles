# Instrumentation and CI

## Required trace fields

At minimum, log:

- `trace_id`, `span_id`, `parent_id`, `kind`, `name`
- `start_ms`, `end_ms`, `duration_ms`, `status`
- `depends_on` and dependency reason when known
- `user_visible`: none/progress/partial/final/irreversible_action
- `model`, `reasoning_effort`, `input_tokens`, `cached_tokens`, `output_tokens`, `reasoning_tokens`
- `streaming_used`, `time_to_first_token_ms`, `time_to_first_user_visible_update_ms`
- `tool_name`, args hash, result bytes, result token estimate
- `mutability`, `usage_policy`, `freshness_policy`, `authority_policy`, `branch_policy`
- `consumed_by` or `result_consumed: true/false`

## Useful derived metrics

- model requests per user task
- tool calls per user task
- serial depth
- critical-path model time
- critical-path tool time
- idle gap time
- TTFU
- final latency
- first irreversible action latency
- input/output/reasoning token totals
- cached-token ratio
- tool result bytes/tokens
- retry count
- handoff count
- cache hit rate

## CI gates

Use gates like:

```yaml
latency_treaty_gates:
  dominant_route:
    max_serial_model_calls: 2
    max_p95_ttfu_ms_regression: 250
    min_cache_hit_ratio_for_cacheable_routes: 0.60
    max_tool_result_bytes_on_model_path: 12000
    require_mutation_treaty: true
    require_dependency_reason_for_serial_tool_calls: true
```

## Regression test pattern

1. Capture a golden trace with final answer and tool outputs.
2. Normalize it.
3. Run TracePact.
4. Apply rewrite behind a feature flag.
5. Replay or re-run the task set.
6. Assert:
   - answer quality is equal or better
   - safety outcomes are unchanged
   - no duplicate mutations occur
   - TTFU/final latency budget improves or does not regress
   - token/cache/tool metrics stay within budget

## Redaction

Before exporting traces, redact:

- secrets
- API keys
- OAuth tokens
- user identifiers
- PII
- raw customer documents
- tool outputs that include private data
- full prompts if they contain confidential system instructions

Keep stable hashes and byte/token counts when content must be removed.
