# Architecture Taxonomy

Use this taxonomy to convert repo evidence into one dominant architecture label plus optional subsystem variants.

## Repo Kind First

Determine the repo kind before the dominant architecture:

- `application-service`: user-facing app, API, worker, or backend service
- `library-sdk`: reusable package, SDK, crate, gem, module, or framework extension
- `cli-tooling`: developer tool, automation repo, local CLI, or utility suite
- `monorepo-platform`: multiple apps, services, or packages under one coordinating repo
- `infra-ops`: deployment, infrastructure, or operational automation
- `data-pipeline`: ETL, analytics workflows, DAGs, or scheduled jobs
- `plugin-extension`: host-plus-extension ecosystem or integration surface

Repo kind is a context layer, not the final architecture label.

## Dominant Architecture Labels

### Layered / N-tier
- Strong clues: `controllers/`, `services/`, `repositories/`, `models/`, `handlers/`, `db/`
- Interpretation: dependencies usually move from delivery to business logic to persistence
- Common false positive: generic folder names with no real boundary enforcement

### MVC / MVVM / Component-Driven UI
- Strong clues: explicit `models`, `views`, `controllers`, `viewmodels`, or UI components paired with state/view layers
- Interpretation: presentation boundaries are the main organizing force
- Common false positive: frontend framework usage with no meaningful separation beyond framework defaults

### Clean / Hexagonal / Onion / Ports-and-Adapters
- Strong clues: `domain`, `application`, `usecases`, `ports`, `adapters`, `infrastructure`, `delivery`
- Interpretation: core logic is intentionally insulated from frameworks or IO
- Require more than naming: confirm dependency direction or adapter boundaries when possible

### Modular Monolith
- Strong clues: one deployable or one tightly coordinated app with clear internal modules, packages, or bounded areas
- Interpretation: module boundaries matter, but deployment/runtime is still mostly singular
- Common false positive: a large repo with folders but no meaningful modular seams

### Microservice / Service-Oriented
- Strong clues: multiple services, apps, deployables, or independently shaped runtimes with explicit RPC/HTTP/message boundaries
- Interpretation: service boundaries dominate architecture more than internal layering does
- Common false positive: one app plus support scripts under `services/`

### Event-Driven / Message-Oriented
- Strong clues: publishers, subscribers, consumers, brokers, topics, queues, or async workflows are first-class
- Interpretation: events or messages are central coordination mechanisms
- Common false positive: incidental queue usage inside an otherwise layered app

### Pipeline / Job-Oriented
- Strong clues: DAGs, workflows, ETL stages, scheduled jobs, ingestion steps, transformers, loaders
- Interpretation: ordered processing stages dominate the design
- Common false positive: a few background jobs in a normal service repo

### Plugin / Extension-Based
- Strong clues: plugins, extensions, hook registries, adapters, provider contracts, dynamic loading, or explicit host/plugin APIs
- Interpretation: extensibility boundaries are part of the architecture, not just utilities
- Common false positive: one small integrations folder with no host/extension model

## Best-Fit Rules

1. Pick one dominant architecture label even when confidence is low.
2. Let repo-wide deployment and control-flow shape beat local folder naming.
3. Use subsystem variants when major slices differ materially from the dominant label.
4. Prefer `modular monolith` over `microservice` unless separate runtime boundaries are evidenced.
5. Prefer `layered` over `clean`/`hexagonal` when the repo names inner layers but dependency direction is unclear.
6. Prefer `component-driven UI` or `mvc`/`mvvm` only when presentation boundaries are a major organizing force.

## Near-Miss Rules

- A `services/` folder alone does not make the repo `microservice`; require multiple runtime or deployment boundaries.
- An `adapters/` or `ports/` folder alone does not make the repo `clean` or `hexagonal`; require believable dependency direction or adapter boundaries.
- A workspace with `apps/` and `packages/` is often a `monorepo-platform` or `modular monolith`, not automatically `microservice`.
- A few queues, jobs, or event handlers inside one service do not make the repo `event-driven` or `pipeline` dominant.
- A small `plugins/` or `integrations/` folder does not make the repo `plugin`-based unless the host/plugin contract is first-class.
- If the repo kind is `library-sdk` or `cli-tooling`, be extra careful not to over-apply app-centric labels from folder aesthetics alone.

## Hybrid Rules

Use hybrid wording only when there is real mixed evidence, for example:

- `Dominant Architecture: modular monolith`
- `Major Subsystems: frontend is component-driven UI; ingestion slice is pipeline-oriented`

Do not invent new top-level labels when dominant-plus-variants is enough.

## Docs Versus Implementation

- Treat architecture docs, READMEs, and ADRs as hypotheses.
- If code or runtime topology contradicts the docs, keep the implemented architecture as the dominant label.
- Record the difference in `Architecture Drift`.

## Repo-Fit Hints By Dominant Architecture

Use these to help downstream agents fit work to the repo as it exists now:

- `layered`: prefer delivery -> service -> persistence seams; keep controllers and handlers thin; avoid pushing business rules into entrypoints.
- `component-driven UI` / `mvc` / `mvvm`: respect presentation boundaries; keep view state and domain state separated; prefer feature-local components before shared abstractions.
- `clean` / `hexagonal` / `onion`: keep framework and IO details outside the core; prefer ports/adapters seams; treat dependency direction as part of the architecture, not just the folder layout.
- `modular monolith`: favor module-owned changes over repo-wide helpers; cross module boundaries only when the stable seam is genuinely shared.
- `microservice`: favor one service boundary at a time; do not invent cross-service helpers to patch a local issue.
- `event-driven`: inspect publishers, consumers, retry boundaries, and event schemas before assuming a request/response seam.
- `pipeline`: look for stage ownership, job boundaries, and handoff formats before modifying orchestration or shared utilities.
- `plugin`: preserve host/plugin contracts and hook registration surfaces; avoid baking plugin-specific assumptions into the host core.

If confidence is low, turn these into conservative `do_not_assume` warnings instead of assertive change guidance.

## Overclaim Boundary

Do not claim these specialized patterns without direct evidence:

- CQRS
- event sourcing
- domain-driven design
- actor model
- service mesh architecture
- saga orchestration

When in doubt, state the simpler broader label and mention the missing proof.
