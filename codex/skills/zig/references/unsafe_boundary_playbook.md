# Zig unsafe boundary, pointer, slice, sentinel, and alignment playbook

Use this playbook when code touches raw pointers, pointer casts, address casts, sentinel conversions, C pointers, volatile memory, packed-field pointers, memory reinterpretation, zero-copy parsing, or lifetimes that cannot be proven by ordinary Zig types.

## Expert objective

Every unsafe boundary needs a boundary note:

1. source type and destination type;
2. length proof;
3. alignment proof;
4. sentinel/nullability proof;
5. lifetime/ownership proof;
6. aliasing and mutation assumptions;
7. target/ABI/endian dependency;
8. validation/test that exercises the boundary.

Do not approve `@ptrCast`, `@ptrFromInt`, `@alignCast`, `@constCast`, `@volatileCast`, `[*c]T`, or packed-field pointer use without this contract.

## Pointer vocabulary

| Type | Meaning | Typical use |
| --- | --- | --- |
| `*T` | Single item pointer. No pointer arithmetic. | Owned object, out parameter, MMIO register pointer. |
| `[*]T` | Many-item pointer without length. | Low-level loops, C-ish APIs where length is separate. |
| `[]T` | Slice: pointer plus length. | Preferred for safe runtime buffers. |
| `[*:sentinel]T` | Many-item sentinel-terminated pointer. | C strings, sentinel-delimited data. |
| `[:sentinel]T` | Slice with sentinel guarantee. | Bounded view plus sentinel proof. |
| `[*c]T` | C pointer with C coercion behavior. | Raw translated C boundary only; wrap quickly. |
| `*align(n) T` | Pointer with explicit alignment. | SIMD, hardware, packed-field interop. |
| `*volatile T` | Side-effecting memory. | MMIO only, not concurrency. |
| `allowzero` | Zero address may be valid. | Freestanding/embedded special cases. |

Default to slices for Zig APIs. Use many-item pointers and C pointers only at boundaries where their weaker guarantees are necessary.

## Cast hierarchy

Prefer safer representations before raw pointer casts:

1. normal typed API;
2. slice narrowing and bounds checks;
3. `std.mem.bytesAsSlice` / `std.mem.bytesAsValue` when alignment and length are validated;
4. `@bitCast` for value reinterpretation of equal-sized values;
5. `@ptrCast` only when the above cannot express the operation;
6. `@ptrFromInt` only for MMIO, freestanding ABI, or documented foreign addresses.

Before `@ptrCast`, prove:

- memory is initialized for the destination type;
- pointer alignment is sufficient, or use `@alignCast` after a runtime check;
- destination size does not exceed source storage;
- source lifetime outlives all destination uses;
- mutation through the destination pointer does not violate aliasing/constness expectations.

## Alignment proof pattern

```zig
fn requireAligned(comptime T: type, bytes: []u8) !*T {
    if (bytes.len < @sizeOf(T)) return error.BufferTooSmall;
    const addr = @intFromPtr(bytes.ptr);
    if (addr % @alignOf(T) != 0) return error.Unaligned;
    const aligned: *align(@alignOf(T)) u8 = @alignCast(bytes.ptr);
    return @ptrCast(aligned);
}
```

Use this pattern as a review shape, not as a blanket recommendation. For many byte-to-value tasks, copying into a value and using endian-aware reads is safer and clearer.

## Sentinel proof

Sentinel conversions must prove the sentinel exists at the promised position.

Review questions:

- Where is the length obtained?
- Is the sentinel byte/value inside allocated storage?
- Is the sentinel guaranteed stable during use?
- Is the data mutable, and can mutation remove the sentinel?
- Is the sentinel conversion only for a boundary call, or does it escape?

Prefer bounded slices plus explicit length for Zig APIs. Use sentinel pointers for C APIs or formats that require sentinel semantics.

## Lifetime and invalidation

Common hazards:

- returning a slice into stack storage;
- keeping a pointer into an `ArrayList` or hash map after mutation/reallocation;
- returning a view into an arena that has already reset/deinitialized;
- casting bytes to a typed pointer before validating length and alignment;
- C function retaining a pointer after the Zig buffer is freed;
- async task using borrowed data after the parent scope exits.

Use witness types for validated borrowed views:

```zig
const BorrowedPacket = struct {
    backing: []const u8,
    payload_range: struct { start: usize, end: usize },

    pub fn payload(self: BorrowedPacket) []const u8 {
        return self.backing[self.payload_range.start..self.payload_range.end];
    }
};
```

The witness stores enough information to project views without redoing unsafe assumptions.

## Volatile vs atomics

`volatile` is for side-effecting memory such as MMIO. It does not make shared memory safe between threads. Use atomics or synchronization primitives for concurrency.

For MMIO:

- make the pointer `*volatile RegisterType`;
- avoid taking pointers to individual packed fields when the architecture cannot address them normally;
- prefer read-modify-write helpers that operate on the whole register value;
- document ordering requirements if the hardware manual requires barriers/fences.

## C pointers

Translated C often emits `[*c]T`. Treat it as a raw boundary type.

Wrap quickly:

- convert nullable C pointers to `?*T` or explicit error returns;
- convert pointer-plus-length to `[]T` only after null/length validation;
- convert sentinel strings with sentinel proof;
- convert ownership conventions into Zig-owned wrappers with `deinit`.

## Review checklist

- Slices are preferred over many-item pointers in Zig-facing APIs.
- Each cast has a written proof for length, alignment, lifetime, and mutability.
- Sentinels are checked before sentinel-typed views are created.
- C pointers are wrapped at the boundary and do not leak into core logic.
- `volatile` is used only for MMIO/side-effecting memory.
- Zero-copy projections are exposed only after validation.
- Packed-field pointers are not passed as normal pointers.
- Unsafe assumptions are tested in Debug/ReleaseSafe and across relevant targets.
