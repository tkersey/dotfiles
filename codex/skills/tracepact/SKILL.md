---
name: tracepact
version: 2.1.0
summary: Turn slow agent traces into typed effect contracts, critical-path rewrites, and enforceable latency regression gates.
description: Analyze OpenAI Responses API logs, Agents SDK traces, OpenTelemetry/LangSmith/Langfuse/custom spans, transcripts, and agent loop code as effectful execution graphs. Use this when reducing agentic latency, eliminating serial round trips, stabilizing prompt caching, routing models, optimizing tool loops, validating speculative execution, or designing proof-carrying rewrites. Produces a Latency Treaty IR, critical-path map, counterfactual schedules, prioritized fixes, instrumentation gaps, and CI-ready regression checks.
---

# TracePact

## Core thesis

Agentic latency is not primarily a “slow model” problem. It is a coordination problem among typed effects.

Treat every model call, tool call, retrieval, guardrail, handoff, cache lookup, UI update, human approval, retry, and state rehydration as an effectful operation with a contract:

- What information or authority does it require?
- What information or authority does it produce?
- Does it have to run fresh, or is replay/cache acceptable?
- Is it copyable, replayable, affine, linear, or ephemeral?
- Is it read-only, externally mutating, user-visible, or safety-critical?
- Which later spans actually consume its result?
- Could it be routed to a different provider, collapsed into another span, run in parallel, run speculatively, moved off the critical path, or replaced by deterministic code?

The skill’s job is to compile the observed run into a **Latency Treaty IR**: a machine-readable execution contract plus a counterfactual rewrite plan. The output should not merely say “parallelize tools.” It should state which dependency, policy, authority, replay, or quality invariant makes the rewrite legal.

## What makes this skill different

Most trace audits summarize what happened. This skill asks what **needed** to happen.

For each span, classify it into one of these roles:

1. **Causal witness**: required to justify the final answer or an irreversible action.
2. **Movable witness**: required eventually but not required before first useful user value.
3. **Treaty blocker**: a safety, authority, freshness, dependency, branch, or replay constraint that prevents a faster schedule.
4. **Policy artifact**: a guardrail, validation, audit, or observability step that must be preserved but may be relocated, batched, cached, or made incremental.
5. **Coordination waste**: work whose result was unused, duplicated, overbroad, late, or caused by avoidable orchestration.
6. **Unknown**: insufficient trace evidence; add instrumentation before claiming savings.

The final answer should be a **rewrite package**: an explanation, a trace-derived treaty, a counterfactual schedule, patch-level implementation guidance, and validation tests.

## Accepted inputs

Accept any of the following:

- Raw agent conversation transcript.
- OpenAI Responses API objects, streaming event logs, tool-call outputs, usage blocks, and `previous_response_id` chains.
- OpenAI Agents SDK trace exports or screenshots/summaries from the Traces dashboard.
- OpenTelemetry, Datadog, Honeycomb, Jaeger, LangSmith, Langfuse, Braintrust, Arize/Phoenix, or custom JSON/JSONL spans.
- Tool schemas, prompt templates, routing code, agent definitions, orchestration pseudocode, CI/eval results, or architectural diagrams.
- Ability/Program-style traces containing session sites, capsules, journals, effects, provider offers, capabilities, routes, treaties, obligations, and branch/replay metadata.

If timings or token counts are missing, perform a qualitative treaty analysis and mark all savings as inferred. Never invent precise millisecond savings.

## Minimum output contract

Every audit must produce these sections, even if some are short:

1. **Verdict**: the single highest-leverage rewrite and why.
2. **Latency Treaty IR**: a compact table or JSON-like summary of operations, providers, dependencies, usage policy, authority policy, replay/cache policy, and critical-path role.
3. **Critical path**: the longest gating chain to first useful output and final output.
4. **Counterfactual schedule**: a before/after DAG or ordered plan showing what moves, collapses, routes, caches, streams, or speculates.
5. **Findings**: prioritized, evidence-backed, with implementation effort, risk, expected savings, rollback, and validation.
6. **OpenAI-specific optimizations**: model routing, Responses/API loop shape, parallel function calls, prompt caching, streaming, WebSocket mode, structured outputs, and tracing gaps.
7. **Validation harness**: evals, replay tests, latency budgets, safety checks, and regression thresholds.
8. **Next patch**: concrete code-level steps or pseudocode.

## Analysis procedure

### 1. Normalize spans into effects

Create a normalized span table. Capture fields when available:

- `span_id`, `parent_id`, `trace_id`, `turn_id`, `agent`, `phase`, `name`
- `kind`: `model`, `tool`, `retrieval`, `guardrail`, `handoff`, `router`, `planner`, `cache`, `state`, `ui`, `sleep`, `retry`, `human`, `other`
- `start_ms`, `end_ms`, `duration_ms`, `status`
- `depends_on`: hard dependency span IDs, or inferred dependencies with reasons
- `consumed_by`: later spans that use this output
- `user_visible`: `none`, `progress`, `partial`, `final`, `irreversible_action`
- `model`, `reasoning_effort`, `service_tier`, `transport`, `parallel_tool_calls`, `structured_output`, `streaming_used`
- `input_tokens`, `cached_tokens`, `output_tokens`, `reasoning_tokens`, `tool_schema_tokens`, `retrieval_tokens`
- `prompt_hash`, `static_prefix_hash`, `dynamic_suffix_hash`, `prompt_cache_key`, `cache_retention`
- `tool_name`, `tool_args_hash`, `tool_result_bytes`, `tool_result_tokens`
- `mutability`: `read_only`, `idempotent_write`, `external_write`, `payment_or_irreversible`, `unknown`
- `usage_policy`: `copyable`, `replayable`, `affine`, `linear`, `ephemeral`, `unknown`
- `freshness_policy`: `fresh_required`, `stale_ok`, `cache_ok`, `replay_only`, `unknown`
- `authority_policy`: provider/capability/route/approval constraints
- `quality_policy`: schema, eval threshold, confidence, abstention, or review requirement

### 2. Infer a Latency Treaty IR

For each operation, infer an effect treaty:

```text
operation: normalized effect surface
provider_offer: who can satisfy it, at what latency/token/quality/authority cost
morphism_offer: legal adaptation to another provider, schema, tool, model, cache, or deterministic function
route: chosen provider path in the observed run
usage: copyable | replayable | affine | linear | ephemeral | unknown
freshness: fresh_required | replay_ok | cache_ok | speculative_ok | unknown
branch_policy: unrestricted | replay_only | single_live_branch | split_required | no_branch | host_owned | unknown
authority: none | read | scoped_write | user_approval | irreversible | unknown
blocking_reason: data_dependency | safety_gate | authority | freshness | branch_policy | output_schema | latency_accident | none
rewrite_legality: why the faster schedule is safe, or what proof is missing
```

A treaty is useful only if it distinguishes real constraints from accidental ordering. A database write may be linear and must stay ordered. A read-only retrieval is usually replayable/cacheable and can often move earlier, parallelize, or compress. A model router may be deterministic enough to replace with code. A policy check may remain mandatory but run concurrently or stream its result.

### 3. Reconstruct critical paths

Compute three paths:

1. **TTFU path**: user request → first useful user-visible output.
2. **Final path**: user request → final answer.
3. **Irreversible path**: user request → first external mutation, payment, send, delete, or user-visible irreversible action.

For each path, report:

- span sequence
- duration and idle gaps
- model/tool/token contribution
- why each span gates the path
- whether the gate is semantic, policy, authority, freshness, or accidental

The central question: **which spans are causal witnesses for useful user value?** Optimize those first.

### 4. Generate counterfactual schedules

Produce at least three candidate rewrites when evidence permits:

- **Conservative rewrite**: no quality semantics change; relocate, batch, cache, stream, and instrument.
- **Architectural rewrite**: change loop shape, split planner/executor, add provider offers, use structured outputs, route models, or convert tool calls to a treaty/dispatcher layer.
- **Radical rewrite**: compile recurring agent behavior into a protocol/program/effect surface; use replay/capsules/journals; make the LLM only decide entropy-bearing steps.

A counterfactual schedule must identify all changed dependencies:

```text
Before: A(model planner) -> B(tool retrieve) -> C(model summarize) -> D(tool DB read) -> E(model final)
After:  A'(small router + query plan) ─┬─ B(retrieve compressed)
                                      ├─ D(DB read)
                                      └─ safety/policy precheck
        -> E'(final with structured context)
Legality: B and D are read-only, independent, replayable, and their results are both consumed only by E'.
```

### 5. Detect high-value latency pathologies

Use these issue families. Each finding must cite evidence from the trace or mark itself as inferred.

#### Coordination pathologies

- `ACCIDENTAL_SERIALIZATION`: independent model/tool spans are serialized by orchestration rather than data/policy dependency.
- `ROUND_TRIP_AMPLIFICATION`: the system turns one decision into repeated model → app → model loops.
- `HANDOFF_LATENCY`: subagents exchange summaries rather than capabilities/results, adding turns without new evidence.
- `STATE_REHYDRATION_TAX`: every turn reloads history, state, tools, or schemas instead of using stable conversation state or compact capsules.
- `POLLING_SLEEP_GAP`: fixed sleeps or polling delays are on the critical path.
- `LATE_USER_VALUE`: no useful UI output appears until after invisible internal work.

#### Model pathologies

- `EXCESSIVE_OUTPUT_TOKENS`: long generation dominates wall-clock or user-perceived latency.
- `UNNECESSARY_REASONING_MODEL`: high-reasoning/planner model used for deterministic, simple, or well-defined work.
- `MISSING_MODEL_ROUTING`: no fast path for easy requests.
- `PLANNER_EXECUTOR_OVERKILL`: planner call plus executor call where a single structured call or deterministic router would suffice.
- `REPAIR_LOOP`: free-form output causes parse/validation retries; structured outputs or tighter schemas would remove retries.

#### Tool and retrieval pathologies

- `DUPLICATE_TOOL_CALL`: same or equivalent tool/args called repeatedly without new information.
- `SERIAL_READ_ONLY_TOOLS`: read-only tools run one after another despite no dependency.
- `TOOL_RESULT_BLOAT`: raw tool/retrieval output is sent to the model instead of a bounded answer slice.
- `OVERBROAD_TOOL_SURFACE`: too many tools or large schemas loaded into every call; use tool search, narrower schemas, or a dispatcher.
- `MUTATION_WITHOUT_TREATY`: mutating tool lacks explicit authority, idempotency, branch, replay, and rollback semantics.

#### Cache and context pathologies

- `CACHE_PREFIX_VOLATILITY`: dynamic content appears before static instructions/tools/examples/schemas.
- `LOW_CACHED_TOKEN_RATIO`: long prompts have low `cached_tokens / input_tokens`.
- `CONTEXT_BLOAT`: repeated history, HTML/noisy retrieval, giant screenshots/files, or unconsumed context inflates prefill.
- `TOOL_SCHEMA_TOKEN_TAX`: tool schemas consume a material fraction of input tokens but only a few are relevant.

#### Safety and policy pathologies

- `GUARDRAIL_IN_WRONG_PLACE`: required safety check is late, duplicated, or blocks work that could safely proceed.
- `AUTHORITY_TOO_BROAD`: the agent holds more tool authority than the current request needs, forcing slow review or riskier policy checks.
- `SPECULATION_WITHOUT_CANCEL`: speculative work is started but cannot be cancelled, bounded, or discarded safely.
- `REPLAY_POLICY_MISSING`: cache/replay could reduce latency, but freshness and branch semantics are undefined.

### 6. OpenAI-specific checks

When the stack uses OpenAI models or SDKs, inspect:

- **Responses API loop shape**: avoid splitting simple model/tool/model loops into avoidable separate requests; use structured outputs when the app needs a machine-readable result.
- **Parallel function calling**: assume zero, one, or many calls can appear; execute independent function calls concurrently when safe.
- **Streaming**: reduce time-to-first-useful-output for long generations and stream function-call argument progress when useful.
- **Prompt caching**: stabilize static prefixes, log `cached_tokens`, select `prompt_cache_key` granularity, avoid timestamps/randomized JSON/tool-order changes in the prefix.
- **WebSocket mode**: for long, tool-call-heavy chains, consider persistent transport with incremental input and `previous_response_id`.
- **Model routing**: use faster GPT workhorse models for well-defined execution; reserve reasoning models for ambiguous planning, hard policy reasoning, and high-stakes synthesis.
- **Tracing**: use Agents SDK traces or equivalent spans for model calls, tool calls, guardrails, handoffs, custom app spans, token usage, cache usage, and result consumption.
- **Tool search / narrowed tools**: do not place huge rarely used tool surfaces in every prompt when tool discovery or routing can defer them.

### 7. Ability / Effect Treaty bridge

When the system resembles Ability’s defunctionalized Program/Session architecture, lean into it:

- Treat each yielded operation/after site as a typed effect site.
- Treat provider manifests/offers as latency and authority surfaces.
- Treat `TreatyResolver`-like logic as the place to choose direct handling, adapted handling, replay, cache, or rejection before a model or provider call.
- Treat capsules and journals as replay/counterfactual infrastructure.
- Treat linear/affine obligations and branch policies as the proof that mutating tools are not accidentally parallelized.
- Treat morphism offers as static rewrites from one protocol/tool/model surface to another.

The strongest rewrite often converts an unstructured agent loop into a typed protocol with explicit provider offers:

```text
Natural-language agent loop -> typed effect surface -> treaty resolver -> provider harness -> journaled replay -> model only at entropy-bearing decisions.
```

### 8. Scoring

Score each finding:

- `critical_path_impact`: `ttfu`, `final`, `irreversible`, `throughput`, `cost_only`, `unknown`
- `severity`: `critical`, `high`, `medium`, `low`
- `expected_savings`: exact measured ms, inferred range, or qualitative `low|medium|high`
- `confidence`: `high`, `medium`, `low`
- `implementation_effort`: `XS`, `S`, `M`, `L`, `XL`
- `quality_risk`: `low`, `medium`, `high`
- `safety_risk`: `low`, `medium`, `high`
- `proof_needed`: dependency, authority, freshness, branch, eval, or instrumentation proof required
- `rollback`: flag, config, route fallback, or kill switch

Prioritize by:

```text
critical-path impact × expected savings × confidence ÷ (implementation effort × quality/safety risk)
```

### 9. Validation harness

Every bold rewrite needs a validation plan:

- Replay old traces through the new schedule where possible.
- Compare final answer quality with task-specific evals.
- Add canary latency budgets: p50, p95, p99, TTFU, time-to-tool, time-to-final.
- Track token metrics: input, cached, output, reasoning, tool schema, retrieval payload.
- Track coordination metrics: model requests per user task, tool calls per task, serial depth, idle gaps, retries, handoffs.
- Track safety metrics: policy check pass/fail, mutation authorization, duplicate mutation prevention, rollback/cancel events.
- Require a regression gate: no new serial LLM round trip on the dominant route without an explicit treaty blocker.

## Report style

Be blunt and specific. The best report feels like a senior systems reviewer marking up a trace, not a generic LLM prompt critique.

Use language such as:

- “This span is not a causal witness.”
- “This dependency is accidental, not semantic.”
- “This is a linear mutation; do not parallelize it until idempotency and rollback are explicit.”
- “The model is being used as glue code here.”
- “The provider should return an answer slice, not a document blob.”
- “This belongs in a treaty resolver, not in the LLM prompt.”
- “The first useful token should appear before this guardrail finishes; preserve safety by withholding unsafe content, not by hiding all progress.”

Avoid vague recommendations such as “optimize prompts,” “use caching,” or “parallelize” without the treaty proof that makes the recommendation legal.

## Tooling included in this skill bundle

- `scripts/tracepact.py`: normalize JSON/JSONL traces, compute critical-path approximations, infer effect treaties, detect latency pathologies, and emit Markdown/JSON/Graphviz DOT.
- `scripts/openai_instrumentation_snippets.py`: print Python/TypeScript snippets for trace fields this skill expects.
- `schemas/normalized_trace.schema.json`: event schema for normalized spans.
- `schemas/latency_treaty.schema.json`: schema for treaty IR.
- `schemas/latency_report.schema.json`: schema for final audit reports.
- `playbooks/`: deeper review methods and patch patterns.
- `examples/`: sample trace, treaty, and report.

## Safe boundaries

Do not recommend removing safety checks. Instead, make them explicit effects and optimize their placement, batching, streaming, or determinism.

Do not recommend speculative execution of externally mutating tools unless idempotency, authority, branch policy, cancellation, and rollback semantics are explicit.

Do not claim exact latency savings without measured timings. Use inferred ranges and state assumptions.

Do not leak private trace contents into third-party tools. Redact secrets, PII, prompts, tool outputs, and customer data before sharing traces outside the trusted environment.
