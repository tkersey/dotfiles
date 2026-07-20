---
name: complexity-mitigator
description: "Existing-code comprehension and local winnowing preflight. Use for simplify/refactor/clean up/untangle, nested branches, boolean soup, opaque names, mixed responsibilities, cross-file state, or review stalls. Factor the local whole, separate essential/incidental/specification-risk factors, winnow dominated or duplicated factors, and emit the smallest clarity cut. Not for broad architectural layer removal, kernel quotienting, invariant remediation, or greenfield planning."
---

# Complexity Mitigator

## Intent

Reduce understanding cost in existing code while preserving essential domain meaning. This skill is a read-only routing rail and analysis preflight, not a delivery owner.

## Doctrine

Use a lightweight local form of:

```text
FACTORING -> WINNOWING
```

- Factor the code into responsibilities, states, effects, decisions, and boundaries.
- Retain essential domain factors.
- Expose specification-risk factors before refactoring.
- Remove, collapse, rename, localize, or delegate incidental factors.
- Do not run full behavioral quotienting unless repeated distinctions and accepted observations make it necessary; route that to `review-fold` or the owning review-closure workflow.

## Activation

Use for:

- hard-to-follow existing code;
- deep nesting, boolean soup, flags, mixed parse/validate/decide/effect;
- cross-file hops, hidden state, ordering dependencies, opaque names;
- review stalls caused by comprehension;
- explicit local simplicity/refactor requests.

Handoff instead:

- broad layer/framework/tooling tax -> `reduce`;
- unclassified review distinctions -> `review-fold`;
- classified owner-boundary pressure -> `$actuating` after `$review-fold`
  authors the current Counterexample Set;
- illegal states / invariant ownership -> `invariant-ace`;
- missing essential structural shape -> `universalist`;
- implementation -> `$actuating` or the owning workflow.

## Modes

### Micro Preflight

Use when another workflow owns implementation.

```text
Complexity preflight:
- whole:
- dominant cost:
- factorization:
- winnow:
- smallest clarity cut:
- do not change yet:
- handoff:
```

### Compact

For one function, file, or review comment:

1. Slice
2. Heat Read
3. Factorization / Winnowing Receipt
4. Essential vs Incidental vs Specification Risk
5. Preferred cut
6. Proof signal
7. Handoff

### Full

Use only when the slice crosses files, behavior is unclear, specification risk is material, or the user asks for deep analysis.

## Definitions

- **Essential complexity**: domain rules, invariants, required state transitions, and irreducible external obligations.
- **Incidental complexity**: complexity introduced by implementation choices; reducing it preserves required behavior.
- **Specification risk**: uncertainty about required behavior, policy, or boundary contract.

## Workflow

1. Choose the slice: entrypoint, inputs, outputs, state, effects.
2. Heat-read nesting, branches, flags, cross-file hops, state to simulate, and hidden side effects.
3. Factor the whole into responsibilities, decisions, state, effects, external constraints, and proof surfaces.
4. Classify each factor as `essential`, `incidental`, `mixed`, or `spec-risk`.
5. Check whether incidental factors are duplicated, dominated, subsumed, vestigial, pass-through, or better delegated to an existing facility.
6. Preserve essential factors and unresolved specification-risk factors.
7. Winnow in this order: delegate, flatten, rename, localize, collapse, extract only after stable repetition appears.
8. State the recomposition rule: how the retained factors still explain the behavior.
9. Name the smallest proof signal and handoff.

## Review finding handoff

When an actuation review profile selects this lens, return factorization
evidence to the review caller. `$review-fold` may cite it when classifying a
`counterexample-set/v1`; `$actuating` alone evaluates that Counterexample
against the current Construction and selects any successor. Do not choose the
repair, architecture, work node, or mutation.

~~~yaml
complexity_counterexample_evidence:
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
~~~

If local repair adds a protocol, state, helper abstraction, repeated branch
family, or wound-specific test family, mark it as semantically growing and
record the structural pressure. Actuating decides whether the current
Construction is a realization, architecture, or ablation defect.

## Factorization / Winnowing Receipt

```yaml
factorization_winnowing_receipt:
  whole: "..."
  factors:
    - id: "F1"
      obligation: "..."
      class: essential | incidental | mixed | spec-risk
      owner: "..."
      evidence_ref: "..."
      status: retain | delete | collapse | delegate | localize | rename | validate-first
  duplicated_or_dominated_factors: []
  irreducible_core: []
  recomposition_rule: "..."
  preservation_relation: observationally-equivalent | refinement-preserving | unknown
  proof_signal: "..."
  handoff: "..."
```

## Guardrails

- No file edits or commits.
- Do not select a review repair or work node.
- Do not confuse lower LOC with lower understanding cost.
- Do not delete essential policy or unresolved external obligations.
- Do not merge accidental rhymes.
- Do not extract abstractions before stable shape is visible.
- If behavior is unclear, recommend a learning artifact: example matrix, contract test, fixture set, state table, or spike.
- If reduction crosses architectural layers, hand off to `reduce`.

## Local playbook

1. Delegate homegrown incidental logic when a current local/platform facility has matching semantics.
2. Flatten control flow while keeping essential protocol/lifecycle steps explicit.
3. Rename vague verbs and implicit state.
4. Move meaning into data when it reduces branching or invalid combinations.
5. Extract only stable repeated concepts; one case is unique, two may be coincidence, three may justify extraction.

## Output

End with:

```text
Winnowing Bottom Line:
- retain:
- remove/collapse/delegate:
- unresolved specification risk:
- recomposition:
- proof:
- handoff:
```
