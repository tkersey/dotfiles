# Syntax / Semantics Pivot

## Core idea

Agentic and software systems often fail because they execute opaque behavior directly. The syntax/semantics pivot separates:

```text
Syntax world    = plans, operations, policies, memory queries, workflow steps, patches, context schemas.
Semantic world  = effects, traces, public behavior, policy outcomes, memory consequences, observations.
Interpreter     = handle / run / compile / lower / render / project.
Law             = accepted syntax denotes valid observed semantics.
```

Syntax gives agents handles. Semantics gives those handles meaning. Laws connect them.

## Use when

- tool calls are raw `name + args` or arbitrary callbacks;
- plans are prose but need validation or replay;
- policies are embedded in prompts or scattered predicates;
- memory/context is raw text rather than typed context;
- workflow behavior is hidden in callbacks or branches;
- patches are produced without semantic intent;
- a syntax exists but no interpreter/law certifies its meaning.

## Repairs

| Smell | Syntax artifact | Semantic artifact | Law |
|---|---|---|---|
| direct tool calls | `ToolOperation` | external effect + trace | allowed op produces allowed trace |
| prose plan | `Plan` IR | execution trace | trace satisfies proof obligations |
| policy in prompt | `PolicyRule` | `PolicyDecision` | evaluation matches allowed observations |
| raw memory chunks | context schema | certified context | rendering preserves observables |
| callbacks | operation/frame IR | interpreter effect | `apply(encoded,x) == oldCallback(x)` |
| patch without intent | `PatchIntent` | behavior/invariant delta | verification matches declared intent |

## Syntax/Semantics Certificate

Use `templates/syntax-semantics-certificate.md` when the repair introduces or modifies syntax, semantics, or an interpreter boundary.

## Soundness / adequacy / preservation

- **Soundness**: every accepted syntax term denotes valid semantic behavior.
- **Adequacy**: required semantic distinctions are representable or observable.
- **Preservation**: syntax transformations preserve declared observations.
- **Falsifier**: accepted syntax with invalid semantics, or needed semantics not expressible in syntax.
