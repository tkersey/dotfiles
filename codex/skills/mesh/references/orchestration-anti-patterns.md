# Mesh Orchestration Anti-Patterns

This note captures orchestration failure modes observed in external swarm-style skills and the
guardrails mesh uses to avoid them.

## 1) Dependency-agnostic scheduling on a dependency-aware plan

Anti-pattern:

- Planning requires explicit task dependencies, but execution later ignores dependency maps.

Why it fails:

- Runs units out of order, increases retries, and shifts correctness burden to late integration.

Mesh guardrail:

- Default to strict dependency gating from `$st deps`; allow advisory dependency handling only with
  explicit user opt-in and disjoint `unit_scope`.

## 2) Multi-writer plan state in parallel waves

Anti-pattern:

- Every worker edits shared plan/state artifacts while other workers are running.

Why it fails:

- Produces merge conflicts and stale status races, then hides true execution state.

Mesh guardrail:

- Single-writer state ownership: workers return structured outputs only; integrator alone mutates
  `.step/st-plan.jsonl`, task logs, and orchestration ledger fields.

## 3) Conflicting concurrency numbers across the same workflow

Anti-pattern:

- One document advertises one pool size while other sections use different limits.

Why it fails:

- Operators cannot predict scheduler behavior; telemetry and reality diverge.

Mesh guardrail:

- One preflight-derived active-unit target is the concurrency authority and must match wave
  generation, `spawn_agents_on_csv.max_concurrency`, and ledger reporting.

## 4) No failure backpressure after bad waves

Anti-pattern:

- Scheduler keeps full parallelism despite rejects, timeouts, or invalid worker outputs.

Why it fails:

- Repeats the same bad conditions and amplifies integration debt.

Mesh guardrail:

- Apply backpressure on failure classes (`reject`, timeout, lifecycle mismatch,
  `invalid_output_schema`): reduce next-wave concurrency (min 1) and serialize overlapping scopes
  until a clean wave passes.

## 5) Executor/runtime coupling disguised as generic orchestration

Anti-pattern:

- Skill contracts rely on runtime-specific executors/roles while presented as portable defaults.

Why it fails:

- Portability breaks between agent runtimes and hidden assumptions leak into core flow.

Mesh guardrail:

- Keep orchestration substrate generic (`spawn_agents_on_csv` + structured output contract), and
  treat role/lane semantics as explicit CSV/instruction data instead of implicit runtime bindings.

## 6) Copy-paste variant drift

Anti-pattern:

- Near-identical skill variants diverge through small edits and contradictory details.

Why it fails:

- Maintenance cost rises and correctness rules become inconsistent between “equivalent” modes.

Mesh guardrail:

- Keep core invariants centralized in one policy/skill pair and update both in the same change set;
  reject handoff if guardrail vocabulary does not match.

