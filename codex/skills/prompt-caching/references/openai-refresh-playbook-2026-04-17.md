# OpenAI prompt caching refresh playbook (verified 2026-04-17)

Use this when you need the **latest** OpenAI Responses / prompt-caching details rather than the bundled snapshot.

## Default rule

If the task depends on any OpenAI-specific fact that could have changed, refresh from official OpenAI docs before finalizing the answer.

Refresh by default for:

- exact parameter names or enum literals
- support matrix / supported models
- current pricing
- current GPT-5.x / GPT-5.4 behavior
- Responses / Conversations / compaction semantics
- ZDR / `store=false` details
- changelog / recent releases / deprecations
- anything the user described as “latest”, “current”, “today”, or “are you sure?”

## Best source order

### 1) Docs MCP first, if available

Preferred server: `https://developers.openai.com/mcp`

This is the best refresh path because it gives read-only search + fetch over official OpenAI docs and is designed to be used from agent tooling.

Suggested AGENTS.md snippet from the Docs MCP page:

> Always use the OpenAI developer documentation MCP server if you need to work with the OpenAI API, ChatGPT Apps SDK, Codex,… without me having to explicitly ask.

Suggested docs-search queries:

- `prompt caching prompt_cache_key prompt_cache_retention cached_tokens`
- `Responses create previous_response_id instructions`
- `allowed_tools function calling prompt caching`
- `conversation state previous_response_id conversation`
- `compaction compact_threshold previous_response_id`
- `reasoning.encrypted_content store=false`
- `WebSocket mode generate false previous_response_not_found`
- `pricing cached input`
- `gpt-5.4 allowed_tools prompt caching`

### 2) Core guide pages

Read these next:

1. Prompt caching guide
2. Responses create reference
3. Function calling guide
4. Conversation state guide
5. Compaction guide
6. Reasoning guide
7. Latest model guide
8. Migrate to Responses guide
9. Your data guide
10. Pricing page
11. Changelog

### 3) Cookbook pages for implementation detail

Use these when you want examples and engineering patterns:

- Prompt Caching 201
- Better performance from reasoning models using the Responses API

### 4) Machine-readable doc indexes

Use these when you need a current doc inventory or a single-file snapshot:

- `https://developers.openai.com/api/llms.txt`
- `https://developers.openai.com/api/llms-full.txt`

## What to re-check by topic

### Prompt caching mechanics
Check:
- threshold (currently 1024 tokens)
- increment size (currently 128 tokens)
- exact-prefix rule
- what parts of the request prefix are cacheable
- `cached_tokens` field location

Primary source:
- prompt caching guide

### Routing and `prompt_cache_key`
Check:
- current routing explanation
- first-prefix hash note
- approximate overflow rate
- current recommendation language around stable keys

Primary source:
- prompt caching guide

### Retention
Check:
- current retention policy names/literals
- current supported models for 24h retention
- current inactivity/max-life description
- ZDR / privacy behavior for extended retention

Primary sources:
- prompt caching guide
- responses/chat API reference
- your data guide

### Responses state
Check:
- `previous_response_id`
- `conversation`
- whether `instructions` carry over
- current replay guidance

Primary sources:
- Responses create reference
- conversation state guide
- migrate to Responses guide

### Tools and caching
Check:
- `allowed_tools`
- current function-calling / tool-search guidance
- latest model-specific tool behavior

Primary sources:
- function calling guide
- latest model guide

### Stateless reasoning
Check:
- `reasoning.encrypted_content`
- current `store=false` / ZDR requirements
- example replay pattern

Primary sources:
- reasoning guide
- reasoning-items cookbook
- your data guide

### Compaction
Check:
- `context_management`
- `compact_threshold`
- `previous_response_id` continuation rules
- standalone `/responses/compact` guidance

Primary sources:
- compaction guide
- conversation state guide
- websocket mode guide

### WebSocket continuation
Check:
- connection-local continuation behavior
- `previous_response_not_found`
- `generate: false` warmup guidance

Primary source:
- WebSocket mode guide

### Pricing
Check:
- current cached-input price
- whether the user is asking about batch/flex/priority/long-context pricing

Primary source:
- pricing page

## Conflict resolution

When docs disagree:

- **API reference / SDK reference wins** for exact field names and enum values.
- **Guides win** for architecture, semantics, and recommended patterns.
- **Pricing page wins** for prices.
- **Changelog wins** for recent launches and deprecations.

If a guide and reference disagree, say so plainly and recommend verifying with a tiny request in the target SDK.

## Known current inconsistency

The prompt caching guide currently uses `in_memory`, while some API reference pages / SDK enums use `"in-memory"` for the default retention policy.

Interpretation:
- rely on the targeted API reference / SDK for exact syntax
- do not hard-code the non-default in-memory literal without verifying it
- `"24h"` is the safer explicit literal

## What a refreshed answer should contain

After refreshing, answer with:

1. the current behavior
2. the exact page(s) used
3. any caveats or doc inconsistencies
4. the concrete code or request-shape change
5. the verification plan (`cached_tokens`, latency, hit rate)
