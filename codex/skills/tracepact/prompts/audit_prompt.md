# TracePact Audit Prompt

Use this prompt with the `tracepact` skill.

You are auditing an agentic system for latency. Treat the transcript or trace as an effectful execution graph, not a conversation. Your goal is to infer which spans were causal witnesses and which spans were accidental coordination.

## Inputs

You may be given:

- raw transcript
- normalized trace rows
- compiler output
- OpenAI Responses API objects
- Agents SDK trace summary
- tool schemas/prompts/code
- architecture notes

## Required report

Return:

1. **Verdict**: the single highest-leverage rewrite.
2. **Latency Treaty IR**: compact table with operation, provider, route, dependency, usage policy, freshness, authority, branch, cache/replay, and critical-path role.
3. **Critical path**: TTFU, final answer, and irreversible-action paths if applicable.
4. **Counterfactual schedule**: before/after DAG or ordered steps.
5. **Findings**: prioritized, evidence-backed, with effort, risk, savings, proof required, rollback, and validation.
6. **OpenAI-specific optimization pass**: Responses loop shape, parallel function calls, prompt caching, streaming, WebSocket mode, model routing, structured outputs, tracing.
7. **Patch plan**: specific code-level steps or pseudocode.
8. **Validation harness**: evals, replay, CI latency budgets, safety checks.

## Style

Be direct. Prefer claims like:

- “This dependency is accidental.”
- “This span is not a causal witness.”
- “This tool is read-only and replayable; it can move off the critical path.”
- “This mutation is linear; do not parallelize without idempotency and rollback.”
- “This policy belongs in a treaty resolver, not the prompt.”

## Constraints

- Do not remove safety checks; optimize their placement or representation.
- Do not parallelize mutating tools without a proof of idempotency, authority, branch safety, and rollback/cancel behavior.
- Do not claim exact milliseconds unless measured.
- Distinguish observed evidence from inference.
- If instrumentation is missing, recommend the smallest fields to add.

## Output template

```markdown
# Latency Treaty Audit

## 1. Verdict

## 2. Latency Treaty IR

| id | op | provider | route | usage | freshness | authority | branch | critical role | rewrite legality |
|---|---|---|---|---|---|---|---|---|---|

## 3. Critical path

### TTFU path
### Final path
### Irreversible-action path

## 4. Counterfactual schedule

### Before
### After
### Legality proof

## 5. Findings

### F1: ...
- Evidence:
- Problem:
- Rewrite:
- Expected impact:
- Effort:
- Risk:
- Proof needed:
- Rollback:
- Validation:

## 6. OpenAI pass

## 7. Patch plan

## 8. Validation harness
```
