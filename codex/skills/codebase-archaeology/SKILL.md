---
name: codebase-archaeology
description: "Systematically explore an unfamiliar codebase and build a reusable architecture and data-flow model. Use for repository onboarding, legacy-code understanding, entry-point discovery, feature or bug tracing, migration preparation, or explicit parallel exploration. Start with project guidance and documentation, then trace representative flows."
---
# Codebase Archaeology

## Mission

Build a practical mental model without reading files randomly.

```text
guidance -> repository shape -> entry points -> domain -> data flow
         -> integrations/config -> tests -> concise synthesis
```

## Common single-agent path

1. Read `AGENTS.md`, README files, architecture notes, and manifests first.
2. Classify the repository shape, runtime, build system, and top-level modules.
3. Identify actual entry points: CLI commands, routes, bootstraps, workers,
   schedulers, and public APIs.
4. Recover the few central domain types, their owners, and lifecycle.
5. Trace representative flows from input through validation, orchestration,
   domain logic, persistence/integration, and output.
6. Map configuration, external systems, files, queues, credentials boundaries,
   and generated surfaces without exposing secrets.
7. Read tests and fixtures to infer intended behavior and proof commands.
8. Separate observed facts, supported inferences, and open questions.
9. Synthesize an architecture map and mental model with concrete file/symbol
   evidence.
10. Stop before implementation unless the user explicitly changes the task.

Documentation first, then data flow.

## Conditional disclosure

Load [references/LANGUAGES.md](references/LANGUAGES.md) only when
language-specific discovery commands are needed.

Load [references/PATTERNS.md](references/PATTERNS.md) only after concrete
structure exists and a named architecture pattern would compress the evidence.

Load [references/EXAMPLES.md](references/EXAMPLES.md) only when the requested
output form is unclear.

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for ordinary single-agent
onboarding or one feature trace. Load it only for explicit parallel exploration,
the full custom-agent topology, specialist packet validation, deep multi-lane
synthesis, or an unported edge route. Its frontmatter is archived source, not a
second skill definition.

## Parallel route

Use subagents only on explicit request. The parent binds one artifact state and
scope, assigns disjoint read-only lanes, validates evidence packets, resolves
disagreements, and synthesizes one model. Worker-specific prompts and topology
must not burden the normal path.

## Output

Prefer a concise architecture summary containing repository shape, entry points,
core types, representative flows, integrations/configuration, tests, a mental
model, open questions, and the most valuable next dives. Do not dump raw notes
or enumerate every type.
