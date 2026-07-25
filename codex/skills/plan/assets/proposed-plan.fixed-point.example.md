<proposed_plan>
# Example Architectonic Fixed-Point Execution Policy

## Plan Identity

`PLAN-example-fixed-point`, revision 1. Target execution owner is intentionally
unselected; `$actuating`, another workflow, a coding agent, or a human executor may
consume the handoff when separately authorized.

## Source and Terminal Contract

The source digest is `sha256:example`. Terminal success requires a source-current
architecture-policy pair with resource predictions, proof, rollback, retirement,
and a valid consumer-neutral execution handoff.

## Architecture and Abstraction

`SEAM-owner` is `source_bounded`. The ordinary candidate preserves two parallel
truth owners. The selected organization canonicalizes truth in `FACTOR-primary`,
retires `FACTOR-shadow`, and makes the former shadow surface a derived projection.

```text
law: every accepted state has exactly one canonical owner
falsifier: a mutation can update the projection without updating the canonical owner
factor dispositions: preserve FACTOR-primary; ablate FACTOR-shadow
required observation: canonical-owner conformance check
```

`ACTION-1` inspects both incumbent factors. `ACTION-2` realizes the canonical owner.
`ACTION-3` retires the shadow path and proves required observations survive.

## Policy State and Unknowns

Known: target branch, required observations, and source-bounded authority are fixed.

Critical unknown: whether any external consumer writes directly through the shadow
path. `ACTION-1` resolves it before architectural mutation.

## Commitment Horizon

Only `ACTION-1` is initially eligible. Mutation remains dormant until the direct
writer observation selects either the migration route or the blocked route.

## Policy Branches

- no direct shadow writers: realize the canonical owner, migrate readers, retire the
  shadow factor, and prove observation preservation;
- direct shadow writers found: block mutation and return for compatibility authority;
- source-fixed contract conflict: return to `$spec-pipeline` when PSC-v1 supplied the
  source, otherwise return to the direct source owner.

## Proof, Rollback, and Terminal States

Focused proof establishes one canonical owner and absence of an independent shadow
write path. Rollback restores both the prior data path and its authority boundary;
restoring files without restoring coherent ownership is insufficient.

Success requires the canonical-owner law, migration proof, retirement proof, final
repository proof, and no live falsifier.

## Policy Delta and Architectonic Transport

The adopted radical candidate replaced an additive synchronization action with
canonical ownership and shadow-path retirement.

```text
architectonic relation: normalize + ablate
preserved actions: ACTION-1
revised actions: none
retired actions: ACTION-sync-shadow
introduced actions: ACTION-2, ACTION-3
square result: commutes under canonical-owner observations
```

The plan became smaller while gaining stronger ownership and proof. This is
accretive justification with ablative surface reduction.

## Policy Synthesis Receipt

PSR-v1 summary:

```text
complete clean nine-lens sweep over architecture and policy: yes
independent press pass: yes
radical candidate: adopt
unresolved errors: 0
untreated material risks: 0
```

Receipt path:

```text
.ledger/plan/PLAN-example-fixed-point/synthesis-receipt.json
```

## Execution Handoff

```yaml
execution_handoff:
  plan_id: PLAN-example-fixed-point
  policy_ref: .ledger/plan/PLAN-example-fixed-point/policy.json
  policy_digest: sha256:example
  synthesis_receipt_ref: .ledger/plan/PLAN-example-fixed-point/synthesis-receipt.json
  synthesis_receipt_digest: sha256:example
  target_repository: example/repository
  target_branch: feature/example
  consumer:
  compatible_consumers:
    - actuating
    - executor
    - human
  proposed_resources:
    - action_id: ACTION-2
      resources:
        - root: path:src/example.zig
          mode: write
    - action_id: ACTION-3
      resources:
        - root: path:src/legacy.zig
          mode: write
  required_authority: accepted execution authority for the selected consumer
  required_evidence:
    - OBS-direct-shadow-writers
  mutation_allowed: no
```
</proposed_plan>
