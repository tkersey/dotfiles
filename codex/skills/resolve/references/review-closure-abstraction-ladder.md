# Review-Closure Abstraction Ladder

The ladder prevents review findings from flowing directly into additive patches.

```text
2. complexity-mitigator
3. simplify-and-refactor-code-isomorphically
4. reduce
5. universalist
6. fixed-point-driver
7. accretive-implementer
```

Earliest owner wins. Do not run every rung by default.

## Rung 2: complexity-mitigator

Use when the finding touches branchy, nested, flag-heavy, hard-to-follow, cross-file, mutable-state, or specification-risky code.

Question: Do we understand the code well enough to cut?

Output: Micro Preflight and smallest clarity cut.

Blocks: patching code the agent does not understand.

## Rung 3: simplify-and-refactor-code-isomorphically

Use when the proposed fix would add or preserve helper/wrapper/adapter/branch/test-case accumulation, duplicate/pass-through/shadow surface, near-clones, parameter-sprawl, local defensive code, or obvious behavior-preserving collapse opportunities.

Question: Can we reduce behavior-preservingly?

Output: isomorphic refactor preflight, equivalence proof route, or behavior-preserving collapse route.

Blocks: adding code when behavior-preserving collapse is available.

## Rung 4: reduce

Use when the finding adds, preserves, or works around layer/tooling/framework/generated/config abstraction tax.

Question: Is this layer or abstraction tax?

Output: `descend | hold | split | ask-universalist`.

Blocks: adding another layer to compensate for layer tax.

## Rung 5: universalist

Use when repeated findings indicate a missing boundary artifact, protocol/state-machine artifact, explicit IR, effect signature, context certificate, canonical composition seam, or wrong shape of truth.

Question: Is the boundary artifact missing?

Output: one-seam boundary/construction call, obstruction report, or proof signal.

Blocks: local patches when the boundary artifact is missing.

## Rung 6: fixed-point-driver

Use when findings are coupled, repeated, invariant-linked, deletion-sensitive, likely to reopen, or involve duplicate truth owners, additive scaffolds, or unresolved ablation pressure.

Question: Are findings coupled enough to require normal form?

Output: normal-form route, ablation status, surface budget, and implementation handoff.

Blocks: repeated local fixes that should become normal-form repair.

## Rung 7: accretive-implementer

Use only after route selection as the single-writer executor.

Question: What is the smallest sufficient owned implementation route?

Output: `right_sized_route`, `surface_delta_call`, and proof receipt.

Blocks: direct mutation before route selection.

## Receipt

```yaml
review_closure_abstraction_receipt:
  review_item_id: "..."
  adjudication_route: "address | delete-collapse-canonicalize | validate-only | resolve-thread-only | do-not-address | blocked"
  primary_smell:
    hard_to_understand_or_spec_risk: yes|no
    duplicate_or_pass_through_surface: yes|no
    layer_or_tooling_tax: yes|no
    missing_boundary_artifact: yes|no
    coupled_or_repeated_findings: yes|no
    implementation_only_after_route_selection: yes|no
  earliest_applicable_rung: "complexity-mitigator | simplify-isomorphic | reduce | universalist | fixed-point-driver | accretive-implementer"
  selected_skill: "..."
  reason_selected: "..."
  rejected_later_rungs:
    - skill: "..."
      reason: "earlier rung owned the pathology"
  selected_route: "no-change | validate-only | delete-collapse-canonicalize | refactor-existing-owner | mutate-existing-owner | add-new-surface | blocked"
  proof_required: []
```

If this receipt cannot be filled, do not mutate.
