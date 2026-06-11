# Specialist Workers for Codebase Archaeology

Use the version-neutral worker model in `../../references/codex-specialist-worker-model.md`. Do not depend on one runtime's subagent invocation syntax or install path.

## Repository worker definitions

This dotfiles repo stores reusable worker TOML files under `codex/agents/`:

```text
codex/agents/archaeology-explorer.toml
codex/agents/archaeology-docs.toml
codex/agents/archaeology-entrypoints.toml
codex/agents/archaeology-domain.toml
codex/agents/archaeology-dataflow.toml
codex/agents/archaeology-integrations.toml
codex/agents/archaeology-tests.toml
```

The active Codex runtime or local dotfiles setup decides how those TOML files become invokable. If worker execution is unavailable, use root-equivalent packets or perform the exploration in the parent thread and state the fallback.

## Recommended fan-out

For deep exploration of a large repository, use these read-only workers when supported:

| Worker | Objective |
|---|---|
| `archaeology_docs` | docs, manifests, repository conventions, setup, declared architecture |
| `archaeology_entrypoints` | entry points, route/command/job topology, bootstrap paths |
| `archaeology_domain` | core types, schemas, entities, state, domain relationships |
| `archaeology_dataflow` | representative end-to-end flows from input to output |
| `archaeology_integrations` | config, storage, external APIs, queues, file I/O, runtime boundaries |
| `archaeology_tests` | tests, fixtures, CI hints, intended behavior, coverage gaps |

For a smaller repository or a broad first pass, use only `archaeology_explorer` or do the pass in the root.

## Parent synthesis contract

The parent/root must assign `artifact_state_id`, validate packets against `../../references/specialist-packet-contract.md`, reject stale or low-value packets before synthesis, de-duplicate repeated findings, normalize terminology, resolve or call out disagreements, separate source-backed facts from inferences, and produce the final architecture summary in the template from `SKILL.md`.

Workers must not modify the repository.
