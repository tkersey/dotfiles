# OpenAI source index for prompt caching / Responses refresh (verified 2026-04-17)

Use this file as the lookup map for current official sources.

## Best source first

### Docs MCP
- Purpose: Read-only search + fetch over official OpenAI docs from agent tooling
- URL: `https://developers.openai.com/mcp`
- Learn page: `https://developers.openai.com/learn/docs-mcp`

## Documentation indexes

### API docs index
- Purpose: machine-readable index of current docs pages
- URL: `https://developers.openai.com/api/llms.txt`

### API docs full export
- Purpose: single-file markdown snapshot of guides and reference docs
- URL: `https://developers.openai.com/api/llms-full.txt`

## Core prompt caching / Responses sources

### Prompt caching guide
- Purpose: canonical behavior for exact-prefix reuse, threshold, increments, retention, routing, `prompt_cache_key`
- URL: `https://developers.openai.com/api/docs/guides/prompt-caching`

### Responses create reference
- Purpose: exact request/response fields and enum shapes
- URL: `https://developers.openai.com/api/reference/resources/responses/methods/create`

### Function calling guide
- Purpose: `tool_choice`, `allowed_tools`, stable tool patterns
- URL: `https://developers.openai.com/api/docs/guides/function-calling`

### Conversation state guide
- Purpose: `previous_response_id`, `conversation`, replay guidance, assistant `phase`
- URL: `https://developers.openai.com/api/docs/guides/conversation-state`

### Compaction guide
- Purpose: `context_management`, `compact_threshold`, standalone compaction, continuation rules
- URL: `https://developers.openai.com/api/docs/guides/compaction`

### Reasoning guide
- Purpose: reasoning models, reasoning items, `reasoning.encrypted_content`
- URL: `https://developers.openai.com/api/docs/guides/reasoning`

### WebSocket mode guide
- Purpose: low-latency continuation, connection-local state, `generate: false`, `previous_response_not_found`
- URL: `https://developers.openai.com/api/docs/guides/websocket-mode`

### Migrate to Responses guide
- Purpose: current migration framing and state differences vs Chat Completions
- URL: `https://developers.openai.com/api/docs/guides/migrate-to-responses`

### Latest model guide
- Purpose: GPT-5.4 / GPT-5.x current behavior, tool best practices, `allowed_tools`
- URL: `https://developers.openai.com/api/docs/guides/latest-model`

### Pricing page
- Purpose: current input / cached-input / output pricing
- URL: `https://developers.openai.com/api/docs/pricing`

### Your data guide
- Purpose: application state retention, ZDR, extended prompt caching data handling
- URL: `https://developers.openai.com/api/docs/guides/your-data`

### Changelog
- Purpose: recent launches, deprecations, changes to supported models/features
- URL: `https://developers.openai.com/api/docs/changelog`

## Cookbook pages

### Prompt Caching 201
- Purpose: optimization patterns, measurement, request-shape examples
- URL: `https://developers.openai.com/cookbook/examples/prompt_caching_201`

### Reasoning items cookbook
- Purpose: stateless reasoning carryover with `reasoning.encrypted_content`
- URL: `https://developers.openai.com/cookbook/examples/responses_api/reasoning_items`

## Skill packaging sources

### Codex skills docs
- Purpose: skill layout, metadata, progressive disclosure behavior
- URL: `https://developers.openai.com/codex/skills`

### Skills API guide
- Purpose: upload/validation rules for skill bundles
- URL: `https://developers.openai.com/api/docs/guides/tools-skills`

## Suggested minimum refresh set by question type

### “Why am I missing cache hits?”
Read:
- prompt caching guide
- function calling guide
- conversation state guide
- compaction guide

### “What exact request fields should I use?”
Read:
- responses create reference
- function calling guide
- conversation state guide

### “What should I do for `store=false` or ZDR?”
Read:
- reasoning guide
- reasoning-items cookbook
- your data guide
- websocket mode guide (if applicable)

### “What’s the latest support/pricing?”
Read:
- prompt caching guide
- pricing page
- changelog
- latest model guide
