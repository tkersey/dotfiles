# Regression: Ability Conformance-Matrix Spec Pipeline Failure

Date observed: 2026-05-08
Session: `019e0901-8fe1-7733-8522-ea2b69f04da9`

## Failure summary

A user supplied a decision-complete Ability implementation brief. The workflow produced a `$plan` artifact, entered a `$grill-me` loop, required a user drift correction, invoked `$spec-pipeline` late, then emitted the spec inside `<proposed_plan>`. The final content was directionally useful, but the state machine was not externally observable.

## Expected behavior

When a brief already provides goal, target surfaces, non-goals, invariant/authority boundary, acceptance criteria, and proof commands:

1. Research discoverable repo facts.
2. Emit exact Evidence Brief labels.
3. Run anti-drift checkpoint against the authoritative brief.
4. Ask no questions unless a material contradiction remains.
5. Emit `spec_decision_packet`.
6. Emit Gate Result with `plan_allowed` and script status.
7. Produce the implementation spec as plain markdown, not `<proposed_plan>`.
8. Run exactly one invariant challenge.
9. Emit Spec Lint Result with script status or explicit skip reason.
10. End with a short Execution Handoff to `$plan`.

## Forbidden regression

Do not produce:

```text
<proposed_plan>
# ... Spec ...
</proposed_plan>
```

Do not include `$plan` convergence sections such as `Round Delta`, `Iteration Change Log`, `Decision Impact Map`, `Adversarial Findings`, or `Contract Signals` in a `spec-pipeline` artifact.

## Mechanical checks

A saved output for this scenario should pass:

```bash
uv run python codex/skills/spec-pipeline/scripts/check_spec_pipeline_output.py path/to/spec-output.md
```

The checker is mechanical. The model must still judge semantic completeness, proof adequacy, and drift.
