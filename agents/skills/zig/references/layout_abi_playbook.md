# Zig layout, ABI, logical bits and wire formats

Use for C ABI, packed/extern types, binary protocols, hardware registers, endian
conversion and target-sensitive layout. Establish the size, alignment, offsets,
valid bit patterns and target assumptions that the interface actually promises.
Use a layout table when it clarifies several fields; do not require one for every
scalar conversion. Ordinary structs do not promise C or portable wire layout.

## Choose the representation

| Form | Contract |
| --- | --- |
| `struct` | Zig semantic data; compiler-selected layout. |
| `extern struct` / `extern union` | Target C ABI, not a target-independent wire format. |
| `packed struct` / `packed union` | Bit layout with packed-field pointer and alignment restrictions. |
| `enum(Int)` | Explicit tag values; check the foreign API's actual integer representation. |
| Explicit endian parser | Portable wire/disk bytes with length and value validation. |

Match target, C flags, libc and calling convention across a foreign boundary.
Check `@sizeOf`, `@alignOf`, `@offsetOf`, and where relevant `@bitOffsetOf` and
`@bitSizeOf`, against independent C constants/assertions or format requirements.
Keep generated translations isolated and wrap pointer/status/ownership semantics.

## Zig 0.17: logical bits are not a memory view

`@bitCast` is now endian-agnostic logical-bit conversion. Array/vector elements
contribute bits from low to high; do not use a successful bit cast as evidence for
host byte layout. In particular, `[2]u8{ 0x12, 0x34 }` logically casts to `u16`
`0x3412` on either endian. A big-endian wire decoder must still read `0x1234`.

Extern structs/unions are no longer valid `@bitCast` operands/results. A pointer
cast or extern-union view is not a mechanical safe replacement: establish storage
size/alignment, lifetime, aliasing, active representation, valid destination bits
and padding policy. Prefer explicit scalar reads/writes for untrusted bytes.
Never inspect unspecified padding as a canonical hash or serialized identity.

Use `@backingInt` / `@fromBackingInt` for the supported enum and integer-backed
packed conversions. `@fromBackingInt` requires the exact backing integer type;
validate hostile enum tags before conversion, rather than relying on a safety
trap. `@intFromEnum` / `@enumFromInt` are deprecated, not removed in this release.

The [release regression example](zig_0_17_regressions.zig) checks logical array and
vector bits against independent constants, explicit little/big-endian reads,
backing conversions and comptime execution. Runtime success on one host does not
prove runtime behavior on another target. Cross-compilation is a separate lane.

## Parsers and MMIO

For wire/disk data, validate lengths before reads, use explicit endian access,
reject reserved/invalid values, then construct a semantic value. Include malformed
inputs and independently expected bytes; encode/decode round trips alone can hide
a shared endian error. Preserve the distinction between syntax and semantic validity.

Packed-field pointers may be under-aligned or bit-offset. For MMIO, prefer
whole-register volatile accesses with values built separately; field writes can
cause unwanted read-modify-write effects. Derive register semantics from the device
manual. Volatile is not thread synchronization, and whole-register writes are not
universally valid for write-one-to-clear or side-effecting registers. Use required
hardware barriers and only use `allowzero` where zero is a valid mapped address.

## Target evidence

Select the actual ABI/endian/word-size lanes; do not blindly run a universal
matrix. Use repository-supported `-Dtarget` and lower-case 0.17 optimize tags.
Record whether the binary was only compiled, executed natively or executed through
a named emulator. For silent bit/layout migrations, include an opposite-endian
compile-time assertion lane when supported and real target execution where the
contract requires it. Backend or emulator failures are unavailable evidence, not
proof that the representation is portable.
