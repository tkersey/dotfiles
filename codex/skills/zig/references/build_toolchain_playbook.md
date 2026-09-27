# Zig build, packages, targets, linking and repository closure

Use for `build.zig`, `build.zig.zon`, cross compilation, package pins, C/C++
integration, generated artifacts, examples, compile-fail fixtures, release modes,
linker/LTO options or reproducibility. Inspect the build inputs and steps relevant
to the task; do not demand a full build contract before an unrelated edit.

## Toolchain and inputs

Use `zig version`, `zig env`, `zig build --help` and the relevant compiler
subcommand's help to establish actual support. Read the repository's pins and
existing options before inventing commands. Important inputs can include target,
CPU, optimize mode, dependencies/forks, C flags/includes, generated artifacts,
linker/backend selection, PIE/PIC, section collection, stripping/debug info and LTO.

For low-level or ABI claims, include relevant modes/targets. Example candidates:

```bash
zig build test -Doptimize=Debug
zig build test -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseFast
zig build -Doptimize=ReleaseSmall
```

They are not an automatic matrix. Pointer width, endian, ABI/layout, SIMD and
optimizer assumptions determine the necessary lanes. Use the repository's harness
when module imports, options or dependencies make bare `zig test` insufficient.

## LTO

LTO is a release/performance/linker choice, not a default correctness lane. Use it
when cross-module inlining, dead-code removal, visible-call specialization or
binary-size reduction is a plausible hypothesis and the target/linker supports it.
Compare baseline and variant under the same workload, CPU, mode and correctness
guard. Leave it out of ordinary debug iteration and unexplained link-failure triage
unless the repository already requires it.

Verify flags with the installed compiler before using these Zig 0.16 examples:

```bash
zig build-exe src/main.zig -O ReleaseFast -flto
zig build-exe src/main.zig -O ReleaseFast -flto=full
zig build-exe src/main.zig -O ReleaseFast -flto=thin
zig build-exe src/main.zig -O ReleaseSmall -flto=thin
zig build-exe src/main.zig -fno-lto
```

For build-system configuration, set the final compile artifact's `lto` field:

```zig
const exe = b.addExecutable(.{
    .name = "app",
    .root_module = b.createModule(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    }),
});
const lto = b.option(std.zig.LtoMode, "lto", "LTO mode: none, full, or thin") orelse .none;
exe.lto = lto;
```

Use `-Dlto=...` only if the repository exposes it. Prefer an explicit enum over a
boolean when exposing the distinct modes, without adding options absent a real
need. Check LLVM/LLD/backend and object-format availability; report the actual
unavailable lane or link error rather than implying LTO is active everywhere.
ThinLTO is a candidate when link-time/memory scaling matters; full LTO needs its
own evidence. Do not promise that either improves performance.

Record baseline/variant commands, workload/checksum, wall-time variance, artifact
size and strip/debug state, target/CPU/mode, backend/linker flags, and build/link
cost where relevant. Profiling that depends on stable DWARF/call graphs may need a
separate lane from the shipping LTO build. Report unmeasured benefits as `UNMEASURED`.

## Packages and overrides

`build.zig.zon` is the dependency source of truth. Review URLs, versions/commits,
content hashes, package fingerprints, paths and source provenance without treating
all those fields as interchangeable identities. Use supported `zig fetch --save`
workflows and inspect the resulting dependency change.

For Zig 0.16 temporary forks, use the repository-supported `zig build --fork=/absolute/path`
override; do not repurpose `.zig-cache` as one. Keep `zig-pkg` untracked unless
intentionally vendored, but never infer that untracked dependency data is disposable.
Preserve edits, local commits and fork targets. The cache helper cannot delete it.
A relevant dependency/fork change invalidates affected validation, not unrelated
checks; [evidence context](evidence_context_playbook.md) owns that rule.

## C translation and interoperability

Prefer build-system translation for new Zig 0.16 integrations. Match target,
C flags, include paths and libc/system libraries at the correct module/artifact.
Keep translated code behind a wrapper that converts raw C pointers/status and
ownership once. Do not hand-edit generated translations. Validate ABI assumptions
on the intended target and preserve a clear regeneration owner.

## Build options and artifacts

For a consequential option, make its purpose/default, artifact/test effect,
ABI/generated-code implications and coverage discoverable. Avoid option explosion.
Identify owners of changed source paths, compile-fail fixtures, diagnostic goldens,
examples, checked docs, headers/constants and package/release manifests.

Use [repository closure](repo_closure_playbook.md) for optional locator commands and
working-tree versus committed-review scope. String matching is not proof that a
generator, dynamic registry or aggregate check includes the changed artifact.
Run required aggregate commands against the actual intended inputs. A provenance
change alone does not force all validation to rerun; do not reuse evidence across
changed relevant inputs or unknown assumptions.
