# Zig layout, ABI, packed/extern, MMIO, and wire-format playbook

Use this playbook for C ABI, `extern` types, `packed` types, hardware registers, binary protocols, file formats, network packets, endian conversions, `@offsetOf`, `@bitOffsetOf`, `@sizeOf`, `@alignOf`, or target-sensitive layout.

## Expert objective

For layout-sensitive code, produce a layout proof table:

| Type/field | Expected size/bits | Alignment | Offset/bit offset | Endian/target assumption | Proof command/test |
| --- | --- | --- | --- | --- | --- |

Do not assume ordinary Zig `struct` layout for wire, disk, or foreign ABI. Ordinary structs are for Zig semantics; `extern` and `packed` are for layout commitments.

## Choosing layout forms

| Form | Use for | Avoid when |
| --- | --- | --- |
| `struct` | Normal Zig data; compiler may choose layout. | C ABI, wire format, MMIO register, disk format. |
| `extern struct` | Target C ABI layout. | Portable wire format independent of target ABI. |
| `packed struct` | Bit-level layout, flags, MMIO register value, compact wire fields. | You need ordinary field pointers or natural alignment. |
| `extern union` | C ABI union. | Tagged safe domain modeling. |
| `packed union` | Bit-level reinterpretation with explicit backing. | General-purpose polymorphism. |
| `enum` with explicit tag type | Stable tag values. | C ABI unless `extern enum` is required. |

## ABI and C interop

For each C-facing type/function:

- confirm target triple and cflags match the C side;
- use `extern struct`, `extern union`, and appropriate calling conventions;
- prove `@sizeOf`, `@alignOf`, and `@offsetOf` against C expectations;
- preserve `const`, nullable, and ownership conventions;
- wrap raw functions in a Zig boundary module.

When using translated C, keep generated declarations isolated and provide safer wrappers for core code.

## Packed types

Packed structs have bit-level layout and can be useful for registers or protocol flags. They also introduce hazards:

- field pointers may be under-aligned or bit-offset;
- byte order matters when bitcasting to/from bytes;
- direct field writes to volatile packed MMIO can generate unexpected read/write behavior;
- packed layout should be tested on each target where it matters.

Prefer helper functions that read/write whole packed values:

```zig
const Control = packed struct(u32) {
    enable: bool,
    mode: u3,
    reserved: u28 = 0,
};

fn setControl(reg: *volatile Control, value: Control) void {
    reg.* = value;
}
```

## Wire-format design

For network/disk data, avoid mapping raw bytes directly to host structs unless the format is explicitly host-ABI-dependent. Prefer parse/serialize functions that:

- validate length before reading;
- use explicit endian reads/writes;
- reject reserved/invalid field values;
- expose a validated semantic type, not raw bytes;
- fuzz parsers and round-trip serializers.

Suggested shape:

```text
raw bytes -> length/endian validation -> semantic struct -> encode/decode tests
```

## MMIO/register design

For hardware registers:

- define a register block only from the hardware manual;
- represent volatile register addresses explicitly;
- avoid copying MMIO pointers into ordinary data structures without lifetime/target notes;
- consider barriers/fences when required by the architecture or device;
- use `allowzero` only when address zero is a valid mapped address and document target assumptions.

Do not confuse MMIO volatility with thread synchronization.

## Layout proof tests

Add tests like:

```zig
test "layout: header" {
    try std.testing.expectEqual(@as(usize, 16), @sizeOf(Header));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(Header));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(Header, "payload_len"));
}
```

For packed fields, use `@bitOffsetOf` and `@bitSizeOf` where appropriate. For C ABI, compare against generated C constants or static assertions when feasible.

## Target matrix

Layout-sensitive code needs target-aware validation. At minimum, consider:

```bash
zig build test -Dtarget=native
zig build test -Dtarget=x86_64-linux-gnu
zig build test -Dtarget=aarch64-linux-gnu
zig build test -Dtarget=x86_64-windows-gnu
```

Use only targets relevant to the project, but do not claim portable layout if only host was tested.

## Review checklist

- Ordinary `struct` is not used for foreign/wire/MMIO layout.
- `extern` is used for target C ABI; `packed` is used for bit layout.
- Size, alignment, and offsets are asserted.
- Endianness is explicit for wire/disk formats.
- Packed-field pointer hazards are avoided or documented.
- MMIO uses volatile whole-register access patterns.
- Target triples and C flags are part of the ABI proof.
- Fuzz/round-trip tests cover parsers and serializers.
