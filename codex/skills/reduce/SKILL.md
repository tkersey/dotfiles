---
name: reduce
description: Deconstruct high-cost abstractions that coding agents do not need; recommend lower-level primitives that reduce tools, indirection, and hidden steps. Use when users ask to simplify architecture, remove framework or codegen layers, cut dependency/tooling overhead, or produce an abstraction audit with a prioritized cut list and migration plan (analysis-only unless implementation is explicitly requested).
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

## When to use
- Agents (or humans) struggle to find where behavior lives.
- Builds/tests are slow or fragile due to tool orchestration.
- Codegen/conventions create hidden steps and large diffs.
- Frameworks/plugins/DI add indirection without proven multi-variant use.
- You want fewer tools, fewer dependencies, and more explicit wiring.

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
- If implementation is requested, hand off to `$tk` or `$code`.

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

### 3. Develop: Propose lower-level replacements
Pick the next lower rung on the replacement ladder (avoid big-bang rewrites).

Replacement ladder (common moves):
- Meta framework -> framework -> stdlib primitives.
- Codegen -> checked-in artifacts + small deterministic generator (or delete entirely).
- ORM -> query builder -> parameterized SQL.
- GraphQL -> REST/JSON -> RPC -> direct function calls (internal only).
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

### 4. Deliver: Report findings and recommendations
Default output must include:
1) Abstraction audit (table).
2) Cut list (prioritized).
3) Migration plan (phased + proof signals + rollback).
4) Patch suggestions (minimal incisions; file/command level; no implementation).

## Output Format (default)

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
- If implementation is requested, hand off to `$tk` or `$code`.

## Pitfalls
- Generic advice without locations/evidence.
- Big-bang rewrites without seams, proof signals, and rollback levers.
- Removing abstractions that are carrying compliance/ops obligations (without a replacement plan).

## Activation cues
- "reduce abstractions" / "too many layers" / "remove framework" / "ditch tooling"
- "codegen is painful" / "build is slow" / "hard to change" / "agents struggle"
