---
name: complexity-mitigator
description: "Existing-code comprehension and local winnowing preflight. Use for simplify/refactor/clean up/untangle, nested branches, boolean soup, opaque names, mixed responsibilities, cross-file state, or review stalls. Factor the local whole, separate essential/incidental/specification-risk factors, winnow dominated or duplicated factors, and emit the smallest clarity cut. Not for broad architectural layer removal, kernel quotienting, invariant remediation, or greenfield planning."
---

# Complexity Mitigator

## Intent

Reduce understanding cost in existing code while preserving essential domain
meaning. This skill is a read-only routing rail and analysis preflight, not a
delivery owner.

```text
FACTORING -> WINNOWING
```

- Factor the code into responsibilities, states, effects, decisions, and
  boundaries.
- Retain essential domain factors.
- Expose specification-risk factors before refactoring.
- Remove, collapse, rename, localize, or delegate incidental factors.
- Route repeated semantic distinctions or causal review pressure to
  `$review-fold` and `$actuating`.

## Activation

Use for hard-to-follow existing code, deep nesting, boolean soup, mixed
parse/validate/decide/effect behavior, cross-file hops, hidden state, ordering
dependencies, opaque names, and review stalls caused by comprehension.

Handoff instead:

- broad framework or layer tax -> `$reduce`;
- unclassified review evidence -> `$review-fold`;
- classified owner-boundary pressure -> `$actuating`;
- illegal states or invariant ownership -> `$invariant-ace`;
- missing essential structural shape -> `$universalist`;
- implementation -> `$actuating` or the owning workflow.

## Workflow

1. Choose the slice: entry point, inputs, outputs, state, effects, and boundary.
2. Factor it into responsibilities, decisions, state, effects, external
   obligations, and proof surfaces.
3. Classify each factor as `essential`, `incidental`, `mixed`, or `spec-risk`.
4. Identify duplicated, dominated, subsumed, vestigial, pass-through, or
   misplaced factors.
5. Preserve essential factors and unresolved specification risk.
6. Winnow in this order: delegate, flatten, rename, localize, collapse, then
   extract only after stable repetition is evidenced.
7. State the recomposition rule and smallest proof signal.
8. Return a handoff; do not implement.

## Review handoff

When selected as an Actuating review lens, return only current-head evidence:

```yaml
complexity_evidence:
  bound_head:
  owner_boundary:
  governing_law:
  participating_abstractions:
    - abstraction:
      live_obligation:
      status: retain | retire | collapse | delegate | replace | validate-first
  dominated_factors: []
  smallest_local_repair:
  local_repair_adds_semantic_machinery: true | false
  structural_pressure: []
  proof_surface_before: []
  proof_surface_after: []
  falsifier:
  evidence_refs: []
```

`$review-fold` may use this evidence while classifying the current review
horizon. `$actuating` evaluates the fold against the incumbent architecture and
its ephemeral Architecture Working Set. This lens never selects a repair,
reopens architecture, grants mutation, or persists workflow state.

If a local repair introduces a protocol, state, helper abstraction, repeated
branch family, compatibility route, or wound-specific proof family, mark it as
semantic growth. Actuating decides whether the incumbent remains closed under
the obligation or architecture selection must reopen.

## Output

```text
Complexity preflight:
- whole:
- dominant cost:
- factorization:
- retain:
- remove/collapse/delegate:
- unresolved specification risk:
- recomposition:
- proof:
- handoff:
```

## Guardrails

- Do not edit files or commit.
- Do not select architecture, review credit, mutation, or closure.
- Do not confuse fewer lines with lower understanding cost.
- Do not delete essential policy or unresolved external obligations.
- Do not extract abstractions before stable shape is visible.
- If behavior is unclear, request an executable learning surface such as an
  example matrix, contract test, fixture set, or state table.
