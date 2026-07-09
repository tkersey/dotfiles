# Zig Build, Package, Target, Linker, and Repository Closure

Use for `build.zig`, `build.zig.zon`, cross compilation, package pins, C/C++ integration, generated artifacts, examples, compile-fail fixtures, repository path registries, release modes, linker options including LTO, or reproducibility.

## Build contract

State:

```text
Zig version
targets and optimize modes
dependencies/fingerprints/forks
build steps and -D options
C/linker inputs
linker/backend options including LTO, LLD, new-linker, PIE/PIC, gc-sections, strip/debug-info
generated artifacts
repository registries/goldens
test/lint/bench/fuzz steps
```

## Inspect first

```bash
zig version
zig build --help
zig build-exe --help | rg -- '-flto|-fno-lto|lld|new-linker'
zig env
find . -maxdepth 4 \( -name build.zig -o -name build.zig.zon \) -print
python3 codex/skills/zig/scripts/zig_repo_closure_scan.py --root .
```

Read existing steps before inventing commands.

## Target and optimize matrix

Low-level and ABI claims require relevant modes/targets.

```bash
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build -Doptimize=ReleaseSmall
```

Target triples are part of proof for ABI/layout/endian/pointer-width/vector and LTO claims.

## Link-time optimization (LTO)

Treat LTO as a release/performance/linker decision, not a default correctness lane.

Use LTO only when:

```text
release artifact or binary-size artifact is being tuned
cross-module or whole-program optimization is plausible for the workload
LLVM/LLD-capable target and linker path are available
baseline and LTO variant can be measured under the same target, optimize mode, CPU, allocator, inputs, and correctness guard
```

Leave LTO off for ordinary debug iteration, compile-error triage, sanitizer/fuzzer minimization, profiler runs that require stable debug information, and unexplained link failures unless the repository already makes LTO part of the artifact contract.

For Zig 0.16-era CLI usage, verify with the installed `zig build-exe --help` or relevant compiler subcommand help, then use explicit modes:

```bash
zig build-exe src/main.zig -O ReleaseFast -flto       # full LTO
zig build-exe src/main.zig -O ReleaseFast -flto=full  # explicit full LTO
zig build-exe src/main.zig -O ReleaseFast -flto=thin  # ThinLTO
zig build-exe src/main.zig -O ReleaseSmall -flto=thin
zig build-exe src/main.zig -fno-lto
```

For `build.zig`, set LTO on the final compile artifact, and prefer the current `lto` field over deprecated boolean wrappers:

```zig
const exe = b.addExecutable(.{
    .name = "app",
    .root_module = b.createModule(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    }),
});

exe.lto = .thin; // .none, .full, or .thin
```

When exposing it as a repository option, keep the default conservative and document CI coverage:

```zig
const lto = b.option(std.zig.LtoMode, "lto", "LTO mode: none, full, or thin") orelse .none;
exe.lto = lto;
```

Current Zig resolves non-`none` LTO through LLD. If the selected target/object format/linker path cannot use LLD, do not silently keep the optimization claim; report the exact unavailable linker lane or compiler error.

Measurement/proof for LTO must include:

```text
baseline command/result without LTO
variant command/result with .thin or .full
target triple, CPU, optimize mode, strip/debug-info state
linker/backend flags: use_lld/use_new_linker/use_llvm/lto
wall-time, binary-size, and workload-specific metric
correctness guard output
build/link time cost and memory pressure when relevant
```

Prefer `.thin` when link-time or memory scaling is the risk; try `.full` only when the artifact is small enough or a measurement justifies the slower/heavier link. Never imply LTO improves speed or size without benchmark data; report `UNMEASURED`.

## Packages

- `build.zig.zon` is dependency source of truth.
- Use `zig fetch --save`.
- Review name, URL, fingerprint/hash, version/tag, and paths.
- Keep `zig-pkg/` untracked unless intentionally vendored.
- Use `zig build --fork=/absolute/path` for temporary overrides.
- Do not use `.zig-cache` as a dependency override.
- Long-lived/security-sensitive pins need origin and release/commit provenance.

Dependency or fork changes invalidate prior proof epochs.

## C translation and interop

Prefer build-system translation for new Zig 0.16 code.

Ensure:

```text
target/cflags match
libc/system libraries linked at correct artifact
translated code behind boundary wrapper
raw C pointers/status/ownership converted once
source/include paths attached to correct module
generated translation not hand-edited
```

## Build options

Each option states:

```text
purpose
default
artifact/test effect
ABI/generated-code effect
CI matrix coverage
```

Avoid option explosion. For LTO specifically, prefer an explicit enum option (`none|thin|full`) over a boolean, because `.thin` and `.full` have materially different build-cost profiles.

## Repository closure

When changing files/generated output, discover:

```text
source/path registries
build enumeration
lint/fmt path lists
compile-fail registration
goldens/expected output
examples checked by CI
generated headers/constants
package/release manifests
```

For each changed path:

```yaml
changed_path:
  build_owner:
  registry_owner:
  generator_owner:
  golden_owner:
  aggregate_proof:
```

A new file compiling locally is not closure if aggregate repository contracts omit it.

Generated output rewrites invalidate proof that ran before regeneration.

## CI/reproducibility

- Zig version pinned/reported.
- Build help exposes intended steps/options.
- Build-system tests cover modules/dependencies.
- Relevant optimize/target/LTO lanes exist when claimed.
- Package pins/forks reviewed.
- C translation matches target/cflags.
- Cache/dependency policy explicit.
- Repository closure scan reviewed.
- Final proof epoch matches generated artifacts and dependencies.