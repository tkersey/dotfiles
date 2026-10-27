# Abstraction altitude

Use this reference when a task could move code either upward into a stronger construction or downward into simpler primitives. `universalist` and `reduce` are not enemies. They are directional moves on the same axis.

## Altitude scale

| Altitude | Shape | Typical good use | Typical overuse |
|---:|---|---|---|
| 0 | Platform primitives | HTML, CSS, JavaScript, files, SQL, shell, HTTP, browser forms, OS processes | Reimplementing framework behavior that is already needed |
| 1 | Explicit local code | functions, modules, records, small scripts, direct constructors | hand-rolled conventions copied everywhere |
| 2 | Domain invariants | refined values, tagged unions, checked constructors, witnesses, invariant-preserving products | premature modeling of unstable rules |
| 3 | Local interpreters/protocols | ASTs, reducers, state machines, transition tables, small interpreters | DSLs or workflow engines where a table/function would do |
| 4 | Framework/tooling layer | React, Next, Rails, ORMs, GraphQL, DI, codegen, bundlers, task runners | hidden control flow, generated surface, slow local loops, build tax |
| 5 | Distributed/platform abstraction | queues, microservices, service meshes, Kubernetes, Helm, Terraform modules, platform gateways | operational complexity without proven scale, ownership, or policy need |

## Legal moves

### Climb

Use `universalist` when a stronger shape of truth removes repeated obligations, impossible states, unchecked agreement, branchy policy logic, or syntax/execution mixing.

### Descend

Use `reduce` when a layer's tax exceeds its proven value and a lower-level primitive can preserve observable behavior.

### Hold

Keep the current altitude when value, public obligation, protocol safety, operational leverage, or team constraints are proven.

### Split

Reduce the incidental wrapper while preserving or strengthening the essential invariant. This is the common best move.

Examples:

- Remove a React/Vite stack from a mostly static site, but keep a checkout flow as an explicit reducer/state table.
- Replace a GraphQL gateway that forwards one internal call, but preserve the external schema behind a compatibility endpoint until clients migrate.
- Remove a DI container with one implementation per interface, but keep a composition root that documents dependency wiring.
- Delete a codegen client for unused endpoints, but keep a narrow typed client for the three endpoints that are externally committed.

## Routing questions

Ask these before moving:

1. What truth does the current abstraction carry?
2. What tax does it impose on a simple change?
3. Which lower primitive could carry the same truth?
4. Which stronger construction would delete repeated obligations?
5. What proof signal would detect behavior loss?
6. What boundary must remain compatible?
7. Is the right answer climb, descend, hold, or split?

## Decision rules

- Climb only when the higher abstraction deletes more obligation than it adds.
- Descend only when the lower primitive preserves the truth the current abstraction was carrying.
- Hold when the proof surface is weak and the external risk is high.
- Split when a framework/tooling wrapper is incidental but a domain invariant or state protocol is essential.

## Common split moves

| Current shape | Descent | Climb or preserve |
|---|---|---|
| React SPA with simple pages and one real wizard | HTML/CSS/JS, native forms, small ES modules | explicit reducer/state table for wizard |
| ORM used for two simple queries plus one transaction | direct SQL/query builder for simple paths | retain transaction helper or unit-of-work wrapper |
| GraphQL gateway forwarding one service | direct REST/RPC or typed call | compatibility schema while clients migrate |
| DI container with static app wiring | explicit constructors/composition root | keep interface only where multiple implementations are real |
| workflow engine used as glorified enum | explicit transition table | preserve retries, timers, audit steps if real |
| codegen client with huge generated surface | handwritten narrow client | preserve schema validation/contract tests |

## Output vocabulary

Use these labels consistently across both skills and subagents:

- `current_altitude`
- `proposed_altitude`
- `move`: `climb | descend | hold | split`
- `essential_truth`
- `abstraction-tax`
- `first_seam`
- `compatibility_boundary`
- `proof_signal`
- `rollback`
- `stop_condition`
