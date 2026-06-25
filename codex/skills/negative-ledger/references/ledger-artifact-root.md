# Negative Ledger Artifact Root

New durable negative-route records belong under:

```text
.ledger/negative-ledger/
```

When a record concerns `$st` execution, bind:

```text
workspace ID
plan ID
action/route
resource set
branch epoch
falsifying transition receipt
reopening criteria
```

A route failure in one plan does not automatically exclude the route in another
plan unless applicability evidence spans both.
