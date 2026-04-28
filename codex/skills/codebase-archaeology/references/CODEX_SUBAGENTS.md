# Codex Subagents for Codebase Archaeology

This skill replaces Claude-style `Task tool -> subagent_type: "Explore"` instructions with Codex-native custom agents.

## Files that create the custom agents

Project-scoped agents are standalone TOML files:

```text
.codex/agents/archaeology-explorer.toml
.codex/agents/archaeology-docs.toml
.codex/agents/archaeology-entrypoints.toml
.codex/agents/archaeology-domain.toml
.codex/agents/archaeology-dataflow.toml
.codex/agents/archaeology-integrations.toml
.codex/agents/archaeology-tests.toml
```

Each agent file defines:

- `name`
- `description`
- `developer_instructions`
- `sandbox_mode = "read-only"`

The skill itself remains under:

```text
.agents/skills/codebase-archaeology/SKILL.md
```

## Recommended fan-out

For deep exploration of a large repository, ask Codex to spawn these six workers:

| Agent | Worker objective |
|---|---|
| `archaeology_docs` | docs, manifests, repository conventions, setup, declared architecture |
| `archaeology_entrypoints` | entry points, route/command/job topology, bootstrap paths |
| `archaeology_domain` | core types, schemas, entities, state, domain relationships |
| `archaeology_dataflow` | representative end-to-end flows from input to output |
| `archaeology_integrations` | config, storage, external APIs, queues, file I/O, runtime boundaries |
| `archaeology_tests` | tests, fixtures, CI hints, intended behavior, coverage gaps |

For a smaller repository or a broad first pass, use only `archaeology_explorer`.

## Prompt examples

Deep parallel exploration:

```text
Use $codebase-archaeology with Codex subagents. Spawn archaeology_docs, archaeology_entrypoints, archaeology_domain, archaeology_dataflow, archaeology_integrations, and archaeology_tests. Keep all agents read-only. Wait for all agents, then synthesize one architecture summary with file:line evidence, open questions, and suggested next dives.
```

Single general worker:

```text
Use $codebase-archaeology. Spawn archaeology_explorer to map this repo read-only, then summarize the architecture, key types, data flow, integrations, config, and tests.
```

Focused feature trace:

```text
Use $codebase-archaeology with Codex subagents for the billing feature. Have archaeology_entrypoints find routes/commands, archaeology_domain map billing entities, archaeology_dataflow trace request to persistence, and archaeology_tests identify the relevant test coverage. Wait for all, then synthesize.
```

## Parent synthesis contract

The parent agent should not merely concatenate worker responses. It should de-duplicate repeated findings, normalize terminology, resolve or call out disagreements, separate source-backed facts from inferences, and produce the final architecture summary in the template from `SKILL.md`.

## Safety and scope

Archaeology agents should not modify the repository. Their job is to inspect, map, and cite. If a user later asks for implementation work, switch to a different agent/workflow and make the requested changes explicitly.
