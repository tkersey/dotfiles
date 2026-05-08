# Adjacent Skill Boundaries

Use this reference to prevent `algebra-driven-design` from absorbing neighboring skills.

## `algebra-driven-design` vs `kan`

Use ADD when the governing question is domain algebra:

- carriers
- operations
- observations
- laws and non-laws
- effects and interpreters
- law-derived architecture
- property/trace/parity tests

Use `kan` when the governing question is a boundary equation:

- extension across `K`
- lift through `P`
- compatibility facade
- generated target semantics
- public projection
- defunctionalized boundary IR
- Yoneda/Coyoneda boundary representation
- categorical witness and law tests

## `algebra-driven-design` vs `universalist`

Use ADD to discover laws and domain operations.

Use `universalist` when the main question is the smallest honest abstraction or construction that makes repeated obligations/impossible states explicit.

## `algebra-driven-design` vs `reduce`

Use ADD to derive structure from laws.

Use `reduce` when the user asks to remove layers, replace frameworks/tools/codegen, or lower abstraction while preserving behavior.

If ADD finds no law-bearing abstraction and only incidental wrappers remain, hand off to `reduce`.

## `algebra-driven-design` vs `invariant-ace`

Use ADD for the full law-to-architecture loop.

Use `invariant-ace` for focused correctness hazards: lifecycle, protocol, state transitions, idempotency, validation sprawl, impossible states, retries, and race risks.

## `algebra-driven-design` vs `spec-pipeline`

Use ADD to model the domain and derive requirements/tests.

Use `spec-pipeline` to turn a decision-complete or grill-complete project request into an implementation-ready spec.

## `algebra-driven-design` vs `ideate`

Use ADD when the user already wants law-driven design or refactor.

Use `ideate` when the user asks what to improve/build and the answer requires repo evidence, opportunity ranking, and a plan seed.

## Handoff pattern

ADD output should hand off with this compact packet when another skill owns the next phase:

```yaml
add_handoff:
  carriers:
  operations:
  observations:
  laws:
  non_laws:
  architecture_implications:
  proof_surfaces:
  recommended_next_skill:
  reason:
```
