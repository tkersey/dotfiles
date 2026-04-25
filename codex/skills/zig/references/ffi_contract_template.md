# FFI contract template

Use one row per external symbol or pointer-bearing boundary.

| Symbol | Direction | Nullability | Length/source | Mutability | Ownership in | Ownership out | Lifetime | Thread-safety | Error mapping | Cleanup | Link proof |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `c.symbol` | Zig -> C | non-null/nullable | explicit len/sentinel/global | const/mut | borrowed/owned/transferred | borrowed/owned/transferred | caller/callee/static | safe/unsafe/locked | errno/result/out-param | `deinit`/`free`/none | command/test |

Boundary review checklist:

- Keep translated C imports or raw `extern` declarations in a small boundary module.
- Centralize `@ptrCast`, `@alignCast`, sentinel conversion, null checks, errno mapping, and cleanup.
- Test happy path, invalid/null inputs, out-param initialization, cleanup, and link wiring.
- When ABI or layout matters, use `@sizeOf`, `@alignOf`, `@offsetOf`, explicit enum tag/backing types, and target-aware tests.
