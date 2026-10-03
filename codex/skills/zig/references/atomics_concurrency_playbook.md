# Zig concurrency, memory ordering and cancellation

Use for shared state, threads, locks, atomics, task groups, reclamation, progress
or cancellation. Establish the required synchronization, ownership/lifetime and
progress guarantees, then choose the simplest mechanism that satisfies them.
An unfilled template is not a reason to substitute a lock or endorse an algorithm.
A necessary guarantee that remains unsupported is a real unresolved obligation.

## Choosing a mechanism

Ownership transfer, sharding and locks often simplify reasoning; atomics and
nonblocking algorithms can be necessary for a specified progress or latency
contract. Compare mechanisms against the actual workload and requirements.

| Need | Candidate and relevant question |
| --- | --- |
| Exclusive mutation | Mutex or single owner; consider contention, lock order and reentrancy. |
| Read-heavy state | Immutable snapshots, sharding or RwLock when the workload justifies it. |
| Independent statistic | Atomic integer; determine whether it publishes any other memory. |
| One-time publication | Explicit publication state and ordering, or a suitable lock. |
| Work handoff | Queue/channel/task ownership with explicit transfer and shutdown. |
| Related I/O tasks | The selected `std.Io` group/lifetime facilities and their completion contract. |
| Required nonblocking progress | Algorithm and reclamation satisfying that requirement; a lock is not a semantics-neutral fallback. |
| Hardware register | Device-defined volatile access, not an assumed concurrent-memory protocol. |

Keep a correct existing design when its guarantees and evidence remain applicable.
Do not add an abstraction merely because an atomic token appears.

## Synchronization argument

Identify the shared invariant, relevant readers/writers, synchronization points,
publication ordering, owner/reclamation strategy and promised progress. Existing
code, comments or a model may already provide the argument. A per-field table can
help with interacting state, but is not required for an ordinary atomic counter.
Document subtle dependencies where maintainers need them rather than duplicating
every property into a separate artifact.

For Zig 0.17, atomic order metadata is `std.lang.AtomicOrder`; inspect the selected
compiler and [language reference](https://ziglang.org/documentation/0.17.0/)
for the actual operation's accepted orders. Typical reasoning:

- `.monotonic` can suffice for an independent statistic that publishes no other memory.
- Release/acquire can publish initialized state when the reader observes the relevant publication; order names alone do not establish that relation.
- `.seq_cst` supplies a stronger order where the algorithm needs it or its simplicity is justified; it does not solve lifetime or reclamation.

Keep success and failure ordering distinct for compare-exchange. A failure does
not perform the successful write. Weak compare-exchange permits spurious failure;
use it with an appropriate retry strategy. Strong compare-exchange avoids spurious
failure for a single attempt, but still fails when the expected value differs.
Verify order restrictions rather than copying a remembered success/failure pair.

## Lifetime and progress

Publishing an address does not keep its referent alive. Establish ownership and
safe reclamation before readers can access or retain it. Consider ABA, reuse,
allocation domains, sequence wraparound and how shutdown coordinates with active
readers. Pointer-stability or thread-safe allocator checks are not a reclamation
scheme.

Distinguish blocking, lock-free, wait-free or other claimed progress. A retry loop
with no mutex is not automatically lock-free; allocation, callbacks and reclamation
can introduce blocking. Analyze contention/starvation, backoff and cancellation
against the contract. For locks, consider acquisition order, callback reentrancy
and whether a blocking/cancelable operation holds a lock needed for completion.
Do not silently weaken a required guarantee to make an implementation simpler.

## Cancellation and task lifetime

Use the selected `std.Io` task/group contract. Establish completion before destroying
borrowed inputs, group storage or shared resources. A cancellation request is not
necessarily completion; inspect whether the API awaits/join completes as part of
cancel or requires a separate operation. Cover success, failure and early-return
paths, including children that have already completed or are blocked.

Cleanup and observable effects are separate. Cancellation may leave a documented
partial write or committed operation; do not claim it rolled back simply because
resources were freed. Use [I/O/effects](io_effects_playbook.md) and
[state transitions](atomic_transition_playbook.md) for those contracts.

## Volatile is not synchronization

Volatile addresses side-effecting memory such as MMIO. It does not publish ordinary
shared data or make conflicting concurrent accesses safe. Device semantics govern
width, ordering, barriers and read-modify-write, including write-one-to-clear and
read-side effects. Atomic CPU operations are not universally appropriate for MMIO.
See [layout/ABI](layout_abi_playbook.md).

## Evidence

Select checks that challenge the live obligation: a sequential specification or
linearizability model, deterministic replay where possible, contention stress,
timeouts for hangs, shutdown/cancellation races or platform tooling. Use the
production mode and additional modes/targets when they discriminate optimizer,
ordering or ABI assumptions. Zig 0.17 mode names are `debug`, `safe`, `fast`, `small`.
A narrow atomic edit need not run a universal matrix.

Stress success is sampled evidence, not proof of linearizability or nonblocking
progress. Report guarantees supported by the algorithm separately from observed
runs and untested platform assumptions. Preserve review-only scope; for authorized
implementation, resolve introduced failures and complete relevant verification.
