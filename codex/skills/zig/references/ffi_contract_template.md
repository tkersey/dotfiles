# FFI Contract Template

Use one row per raw symbol. Keep the table next to the wrapper module or in the PR notes.

| Symbol | C signature | Zig wrapper | Nullability | Length source | Ownership in/out | Lifetime | Thread-safety | Error mapping | Linkage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sqlite3_open` | `int sqlite3_open(const char*, sqlite3**)` | `Db.open` | path non-null, out ptr non-null | N/A | caller owns path buffer, callee initializes handle | handle valid until `sqlite3_close` | thread-safe per SQLite mode | non-zero -> `error.OpenFailed` | `linkLibC` + `linkSystemLibrary("sqlite3")` |

Checklist:

1. Put raw `extern fn` declarations in a small boundary module.
2. Centralize `@ptrCast`, sentinel conversion, null handling, and errno/result translation in the Zig wrapper layer.
3. Mirror boundary assumptions in wrapper types, asserts, or witness constructors.
4. Test happy path, null or invalid inputs, out-param initialization, cleanup, and link wiring.
5. If the upstream C dependency changes, compare signatures and ABI expectations before trusting the upgrade.
