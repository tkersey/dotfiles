# OpenAI prompt caching facts (verified 2026-04-17)

This note is a compact reference for the skill. Re-check the current official docs before shipping production changes.

## Core behavior

- Prompt caching is automatic on all recent OpenAI models, described by OpenAI as **gpt-4o and newer**.
- Prompt caching reduces **input latency and input cost**. It does **not** memoize or reuse final answers.
- Cache hits require an **exact repeated prefix**.
- Prompt caching is **best-effort** and routing-aware. A stable prefix helps, but cache hits are not guaranteed.
- The prompt caching guide says it can reduce latency by **up to 80%** and input token costs by **up to 90%**.

## Thresholds and measurement

- Prompt caching becomes available for prompts containing **1024 tokens or more**.
- Cache hits occur in **128-token increments**.
- The usage object reports cached tokens:
  - `usage.prompt_tokens_details.cached_tokens` in prompt-oriented usage objects
  - `usage.input_tokens_details.cached_tokens` in input-oriented usage objects
- For requests under 1024 tokens, the cached-token count is expected to be zero.

## What can be cached

OpenAI explicitly documents the request prefix as cacheable, including:

- messages
- images
- audio
- tool definitions
- structured-output schemas

Practical implication: if any of these change near the front of the request, cache reuse drops.

## Routing and `prompt_cache_key`

- Requests are routed using a hash of the initial prefix. OpenAI documents that this typically uses roughly the **first 256 tokens** (model-dependent).
- `prompt_cache_key` is combined with that prefix hash to improve routing stickiness.
- OpenAI documents an approximate limit of **~15 requests per minute per prefix + key combination** before overflow can reduce cache effectiveness.
- A good key is stable across requests with the same long prefix but not so broad that one bucket receives all traffic.

## Retention

OpenAI currently documents two retention policies:

- in-memory retention (default)
- extended retention up to **24 hours** on supported models

Current guide notes:

- In-memory cache retention generally lasts **5–10 minutes of inactivity**, up to a maximum of **1 hour**.
- The prompt caching guide currently lists extended retention support for:
  - `gpt-5.4`
  - `gpt-5.2`
  - the `gpt-5.1` family
  - `gpt-5`
  - `gpt-5-codex`
  - `gpt-4.1`

### Important doc note

The public guide currently spells the in-memory literal as `in_memory`, while some API reference pages / SDK enums show `"in-memory"`. Treat this as a docs inconsistency and verify the current literal in the API reference / SDK you are actually targeting before hard-coding it. The `"24h"` literal is documented consistently.

## Privacy and org scope

- Prompt caches are not shared across organizations.
- Prompt caching does **not** change output generation; it only affects prompt processing.
- Cached tokens still count toward TPM limits.
- Extended prompt caching stores only key/value tensors in GPU-local storage and does not retain the original prompt text in local storage.
- The data-controls guide says extended prompt caching requests are compatible with ZDR. It also says server-side compaction retains no data when `store=false`.

## Responses API facts that matter for caching

- OpenAI recommends Responses for stateful workflows and conversation state.
- `previous_response_id` lets you chain turns by sending only the new input items.
- The Conversations API provides a durable conversation object that can be reused across sessions, devices, or jobs.
- The `instructions` parameter applies only to the current response. If you use `previous_response_id`, prior `instructions` are **not** implicitly carried over.
- For reasoning models in stateless mode (`store=false` or ZDR), OpenAI documents using `include: ["reasoning.encrypted_content"]` so encrypted reasoning items can be carried across turns.
- The reasoning guide says those encrypted reasoning items must be retained across turns in stateless mode.

## Why Responses often helps

OpenAI’s current docs and blog are explicit that Responses is the preferred API for reasoning-heavy, tool-heavy workflows. The current public material says:

- Responses can preserve state across turns with `previous_response_id` or `conversation`
- OpenAI has seen **40–80% better cache utilization** versus Chat Completions in internal benchmarks for the relevant workloads
- The latest-model guide says Responses can pass the previous turn’s CoT/state between turns, which leads to fewer reasoning tokens, higher cache hit rates, and lower latency

Important nuance: that advantage matters most for reasoning-heavy or tool-heavy agent loops, not for every simple single-turn request.

## Compaction and truncation

- Compaction reduces context size while preserving enough state for later turns.
- Server-side compaction is available through `context_management` with `compact_threshold`.
- The compaction guide says that when using `previous_response_id`, you should pass **only the new user message each turn** and **not manually prune**.
- Truncation or compaction changes the history and can break the cache. Caching and context engineering must be balanced deliberately.

## WebSocket continuation note

OpenAI’s WebSocket mode is useful for tool-heavy long chains:

- it keeps the connection open
- you continue with only incremental input plus `previous_response_id`
- the service retains one recent response in connection-local memory for faster continuation
- with `store=false`, there is no persisted fallback if that response is uncached; the documented failure is `previous_response_not_found`
- the WebSocket guide also documents an advanced `generate: false` warmup pattern for preparing request state before a later generated turn

## Refresh first when the user asks about

Always refresh from official sources before answering questions about:

- current support matrix for extended retention
- exact enum literals or field names
- current pricing / cached-input pricing
- current GPT-5.x or GPT-5.4 behavior
- current Responses / Conversations / compaction semantics
- recent releases, deprecations, or changelog items

## Source basis

Verified against these official OpenAI docs/pages on 2026-04-17:

- Prompt caching guide
- Prompt Caching 201 cookbook
- Responses API create reference
- Function calling guide
- Conversation state guide
- Compaction guide
- Reasoning guide
- reasoning-items cookbook
- WebSocket mode guide
- Latest model guide
- Migrate to Responses guide
- Your data guide
- Current API pricing page
- Changelog
- Docs MCP page
- API docs `llms.txt` / `llms-full.txt`
- Codex skills docs
- Skills API docs
