# Fallible Mutation Atomicity

Use when a function mutates state while later work can fail.

## Objective

After any failed operation:

```text
all observable owners equal their pre-state
or
the transition is durably committed and explicitly recoverable
```

Memory cleanup alone is insufficient.

## Observable state inventory

```yaml
atomic_transition:
  transition_id:
  owners:
    - owner_id:
      pre_state_probe:
      mutations: []
      rollback:
  fallible_steps: []
  first_observable_mutation:
  commit_point:
  publications: []
  ownership_transfers: []
  prepare_steps: []
  rollback_steps: []
  failure_injection:
  proof:
```

Include:

```text
containers
ledgers/journals
outboxes
event streams
counters
indexes
caches used as authority
filesystem/database effects
transferred allocations/refs
returned identifiers
```

## Preferred topology

### Prepare

Perform:

```text
allocation
clone/duplication
parse/decode
validation
capacity reservation
ref/evidence construction
event construction
external preflight
```

No observable mutation.

### Commit

Perform one non-fallible state transition, or a transaction whose rollback covers every owner.

### Publish

Only after commit:

```text
events
receipts
refs
outbox work
external visibility
callbacks
```

## Anti-patterns

- disarming `errdefer` before all fallible returned refs exist;
- appending first event before allocating second event;
- moving ownership into owner A before owner B can reject;
- committing a ledger before evidence allocation;
- returning an ID for a state change that later rolls back;
- freeing memory while leaving a counter/index/journal changed;
- rollback that itself allocates or can fail.

## Proof

Prefer deterministic fail-index tests.

For every injected failure:

```text
operation returns expected error
full observable pre-state == full observable post-state
no leak
no double free
no emitted event/ref/receipt
no ownership ambiguity
```

If external effects cannot be rolled back, make the durable commit/recovery protocol explicit and test replay/idempotency.
