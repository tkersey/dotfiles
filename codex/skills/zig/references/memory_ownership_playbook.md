# Zig Memory Ownership, Allocator, and Escape Playbook

Use when code touches allocators, containers, arenas, pools, buffers, parsing/decoding, returned slices/refs, snapshots, reports, certificates, ownership transfer, leaks, OOM, or lifetime-sensitive APIs.

## Objective

Every allocation and borrowed view has an explicit owner, lifetime, invalidation point, failure path, and proof.

```text
who owns it
which allocator/storage created it
who frees/resets/deinitializes it
whether ownership transfers
what invalidates borrows
what happens on every failure edge
how escape and OOM behavior are proved
```

No low-level Zig API should leave ownership implicit.

## Vocabulary

| Term | Meaning |
| --- | --- |
| borrowed | Caller/backing owner retains ownership; use is limited to a documented lifetime. |
| owned | Returned object/callee must eventually free/deinit. |
| transferred | Ownership moves; old owner must not free/use. |
| arena-owned | Lifetime ends at arena reset/deinit. |
| caller-allocated | Caller supplies output storage. |
| allocator-backed | Object stores allocator and owns allocations. |
| unmanaged | Allocator is passed to mutation/deinit functions. |
| snapshot-borrowed | View is valid only for a named snapshot/epoch and backing owner. |

Prefer visible APIs/types such as:

```text
OwnedBytes
BorrowedFrame
ValidatedView
initOwned
fromBorrowed
clone
toOwnedSlice
release
intoInner
```

## Mandatory escape table

Whenever slices/refs cross a function boundary, include:

```yaml
escape_table:
  - field:
    source:
    backing_owner:
    allocator_or_storage:
    returned_lifetime:
    invalidated_by: []
    result_ownership:
      borrowed |
      duplicated |
      transferred |
      owner-carried
    deinit_owner:
    failure_cleanup:
    proof:
```

Use this for:

```text
parsed JSON
decoded binary
arena-backed state
container-backed slices
staged transaction refs
snapshots/reports/certificates
public []const u8 fields
returned plans/descriptors/tables
```

## Default escape rule

If runtime-owned slices escape:

```text
duplicate into the returned owner
or
transfer/carry the backing owner with the returned value
```

Do not return slices backed by temporary input, soon-deinitialized arenas/reports, moved staging objects, or containers that can reallocate unless the API exposes and enforces that lifetime.

## Allocator selection

| Use case | Prefer |
| --- | --- |
| Library API | Caller-provided `std.mem.Allocator`. |
| Leak tests | `std.testing.allocator`. |
| OOM tests | `checkAllAllocationFailures` or targeted failing allocator. |
| Known maximum | `FixedBufferAllocator` / caller storage. |
| Short CLI operation | Arena with one explicit lifetime boundary. |
| Per-request scratch | Arena reset/deinit at request boundary. |
| Long-running service | Explicit free, bounded pools/slabs, or resettable arenas. |
| Hot path | Preallocation/caller storage and measured allocation count. |

Avoid `page_allocator` as a lazy library default.

## API patterns

### Caller-owned output

```zig
pub fn encodeInto(out: []u8, input: []const u8) ![]u8 {
    if (out.len < input.len) return error.NoSpaceLeft;
    @memcpy(out[0..input.len], input);
    return out[0..input.len];
}
```

Returned slice borrows `out`.

### Returned owned allocation

```zig
pub fn duplicateOwned(
    allocator: std.mem.Allocator,
    input: []const u8,
) ![]u8 {
    return allocator.dupe(u8, input);
}
```

Caller frees with the same allocator.

### Owner-carrying result

When several returned slices borrow one parsed arena/buffer, return an owning wrapper:

```zig
const Parsed = struct {
    arena: std.heap.ArenaAllocator,
    value: Value,

    pub fn deinit(self: *Parsed) void {
        self.arena.deinit();
        self.* = undefined;
    }
};
```

The wrapper must not be accidentally copied as duplicate ownership.

## Multi-step acquisition

Use `errdefer` immediately after each acquisition.

```zig
const a = try allocator.alloc(u8, a_len);
errdefer allocator.free(a);

const b = try allocator.alloc(u8, b_len);
errdefer allocator.free(b);
```

Do not disarm rollback until ownership transfer is complete and all later fallible returned data is prepared.

For observable multi-owner mutation, use the atomic-transition playbook; allocator cleanup alone is not rollback.

## Container invalidation

Review:

- append/insert reallocation;
- hash-map rehash;
- swap/remove;
- arena reset;
- vector/list growth;
- snapshot refresh;
- object move/copy;
- owner deinit.

A slice/pointer returned before mutation may dangle afterward.

## Arena discipline

Good:

- temporary parse then copy compact durable result;
- request/frame lifetime;
- bounded CLI command.

Bad:

- returning arena-backed fields after deinit;
- long-running unbounded arena;
- hiding ownership ambiguity;
- resetting while snapshots/refs remain public.

## Stable proof identities

Do not build long-lived fingerprints/certificates from borrowed labels or descriptor names unless lifetime and canonical bytes are stable.

Prefer authoritative stable fields:

```text
domain
format/version
owner/subject identity
canonical content fingerprint
artifact state
```

## Failure-path review

Inspect:

- every `try` after acquisition;
- branches before transfer;
- early returns;
- callbacks retaining borrows;
- container mutations that invalidate views;
- partial result construction;
- deinit ordering;
- copies of owner-bearing structs.

## Proof

Normally include:

- zero/max inputs;
- repeated init/deinit;
- deterministic failure after each allocation;
- no observable mutation after OOM;
- escape remains valid for promised lifetime;
- escape becomes invalid only at documented boundary;
- mutation invalidation regression;
- leak check;
- allocation-count profile when performance is claimed.

## Checklist

- Every allocation has one owner.
- Allocation and free use compatible allocator domains.
- Every owner has exactly one cleanup path.
- Borrowed/owned/transferred state is explicit.
- Every escaping field appears in the escape table.
- No arena/temp/report-backed slice outlives its owner.
- Reallocation invalidation is explicit.
- `errdefer` protects partial acquisition.
- OOM is propagated and tested.
- Observable atomicity is proved separately.
