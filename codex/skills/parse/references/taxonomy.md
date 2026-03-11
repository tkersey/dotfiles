# Architecture Taxonomy

Use this taxonomy to convert repo evidence into one dominant architecture label plus optional subsystem variants and up to two directly evidenced coexisting patterns.

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
- Claim when: 3 or more persistent layers exist and most dependencies flow downward across delivery, business, and persistence seams
- Common false positive: generic folder names with no real boundary enforcement

### MVC / MVVM / Component-Driven UI
- Strong clues: explicit `models`, `views`, `controllers`, `viewmodels`, bindable state, or reusable UI components paired with stories, design tokens, or clear state/view layers
- Interpretation: presentation boundaries are the main organizing force
- Claim when: presentation boundaries are a primary organizing force rather than framework defaults alone
- Common false positive: frontend framework usage with no meaningful separation beyond framework defaults

### Clean / Hexagonal / Onion / Ports-and-Adapters
- Strong clues: `domain`, `application`, `usecases`, `ports`, `adapters`, `infrastructure`, `delivery`
- Interpretation: core logic is intentionally insulated from frameworks or IO
- Claim when: at least one inbound and one outbound port or adapter boundary is visible and the core is exercised without framework or persistence coupling
- Require more than naming: confirm dependency direction or adapter boundaries when possible

### Modular Monolith
- Strong clues: one deployable or one tightly coordinated app with clear internal modules, packages, or bounded areas
- Interpretation: module boundaries matter, but deployment/runtime is still mostly singular
- Claim when: one deployable codebase has business-capability modules plus local APIs, events, or some real boundary enforcement
- Common false positive: a large repo with folders but no meaningful modular seams

### Microservice / Service-Oriented
- Strong clues: multiple services, apps, deployables, or independently shaped runtimes with explicit RPC/HTTP/message boundaries
- Interpretation: service boundaries dominate architecture more than internal layering does
- Claim when: repo-local evidence shows independent build, deploy, runtime, or data ownership boundaries
- Common false positive: one app plus support scripts under `services/`

### Event-Driven / Message-Oriented
- Strong clues: publishers, subscribers, consumers, brokers, topics, queues, or async workflows are first-class
- Interpretation: events or messages are central coordination mechanisms
- Claim when: events or messages are a primary integration mechanism across modules or services, not incidental background work
- Common false positive: incidental queue usage inside an otherwise layered app

### Pipeline / Job-Oriented
- Strong clues: DAGs, workflows, ETL stages, scheduled jobs, ingestion steps, transformers, loaders
- Interpretation: ordered processing stages dominate the design
- Claim when: ordered stages, workflows, or handoff artifacts are core product logic rather than CI or support jobs
- Common false positive: a few background jobs in a normal service repo

### Plugin / Extension-Based
- Strong clues: plugins, extensions, hook registries, adapters, provider contracts, dynamic loading, or explicit host/plugin APIs
- Interpretation: extensibility boundaries are part of the architecture, not just utilities
- Claim when: stable host/plugin contracts or runtime discovery/loading are first-class architecture surfaces
- Common false positive: one small integrations folder with no host/extension model

## Best-Fit Rules

1. Pick one dominant architecture label even when confidence is low.
2. Let repo-wide deployment and control-flow shape beat local folder naming.
3. Use subsystem variants when major slices differ materially from the dominant label.
4. Prefer `modular monolith` over `microservice` unless separate runtime boundaries are evidenced.
5. Prefer `layered` over `clean`/`hexagonal` when the repo names inner layers but dependency direction is unclear.
6. Prefer `component-driven UI` or `mvc`/`mvvm` only when presentation boundaries are a major organizing force.
7. After choosing the dominant label, capture up to 2 directly evidenced coexisting patterns only when they materially shape seams, contracts, or control flow.

## Near-Miss Rules

- A `services/` folder alone does not make the repo `microservice`; require multiple runtime or deployment boundaries.
- An `adapters/` or `ports/` folder alone does not make the repo `clean` or `hexagonal`; require believable dependency direction or adapter boundaries.
- A workspace with `apps/` and `packages/` is often a `monorepo-platform` or `modular monolith`, not automatically `microservice`.
- A few queues, jobs, or event handlers inside one service do not make the repo `event-driven` or `pipeline` dominant.
- A small `plugins/` or `integrations/` folder does not make the repo `plugin`-based unless the host/plugin contract is first-class.
- A `components/` folder alone does not make the repo `component-driven UI`; look for reusable composition surfaces, stories, or explicit state/view separation.
- A command and query folder pair does not make the repo `CQRS`; treat it as secondary command/query separation unless projections or separate models are directly evidenced.
- If the repo kind is `library-sdk` or `cli-tooling`, be extra careful not to over-apply app-centric labels from folder aesthetics alone.

## Repo-Kind Signals That Change The Read

- `library-sdk`: exported API roots, examples/tests/bench/docs as contract surfaces, adapter or integration packages, provider registries, and a clear core/runtime split often matter more than missing app-style entrypoints.
- `cli-tooling`: command trees, pass/pipeline stages, provider/plugin seams, thin IO shells over reusable core modules, and command help/docs can be stronger signals than folder naming alone.
- `monorepo-platform`: classify the smallest coherent runtime or package first; root workspace tooling is often only a coordination surface.
- `infra-ops`: deployment graphs, environment layering, modules, or workflow definitions may dominate over application-style labels.

## Hybrid Rules

Use hybrid wording only when there is real mixed evidence, for example:

- `Dominant Architecture: modular monolith`
- `Major Subsystems / Coexisting Patterns: frontend is component-driven UI; ingestion slice is pipeline-oriented; repo-wide command/query separation shapes handlers`

Do not invent new top-level labels when dominant-plus-variants is enough.

## Coexisting Patterns (Secondary Only)

Capture at most 2 directly evidenced patterns that materially shape seams or contracts without displacing the dominant label. For each pattern, state whether it is a `repo-wide modifier`, `slice-local variant`, or `near-miss`.

### Usually Safe To Mention As Secondary

- `package-by-feature` / capability modules: repeated feature-local bundles with mostly intra-feature imports across 3 or more capabilities.
- `vertical slices`: use-case handlers, commands, queries, or tests stay slice-shaped across multiple flows instead of collapsing into one broad service layer.
- `functional core / imperative shell`: pure transform-heavy core plus thin IO shells or adapters.
- `command/query separation`: explicit read/write handlers or models without full CQRS proof.
- `generated-code boundary`: generated directories plus an authoritative schema/spec and thin wrappers around generated surfaces.

### Stronger Evidence Only

- `plugin seam` / provider registry: stable extension contract or runtime discovery. Say `plugin seam` unless runtime loading is explicit.
- `workflow / durable execution boundary`: workflow, activity, or state-machine artifacts plus retries, timers, or long-running orchestration. Do not infer from cron or queues alone.
- `translation seam` / anti-corruption boundary: explicit mappers shielding local vocabulary from external or legacy systems.

Do not promote a coexisting pattern to the dominant label unless it clearly dominates repo-wide runtime topology, control flow, or ownership seams.

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
- `library-sdk` repo kinds: favor public package roots, examples/tests-as-contract, and integration seams over app-style entrypoints when placing changes.
- `cli-tooling` repo kinds: preserve command boundaries, provider registries, and thin core/IO splits.

If confidence is low, turn these into conservative `do_not_assume` warnings instead of assertive change guidance.

## Overclaim Boundary

Do not claim these specialized patterns without direct evidence:

- CQRS
- event sourcing
- domain-driven design
- actor model
- service mesh architecture
- saga orchestration
- workflow engine / durable execution
- anti-corruption layer

When in doubt, state the simpler broader label and mention the missing proof.
