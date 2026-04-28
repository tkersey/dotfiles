# Common Architecture Patterns

Use these signals to recognize the system shape quickly. A repository can combine several patterns.

## Layered / MVC / N-tier

Signals: directories like `controllers/`, `routes/`, `handlers/`, `services/`, `repositories/`, `models/`; flow resembles route/controller → service/use case → repository/model.

```bash
rg -n "controller|handler|route|router|service|repository|dao" src app lib
rg -n "class .*Controller|func .*Handler|app\.(get|post)|@router\." src app lib
```

Ask: Which layer owns validation? Which layer owns transactions? Are repositories thin persistence wrappers or domain abstractions?

## Hexagonal / Ports and Adapters

Signals: `domain/` or `core/` has interfaces/ports that do not import infrastructure; `adapters/`, `infra/`, or `drivers/` implement databases, HTTP clients, queues, or file systems.

```bash
rg -n "port|adapter|gateway|driver|infrastructure|interface .*Repository|trait .*Repository" src app crates
rg -n "domain|core|infra|adapter" .
```

Ask: What are the primary and secondary ports? Are domain modules isolated from framework dependencies?

## Event-Driven / Message-Based

Signals: `events/`, `consumers/`, `subscribers/`, `handlers/`, `workers/`, `queues/`; terms like event, command, handler, consumer, producer, projector.

```bash
rg -n "event|consumer|subscriber|producer|queue|message|topic|handler|projector" src app lib
rg -n "kafka|sqs|sns|rabbit|nats|pubsub|bull|celery|sidekiq" .
```

Ask: What events enter and leave? Are handlers idempotent? Where are retry, dead-letter, and ordering semantics defined?

## CQRS / Command-Query Separation

Signals: `commands/`, `queries/`, `handlers/`, `read-models/`, `projections/`; write paths and read paths have separate models or services.

```bash
rg -n "command|query|projection|projector|readModel|read_model|writeModel|write_model" src app lib
```

Ask: What commands mutate state? What query paths read state? Are projections synchronous, asynchronous, or eventually consistent?

## Monorepo / Multi-Service

Signals: `apps/`, `packages/`, `services/`, `crates/`, `libs/`, `modules/`; multiple manifests or service configs.

```bash
find . -maxdepth 3 -type f \( -name 'package.json' -o -name 'Cargo.toml' -o -name 'go.mod' -o -name 'pyproject.toml' -o -name 'pom.xml' \) -print
find . -maxdepth 2 -type d \( -name apps -o -name packages -o -name services -o -name crates -o -name libs \) -print
```

Ask: Which package is the app entry point? Which packages are shared libraries? How do packages depend on each other?

## Plugin / Extension System

Signals: `plugins/`, `extensions/`, `hooks/`, `registry/`, `providers/`; registration, discovery, dynamic imports, or dependency injection containers.

```bash
rg -n "plugin|extension|hook|registry|register|provider|discover|dynamic import|import\(" src app lib
```

Ask: What is the plugin interface? Where are plugins discovered and registered? What lifecycle hooks exist?

## Background Jobs / Schedulers

Signals: `jobs/`, `workers/`, `cron/`, `schedulers/`, `tasks/`; libraries like Celery, Sidekiq, Bull, Agenda, Quartz, cron, Temporal.

```bash
rg -n "job|worker|cron|schedule|scheduler|task|perform|enqueue|queue" src app lib
rg -n "celery|sidekiq|bull|agenda|temporal|quartz|cron" .
```

Ask: What triggers each job? What state does it mutate? What are retry and failure semantics?

## Client-Server Split

Signals: `frontend/`, `web/`, `client/`, `ui/` paired with `api/`, `server/`, `backend/`; generated clients, shared schemas, OpenAPI/GraphQL definitions.

```bash
find . -maxdepth 2 -type d \( -name frontend -o -name web -o -name client -o -name ui -o -name api -o -name server -o -name backend \) -print
rg -n "openapi|swagger|graphql|trpc|zod|protobuf|grpc" .
```

Ask: What is the API boundary? Are schemas shared or duplicated? Where are authentication and session state handled?

## Data Pipeline / ETL

Signals: `pipelines/`, `dag/`, `extract/`, `transform/`, `load/`, `notebooks/`, `jobs/`; Airflow, Dagster, dbt, Spark, Beam, Kafka, or warehouse clients.

```bash
rg -n "pipeline|extract|transform|load|dag|airflow|dagster|dbt|spark|beam|warehouse|snowflake|bigquery" .
```

Ask: What is the source data? How is schema evolution handled? Where do outputs land? How are jobs scheduled and retried?
