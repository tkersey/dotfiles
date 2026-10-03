# Zig ownership, allocators and lifetime escape

Use for allocated or borrowed results, containers, arenas, pools, parsing,
snapshots, ownership transfer, leaks and allocation failure. Identify the owner,
allocator/storage domain, cleanup owner, borrow lifetime, invalidation point and
failure guarantee. Make consequential ownership explicit in APIs and tests; use
an escape table only when several fields or owners make the relationship unclear.
A small borrowed-slice helper does not require a separate reporting artifact.

## Ownership at the boundary

Distinguish borrowed, owned, transferred, arena-owned and caller-allocated values.
A returned slice must either expose its backing lifetime, duplicate into a durable
owner, or carry/transfer the backing owner. Never return a view into a temporary
arena, deinitialized parser, moved staging object or reallocating container without
an enforced lifetime contract. An owning wrapper must not be copied into duplicate
ownership. Preserve allocator provenance through transfer and deinitialization.

For several escaping fields, a useful optional table records field, backing owner,
allocator/storage, lifetime, invalidators, transfer/deinit owner and failure cleanup.
It is the ownership argument, not filling the table, that matters.

## Allocator selection

| Workload | Candidate and obligation |
| --- | --- |
| Library | Caller-provided `std.mem.Allocator`; no hidden process-global allocator. |
| Leak/failure tests | `std.testing.allocator`, allocation-failure injection and explicit cleanup. |
| Known maximum | Caller storage or `FixedBufferAllocator`; bounded failure is normal. |
| Request/frame scratch | Arena with an explicit reset/deinit boundary and no escaping borrows. |
| Short CLI | Arena if one lifetime fits; do not generalize to a long-running service. |
| Long-running/hot path | Explicit frees, bounded pools, preallocation; measure allocation count and contention. |

Avoid `page_allocator` as a lazy library default. In Zig 0.17, `SafeAllocator`
replaces the deprecated `DebugAllocator`. Its checks and leak reporting are useful
diagnostics, not a replacement for ownership or OOM tests. It frees backing memory
on deinit; references remain invalid afterward. Thread-safe allocation does not
make stored user data thread-safe. Its non-reuse behavior depends on the backing
allocator; do not treat addresses as durable generation identities.

`StackFallbackAllocator` now accepts caller-provided stack storage via
`.init(buffer, gpa)` rather than a comptime-sized generic. Neither the allocator
state nor allocations backed by that buffer may escape its lifetime. Test the
fallback boundary, not just the all-stack fast path. Inspect the installed API
before adapting older initialization or allocator-access recipes.

## Acquisition, transfer and invalidation

Protect each successful acquisition with `errdefer` before the next fallible step:

```zig
const a = try allocator.dupe(u8, input_a);
errdefer allocator.free(a);
const b = try allocator.dupe(u8, input_b);
errdefer allocator.free(b);
```

Transfer ownership only after later fallible returned data is prepared. Memory
cleanup alone does not roll back observable counters, indexes or publication; use
[state transitions](atomic_transition_playbook.md) for the advertised guarantee.

Check append/insert reallocation, map rehash, removal/swapping, arena reset,
snapshot refresh, object moves/copies and deinit. Zig 0.17 ArrayList pointer-
stability checks can detect certain illegal mutations; they do not extend borrow
lifetimes, forbid all aliases or synchronize concurrent access. Use the actual
container's lock/mutation contract rather than assuming all list methods check it.

Keep arena-backed parses and their views inside one owner. The 0.17 ZON parser's
options/arena and allocating-versus-nonallocating changes require revisiting
ownership at the call site, not just renaming functions. Configuration updates also
need the advertised partial-update or atomicity behavior tested independently.

## Evidence

Exercise zero/max inputs, repeated init/deinit, ownership transfer exactly once,
container invalidation and each consequential allocation-failure edge. Use
`checkAllAllocationFailures` for allocation failures and separate fail points for
I/O/callback/publication failures. Do not require no observable mutation unless the
API promises that guarantee. Test valid continued use or reported partial progress
for weaker guarantees. Keep fingerprint/certificate bytes and labels alive for
the claimed identity lifetime. Measure allocation count, live/peak requested bytes
and contention when performance is the question; allocator metrics are not latency.
