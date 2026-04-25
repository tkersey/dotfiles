# Zig build, cross-compilation, package, and C toolchain playbook

Use this playbook for `build.zig`, `build.zig.zon`, cross-compilation, package pins, `zig fetch`, `zig-pkg`, `zig build --fork`, C/C++ interop, release modes, linker options, or reproducibility.

## Expert objective

Build work should produce a reproducible build contract:

1. exact Zig version;
2. targets and optimization modes;
3. dependencies and hashes/fingerprints;
4. build steps and user-facing `-D` options;
5. C toolchain/linker inputs;
6. test/lint/bench/fuzz steps;
7. local overrides and whether they are ephemeral.

## Inspect first

Before changing build logic:

```bash
zig version
zig build --help
zig env
find . -maxdepth 3 \( -name build.zig -o -name build.zig.zon \) -print
```

Read existing steps before inventing new commands. Prefer adding named steps (`test`, `lint`, `bench`, `fuzz`, `docs`) that compose existing artifacts.

## Target and optimize matrix

Do not validate systems code in Debug only. Use relevant lanes:

```bash
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build -Doptimize=ReleaseSmall
zig build test -Dtarget=native
```

For cross-platform libraries, add explicit target triples that match supported platforms. For ABI/layout code, target triples are part of the proof.

## Package workflow

Rules:

- Treat `build.zig.zon` as source of truth.
- Use `zig fetch --save ...` to add dependencies.
- Review name, fingerprint/hash, version/tag, URL, and paths.
- Keep `zig-pkg/` out of source control unless intentionally vendoring.
- Use `zig build --fork=/absolute/path` for temporary local package overrides.
- Do not edit `.zig-cache` as a dependency override.

For long-lived or security-sensitive pins, record origin repository, tag/commit, fetch date, and signer/attestation evidence if available.

## C/C++ interop and translation

For Zig 0.16, prefer build-system C translation for new code:

```zig
const translate_c = b.addTranslateC(.{
    .root_source_file = b.path("src/c.h"),
    .target = target,
    .optimize = optimize,
});
translate_c.linkLibC();

exe.root_module.addImport("c", translate_c.createModule());
```

Expert checks:

- target triple and cflags match the C ABI being compiled against;
- system libraries are linked at the right artifact boundary;
- translated C stays in a boundary module;
- raw `[*c]T`, nullability, ownership, and errno/status are wrapped;
- C source files and include paths are attached to the correct module/artifact;
- generated/translated code is not edited unless intentionally vendored.

## Build options

Expose intentional knobs through `b.option` and document them in `zig build --help`.

Avoid option explosion. Each option should answer:

- user-facing purpose;
- default;
- effect on artifacts/tests;
- whether it changes ABI or generated code;
- whether CI covers both values.

## Linker/profiling interaction

For profiling, debug info matters. Be careful with linker flags or incremental linker choices that remove or degrade DWARF or symbols. If CPU sampling uses DWARF call graphs, validate that the produced binary contains the expected debug information.

## CI/reproducibility checklist

- `zig version` pinned or reported.
- `zig build --help` exposes expected steps/options.
- `zig build test` runs through the build system, not only bare `zig test`, when modules/deps exist.
- ReleaseSafe and ReleaseFast lanes exist for low-level code.
- Package pins are reviewed.
- Local forks are not accidentally committed as permanent overrides.
- C translation uses matching target/cflags.
- Build cache and `zig-pkg` policy is explicit.
