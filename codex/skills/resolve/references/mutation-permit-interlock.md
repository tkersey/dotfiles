# Mutation Permit Interlock

After same-cluster recurrence, no production mutation may occur unless the immediately preceding assistant decision emits:

```yaml
RGR-V2-MUTATION-PERMIT:
```

The permit is the actuator interlock.

It proves:

- route is not raw `mutate-existing-owner`;
- positive production net is warranted or not expected;
- owner coarseness is resolved;
- boundary inventory is resolved;
- negative-ledger query/map was operational;
- proof matrix is family-level;
- handoff is allowed.

No permit, no post-recurrence production mutation.
