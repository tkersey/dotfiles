# Agent-editability counters

Use these counters to make abstraction tax measurable. Do not rely on taste alone.

## Counters

| Counter | Definition | Low tax | High tax |
|---|---|---|---|
| Edit hops | Files that must change for one behavior change | 1-2 predictable files | many files across layers/config/generated code |
| Lookup hops | Files an agent must read before locating behavior | direct entrypoint and local module | hidden lifecycle, registry, framework magic |
| Tool hops | Commands needed before a change can be checked | one test/typecheck command | install, generate, build, migrate, bootstrap, services |
| Hidden hops | Non-code lifecycle steps | direct function call | decorators, reflection, plugin discovery, DI, framework callbacks |
| Diff opacity | Lines changed per semantic change | small hand-written diff | generated/reformatted artifacts dominate |
| Proof latency | Fastest deterministic verification | seconds/local | minutes, external services, flaky integration only |
| Deploy weight | Artifact and release complexity | static files/simple binary | bundle pipeline, orchestrator, multi-service deployment |

## How to record

Use compact evidence:

```md
edit_hops: 7 files for one endpoint field
lookup_hops: route -> controller -> decorator -> generated schema -> resolver -> service -> mapper
tool_hops: pnpm install, pnpm codegen, pnpm build, docker compose up, pnpm test:e2e
hidden_hops: decorator registration and runtime DI container
diff_opacity: 1 semantic line plus 600 generated lines
proof_latency: fastest local check ~45s; full confidence only e2e
```

## Scoring guidance

- Use these counters to support `T`, not to replace judgment.
- High tax can be justified when value is proven.
- Low tax does not mean the abstraction is useful; it only means it is cheap.
- If counters are estimated, mark confidence medium or low.

## Agent-native web note

Coding agents make direct platform code more viable when the behavior is simple and testable. HTML, CSS, native forms, native constraint validation, URL state, browser APIs, ES modules, small reducers, and server-rendered templates are often easier for agents to inspect and edit than framework stacks with build steps and hidden conventions. Keep higher web layers when their value is proven by real client state, ecosystem leverage, hydration/islands, routing needs, accessibility infrastructure, or team/runtime constraints.
