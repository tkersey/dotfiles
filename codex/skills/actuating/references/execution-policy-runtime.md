# Execution Policy Runtime

`$actuating` interprets one EPG action at a time.

```text
EPG + EPS
-> EPD
-> one `$st` commitment horizon
-> GCR
-> policy-bound ASL/FPS
-> FPSR + proof + observations
-> ETR
-> next EPS
```

## Runtime lineage

Every materialized task and actuation slice should preserve:

```text
policy ID/revision/digest
state ID/digest
decision ID
action ID
commitment-horizon sequence
```

A mismatch makes the materialization stale.

## Horizon discipline

Only the selected action becomes active `$st` work.

Dormant conditional actions remain in EPG and must not pollute ready, blocked, or proof frontiers.

## Failure routes

```text
shield block       -> blocked/rollback/authority return
new branch         -> return to policy
model failure      -> revise policy before another material action
intent failure     -> return to `$spec-pipeline`
graph failure      -> graph-repair mode
proof failure      -> action failure or return to policy
```

## Terminal discipline

A success terminal is a policy decision, not delivery proof.

Shipping still requires current GCR, proof-complete `$st`, terminal obligations, valid transition receipts, and explicit PR mode.
