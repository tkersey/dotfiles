# Zig pointer, slice, sentinel and alignment boundaries

Use for raw pointer or qualifier casts, foreign addresses, sentinel conversions,
packed-field pointers, byte projection and lifetime-sensitive views. Establish the
properties needed by the operation using code, types, caller contracts and tests.
Add concise safety notes where an obligation is non-obvious; a new eight-field
report is not required for a boundary already justified by existing evidence.
Do not approve an operation whose necessary invariant remains unsupported.

## Pointer vocabulary

| Type | Relevant contract |
| --- | --- |
| `*T` | Single-item pointer; ownership is not encoded by this spelling. |
| `[*]T` | Many-item pointer without a carried bound. |
| `[]T` | Pointer and length; lifetime and aliasing still need an owner. |
| `[*:sentinel]T` | Sentinel-terminated many-item pointer. |
| `[:sentinel]T` | Slice with a sentinel at the promised end position. |
| `[*c]T` | C pointer/coercion behavior; validate before exposing a stronger Zig interface. |
| `*align(n) T` | Explicit alignment, not proof of size or valid destination bits. |
| `*volatile T` | Side-effecting memory access, not synchronization. |
| `allowzero` | Zero may be a valid address under a specific mapping contract. |

Prefer slices for bounded Zig buffers. Use weaker pointer forms where the actual
foreign, hardware or low-level contract needs them, without widening their reach
through unrelated core code.

## Choose by semantics, not a cast ladder

A typed operation, checked slice, explicit-endian load, value conversion or borrowed
view can each be the right representation. They are not interchangeable rungs in
a universal hierarchy. For 0.17, `@bitCast` converts logical bits independently of
endianness; it is not a memory view and does not accept extern aggregates. See
[layout/ABI](layout_abi_playbook.md) and the [migration map](zig_0_17_migration.md).

For pointer projection, establish source/destination extent, sufficient alignment,
initialization and valid bit patterns, provenance, lifetime, mutability and
aliasing. Include ABI/endian or address-space requirements when relevant.
`std.mem.bytesAsSlice` and `bytesAsValue` do not by themselves discharge those
obligations. A valid cast does not prove that all subsequent typed loads are legal.

A length/alignment check can establish those two properties without establishing
arbitrary `T` validity. For example, byte storage large enough for an enum can
still contain an invalid tag. Prefer scalar validation and semantic construction
for hostile wire data rather than presenting a generic bytes-to-`*T` helper as
safe. For trusted native data, carry the remaining caller contract explicitly.

`@alignCast` checks alignment only where runtime safety is enabled. For a public
fallible API accepting untrusted alignment, check it and return an error before
using the cast; do not advertise a recoverable error while relying on a trap.
Qualifier casts do not make read-only storage mutable or side-effecting access
ordinary. Treat changes of constness, volatility and address space according to
the actual storage and access contract.

## Bounds and sentinels

Use overflow-safe extent checks. Establish `offset <= buffer.len` before checking
`len <= buffer.len - offset`. Keep validated offsets tied to the same backing
extent. A checked range from one buffer is not authority to index another.

A sentinel conversion needs storage for the sentinel at the promised position,
a valid bound for finding it, and stability for the duration of use. Review whether
mutation can remove it, whether a C call retains the pointer, and whether the view
escapes. Prefer pointer-plus-length or bounded slices when the interface permits;
do not perform an unbounded scan of an untrusted foreign address.

## Lifetime, witnesses and invalidation

Check stack/arena lifetime, container reallocation, map rehash, removal, object
moves, callback retention and task lifetime. Preserve allocator identity and a
single cleanup owner. A context or wrapper cannot extend the life of storage it
merely references. Use [ownership](memory_ownership_playbook.md) for transfer and
failure cleanup.

A witness can bind a validated range to backing storage and simplify projection.
It only proves what construction and all supported mutation paths maintain. A
publicly constructible value or replaceable backing field may bypass validation;
a type named `BorrowedPacket` or `AlignedBytes` is not sufficient evidence. Prefer
the smallest representation that actually carries the invariant, not a new wrapper
for every cast. Do not infer static borrow checking where Zig does not provide it.

## MMIO and concurrency

Use volatile for side-effecting memory, and synchronization/ownership for shared
concurrent state. Check device-defined widths, addresses, ordering and reserved
bits. Avoid taking packed-field pointers where ordinary addressability is absent.
Whole-register access may avoid a compiler-generated field read-modify-write, but
hardware semantics still govern: write-one-to-clear and read-side effects can
forbid such sequences. Use required barriers rather than treating volatile as one.
See [concurrency](atomics_concurrency_playbook.md) for publication and reclamation.

## Foreign pointers

At a translated-C boundary, validate nullability and pointer/length agreement
before constructing optional pointers or slices. Establish the foreign function's
ownership/free domain and whether returned data is static, borrowed, thread-local
or invalidated by another call. Sentinel views require the same storage and
lifetime reasoning as other pointer projections. Expose a stronger interface where
it removes repeated hazards, while preserving the actual foreign contract.

## Verification

Exercise the actual boundary with valid and relevant invalid cases, including
alignment, sentinels, lifetime/invalidation, failure cleanup and target-specific
layout where applicable. Preserve sufficiently independent expected values for
wire encodings; round trips alone can repeat the same error in both directions.
Use production and other discriminating modes/targets, with 0.17 mode names
`debug`, `safe`, `fast`, `small`; do not impose a full matrix on an unrelated edit.
Existing applicable evidence can be reused. Distinguish tested cases from a
source-level safety argument and from unexecuted target assumptions.
