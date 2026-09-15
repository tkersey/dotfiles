# Agent-system performance and effectiveness

Use with [performance.md](../performance.md) for prompts, tools, retrieval,
context assembly, orchestration, harness code, or model configuration. The target
need not be packaged as a skill. If a tool or runtime is the bottleneck, also use
[software-performance.md](software-performance.md); do not force a prompt remedy.
A skill-package intervention additionally follows Tune's existing authoring path.

## Define a successful outcome, not a proxy

Optimize the requested objective subject to explicit quality, reliability,
safety, privacy, latency, and cost guardrails. Examples: lower completion latency
at non-inferior task success, improve task success within a cost budget, or lower
cost per successful task with quality held above the accepted floor. Preserve
required human approvals, policy enforcement, tool authority, and data isolation.
Improving behavior need not reproduce the incumbent's erroneous answers.

Measure success with task-specific checks: correct artifact/state, accepted
answer, task completion, recovery, required refusal/escalation, or another
observable user outcome. An LLM judge is evidence with its own error modes;
calibrate against deterministic checks or human-labeled examples where feasible.
Do not tune only against the same examples used to select the intervention.

Record total cost across all attempts divided by successful tasks, alongside
success count/rate and total attempts. With zero successes, cost per success is
undefined, not zero. Include retry, failed, timed-out, tool, and subagent costs
when present; state missing usage coverage. Report end-to-end latency and failure
rate together so dropping hard cases cannot manufacture a faster agent.

## Build a matched comparison

Use a representative task corpus with easy, hard, near-miss, recovery, and failure
cases. Hold task inputs, tool/data snapshots, acceptance criteria, model/version,
reasoning configuration, budgets, and environment comparable except the declared
lever. Respect a pinned model policy; a smaller/different model is not implicitly
authorized. Record exact model/configuration and provider version information
available rather than claiming full determinism from a seed or temperature zero.

Repeat stochastic cases sufficiently for the claimed effect; report sample size,
variance/intervals and uncertainty, especially for small changes. A paired or
randomized comparison helps isolate task mix and temporal service noise. Keep a
holdout/regression set for adoption. For expensive or effectful tools, use replay,
fixtures, or a sandbox with explicit evaluation authority and budget. Do not send
private transcripts to a new provider or run real transactions to collect scores.

Record the joint quality/resource result. A reduction in tokens, calls, or steps
is diagnostic, not an acceptance criterion by itself. Trace evidence can explain
a causal mechanism but does not prove that a changed instruction caused success.
For skill-attribution questions, retain the existing distinctions between
activation, decision influence, and outcome causality.

## Profile the critical path

Separate time to first output from time to useful output and full completion.
Attribute model prefill/generation, queueing, tool calls, retries, retrieval,
serialization, context construction, subagent scheduling, and human waits where
observable. Do not add overlapping span durations as if they were serial. Track
unobserved provider time honestly rather than assigning it to invented causes.

| Observed mechanism | Candidate lever | Guard/discriminator |
|---|---|---|
| Repeated work or avoidable model round trips | Reuse verified results, deterministic computation, batch compatible tools | Preserve task coverage, freshness, semantics, and recovery; test full completion |
| Serial independent tool spans | Bounded concurrency or dependency restructuring | Side-effect independence, ordering, cancellation, quotas, backpressure |
| Oversized context/retrieval | Better selection, indexing, incremental context, result shaping | Recall, provenance, hard-case success, and invalidation |
| Repeated prompt prefill | Stable reusable prefixes and supported cache controls | Measure actual cache hits under realistic traffic; protect tenant isolation |
| Output generation dominates | Remove unnecessary output or choose a suitable permitted configuration | Preserve required content and reasoning/task quality; distinguish perceived from total latency |
| Retry/recovery dominates | Repair schemas, tool errors, stale state, brittle routing | Count avoided failures and changed success rate, not merely fewer attempts |
| Subagent overhead dominates | Change granularity, remove redundant delegation, reuse scoped results | Preserve useful parallel work and independent checks; do not delete required reviews |
| Decision quality limits success | Clarify contracts, tools, evidence, or reasoning at the actual decision | Matched outcome tests plus positive, near-miss, and characteristic failure cases |

Batching external inference can trade latency for cost; parallelism can increase
contention and retries. Neither is universally better. Keep deterministic tool
correctness separate from stochastic agent-quality evidence.

## Cache-aware experiments

Treat prefix/KV caching, retrieval caches, and semantic/answer caches as different
mechanisms. Prefix reuse does not authorize reusing an answer or stale tool output.
Inspect the actual serialized request layout, tool definitions, dynamic content,
cache key/partitioning, retention, and observed cached-token usage supported by the
provider. Preserve instruction precedence and tool availability when reordering
content. Do not equate textual similarity with a measured cache hit.

Measure cold starts, warm steady state, evolving conversations, and realistic
concurrency/arrival rates separately when material. Alternating candidates can
cross-warm a shared cache; isolate or record that interference. Compare prefix
compression against lost reuse and total cost/latency, not bytes alone. Version
and scope cached artifacts; account for invalidation, eviction, capacity, stale
results, and cross-tenant exposure. Never put secrets into routing keys.

Provider rules and SDK fields change. Consult current primary documentation for
the pinned provider/model before using controls. For OpenAI, start with the
[official prompt-caching guide](https://developers.openai.com/api/docs/guides/prompt-caching).
Do not hardcode universal retention times, thresholds, hit-rate promises, or
routing-key formulas into a general optimization policy.

## Acceptance and delivery

Accept only when the declared quality/reliability guards hold and the measured
objective improves. A quality/cost tradeoff needs an accepted budget and explicit
labeling, not a claim of unchanged behavior. Keep failed and inconclusive trials
in the comparison. Preserve regression tasks and their configuration in existing
evaluation infrastructure, without creating a mandatory judge service or ledger.

For a cognitive skill intervention, preserve Tune's cognitive-compilation and
positive/near-miss/shadow-failure probes. For a mechanical harness optimization,
skip that authoring procedure. Distinguish structural checks, executed task
evaluations, and causal claims in Tune's report. Missing live model access must
remain a validation limit rather than a fabricated behavioral pass.
