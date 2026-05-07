# Lan vs Ran decision trace

Problem: migrate API v1 users to API v2 while keeping old client behavior.

`Lan` design:

- Generate v2 resources from v1 resources.
- Good when v2 should be populated freely from v1.
- Risk: accidental merging/defaults hide missing semantics.

`Ran` design:

- Define v2 facade by all old observations that must remain valid.
- Good when compatibility is stricter than generation.
- Risk: overconstrained product of old observations.

Decision rule:

- If the next task is data creation/code generation, start with `Lan`.
- If the next task is compatibility/read behavior, start with `Ran`.
- Use `Δ` for old clients reading the new API.
