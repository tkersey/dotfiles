# Zig 0.17 migration map

Use for an actual 0.17 upgrade or a version-sensitive decision. This is not an
instruction to upgrade a pinned project or load every reference. Release facts
are anchored in [0.17 notes](https://ziglang.org/download/0.17.0/release-notes.html)
and the [matching language reference](https://ziglang.org/documentation/0.17.0/).
Verify later patches and development builds separately.

## Prioritize meaning before spelling

| Surface | 0.17 migration decision | Relevant verification |
| --- | --- | --- |
| Struct/union reflection | Parallel `field_names`, `field_types`, `field_attrs`; constructor attributes are `std.lang.Type.Struct.FieldAttributes` / `Union.FieldAttributes`. | Empty/mixed shapes, field order, comptime-field policy and generated defaults. |
| `@hasDecl` | Public declarations only, including within the defining file. A private customization hook can silently disappear. | Positive public hook and negative private hook controls. |
| `@bitCast` | Logical, endian-independent bits; array/vector casts may silently change. `extern` aggregate casts are no longer accepted. | Independent constants, explicit wire-endian tests, relevant target execution. |
| Enum/bitpack conversion | Prefer `@backingInt` / `@fromBackingInt`; the input must have the exact backing integer type. Old enum conversion builtins are deprecated, not all removed. | Validate untrusted tags before conversion; do not depend on safety traps as parsing. |
| Optimize mode | `std.lang.Optimize`, tags `debug`, `safe`, `fast`, `small`; use current spellings in CLI/build options too. | Exercise actual selected modes; equality checks cannot rely on deprecated enum-name aliases. |
| Safety query | `@import("builtin").mode.runtimeSafety()` describes this module's mode. | It is not proof that every local scope has safety enabled; inspect local overrides. |
| Target constants | Use `builtin.target.cpu/os/abi/ofmt` rather than deprecated redundant constants. | Explicit target/CPU and ABI checks, not host inference. |
| Allocators/containers | Prefer `SafeAllocator` for diagnostics; adapt stack fallback and pointer-stability APIs by their actual contracts. | Leaks, failure injection, lifetime escape, invalidation and synchronization remain separate concerns. |
| ZON | New option-struct/arena-based parsing and renamed allocating/nonallocating entry points. | Result lifetime, diagnostics ownership and partial-update guarantees. |
| Build graph/cache | Configurer/maker separation; declare configuration dependencies and use lazy make-time tools where possible. | Edit file contents, directory membership and options and observe correct invalidation. |
| C interop | `@cImport` removed; `Step.TranslateC` deprecated in favor of the official `translate-c` package. | Pin translator as a separate dependency; match target/includes/flags and check C ABI. |

The [migration locator](../scripts/zig_0_17_audit_rg.sh) finds candidates, not
proof of incompatibility. Run from the relevant project root. It never rewrites
code, downloads tools, changes pins or deletes caches. Review excluded dependency
roots and custom package paths when they are part of the task.

## Mechanical edits are not semantic validation

Use the selected compiler's `zig fmt` on authorized files, inspect its diff, then
compile. It performs some migrations but does not establish wire-format,
ownership, dependency-tracking or hook-selection correctness. Keep migrations
scoped; do not format unrelated changes or generated/vendor sources.

Replace removed array repetition with typed `@splat` when repeating a single
element; a repeated multi-element pattern needs explicit construction. Replace
`void{}` with `{}`. Remove `errdefer |err|` captures: retain cleanup with `errdefer`
and observe errors at an appropriate `catch` boundary. Do not log twice or alter
the advertised failure guarantee. `i0` and the `internal`/`link_once` global
linkages also require review. `@divCeil` still requires nonzero denominator and a
representable result; it is not a checked-input validation function.

`std.mem.eql` no longer shortcuts float slices merely because addresses match.
Make equality and hashing policies explicit for NaNs and signed zero. Existing
bitwise hashing must not be presented as ordinary floating-point equality.

Other task-dependent churn includes allocator printing (`Allocator.print`),
`bit_set` names, `HostName.fromUri` validation, build `Run` argument APIs,
`addPassthruArgs`, `b.pathList` for formatting paths and explicit option-path kinds.
Use actual 0.17 signatures instead of guessing from an older example. Keep
removed, deprecated, renamed and newly unsafe-to-assume cases distinct.

## Performance and tooling boundaries

Read the [build](build_toolchain_playbook.md) and
[performance](performance_engineering_playbook.md) references for mechanisms.
Separate first-use toolchain setup, cold compilation, warm configure-cache hits,
watch-mode incremental rebuilds, and application runtime. An upstream benchmark
is not a measurement of this repository.

The 0.17 incremental-compilation recommendation chiefly targets `x86_64-linux`
with `-fincremental --watch`; do not transplant that support claim to Apple
Silicon/macOS. The new ELF linker is not a universal default. The self-hosted WASM
backend's progress does not imply complete debug-info support or a changed default.
LLVM loop vectorization remains disabled for a correctness workaround; do not
re-enable it merely to obtain attractive benchmark numbers.

At release time the build-runner change disrupted ZLS integration. Check the
actual ZLS build and current compatibility statement before recommending an
upgrade; do not interpret editor failure as a language/compiler failure or restore
a removed build-runner override. `--print-configuration` and the build-server
protocol are the relevant inspection/integration surfaces, not mandatory tooling
for ordinary edits.

Known release regressions include response-file build uses and selected
panic/libc/backend cases. Consult the current issue for the actual failing lane;
do not label all linker or build errors as those bugs. Reproduce and minimize
before changing safety, architecture or backend defaults.

## Focused evidence

The [example runner](../tests/check_zig_examples.py) discovers all top-level
`references/*.zig` and checks forced diagnostic-specific negative fixtures.
[Semantic tripwires](zig_0_17_regressions.zig) cover public-hook discovery, logical
bits versus wire-endian decoding, backing integers, splats, division and NaN
slice equality. They are deliberately small, not a claim that every user program
or generic instantiation has been validated.

Use native execution for runtime evidence. `--compile-only --target ...` can
check semantic analysis for another target, including the comptime bit-cast
checks, but cannot establish that target's runtime code generation. A normal test
run of the fuzz template is not an extended fuzz campaign. Missing compiler,
version mismatch or unavailable target support must remain visible.
