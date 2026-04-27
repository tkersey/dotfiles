# Profiling LLM / AI Applications

> Profiling apps that call LLM APIs (Claude, GPT, Gemini, Llama, etc.) or run local inference. Different metrics, different bottlenecks, different tradeoffs.

## Contents

1. [The metrics that matter](#the-metrics-that-matter)
2. [TTFT, TPOT, end-to-end — defined](#ttft-tpot-end-to-end--defined)
3. [Token counts and budgeting](#token-counts-and-budgeting)
4. [Prompt caching — the single biggest lever](#prompt-caching--the-single-biggest-lever)
5. [Streaming latency](#streaming-latency)
6. [Provider comparison](#provider-comparison)
7. [Local inference profiling](#local-inference-profiling)
8. [Observability: OpenTelemetry GenAI conventions](#observability-opentelemetry-genai-conventions)
9. [Instrumentation with the Anthropic SDK](#instrumentation-with-the-anthropic-sdk)
10. [Common LLM perf pathologies](#common-llm-perf-pathologies)
11. [Vercel AI SDK specifics](#vercel-ai-sdk-specifics)
12. [Cost vs latency tradeoffs](#cost-vs-latency-tradeoffs)

---

## The metrics that matter

Not latency, throughput, or RSS — or rather, not only those. For an LLM app you care about:

| Metric | Definition | Why it matters |
|--------|------------|----------------|
| **TTFT** (Time to First Token) | Client send → first token received | Perceived responsiveness; chat UX depends on this |
| **TPOT** (Time per Output Token) | Average ms/token during streaming | Reading pace; streaming feel |
| **Total generation time** | Client send → last token received | Total wait on non-streamed flows |
| **Input tokens** | Prompt size | Cost driver; latency contributor at very large contexts |
| **Output tokens** | Response size | Cost + time driver (TPOT × output tokens) |
| **Cache hit rate** | % of input tokens served from prompt cache | The biggest single cost and latency reducer |
| **Cost per request** | $ per query | Product economics |
| **Retry rate** | % of requests that retried | Reliability; hides latency tail |
| **Rate-limit hit rate** | % of requests throttled | Throughput ceiling signal |

---

## TTFT, TPOT, end-to-end — defined

A typical LLM request timeline:

```
t0 ── client.send ────── network ───── queue at provider ───── prefill ───── first token sent
│                                                                                    │
│                                                                                    ▼
│                                                                            TTFT ends here
│                                                                                    │
│                                                                                    ▼
│                                                                        streaming decode
│                                                                        token by token...
│                                                                                    │
│                                                                                    ▼
│                                                                        last token sent
│                                                                                    │
▼                                                                                    ▼
t0                                                                                t_end

E2E = t_end - t0
TTFT = (first token received time) - t0
TPOT = (E2E - TTFT) / output_tokens    (mean per-token decode latency)
```

### Where time goes at large contexts

- **Prefill** (scanning input context): scales with input tokens, typically dominant for long prompts
- **Decode** (generating output): scales with output tokens × TPOT
- **Network**: typically tens of ms but scales with payload size
- **Queue**: highly variable, often the tail source

Rule of thumb: long-context, short-output requests are prefill-bound. Short-context, long-output are decode-bound.

### Capture per-request

```python
from time import perf_counter

t0 = perf_counter()
first_token_time = None
output_tokens = 0

with client.messages.stream(...) as stream:
    for chunk in stream:
        if first_token_time is None and chunk.type == "content_block_delta":
            first_token_time = perf_counter()
        if chunk.type == "content_block_delta":
            output_tokens += 1  # approximate; proper count comes at end
    # final totals from stream.final_message
    final = stream.get_final_message()
    output_tokens = final.usage.output_tokens
    input_tokens = final.usage.input_tokens
    cache_read = final.usage.cache_read_input_tokens or 0

t_end = perf_counter()

metrics = {
    "ttft_ms": (first_token_time - t0) * 1000,
    "e2e_ms": (t_end - t0) * 1000,
    "tpot_ms": ((t_end - first_token_time) / output_tokens) * 1000,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "cache_hit_pct": cache_read / input_tokens * 100 if input_tokens else 0,
}
```

---

## Token counts and budgeting

### Before the call: estimate

- **Claude**: `client.messages.count_tokens(...)` (or use `tiktoken` compatible approximation)
- **OpenAI**: `tiktoken` (encoding depends on model)
- **Local (llama.cpp etc.)**: tokenizer is bundled with model

Budget:
- **Claude context windows**: 200K standard, 1M for extended context models. Going over = HTTP 400.
- **Output max**: typically 4K-8K tokens; larger models accept 32K+. Request-side cap via `max_tokens`.

### After the call: record

Every production call should log:
```
input_tokens
output_tokens
cache_creation_input_tokens    (Claude specific)
cache_read_input_tokens        (Claude specific)
stop_reason                    (end_turn / max_tokens / stop_sequence / tool_use)
```

Histogram these across requests; outliers indicate prompt templates that grew unexpectedly or runaway generations.

---

## Prompt caching — the single biggest lever

Modern providers (Claude, OpenAI, Gemini) support prompt caching: repeated prompt prefixes are cached server-side; subsequent requests with the same prefix charge less and return faster.

### Claude prompt caching

- Cache breakpoints via `cache_control: {"type": "ephemeral"}` in system / messages blocks
- Cache hit: input tokens served from cache cost 10% of normal rate (Claude Opus 4.x)
- Cache TTL: 5 min standard, 1 hour extended; cache write costs 25% more than a normal input token
- Breakeven: prompt reused ≥ 2 times pays back the write cost

**Measure**:

```python
usage = response.usage
total_input = usage.input_tokens
cache_read = usage.cache_read_input_tokens or 0
cache_create = usage.cache_creation_input_tokens or 0
hit_rate = cache_read / (total_input + cache_read) if (total_input + cache_read) > 0 else 0

log.info("claude.cache",
    total_input=total_input,
    cache_read=cache_read,
    cache_create=cache_create,
    hit_rate=hit_rate,
    cost_saved=cache_read * 0.9 * price_per_input_token)
```

### When caching is the fix

- Prompt prefix (system, tools, docs, examples) is > 1024 tokens AND stable across requests
- Request rate to the same prefix is > 1/5min
- Cost savings × request volume justifies the (minor) code complexity

### When it's not

- Each request has a unique prefix (no commonality)
- Prefix is tiny (< 1024 tokens; below cache threshold for Claude)
- Request volume is low (< 10 requests per prefix per day)

### Claude prompt caching — placement

Cache breakpoints go at STABLE boundaries. Common layout:

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "text", "text": SYSTEM_TOOLS_SPEC,
             "cache_control": {"type": "ephemeral"}},      # long stable
            {"type": "text", "text": LARGE_DOC_CONTEXT,
             "cache_control": {"type": "ephemeral"}},      # long stable
            {"type": "text", "text": user_query}           # unique per request
        ]
    }
]
```

The last block has no cache_control — that's where the cache prefix ends and unique input begins.

---

## Streaming latency

Streaming is perceived responsiveness. Optimize TTFT hard.

### Techniques

1. **Minimize input tokens via caching** — prefill is the biggest TTFT contributor. Cache hit cuts prefill time.
2. **Streaming response upstream** — if your backend is streaming to a frontend, don't buffer. Use SSE / chunked.
3. **Pick a smaller model when quality permits** — Haiku (Claude), Mini (GPT), Flash (Gemini) have materially lower TTFT.
4. **Use provider-side edge deployment** — some providers offer geo-close endpoints.
5. **Avoid serialization cliffs** — don't `JSON.parse` large structured outputs inside the streaming path; parse at end.

### Anti-patterns

- `await client.messages.create(...)` (non-streaming) for chat UX — user stares at loading indicator for the full E2E
- Buffering the stream to re-emit at end — loses the point
- Per-chunk database writes — adds fsync latency per token

### Measure TTFT separately

TTFT alone is often more impactful than total time. A 2s E2E with 200ms TTFT feels faster than 1.5s E2E with 1s TTFT.

---

## Provider comparison

As of 2026-04:

| Provider | Model tier | Typical TTFT | Typical TPOT | Cache? | Notes |
|----------|------------|--------------|--------------|--------|-------|
| Claude (Anthropic) | Opus 4.7 | 500-1500ms | 15-30ms | Yes | Best long-context; prompt cache mature |
| Claude | Sonnet 4.6 | 300-700ms | 8-15ms | Yes | Balanced; cache same mechanism |
| Claude | Haiku 4.5 | 150-400ms | 5-10ms | Yes | Fastest Claude tier |
| OpenAI GPT-5.x | Standard | 400-1000ms | 10-20ms | Yes (automatic, 50% of tokens) | Auto-cache at ≥ 1024 tokens |
| OpenAI GPT-5 mini | Mini | 150-400ms | 5-10ms | Yes | |
| Gemini 3 Pro | Standard | 300-800ms | 10-25ms | Yes (context caching) | Explicit cache API |
| Gemini Flash | Fast | 150-400ms | 5-12ms | Yes | |
| Self-hosted llama.cpp | 70B quantized | 100-500ms | 30-80ms | Local; no network | GPU-dependent |
| Self-hosted vLLM | 70B bf16, A100/H100 | 50-200ms | 15-35ms | Local | Good throughput |

Times are coarse; real numbers depend on prompt length, concurrency, time of day, region.

**Always measure on your workload.** Provider benchmarks don't predict your p99.

---

## Local inference profiling

For self-hosted (llama.cpp, vLLM, TGI, Ollama, etc.):

### GPU metrics

```bash
# Continuous monitor
nvidia-smi dmon -s pucvmet -c 100
# (p)ower (u)tilization (c)lock (v)oltage (m)emory (e)ncode/decode (t)emperature

# Per-process
nvidia-smi pmon -s um -c 30

# For AMD (ROCm)
rocm-smi
```

### vLLM metrics

vLLM exposes Prometheus metrics:
```
vllm:num_requests_running
vllm:num_requests_waiting
vllm:time_to_first_token_seconds
vllm:time_per_output_token_seconds
vllm:gpu_cache_usage_perc
vllm:request_prefill_time_seconds
vllm:request_decode_time_seconds
```

### llama.cpp

`./llama-bench` and `./llama-cli` with `--verbose` prints prefill / decode throughput.

### Quantization tradeoffs

| Precision | Throughput | Quality | Memory |
|-----------|------------|---------|--------|
| fp32 | 1× | reference | 1× |
| fp16 / bf16 | 2× | ~indistinguishable | 0.5× |
| Q8_0 | 3× | very close | 0.25× |
| Q5_K_M | 5× | mild degradation | 0.16× |
| Q4_K_M | 6× | noticeable degradation | 0.125× |

Profile both throughput and quality (perplexity / task accuracy) when picking quant.

### Batching

- Continuous batching (vLLM, TGI) vs static — continuous wins on mixed-length workloads
- `max_num_seqs`, `max_num_batched_tokens` tune throughput/latency tradeoff
- Higher batch size → higher throughput, worse p99 TTFT

---

## Observability: OpenTelemetry GenAI conventions

OTel has defined semantic conventions for LLM calls. Emit these as span attributes:

```
gen_ai.system                  # "anthropic" | "openai" | "gemini"
gen_ai.request.model           # "claude-opus-4-7"
gen_ai.request.max_tokens      # 4096
gen_ai.request.temperature     # 1.0
gen_ai.response.model          # actual model used
gen_ai.response.finish_reasons # ["end_turn"]
gen_ai.usage.input_tokens      # 1234
gen_ai.usage.output_tokens     # 567
gen_ai.usage.input_tokens.cache_read    # (Anthropic extension)
gen_ai.usage.input_tokens.cache_create  # (Anthropic extension)
```

Span name: `chat <model>` or `completion <model>`.

Use OTel Python / TS / Rust SDKs with auto-instrumentation if available; fall back to manual spans around each `client.messages.create` / `chat.completions.create`.

### Linking metrics to traces

Emit a histogram alongside spans:
- `gen_ai.client.operation.duration` (histogram, seconds) — end-to-end
- `gen_ai.client.token.usage` (histogram, tokens) — for input and output, labeled by type

These roll up to dashboards, while spans give per-request drill-down.

---

## Instrumentation with the Anthropic SDK

```python
from anthropic import Anthropic
import logging, time, json

client = Anthropic()
log = logging.getLogger("llm")

def chat(messages, **kwargs):
    t0 = time.perf_counter()
    first_tok = None
    with client.messages.stream(model="claude-opus-4-7", messages=messages, **kwargs) as stream:
        for event in stream:
            if first_tok is None and event.type == "content_block_delta":
                first_tok = time.perf_counter()
        final = stream.get_final_message()
    t_end = time.perf_counter()

    u = final.usage
    log.info("claude.call", extra={
        "gen_ai.system": "anthropic",
        "gen_ai.request.model": kwargs.get("model", "claude-opus-4-7"),
        "gen_ai.response.model": final.model,
        "gen_ai.response.finish_reasons": [final.stop_reason],
        "gen_ai.usage.input_tokens": u.input_tokens,
        "gen_ai.usage.output_tokens": u.output_tokens,
        "gen_ai.usage.input_tokens.cache_read": u.cache_read_input_tokens or 0,
        "gen_ai.usage.input_tokens.cache_create": u.cache_creation_input_tokens or 0,
        "gen_ai.latency.ttft_ms": (first_tok - t0) * 1000 if first_tok else None,
        "gen_ai.latency.e2e_ms": (t_end - t0) * 1000,
        "gen_ai.latency.tpot_ms": ((t_end - first_tok) / max(u.output_tokens, 1)) * 1000 if first_tok else None,
    })
    return final
```

---

## Common LLM perf pathologies

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| TTFT climbs with each request | Cache not hitting; prefix changed | Inspect prompt; stabilize prefix; mark cache breakpoint |
| TPOT is high | Model too large for SLA | Cheaper/faster model tier; streaming; shorter outputs |
| E2E bimodal (fast/slow) | Cache miss vs hit | Log cache_read_input_tokens; hit rate should be > 70% for cacheable prefixes |
| Retry rate climbing | Rate-limit or 5xx | Exponential backoff with jitter; slow down; use a second key |
| Tool-use round-trips slow | Model → tool → model → tool loop | Minimize tool calls per task; batch tools where possible |
| Cost rose 5× week-over-week | Prompt grew; cache not hitting; output limit raised | Audit prompt size history; cache hit rate; max_tokens |
| Streaming stalls mid-response | Server-side buffering, SSE dropped | Check Content-Encoding; disable reverse-proxy buffering |
| First call after idle is slow | Provider warm-up (rare); local warmup (common); DNS | Pre-warm on deploy; keepalive |

---

## Vercel AI SDK specifics

If using `vercel:ai-sdk` (see that skill):

- `streamText` / `streamObject` return a stream; TTFT = first token arriving
- `onFinish` callback carries full `usage` — log there
- Model switching across providers has ~identical API; apples-to-apples A/B is easy
- AI Gateway provides unified billing + retries + provider fallback

Measure provider fallback cost: if your primary is slow, fallback adds the primary's TTFT to the total.

---

## Cost vs latency tradeoffs

| Lever | Latency Δ | Cost Δ | Notes |
|-------|-----------|--------|-------|
| Cache hit (reuse prompt prefix) | -30-80% TTFT | -80-90% input cost | Best ROI; always evaluate |
| Smaller model tier | -30-70% E2E | -80-95% per call | Quality must be tested |
| Streaming (vs batch) | -N/A (same E2E) | same | Perceived latency fix, not real |
| Shorter outputs (max_tokens) | -linear in output_tokens | -linear in output_tokens | Quality may suffer |
| Parallel tool calls | -serial loops | same | Architecturally better |
| Larger model (quality up) | +30-100% E2E | +3-10× | Use only for critical steps |
| More context (quality up) | +prefill time | +input tokens | Cache to amortize |

The lever that almost always wins: **prompt cache optimization**. Before anything else, measure `cache_read_input_tokens / input_tokens` and fix it if < 50%.

---

## Artifacts to capture for an LLM perf run

```
tests/artifacts/perf/<run-id>/llm/
├── request_log.jsonl              # one entry per request with TTFT/TPOT/E2E/tokens/cache
├── provider_comparison.csv        # A/B across providers on the same workload
├── cache_hit_histogram.csv        # hit rate distribution over 1000 requests
├── token_size_histogram.csv       # input/output token distributions
├── retries.csv                    # retry counts, reasons
├── cost_per_request.csv
└── otel_spans.json                # if using OTel
```

Reference these from hotspot_table.md / BUDGETS.md for the LLM-specific surface.

See also `claude-api` skill for model-migration and feature-specific API guidance.
