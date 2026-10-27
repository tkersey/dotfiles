# Replacement ladder

Use this ladder to choose simpler primitives. Do not apply it mechanically. Preserve behavior and essential truth first.

## General ladder

1. **Delete** unused layer.
2. **Inline** one-off behavior into the caller.
3. **Extract explicit function** when behavior is reused.
4. **Use direct data structure** such as map, list, table, enum, config object, or native record.
5. **Use explicit composition root** instead of runtime discovery.
6. **Use compatibility wrapper** for external callers while internals simplify.
7. **Keep the abstraction** when it carries essential value.
8. **Split** when the wrapper is incidental but an invariant/protocol must remain explicit.

## Common replacements

| Costly layer | Lower-level primitive | Keep when |
|---|---|---|
| Dependency injection container | Direct constructors, explicit parameters, composition root | Runtime swapping, plugins, lifecycle management, or test doubles are heavily used |
| Service locator | Explicit dependency passing | Dynamic lookup is required by external plugin API |
| Factory with one implementation | Direct constructor/function | Multiple concrete variants are real and selected at runtime |
| Adapter layer that only forwards | Direct call or compatibility wrapper | It isolates an external API or volatile vendor boundary |
| Plugin registry | Explicit map/table of supported handlers | Third-party extension or dynamic discovery is required |
| Decorators/reflection | Explicit metadata object or function calls | Framework lifecycle/security depends on annotations |
| Middleware chain | Named function pipeline or direct handler composition | Ordering/security/cross-cutting concerns are non-trivial |
| Codegen | Narrow handwritten type/client, checked-in schema, or smaller generator | Schema churn, many clients, or compatibility checks justify generation |
| ORM | Query builder or raw SQL behind small repository/function | Migrations, relationships, transactions, or portability are valuable |
| GraphQL gateway | REST/RPC endpoints, typed client calls, or direct service calls | Multiple clients need flexible graph-shaped queries or federation |
| Event bus for in-process behavior | Direct function calls or explicit queue boundary | Async decoupling, retries, fanout, or durability are required |
| Workflow engine | Explicit state machine/reducer or job queue | Long-running retries, audit trails, human steps, or timers are required |
| Monorepo orchestrator | Package manager workspaces, Makefile/just, direct scripts | Cache, affected graph, release orchestration, or scale proves value |
| Task runner wrapper | Native package scripts, shell script, Makefile/just | Cross-platform behavior or parallel orchestration is proven |
| Config inheritance stack | Local explicit config plus shared comments/docs | Central policy enforcement is required |
| Helm/Kustomize layer | Plain manifests or smaller deployment script | Multi-env templating, policy, and rollback are proven |
| Terraform module stack | Direct resource definitions or smaller module | Reuse, policy, compliance, and state management are proven |
| Microservice boundary | Internal module/library or in-process adapter | Independent scaling, ownership, security boundary, or deploy cadence is real |
| Feature flag platform | Static config/env var for retired flags | Remote targeting, experiments, or emergency kill switches are active |
| State manager | Local reducer/state machine/table | Cross-view synchronization, undo/redo, persistence, concurrency, or protocol safety matters |

## Web UI ladder

| Costly layer | Lower-level primitive | Keep when |
|---|---|---|
| React SPA with no complex client state | HTML + CSS + small JavaScript modules | Cross-view state, ecosystem components, hydration, or accessibility/state complexity is real |
| Component framework for mostly static pages | server-rendered templates or static HTML | component composition materially reduces risk or delivery time |
| Bundler for a few modules | native ES modules, import maps, or no-build script | transforms, bundling, code splitting, or package ecosystem are necessary |
| Global state manager | local reducer, explicit state table, URL state, or form state | cross-view synchronization, undo/redo, persistence, optimistic updates, concurrency matter |
| CSS-in-JS pipeline | CSS files, custom properties, cascade layers | dynamic theming, co-location, critical CSS, or design-system constraints are proven |
| Client router for small app | normal links + server routes, or tiny route table | nested routes, data loading, transitions, auth guards, offline behavior matter |
| Form abstraction | native forms + constraint validation + explicit submit handler | schema-driven forms, accessibility, multi-step validation, or complex field arrays matter |
| Hydration/island layer for static content | static HTML with progressive enhancement | interaction requires server/client continuity |
| Build-time site generator for tiny app | direct static files or minimal script | content pipeline, templating, RSS/sitemap, localization, or image processing are proven |

## Migration patterns

### Compatibility wrapper

Keep the external API, simplify internals.

Use when:

- external callers depend on the current shape;
- risk is medium/high;
- you need to prove behavior before changing call sites.

### Strangler seam

Route a narrow path through the new primitive while the old layer remains for other paths.

Use when:

- the abstraction has many users;
- behavior proof is localizable;
- rollback must be immediate.

### Slice unused surface

Remove disabled plugins, unused generated endpoints, dead configuration branches, or one-off interfaces before replacing the core layer.

Use when:

- the layer has some value but much unused surface;
- replacement would be too risky as a first move.

### Composition root extraction

Make object construction explicit in one place, then remove container/service-locator usage incrementally.

Use when:

- DI is the target;
- implementation count is small;
- lifecycle rules are understandable.

### Dual-run proof

Run old and new implementations in parallel for a narrow path and compare outputs.

Use when:

- correctness risk is high;
- test coverage is weak;
- output is deterministic enough to compare.

### Contract-first replacement

Write or identify contract tests before replacing the abstraction.

Use when:

- public API or schema compatibility matters;
- external obligation risk is medium/high.

### Split move

Reduce the wrapper while preserving or strengthening the invariant.

Use when:

- a framework/tool/generator is high tax;
- the current layer also encodes real state, validation, agreement, behavior selection, syntax, or protocol truth.

Example: replace React/Vite with HTML/CSS/native ES modules for static pages, but preserve checkout lifecycle as a reducer with invalid-transition tests.

## Red flags

Do not recommend replacement when:

- the lower-level primitive would require reimplementing most of the abstraction;
- the replacement introduces a new framework of similar size;
- public behavior cannot be proven;
- operational rollback is unclear;
- the only evidence is personal preference;
- the abstraction encodes state transitions you have not modeled;
- the abstraction encodes external obligations you have not bounded.
