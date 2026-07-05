<proposed_plan>
# Example Fixed-Point Execution Policy

## Plan Identity

`PLAN-example-fixed-point`, revision 1. Target execution owner: `$actuating`.

## Source and Terminal Contract

The source digest is `sha256:example`. Terminal success is a source-current policy with resource predictions, proof, rollback, and a valid `$actuating` handoff.

## Policy State and Unknowns

Known: target branch and owner boundary are fixed by source authority.

Unknowns: none remain ungated after synthesis.

## Actions and Resource Predictions

- `ACTION-1`: inspect and bind current resources before mutation.
- `ACTION-2`: perform the bounded mutation after `$actuating` establishes mutation authority.
- Unknown resources default to `repo:all / exclusive`.

## Decision/Observation Rules

If resource prediction fails, block for controller selection. If a semantic gap appears, return to `$spec-pipeline` or `$grill-me`.

## Proof, Rollback, and Invalidators

Focused proof covers `ACTION-2`; final proof runs on the integrated target branch. Rollback reverts the bounded delivery and reopens resource prediction.

## Policy Synthesis Receipt

PSR-v1 summary:

```text
complete clean sweep: yes
independent press pass: yes
radical candidate: adopt
unresolved errors: 0
untreated material risks: 0
```

Receipt path:

```text
.ledger/plan/PLAN-example-fixed-point/synthesis-receipt.json
```

## `$actuating` Handoff

```yaml
actuating_handoff:
  plan_id: PLAN-example-fixed-point
  policy_ref: .ledger/plan/PLAN-example-fixed-point/policy.json
  policy_digest: sha256:example
  synthesis_receipt_ref: .ledger/plan/PLAN-example-fixed-point/synthesis-receipt.json
  synthesis_receipt_digest: sha256:example
  target_branch: feature/example
  proposed_resources:
    - action_id: ACTION-2
      resources:
        - root: path:src/example.zig
          mode: write
  proposed_cross_plan_dependencies: []
  mutation_allowed: no
```
</proposed_plan>
