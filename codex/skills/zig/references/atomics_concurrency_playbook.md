# Zig atomics, concurrency, cancellation, and MMIO distinction playbook

Use this playbook for shared state, threads, async/group I/O, locks, atomics, `std.atomic.Value`, `@atomicLoad`, `@atomicStore`, `@atomicRmw`, `@cmpxchgWeak`, `@cmpxchgStrong`, memory ordering, cancellation, or `volatile` confusion.

## Expert objective

Do not approve concurrent code without a concurrency contract:

1. shared state;
2. ownership/lifetime of shared state;
3. invariant;
4. synchronization primitive;
5. memory order for every atomic operation;
6. progress guarantee or lock discipline;
7. cancellation behavior;
8. stress/replay/model tests.

Prefer simple ownership transfer, sharding, or locks before lock-free code.

## Volatile is not synchronization

`volatile` is for memory whose loads/stores have side effects, mainly MMIO. It does not make inter-thread shared memory safe. If the state is shared between threads/tasks, use atomics, locks, channels/queues, or task ownership.

## Choosing the mechanism

| Need | Prefer |
| --- | --- |
| Exclusive mutation with low contention | Mutex. |
| Many readers/few writers | RwLock if workload proves benefit. |
| Counter/statistic | Atomic integer with documented order. |
| One-time publication | Atomic state plus release/acquire or a lock. |
| Work handoff | Queue/channel/task group; transfer ownership. |
| Many independent tasks with shared lifetime | `std.Io.Group.async` where appropriate. |
| Cancelable I/O work | `std.Io` task/cancellation model. |
| Hardware register | `volatile`, not atomics unless hardware docs require atomic CPU ops. |

## Atomic review template

For every atomic field:

```text
field: state
atomic type: std.atomic.Value(T) or builtin atomic operation on T
writers: ...
readers: ...
invariant: ...
load order(s): ...
store order(s): ...
rmw/cmpxchg order(s): ...
ABA/lifetime hazard: ...
progress: lock-free / wait-free / blocking / obstruction-free / not claimed
```

If the answer cannot fill this in, use a lock.

## Memory-order guidance

Avoid cargo-culting `.seq_cst`. It is sometimes correct but not a substitute for a proof.

Common patterns:

- `.monotonic` for counters/statistics where no ordering of other memory is required;
- release store + acquire load for publishing initialized data;
- acquire/release or stronger orders around state-machine transitions;
- `.seq_cst` only when a single global order is part of the reasoning or simplicity outweighs cost and is stated.

Always check the actual Zig 0.16 atomic order names/types in the target codebase before editing.

## Compare-exchange discipline

Use weak compare-exchange inside retry loops when spurious failure is acceptable. Use strong compare-exchange when a single operation must not fail spuriously.

Review loop hazards:

- ABA problem;
- pointer lifetime after pop/free;
- reclamation strategy;
- starvation under contention;
- order on success and failure;
- missed cancellation or shutdown flag.

## Cancellation and task lifetime

For async/I/O tasks:

- tie tasks to a clear group or parent lifetime;
- cancel or await on every path;
- close/deinit resources on cancellation;
- ensure borrowed data outlives the task;
- test cancellation before, during, and after the effectful operation.

## Testing strategy

Concurrency tests should include:

- sequential reference/model test;
- deterministic seed/replay when possible;
- many-iteration stress test under Debug and ReleaseSafe;
- ReleaseFast smoke for optimizer-sensitive paths;
- timeout lane to catch hangs;
- cancellation tests for I/O/task code;
- sanitizer/platform tools if available.

Stress tests do not prove lock-free algorithms. They only increase confidence.

## Review checklist

- Shared state is explicitly identified.
- A simpler non-lock-free design was considered.
- Every atomic has documented memory orders.
- `volatile` is not used for thread synchronization.
- Lifetime/reclamation is solved before pointer publication.
- Cancellation paths await/cancel/cleanup correctly.
- Tests include model/reference behavior plus stress/timeout lanes.
- Remaining concurrency risk is reported honestly.
