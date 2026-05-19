# Issue taxonomy

## Coordination

- `ACCIDENTAL_SERIALIZATION`: spans run one at a time without semantic, authority, freshness, or safety dependency.
- `ROUND_TRIP_AMPLIFICATION`: extra model/app/model cycles are introduced by orchestration rather than task requirements.
- `HANDOFF_LATENCY`: handoffs add summary turns but no new evidence or authority.
- `STATE_REHYDRATION_TAX`: history, tool definitions, schemas, or state are resent/reloaded every turn.
- `POLLING_SLEEP_GAP`: fixed polling/sleep intervals gate user value.
- `LATE_USER_VALUE`: useful progress is withheld until internal work completes.

## Model

- `EXCESSIVE_OUTPUT_TOKENS`: decoding dominates latency.
- `UNNECESSARY_REASONING_MODEL`: expensive reasoning model used for deterministic/simple work.
- `MISSING_MODEL_ROUTING`: no fast model or deterministic fast path.
- `PLANNER_EXECUTOR_OVERKILL`: planner and executor are serialized where one structured call or deterministic router suffices.
- `REPAIR_LOOP`: parse/validation failures cause retries that structured outputs could avoid.

## Tools and retrieval

- `DUPLICATE_TOOL_CALL`: same tool and equivalent args repeated.
- `SERIAL_READ_ONLY_TOOLS`: independent read-only tools serialized.
- `TOOL_RESULT_BLOAT`: raw results are sent to the model instead of bounded answer slices.
- `OVERBROAD_TOOL_SURFACE`: irrelevant tools or verbose schemas loaded into every model call.
- `MUTATION_WITHOUT_TREATY`: mutating tool lacks explicit idempotency, authority, replay, branch, and rollback policy.

## Cache and context

- `CACHE_PREFIX_VOLATILITY`: dynamic content destabilizes cacheable prefix.
- `LOW_CACHED_TOKEN_RATIO`: long prompts have low cached-token fraction.
- `CONTEXT_BLOAT`: large unconsumed history/RAG/files/images inflate prefill.
- `TOOL_SCHEMA_TOKEN_TAX`: tool schemas dominate input despite sparse use.

## Safety and policy

- `GUARDRAIL_IN_WRONG_PLACE`: safety check is late, duplicated, blocking, or not incremental.
- `AUTHORITY_TOO_BROAD`: tool/provider authority is wider than needed.
- `SPECULATION_WITHOUT_CANCEL`: speculative work lacks cancellation/discard semantics.
- `REPLAY_POLICY_MISSING`: caching or replay would help, but freshness/branch policy is undefined.
