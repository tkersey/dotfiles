---
name: reduce
description: De-abstraction audit for over-engineered codebases. Use when change latency or agent difficulty comes from frameworks, plugins, DI, codegen, task runners, config indirection, ORMs, GraphQL, monorepo/infra tooling, or the user asks to remove layers while preserving behavior. Produces evidence-backed cut list, lower-level replacements, phased migration, and rollback. Do not use for local readability cleanup or implementation unless asked.
---

# Reduce

## Purpose

Act as an architecture simplification reviewer. Find costly abstractions whose value is unproven, expired, redundant, or outweighed by the change latency they impose. Recommend lower-level primitives while preserving observable behavior.

Your default product is a decision package, not a patch. Implement only when the user explicitly asks for implementation.

## When to use

Use this skill when the user asks to remove, reduce, replace, or challenge layers such as:

- frameworks, plugins, decorators, middleware stacks, dependency injection containers, service locators, factories, adapters, or reflection-driven wiring
- code generation, generated clients, schema generators, build generators, task runners, monorepo tooling, or config inheritance
- ORMs, GraphQL gateways, query abstraction layers, repository layers, API gateways, event buses, workflow engines, queues, or microservice boundaries
- infrastructure indirection such as Helm, Kustomize, Terraform modules, Kubernetes layers, deployment wrappers, or CI/CD orchestration
- any architecture where a simple change requires many files, tools, generated artifacts, conventions, or hidden control flow

Use it for prompts like: "this is over-engineered," "too many layers," "remove the framework," "ditch codegen," "reduce the codebase," "start simpler," "make this agent-editable," or "what can we delete?"

## Do not use

Do not use this skill for ordinary local cleanup. Hand those requests to the normal coding/refactoring process unless the user explicitly frames the problem as layer removal.

Do not use for:

- making one function easier to read
- naming, formatting, or small control-flow cleanup
- bug fixing where the abstraction is not the suspected cause
- performance tuning where the abstraction/tooling stack is not in scope
- implementing a feature inside the current architecture without questioning the architecture
- adding a new abstraction unless the user explicitly asks for one

## Operating rules

1. Preserve observable behavior unless the user asks for a semantic change.
2. Use repo-local evidence first: code paths, call sites, tests, scripts, docs, deploy config, CI, runtime entrypoints, and generated artifacts.
3. Treat external obligations as risk, not as value proof. Compliance, SLOs, vendor constraints, platform policies, contracts, and public API commitments may be real even if absent from the repo.
4. Prefer reversible cuts: seam first, slice second, replace third, delete only with strong proof.
5. Never recommend a big-bang rewrite when a compatibility wrapper, strangler seam, or phased migration can prove the move incrementally.
6. Do not break public or cross-team interfaces without a compatibility plan and explicit approval.
7. Do not add dependencies or tools to remove dependencies or tools unless the user explicitly asks and the replacement is demonstrably simpler.
8. If evidence is incomplete, mark the audit provisional and cap destructive verdicts at `wrap` or `slice`.

## Evidence-first workflow

Follow this sequence.

### 1. Build an evidence packet

Inspect at least these categories when available:

- package/build files: `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `Makefile`, `justfile`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, Gradle files
- entrypoints: app startup, CLI commands, HTTP handlers, workers, cron jobs, deploy hooks
- orchestration: CI workflows, Dockerfiles, Compose files, Kubernetes/Helm/Kustomize/Terraform, release scripts
- abstraction boundaries: generated directories, adapters, service layers, factories, providers, containers, interfaces, decorators, middleware, plugin registries
- tests and docs: integration tests, fixture setup, API contracts, migration notes, ADRs, runbooks

Use `scripts/reduce-scan.sh` when present for a non-destructive first pass. Treat script output as inventory, not proof.

### 2. Trace one real path

For each major abstraction under review, trace at least one real change/request/command path through it. Record:

- initial entrypoint
- files touched by the path
- generated/configured layers crossed
- runtime side effects
- tests or commands that prove behavior
- where the path becomes hard to reason about

### 3. Identify abstraction candidates

List candidates that cause one or more of these costs:

- hidden control flow
- generated or reflected behavior
- many-hop edits for simple changes
- local development friction
- fragile ordering, lifecycle, or registration rules
- dependency bloat
- duplicated behavior across layers
- test setup disproportionate to business logic
- toolchain coupling that blocks agent edits or simple diffs

### 4. Score each candidate

Use the scoring model in `references/rubric.md`.

- `T` = agent/change tax, 0 to 3
- `V` = proven value, 0 to 3
- `D = T - V`
- `confidence` = high, medium, low
- `external obligation risk` = high, medium, low, unknown

Keep value and obligation risk separate. Lack of repo proof may reduce `V`, but it does not prove the layer is safe to remove.

### 5. Classify the move

Use one of these verdicts:

- `keep`: value is proven, tax is low, or external obligation risk is too high
- `wrap`: keep the external surface but hide or centralize the abstraction behind a simpler seam
- `slice`: retain only the useful subset and remove unused features, configuration, plugins, generated surface, or dependency paths
- `replace`: move to a lower-level primitive with equivalent behavior and a migration proof
- `delete`: remove the layer because usage is absent/redundant and rollback is trivial

### 6. Check for stateful protocol value

Before flattening an abstraction that may encode evolving interaction state, read `references/protocol-evolution.md` and construct a transition table. Do not remove state management just because it is indirect. Simplify stateful protocols only after proving the state, transitions, guards, and invariants are preserved or intentionally changed.

### 7. Produce a migration plan

For each proposed cut, provide:

- smallest safe phase
- changed files or commands
- behavior proof signal
- rollback action
- risk and owner of unknowns

## Required output

For normal audits, produce this structure:

1. **Scope and assumptions**
   - What codebase area you inspected.
   - What evidence is present.
   - What evidence is missing.
   - Whether the audit is provisional.

2. **Evidence ledger**
   - Path, command, or file.
   - What it proves.
   - What it does not prove.
   - Confidence.

3. **Abstraction audit table**
   - Abstraction.
   - Evidence.
   - Tax drivers.
   - Proven value.
   - `T`, `V`, `D`.
   - Confidence.
   - External obligation risk.
   - Verdict.
   - Lower-level primitive or reason to keep.

4. **Prioritized cut list**
   - Highest-confidence, highest-payoff cuts first.
   - Avoid sequencing dependent cuts before their proof seams exist.

5. **Migration plan**
   - Phases.
   - Proof signals.
   - Rollback.
   - Tests/commands.

6. **Patch suggestions**
   - File-level or command-level changes.
   - Do not implement unless asked.
   - Keep suggestions small enough to review.

7. **Risks and unknowns**
   - External obligations.
   - Runtime behavior not visible in repo.
   - Migration assumptions.

Use templates in `references/output-templates.md` when you need a strict format.

## Concise mode

If the user asks for a quick answer, output only:

- top 3 abstractions to cut or keep
- one-sentence evidence per item
- recommended verdict
- first safe move
- biggest unknown

## Implementation mode

If the user explicitly asks you to implement:

1. Start from the smallest phase of the migration plan.
2. Preserve the old surface until tests prove replacement behavior.
3. Make narrow patches.
4. Run or state the relevant proof commands.
5. Leave rollback obvious.
6. Do not continue into later phases unless the request clearly covers them.

If implementation is requested together with an audit, do the audit first, then implement only the first safe phase or the specific cut named by the user.

## References

- `references/rubric.md`: scoring, confidence, and verdict thresholds
- `references/evidence-model.md`: evidence packet and trace checklist
- `references/replacement-ladder.md`: common lower-level primitives and migration patterns
- `references/protocol-evolution.md`: stateful protocol safeguards
- `references/output-templates.md`: full, quick, provisional, and implementation templates
- `references/eval-prompts.md`: trigger and non-trigger test prompts
