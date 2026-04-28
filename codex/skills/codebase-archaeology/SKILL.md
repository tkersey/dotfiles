---
name: codebase-archaeology
description: Codex-native workflow for systematically exploring unfamiliar codebases and building reusable technical architecture summaries. Use when onboarding to a repo, understanding legacy code, mapping data flow, finding entry points, or running explicit parallel Codex subagent exploration.
---

# Codebase Archaeology — Codex Native

## Purpose

Build a practical mental model of an unfamiliar codebase without reading files randomly. Start with project guidance and documentation, then trace from entry points through domain logic, storage, integrations, configuration, and tests.

Use this skill for onboarding to a new repository, answering “what does this project do?”, understanding legacy or inherited code, mapping architecture before a migration/refactor/feature, tracing a bug or feature path, and creating a reusable technical architecture summary.

## Core Rule

Documentation first, then data flow.

Before reading source, inspect the project-level context that Codex should already respect:

```bash
cat AGENTS.md README.md 2>/dev/null | head -200
find . -maxdepth 2 \( -name 'AGENTS.md' -o -name 'README*' -o -name 'CONTRIBUTING*' -o -name 'docs' \) -print
```

Do not skip this step. `AGENTS.md`, README files, and docs often contain architecture notes, setup assumptions, local conventions, and non-obvious constraints that are expensive to rediscover from code alone.

## Codex Compatibility Rules

This skill is written for Codex CLI, Codex IDE, and Codex app.

- Do not use Claude Code `Task`, `Agent`, `subagent_type`, or tool-call syntax.
- Do not assume an `agents/` folder inside the skill creates subagents.
- Codex skills live in `.agents/skills/<skill-name>/SKILL.md` or another Codex skill discovery location.
- Codex custom agents are standalone TOML files under `.codex/agents/` for project-scoped agents or `~/.codex/agents/` for personal agents.
- Codex only spawns subagents when the user explicitly asks for subagents, parallel agents, one agent per topic, or equivalent multi-agent work.
- Subagents are read-only by default in this package. They gather evidence and return summaries; the parent agent performs synthesis.

## Inputs

Resolve these from the user prompt and repository context:

| Input | Default | Notes |
|---|---:|---|
| `scope` | whole repository | May be a package, service, directory, feature, route, command, or file set. |
| `depth` | `standard` | Use `quick` for a fast map, `standard` for a normal architecture summary, `deep` for parallel/subagent exploration. |
| `focus` | architecture + data flow | May be entry points, one feature, storage, config, test strategy, module ownership, or legacy risk. |
| `subagents` | false | True only when the user explicitly asks for Codex subagents or parallel agents. |
| `output` | technical architecture summary | Adapt if the user asks for a map, migration notes, bug trace, or onboarding guide. |

## Standard Single-Agent Workflow

### 1. Read project guidance and docs

```bash
cat AGENTS.md README.md 2>/dev/null | head -240
find . -maxdepth 3 \( -name 'README*' -o -name 'CONTRIBUTING*' -o -name 'ARCHITECTURE*' -o -name 'docs' \) -print
```

Capture purpose, runtimes, package managers, local commands, repository conventions, and named services/apps/packages.

### 2. Classify repository shape

```bash
find . -maxdepth 2 -type f \( -name 'package.json' -o -name 'Cargo.toml' -o -name 'pyproject.toml' -o -name 'go.mod' -o -name 'pom.xml' -o -name 'build.gradle*' -o -name 'composer.json' \) -print
find . -maxdepth 2 -type d | sed 's#^./##' | sort | head -120
```

Classify the repo as CLI/tooling, web frontend, backend service, full-stack app, library/package, monorepo, data pipeline, or infrastructure/config.

### 3. Identify entry points

```bash
rg -n "fn main|def main|if __name__ == ['\"]__main__['\"]|func main|public static void main|function main|export default|createRoot|FastAPI\(|Flask\(|express\(|Router\(|app\.(get|post|put|delete)|@app\.|clap|argparse|click|typer|cobra|commander|yargs" .
```

Record CLI commands, HTTP routes, app/bootstrap modules, workers/schedulers/consumers/jobs, and library public APIs.

### 4. Find the core domain model

```bash
rg -n "^(export )?(pub )?(struct|enum|class|interface|type) [A-ZA-Za-z0-9_]+|^type [A-ZA-Za-z0-9_]+ struct|@dataclass|BaseModel|Schema|z\.object|createTable|model " .
```

Do not list every type. Identify the central 3-5 types and explain relationships, ownership, and lifecycle.

### 5. Trace data flow

Follow representative flows:

```text
entry point → parser/router/controller → service/use case → domain logic → storage/integration → response/output
```

For each important flow, answer what input arrives, where validation/normalization happens, which module orchestrates, which domain objects are created or changed, where persistence or external I/O happens, and what output is returned/emitted.

### 6. Map integrations and configuration

```bash
rg -n "process\.env|std::env|os\.environ|os\.getenv|dotenv|BaseSettings|config|settings|viper|serde::Deserialize" .
rg -n "fetch\(|axios|reqwest|requests\.|aiohttp|httpx|grpc|GraphQL|sqlx|rusqlite|diesel|prisma|sequelize|typeorm|sqlalchemy|redis|kafka|sqs|s3|open\(|File::|fs\." .
```

Capture databases, external APIs/SDKs, file I/O, queues/event buses, cron/jobs, environment variables, config files, defaults, CLI flags, and credential loading points without exposing secret values.

### 7. Read tests for intended behavior

```bash
find . -maxdepth 3 -type d \( -name test -o -name tests -o -name __tests__ -o -name spec -o -name specs \) -print
rg -n "describe\(|it\(|test\(|pytest|unittest|#\[test\]|func Test|@Test" .
```

Capture the test framework, test command, key fixtures, important tested behavior, and gaps where critical flows lack tests.

### 8. Synthesize, do not dump raw notes

Return a concise architecture model with file citations and a clear map. Do not paste large source snippets. Prefer exact `file:line` references when possible.

## Codex Subagent Workflow

Use this section only when the user explicitly asks for Codex subagents, parallel exploration, or one agent per topic. For normal questions, use the single-agent workflow above.

### Available custom agents

This package includes project-scoped custom agents:

| Agent | Role |
|---|---|
| `archaeology_explorer` | General read-only explorer for one comprehensive technical summary. |
| `archaeology_docs` | Reads docs, manifests, setup, repository conventions, and declared architecture. |
| `archaeology_entrypoints` | Maps bootstraps, routes, CLI commands, jobs, public APIs, and module topology. |
| `archaeology_domain` | Finds core entities, types, schemas, state, and domain relationships. |
| `archaeology_dataflow` | Traces representative input → processing → storage/output paths. |
| `archaeology_integrations` | Maps configuration, persistence, external APIs, queues, file I/O, and runtime boundaries. |
| `archaeology_tests` | Reads tests, fixtures, mocks, and CI hints to infer intended behavior and quality gates. |

### When to spawn which agents

For a large codebase or deep onboarding request, spawn these six agents in parallel:

1. `archaeology_docs`
2. `archaeology_entrypoints`
3. `archaeology_domain`
4. `archaeology_dataflow`
5. `archaeology_integrations`
6. `archaeology_tests`

For a smaller codebase or when the user asks for a single exploration agent, spawn only `archaeology_explorer`.

If the custom agents are not installed, use Codex's built-in `explorer` agent with the same prompts, or perform the exploration yourself and state which fallback was used.

### Parent orchestration rules

When using subagents: give every worker the same scope and constraints; instruct workers not to edit files; require file/symbol evidence; wait for all workers; merge into one mental model; de-duplicate facts; resolve disagreements; distinguish facts from inferences and open questions.

### Worker prompt template

```text
Run a read-only codebase archaeology pass for [SCOPE].
Focus: [DOCS|ENTRYPOINTS|DOMAIN|DATAFLOW|INTEGRATIONS|TESTS|GENERAL].
Depth: [quick|standard|deep].
Do not edit files. Prefer rg and targeted file reads. Cite concrete files and line numbers where possible.
Return:
1. Scope inspected
2. Key findings
3. Evidence table with path:line and symbol/module
4. Open questions or assumptions
5. Suggested next places to inspect
Keep the result concise; the parent agent will synthesize the final architecture summary.
```

## Output Template

```markdown
# [Project Name] — Technical Architecture Summary

## Executive Summary
[Project] is a [type of system] that [purpose]. Its main architectural shape is [pattern], with [major components].

## Repository Shape
- **Languages/runtimes:** [list]
- **Package/build system:** [list]
- **Top-level modules:** [brief map]
- **Main commands:** [setup/test/build/run commands if found]

## Entry Points
| Entry | Location | Purpose |
|---|---|---|
| [name] | `path:line` | [what starts here] |

## Architecture Map
```text
[input/client/CLI/job]
  → [router/command/parser]
  → [service/use case]
  → [domain model]
  → [storage/integration]
  → [output/response/artifact]
```

## Key Types and Data Structures
| Type/Schema | Location | Purpose | Related Modules |
|---|---|---|---|
| [Type] | `path:line` | [role] | [modules] |

## Data Flow
### [Flow name]
1. `path:line` — [entry]
2. `path:line` — [validation/transformation]
3. `path:line` — [domain logic]
4. `path:line` — [persistence/integration/output]

## Integrations and Configuration
| Boundary | Location | Notes |
|---|---|---|
| [database/API/file/env] | `path:line` | [what it does] |

## Tests and Intended Behavior
- **Framework:** [framework]
- **Commands:** [commands]
- **Notable coverage:** [important tested flows]
- **Gaps:** [critical flows not obviously covered]

## Mental Model
[One or two paragraphs explaining how to reason about the system when making a change.]

## Open Questions
- [Things that need runtime access, credentials, product context, or deeper inspection]

## Suggested Next Dives
- [Most valuable files/features to inspect next]
```

## Quick Prompts

Single-agent exploration:

```text
Use $codebase-archaeology to map this repo. Start with docs, then find entry points, core types, data flow, integrations, config, and tests. Return a concise technical architecture summary with file:line evidence.
```

Codex subagent exploration:

```text
Use $codebase-archaeology with Codex subagents. Spawn archaeology_docs, archaeology_entrypoints, archaeology_domain, archaeology_dataflow, archaeology_integrations, and archaeology_tests. Keep all agents read-only, wait for all of them, then synthesize one architecture summary with evidence and open questions.
```

Feature-specific trace:

```text
Use $codebase-archaeology to trace how [feature/route/command] works from entry point to storage/output. Include key files, data structures, config dependencies, and tests.
```

## Anti-Patterns

| Do not | Do instead |
|---|---|
| Start by reading random large files | Read docs, manifests, and entry points first |
| Dump raw source into the answer | Synthesize a mental model with citations |
| List every class/type | Identify the few core abstractions |
| Ignore tests | Use tests to infer intended behavior |
| Treat inferred architecture as fact | Label inferences and open questions clearly |
| Use Claude `Task` or `subagent_type` syntax | Ask Codex to spawn named custom agents explicitly |
| Let subagents edit files | Keep archaeology workers read-only |

## References

| Need | File |
|---|---|
| Codex subagent setup and examples | `references/CODEX_SUBAGENTS.md` |
| Language-specific searches | `references/LANGUAGES.md` |
| Architecture pattern recognition | `references/PATTERNS.md` |
| Example exploration sessions | `references/EXAMPLES.md` |
