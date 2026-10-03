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
A minimum version in `build.zig.zon` is not an exact compiler pin.

The 0.17 optimize type is `std.lang.Optimize`, with `debug`, `safe`, `fast` and
`small` tags. Use that vocabulary for new commands and mode comparisons; inspect
project-specific option parsing rather than assuming compatibility aliases work.
Example candidates for low-level claims:

```bash
zig build test -Doptimize=debug
zig build test -Doptimize=safe
zig build test -Doptimize=fast
zig build -Doptimize=small
```

They are not an automatic matrix. Pointer width, endian, ABI/layout, SIMD and
optimizer assumptions determine necessary lanes. Use the repository's harness
when module imports, options or dependencies make bare `zig test` insufficient.
Cross-target compilation does not establish target runtime behavior.

## Configuration is now a cacheable input

In 0.17, configuration and graph execution are separate processes. Treat
`build.zig` as producing a graph, not as an arbitrary script whose every side
effect is rerun on every build. Review filesystem/environment/tool observations
that affect graph shape and outputs. Declare tracked configuration inputs with
`dependOnFileContents`, `dependOnFileMetadata`, `dependOnDirectoryContents` or
`dependOnDirectoryMetadata` as appropriate. A directory-entry dependency does not
recursively prove that every file's contents were tracked.

Prefer `findProgramLazy` when a tool is needed only by a make-time step.
`findProgram` remains appropriate when configuration needs the result, but poisons
configuration reuse. Do not hide untracked observations with
`--cache-poison=ignored`. Use `--cache-poison=disallowed` as a scoped diagnostic
when investigating unexpected poisoning, not a universal build requirement.
Use `--print-configuration` to inspect the produced graph and `zig cache-cat` for
binary cache diagnostics. A clean rebuild alone can hide an invalidation defect.
Test the relevant change, including file-content or directory-entry changes.

Replace configure-time `b.args` inspection with the run step's `addPassthruArgs`.
Review renamed `Run` argument methods and their option structs rather than adding
`2` mechanically. Formatting paths use `LazyPath` lists (`b.pathList`); option
paths distinguish tracked files, tracked directories and intentionally untracked
paths. Review `b.build_root` -> `b.root` as a type change, not just a rename.

Custom build-runner overrides are gone. Use the build-server protocol for tooling
that actually needs it; verify the installed ZLS version against 0.17 rather than
assuming compiler and editor support arrive together.

## LTO

LTO is a release/performance/linker choice, not a default correctness lane. Use it
when cross-module inlining, dead-code removal, visible-call specialization or
binary-size reduction is a plausible hypothesis and the target/linker supports it.
Compare baseline and variant under the same workload, CPU, mode and correctness
guard. Leave it out of ordinary debug iteration and unexplained link-failure triage
unless the repository already requires it.

Verify flags with the selected compiler before using these 0.17 examples:

```bash
zig build-exe src/main.zig -O fast -fno-lto
zig build-exe src/main.zig -O fast -flto=full
zig build-exe src/main.zig -O fast -flto=thin
zig build-exe src/main.zig -O small -flto=thin
```

Configure LTO on the final compile artifact, not an unrelated module:

```zig
const exe = b.addExecutable(.{
    .name = "app",
    .root_module = b.createModule(.{
        .root_source_file = b.path("src/main.zig"),
        .target = target,
        .optimize = optimize,
    }),
});
exe.lto = .thin;
```

Only expose/use `-Dlto=...` when the repository has a real need for that option.
Use the selected stdlib's actual enum type when exposing distinct modes. Check
LLVM/LLD/backend and object-format availability; report unavailable lanes rather
than implying LTO works everywhere. ThinLTO and full LTO each need evidence.
Record exact commands, workload/checksum, variance, artifact size and strip/debug
state, target/CPU/mode, backend/linker, and relevant build/link cost. Keep a separate
profiling build when shipping flags compromise the needed debug information.

## Packages and overrides

`build.zig.zon` owns dependency declarations. Review URLs, versions/commits,
content hashes, fingerprints, paths and provenance without treating them as
interchangeable identities. Use supported `zig fetch --save` workflows and inspect
the resulting dependency change. Pin any independently released translator too.

0.17 observes `--pkg-path` / `ZIG_LOCAL_PKG_DIR` in fetch and build. A plain fetch
populates the global cache; saving additionally populates the local package path,
and builds fetch locally too. Inventory the actual configured location rather
than assuming every dependency lives under `zig-pkg`. Package sources, local
forks and edits are not disposable compiler output. Never target a configured
package path or its ancestors with cache cleanup. Keep ordinary package trees
untracked unless intentionally vendored, without treating untracked as disposable.

Use `--fork=/absolute/path` only when supported by the selected toolchain and
project workflow; do not substitute a cache directory for a fork. Dependency/fork
changes invalidate affected validation, not unrelated checks; the
[evidence-context](evidence_context_playbook.md) reference owns that rule.

## C translation and interoperability

For 0.17, `@cImport` is removed and `std.Build.Step.TranslateC` is deprecated.
Prefer the official [translate-c package](https://codeberg.org/ziglang/translate-c)
for new integrations. Select a compatible tag/revision, retain its package hash,
and inspect its `Translator` options. The package's `Translator.init` consumes
the dependency and translation configuration; its `mod` supplies the translated
module. Do not teach deprecated `addTranslateC` as the new default.

Match target, C flags, includes and libc/system libraries. Keep translated code
behind a wrapper that converts raw pointers/status and ownership once. Do not
hand-edit generated translations. Validate ABI assumptions on the intended target
and preserve a clear regeneration owner. A compiler upgrade does not authorize
unrelated dependency upgrades.

## Build options and artifacts

Make consequential option purposes/defaults, artifact/test effects,
ABI/generated-code implications and coverage discoverable. Avoid option explosion.
Identify owners of source paths, compile-fail fixtures, diagnostic goldens,
examples, checked docs, headers/constants and package/release manifests.

Use [repository closure](repo_closure_playbook.md) for locator commands and
working-tree versus committed-review scope. String matching is not proof that a
generator, registry or aggregate check includes an artifact. Run required checks
against the intended inputs. A provenance change alone does not force all checks
to rerun; do not reuse evidence after relevant inputs change or become unknown.
