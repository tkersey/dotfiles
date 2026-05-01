# Eval prompts

Use these prompts to check whether the skill triggers only in the intended situations.

## Should trigger

```text
This repo feels over-engineered. Use $reduce to find layers we can remove.
```

Expected behavior: full or provisional de-abstraction audit with T/V/D scoring.

```text
Can we ditch the GraphQL layer and use simpler handlers without breaking clients?
```

Expected behavior: API-layer audit, external-consumer risk, compatibility-wrapper plan.

```text
We have a DI container but only one implementation for most services. What can we simplify?
```

Expected behavior: DI/plugin analysis, call-site evidence, slice/replace recommendations.

```text
Review this codegen setup. It is making every change expensive.
```

Expected behavior: generator/source-output inventory, generated import audit, staged replacement plan.

```text
How much of this Kubernetes/Helm/Terraform setup can we collapse for a single service?
```

Expected behavior: infra abstraction audit, environment-variation check, rollback/proof emphasis.

```text
The workflow changes valid actions after each user step. Make the interface simpler without losing that behavior.
```

Expected behavior: protocol-evolution analysis and transition table before flattening.

```text
Reduce the codebase before we build new features.
```

Expected behavior: broad abstraction-stack audit, not local style refactoring.

## Should not trigger

```text
Make this function easier to read.
```

Expected behavior: local refactoring skill, not `$reduce`.

```text
Fix this failing test.
```

Expected behavior: debugging/implementation, not de-abstraction audit unless the failure is from an abstraction cut.

```text
Rename these variables and clean up formatting.
```

Expected behavior: no `$reduce`.

```text
Optimize this SQL query.
```

Expected behavior: performance/database tuning, not `$reduce` unless the ask is to remove ORM/query-builder layers.

```text
Add a new endpoint for exporting reports.
```

Expected behavior: feature implementation, not `$reduce` unless the user asks to remove layers first.

```text
Find security vulnerabilities in this service.
```

Expected behavior: security review, not `$reduce` unless security risk is caused by abstraction/tooling layers.

## Borderline prompts

```text
This controller is too complicated.
```

Trigger only if the complexity comes from framework hooks, middleware, DI, decorators, generated code, or routing indirection. Otherwise use local complexity cleanup.

```text
The build is slow.
```

Trigger only if the likely cause is task-runner, monorepo, codegen, or tooling abstraction. Otherwise use build-performance analysis.

```text
Can we simplify auth?
```

Trigger if the ask is about reducing auth framework/layering. Do not flatten stateful auth/session/capability protocols without a transition table.

## Routing assertions

A correctly tuned `description` should match:

- de-abstraction
- fewer layers
- over-engineered
- remove framework/plugin/DI/codegen/task runner/ORM/GraphQL/infra
- lower-level primitives
- preserve behavior

It should not match ordinary:

- bug fix
- readability refactor
- formatting
- naming
- isolated performance tuning
- feature implementation
