# Zig Error, Failure-Path, and Atomic Transition Playbook

Use for fallible APIs, `try`/`catch`, `errdefer`, precise error sets, boundary mapping, partial mutation, ownership transfer, event/ledger writes, or cleanup proof.

## Error contract

State:

```text
precise error set
domain/resource/environment/programmer categories
translation boundary
cleanup and rollback
observable atomicity
tests for success, domain failure, resource failure, and cleanup
```

## Error taxonomy

| Category | Examples | Handling |
| --- | --- | --- |
| Domain/protocol | invalid header/version/state | Precise error; caller may switch. |
| Resource | OOM/no space/capacity | Propagate and inject in tests. |
| Environment | file/permission/network | Add context at integration boundary. |
| Programmer bug | impossible internal state | Assert/unreachable only with proof. |
| Foreign/system | errno/status | Translate once in boundary module. |

Do not turn domain failures into panics or bugs into vague `anyerror`.

## Precise errors

Prefer named/inferred error sets inside libraries.

```zig
const ParseError = error{
    Empty,
    InvalidChar,
    Overflow,
};
```

Widen only at genuine integration boundaries.

## `try`, `catch`, and `errdefer`

For every `try`:

- is propagation correct?
- should it map to a domain error?
- has state been acquired or mutated?
- does rollback cover all owners?
- does `catch` discard useful evidence?
- is `catch unreachable` actually closed-world?

Use `errdefer` for resource rollback, but do not confuse it with full transaction rollback.

## Atomic-transition gate

When later work can fail after mutation, inventory:

```yaml
failure_atomicity:
  owners: []
  first_observable_mutation:
  later_fallible_steps: []
  ownership_transfers: []
  publications: []
  commit_point:
  rollback:
  deterministic_failure_injection:
  observable_pre_state:
  observable_post_state:
```

Preferred:

```text
prepare fallible data
-> commit non-fallible state
-> publish
```

Prepare includes allocations, clones, parsing, validation, reservation, event/ref construction, and external preflight.

Publish only after commit includes receipts, refs, events, outbox work, callbacks, and external visibility.

## Partial mutation anti-patterns

- append one half of an event pair;
- commit owner A before owner B can fail;
- transfer ownership then allocate returned evidence;
- disarm rollback before all fallible work;
- mutate counters/indexes but roll back only memory;
- persist journal state before proof construction;
- rollback that itself allocates/fails;
- return a ref for a transition that later fails.

## Boundary mapping

Centralize:

```text
raw status/errno
-> boundary-specific error set
-> core domain behavior
```

Include unknown statuses.

## Proof

Test:

1. success;
2. each domain failure;
3. allocation/resource failure;
4. cleanup after partial acquisition;
5. full observable pre-state equals post-state at each injected failure;
6. no event/ref/receipt/publication escaped;
7. ownership freed/transferred exactly once;
8. durable external effects follow explicit recovery/idempotency protocol.

Use `std.testing.checkAllAllocationFailures` for bounded allocation behavior and targeted fail indices for stateful transitions.

## Reporting

Report:

- error set before/after;
- widened/narrowed errors;
- translation boundary;
- resource rollback;
- state rollback/commit point;
- failure injection coverage;
- remaining `catch unreachable` proofs;
- unavailable atomicity proof.
