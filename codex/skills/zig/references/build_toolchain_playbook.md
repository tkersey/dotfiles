# Zig Build, Package, Target, and Repository Closure

Use for `build.zig`, `build.zig.zon`, cross compilation, package pins, C/C++ integration, generated artifacts, examples, compile-fail fixtures, repository path registries, release modes, linker options, or reproducibility.

## Build contract

State:

```text
Zig version
targets and optimize modes
dependencies/fingerprints/forks
build steps and -D options
C/linker inputs
generated artifacts
repository registries/goldens
test/lint/bench/fuzz steps
```

## Inspect first

```bash
zig version
zig build --help
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

Target triples are part of proof for ABI/layout/endian/pointer-width/vector claims.

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

Avoid option explosion.

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
- Relevant optimize/target lanes exist.
- Package pins/forks reviewed.
- C translation matches target/cflags.
- Cache/dependency policy explicit.
- Repository closure scan reviewed.
- Final proof epoch matches generated artifacts and dependencies.
