# Zig memory ownership and allocator playbook

Use this playbook when the request touches `std.mem.Allocator`, containers, arenas, pools, buffers, `defer`, `errdefer`, ownership transfer, leak fixes, out-of-memory behavior, or lifetime-sensitive APIs.

## Expert objective

Do not merely make allocation compile. Produce the memory contract:

1. who owns each allocation;
2. which allocator creates it;
3. who frees it and when;
4. whether ownership transfers across the API boundary;
5. what happens on every failure edge;
6. how allocation failure and leaks are tested.

No low-level Zig API should leave ownership implicit.

## Ownership vocabulary

Use precise terms in answers and comments:

| Term | Meaning |
| --- | --- |
| borrowed | Caller keeps ownership; callee may read/use only for the documented lifetime. |
| owned | Callee or returned object must eventually free/deinit it. |
| transferred | Ownership moves from one component to another; old owner must not free/use. |
| arena-owned | Lifetime is tied to arena reset/deinit rather than individual free. |
| caller-allocated | Caller supplies storage; callee writes into it without heap allocation. |
| allocator-backed | The object owns heap allocations using a stored allocator. |
| unmanaged | Container/object does not store allocator; allocator is passed to mutating/deinit functions. |

Prefer making this visible in type names and APIs: `OwnedBytes`, `BorrowedFrame`, `initOwned`, `fromBorrowed`, `deinit`, `clone`, `toOwnedSlice`, `release`, `intoInner`.

## Allocator selection

Choose based on lifetime and failure semantics, not habit.

| Use case | Prefer |
| --- | --- |
| Library API | Accept `std.mem.Allocator` from caller. |
| Test leak checks | `std.testing.allocator`. |
| Test OOM behavior | `std.testing.FailingAllocator` or `std.testing.checkAllAllocationFailures`. |
| Compile-time/known maximum storage | `std.heap.FixedBufferAllocator`. |
| CLI that exits after one operation | Arena with one final `deinit`. |
| Per-request/per-frame scratch | Arena reset/deinit at request/frame boundary. |
| Long-running service | Explicit frees, pools, slabs, or arenas with bounded reset points. |
| Hot path | Avoid allocation, preallocate, use caller storage, or prove allocation count with `zprof`. |

Avoid `page_allocator` as a lazy default in libraries. It hides leak/failure behavior and loses caller control.

## API patterns

### Caller-owned output buffer

Use when the maximum output is known or bounded.

```zig
pub fn encodeInto(out: []u8, input: []const u8) ![]u8 {
    if (out.len < input.len) return error.NoSpaceLeft;
    @memcpy(out[0..input.len], input);
    return out[0..input.len];
}
```

Contract: caller owns `out`; returned slice borrows `out`; no allocation.

### Returned owned allocation

Use when the API must allocate and transfer ownership to the caller.

```zig
pub fn duplicateOwned(allocator: std.mem.Allocator, input: []const u8) ![]u8 {
    return allocator.dupe(u8, input);
}
```

Contract: caller must free with the same allocator.

### Object owns allocator-backed state

```zig
const Buffer = struct {
    allocator: std.mem.Allocator,
    bytes: []u8,

    pub fn init(allocator: std.mem.Allocator, len: usize) !Buffer {
        const bytes = try allocator.alloc(u8, len);
        return .{ .allocator = allocator, .bytes = bytes };
    }

    pub fn deinit(self: *Buffer) void {
        self.allocator.free(self.bytes);
        self.* = undefined;
    }
};
```

Contract: every successful `init` requires exactly one `deinit`.

### Multi-step init with rollback

Use `errdefer` immediately after each successful acquisition.

```zig
pub fn initPair(allocator: std.mem.Allocator, a_len: usize, b_len: usize) !Pair {
    var a = try allocator.alloc(u8, a_len);
    errdefer allocator.free(a);

    var b = try allocator.alloc(u8, b_len);
    errdefer allocator.free(b);

    return .{ .allocator = allocator, .a = a, .b = b };
}
```

Contract: no partial allocation leaks on `error.OutOfMemory` or later initialization failure.

## Managed vs unmanaged containers

For library internals, prefer unmanaged containers when it improves allocator visibility and lets callers choose allocation scope. For application-level convenience, a managed wrapper may be appropriate.

Review questions:

- Does the type store an allocator? If yes, is that allocator part of the type's lifetime?
- Does `deinit` need an allocator parameter? If yes, the type is effectively unmanaged.
- Does copying the type duplicate allocator ownership accidentally?
- Is there a `clone` or `toOwned` operation when ownership must be duplicated?
- Are slices returned from containers invalidated by future mutation?

## Arena discipline

Arenas are lifetime tools, not leak excuses.

Good arena uses:

- parse all temporary data, then convert a small validated result to owned storage;
- serve a request/frame and deinit/reset everything at the boundary;
- short-lived CLI command where freeing everything at exit is the correct lifetime.

Bad arena uses:

- long-lived service without reset points;
- hiding ownership bugs;
- allocating unbounded data without an admission-control limit;
- returning arena-backed slices beyond arena lifetime.

## Failure-path review

For each fallible function, inspect:

- every `try` after an allocation;
- every branch between acquisition and ownership transfer;
- every early `return`;
- every callback that might retain a borrowed slice;
- every container mutation that may reallocate and invalidate pointers/slices.

Use `errdefer` for rollback and document ownership transfer points explicitly.

## Test obligations

Allocator-using code should normally have:

```zig
test "allocation failure coverage" {
    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        functionUnderTest,
        .{ /* args */ },
    );
}
```

Also test:

- zero-length and maximum-size inputs;
- repeated init/deinit cycles;
- failed second/third allocation in multi-step constructors;
- returned slices after mutation when invalidation is possible;
- leak check using `std.testing.allocator` or a debug allocator;
- profiler lane (`zprof`) for allocation counts when performance is claimed.

## Review checklist

- Every allocation has an owner.
- Every owner has a cleanup path.
- Cleanup uses the same allocator that allocated the memory.
- `errdefer` protects partial initialization.
- Returned slices document whether they are borrowed or owned.
- Arena-backed results do not outlive the arena.
- Container mutation invalidation is documented.
- `error.OutOfMemory` is not swallowed.
- Allocation-failure testing is present or labeled unavailable.
