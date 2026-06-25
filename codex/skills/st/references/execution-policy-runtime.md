# EPG Runtime Integration

`$st` materializes the current EPG commitment horizon.

Authoritative lineage:

```text
EPG-v1 policy
EPS-v1 current state
EPD-v1 selected action
-> `$st` contracted task capsule
-> GCR-v1
```

Do not flatten dormant conditional actions into ready durable tasks.

Recommended task source fields:

```text
policy_id
policy_revision
policy_digest
state_id
state_digest
decision_id
action_id
```

The selected action contributes:

```text
owner
preconditions
required prior actions
mutation boundary
lock roots
expected observations/effects
proof obligations
rollback
```

GCR remains the execution authority.

After ETR-v1 advances policy state:

```text
record current obligation proof
complete/block current materialized tasks
retire or archive expired horizon tasks
materialize the next selected action
recompile GCR
```

Native command work is specified in `ST_EXECUTION_POLICY_RUNTIME_SPEC.md`.
