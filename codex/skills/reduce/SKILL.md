---
name: reduce
description: Deconstruct high-cost abstractions and recommend lower-level primitives that reduce tooling, indirection, and hidden steps. Use when requests ask for fewer layers (for example "too many layers", "remove this framework/plugin/DI", "ditch codegen/task runners", "replace with plain scripts/config/SQL"), or when prompts say "it feels over-engineered", "start simpler", or "reduce the size of the codebase" (analysis-only unless implementation is explicitly requested).
---

# Reduce (De-abstraction for Agents)

## Overview
Diagnose abstraction cost versus value and recommend lower-level primitives using a surgical, minimal-incision mindset.

Defaults:
- Optimize for agent-editability (few layers, explicit config, deterministic commands).
- Be aggressive: prefer primitives even if it increases short-term duplication or migration work.
- Preserve observable behavior unless the user explicitly requests a semantic change.
- Analysis/recommendations only; do not implement unless explicitly asked.

## Double Diamond fit
Reduce is a Discover/Define-heavy skill that produces a concrete cut list and migration plan without writing code.
- Discover: inventory the abstraction stack and locate indirection points.
- Define: score each abstraction (agent-tax vs value) and choose keep/cut.
- Develop: select the next-lower replacement rung and the smallest reversible migration.
- Deliver: report an audit table + prioritized cut list + migration plan + minimal-incision patch suggestions.

## Entry Criteria
Use this skill only when at least one condition is true:
- Change latency is dominated by abstraction/tooling hops rather than local readability.
- Behavior is controlled by framework hooks, plugins, codegen, or configuration indirection.
- The target outcome is to remove or downgrade layers while preserving observable behavior.
- The current interface is changing during interaction, but that evolution is hidden in ad-hoc runtime checks instead of explicit protocol/state boundaries.

## Triage Gate
- Prefer `$reduce` for architecture/tooling de-abstraction and dependency cuts.
- Prefer `$complexity-mitigator` for local readability or control-flow simplification inside the current stack.
- If both apply, run `$reduce` first to delete layers, then simplify the residue.
- If interaction-dependent interfaces are core to the domain (session/capability/progressive protocol), reduce incidental wrappers first; do not flatten the protocol itself without proof.

## Core Principles
- Minimal incision, maximal simplification: target the smallest change that deletes the most indirection.
- Agent-friendly primitives win: plain files, explicit config, simple CLIs, no hidden generators, no interactive prompts.
- Prefer deletion over replacement when behavior is unused or redundant (prove unused via repo evidence).
- Prefer one obvious path over flexible multiplexing (plugins, adapters, DI containers) unless value is proven.

## Guardrails
- Default to repo-local evidence; do not guess usage/value.
- Do not recommend big-bang rewrites; require seams, phases, proof signals, and a rollback lever.
- Do not propose breaking external surfaces without a compatibility wrapper or an explicit user ask.
- Do not add tools/dependencies unless explicitly requested.
- If implementation is requested, hand off to `$tk`.
- Do not collapse an essential evolving interface into one global fixed interface unless the same observable protocol can be proven with deterministic tests.

## What "Agent-editability" Means (practical)
An agent can:
- Find where behavior lives (few hops; few conventions; minimal magic).
- Change it with a small diff (no repo-wide cascading edits).
- Run/verify quickly (one deterministic command; minimal environment).

Non-goals (unless explicitly requested):
- Beautification refactors.
- Re-platforming for its own sake.
- Tuning performance/scale beyond what the existing contract requires.

## Workflow

### 1. Discover: Map the abstraction stack
Inventory what makes change hard.

Required scan (repo-local):
- Toolchain: build/test commands, task runners, codegen, formatter/linter, monorepo tooling.
- Runtime: frameworks/meta frameworks, plugin systems, DI, reflection, middleware layers.
- Data: ORMs/query builders/migrations, caches, queues, service mesh.
- Frontend: SPA frameworks, bundlers, state libraries.
- Infra/deploy: k8s, Helm, Terraform layers, bespoke pipelines.

Evidence collection defaults:
- Prefer direct evidence: `package.json` scripts, `Makefile`/`justfile`, CI config, `Dockerfile`, deploy manifests.
- Trace one real request path: input -> validation -> core rule -> persistence -> output.
- Note every indirection point (codegen boundary, framework hook, config indirection, adapter layers).
- If interface evolution is suspected, trace at least 2-3 interaction paths and record how the allowed operation set changes after each response/event.

### 2. Define: Decide whether abstraction cost is too high
Classify each abstraction as: keep | wrap | slice | replace | delete.

Cost signals (agent-tax):
- Hidden steps: codegen, implicit conventions, runtime magic, reflection, decorators.
- Indirection: behavior lives in hooks/middleware/config rather than code you can edit.
- Tool weight: slow installs/builds/tests; large dependency graph; multi-tool orchestration.
- Non-determinism: environment-sensitive behavior, flaky tests, network-required dev loops.
- Churn risk: upgrades break frequently; generated diffs; brittle integrations.

Value signals (justification):
- Hard constraints: compliance, multi-tenant isolation, true scale needs, audited change control.
- Proven reuse: multiple independent consumers, stable shared domain rules.
- Operational leverage: materially reduces oncall risk (with evidence).
- Protocol realism: allowed operations genuinely change with interaction state (for example session phase, capability grants/revocations, adaptive UI state, progressive model stages).

Scoring rubric (make cut decisions mechanical):
- Agent-tax score (T): 0-3
  - 0 = negligible (direct code; obvious entrypoints; no extra tools)
  - 1 = mild (one extra layer; still searchable; deterministic commands)
  - 2 = high (codegen/indirection; slow loops; multi-tool orchestration)
  - 3 = severe (hidden magic; multiple generators; interactive/manual steps; flaky loops)
- Value score (V): 0-3 (score 0 if you cannot cite evidence)
  - 0 = unproven/optional (no tests/docs/callsites/ops evidence)
  - 1 = convenience (small DX win; could be replaced without changing the contract)
  - 2 = proven leverage (multiple consumers; reduces a bug-class; real ops benefit)
  - 3 = mandatory (compliance/legal requirement; SLO-critical; audited change control)
- Delta (D) = T - V

Default verdict mapping (aggressive, but not reckless):
- D >= 2: replace or delete (prefer delete if unused)
- D == 1: slice now, replace next (or wrap to isolate first)
- D == 0: wrap or slice (reduce surface area and remove sharp edges)
- D == -1: keep, but simplify interfaces/entrypoints
- D <= -2: keep

Definitions (verdicts):
- keep: retain abstraction; reduce incidental friction (docs, scripts, entrypoints).
- wrap: keep internally, but put a stable adapter in front to localize future removal.
- slice: remove optional flexibility (plugins, multi-variant configs) to the one proven path.
- replace: swap for a lower-level primitive with a migration seam.
- delete: remove entirely.

Aggressive default policy:
- If value is not proven (tests/docs/callsites/ops evidence), treat it as optional and recommend reduction.
- If the abstraction exists "for flexibility" but only one variant is used, inline to the one variant.
- If an abstraction exists to prevent duplication but adds hops/tooling, prefer duplication.

Evidence-confidence modifier (required before final verdict):
- Confidence level (C): high | medium | low
  - high: constraints/value are proven with repo-local evidence (tests/docs/callsites/ops config).
  - medium: partial evidence exists, but at least one critical assumption is inferred.
  - low: external obligations are plausible (compliance/SLO/audit/runtime policy), but not proven locally.
- External-obligation guardrail:
  - If C=low and verdict is `replace` or `delete`, cap to `slice` or `wrap` until one of these is true:
    - explicit user approval to change external obligations, or
    - evidence proving no such obligations exist.
- Report confidence in the audit row notes for every `replace`/`delete` recommendation.

Interaction-evolution guardrail:
- If evidence shows interface evolution is essential (state-dependent allowed operations), treat that protocol boundary as core domain structure.
- In that case, prefer `slice`/`wrap` on incidental tooling around the protocol before attempting `replace`/`delete` of the protocol model itself.

### 3. Develop: Propose lower-level replacements
Pick the next lower rung on the replacement ladder (avoid big-bang rewrites).

Replacement ladder (common moves):
- Meta framework -> framework -> stdlib primitives.
- Codegen -> checked-in artifacts + small deterministic generator (or delete entirely).
- ORM -> query builder -> parameterized SQL.
- GraphQL -> REST/JSON -> RPC -> direct function calls (internal only).
- Implicit runtime gating -> explicit state-indexed protocol map (operation set per state) -> optional typed client/session wrappers.
- SPA -> server-rendered pages -> static HTML/CSS/JS.
- k8s -> Docker Compose -> single process + systemd (or platform native).
- Monorepo tool -> package-manager workspaces -> plain scripts.
- DI container -> explicit constructors/wiring.
- Custom DSL -> JSON/YAML/TOML with a small parser + schema.

Deconstruction patterns (agent-centric):
- "Make the invisible visible": replace conventions with explicit entrypoints and wiring.
- "Collapse configuration": many layers -> one canonical config file (with comments only if unavoidable).
- "Delete the orchestrator": replace toolchains with a single `scripts/dev` and `scripts/test` (or `make dev/test`).
- "Strangler seam": introduce a stable adapter boundary; implement the primitive behind it; migrate callers incrementally.
- "State-index the protocol": move scattered runtime checks into one explicit transition table (state x operation -> next state).

### 4. Deliver: Report findings and recommendations
Default output must include:
1) Abstraction audit (table).
2) Cut list (prioritized).
3) Migration plan (phased + proof signals + rollback).
4) Patch suggestions (minimal incisions; file/command level; no implementation).

## Output Profiles
Use one profile per response.

- Full profile (default): use the complete format in `Output Format (default full profile)`.
- Quick profile (small audits): use only when both conditions hold:
  - Scope is narrow (<=3 abstractions or one subsystem), and
  - The user asked for concise/minimal output.

Quick profile sections (exact order):
**0) Scope + assumptions**
**1) Top Abstractions (mini-audit)**
**2) First Cut Recommendation**
**3) Minimal Migration + Rollback**
**4) Risks / unknowns**

Quick profile minimums:
- Still include T/V/D for each listed abstraction.
- Still cite repo-local evidence (or explicitly mark missing evidence).
- Still provide one deterministic proof signal.
- If interface evolution is in scope, include one compact state-transition sketch (table or bullets) before final cut recommendations.

## Output Format (default full profile)
Use these exact section headers in order. If evidence is missing, keep the header and write `Not enough repo evidence yet.` rather than omitting sections.

**0) Scope + assumptions**
- In-scope surfaces: ...
- Out-of-scope: ...
- Constraints discovered: ...

**1) Abstraction Audit (table)**
Include one row per abstraction.

| Abstraction | Where | Why it exists (hypothesis) | Agent-tax (T:0-3 + why) | Value (V:0-3 + evidence) | Delta (D=T-V) | Verdict | Replacement |
|---|---|---|---|---|---|---|---|
| ... | ... | ... | T:2 - ... | V:1 - ... | +1 | keep/wrap/slice/replace/delete | ... |

Notes:
- "Value" must cite repo-local proof: tests/docs/callsites/ops config.
- If you cannot cite evidence, score V:0.
- "Verdict" must be one of: keep | wrap | slice | replace | delete.

**2) Cut List (prioritized)**
- P0 (delete first): ...
- P1: ...
- P2: ...

Each item must include: expected simplification, blast radius, and fastest proof signal.

**3) Migration Plan (per cut item)**
For each P0/P1 item:
- Seam/boundary: ...
- Phase 1 (reversible): ...
- Phase 2 (switch traffic/callers): ...
- Phase 3 (delete old path): ...
- Proof signals: ... (tests/build/run)
- Rollback lever: ...

**4) Patch Suggestions (minimal incisions; no code)**
List concrete, reviewable edits:
- Files to add/modify/delete: ...
- Commands to run (deterministic): ...
- What "done" looks like (signal): ...

**5) Risks / limits**
- ...

## Replacement Patterns (Examples)
- React/SPA for a small static site -> HTML/CSS/JS, no build step.
- Headless CMS for small docs/marketing -> Git + Markdown (+ static site generator if truly needed).
- ORM for simple CRUD -> parameterized SQL queries.
- GraphQL for a single client -> REST/JSON endpoints.
- State management framework for a small UI -> local state with explicit event handlers.
- Heavy task runner -> `scripts/*` or `Makefile` with 3-5 canonical commands.
- Multi-layer config system -> one config file + a small loader.
- Scattered auth/runtime guards -> explicit session-state protocol map (Anonymous/Authed/etc.) + thin per-state adapters.
- Dynamic capability checks spread across services -> capability-state transition table + adapter selection keyed by capability state.

## Interaction-Evolving Interface Addendum
Use this when the system's interface changes as a result of interaction.

Detection checklist:
- The allowed operation set changes after specific responses/events.
- Current behavior relies on distributed `if authorized`, feature flag, or capability checks across many call sites.
- Clients must "guess and fail" at runtime instead of knowing legal next operations from state.

Recommendation policy:
- Preserve essential protocol evolution; reduce incidental machinery around it.
- Prefer explicit protocol boundaries:
  - `state x operation -> next_state`
  - allowed responses per operation
  - adapter rules (`act`) and state updates (`upd`) for integration points
- Cut targets first: duplicated wrappers, hidden indirection, multipath config, and non-deterministic orchestrators around the protocol.

Proof signals for this mode:
- Depth-bounded trace tests (at least to depth 3) over legal transitions.
- One negative test proving an invalid transition is rejected or unrepresentable.
- Compatibility check showing a fixed-interface simplification (if proposed) preserves observable traces.

## Real Trigger Phrases (from session prompts)
Use these phrases as natural-language routing cues for `$reduce`:
- "It just feels over-engineered for what I want. Is there a way you can see that we could start simpler and build things back up?"
- "I really want to reduce the size of the codebase before building it back up."
- "Only the minimal needed to support what is needed to remain."
- "How much could we simplify things?"
- "Brilliant or over-engineered?"

Weekly re-measure loop:
- Baseline and trend:
  - `seq skill-report --root ~/.codex/sessions --skill reduce --snippets 20`
- Prompt-cue hit sampling:
  - `seq query --root ~/.codex/sessions --spec '{"dataset":"messages","where":[{"field":"role","op":"eq","value":"user"},{"field":"text","op":"regex_any","value":["(?i)over-?engineered","(?i)start simpler","(?i)reduce the size of the codebase","(?i)minimal needed","(?i)simplify things"]}],"select":["timestamp","path","text"],"sort":["-timestamp"],"limit":50,"format":"jsonl"}'`
- After one week, compare cue-hit samples and update frontmatter trigger examples only if precision improves.

## Questions (Judgment Calls Only)
- Research first; do not ask for discoverable facts.
- Ask only judgment calls, prefer 1 question, max 3.
- Use `request_user_input` when available; otherwise ask in a short numbered block.

Good questions (examples):
- "Can we accept some short-term duplication to delete this framework (recommended: yes)?"
- "Is it acceptable to add a compatibility wrapper so external callers remain stable (recommended: yes)?"
- "Is infra allowed to change, or is this strictly code-level (recommended: code-level only)?"

## Handoffs
- If trade-offs remain unclear, invoke `$creative-problem-solver`.
- If implementation is requested, hand off to `$tk`.

## Pitfalls
- Generic advice without locations/evidence.
- Big-bang rewrites without seams, proof signals, and rollback levers.
- Removing abstractions that are carrying compliance/ops obligations (without a replacement plan).
