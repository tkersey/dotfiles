# Zig skill regression checks

Requirements: Python 3.11+, Git and `uv`; Zig 0.17.0 for compiler checks. The shared
`toolchain.py` owns the bundled example version and canonical optimize tags. This
is not a mandate to upgrade consuming projects. Helpers use disposable temporary
directories and stub compiler/process discovery, without production access.

From this skill directory:

```bash
uv run python3 -m unittest discover -s tests -p 'test_*.py'
uv run python3 tests/check_zig_examples.py --zig zig --optimize debug
uv run python3 tests/check_zig_examples.py --zig zig --optimize safe
```

The compiler runner discovers every top-level `references/*.zig` file, rather
than maintaining a three-file allowlist, and all forced diagnostic-specific
negative fixtures. This exercises present tests, not every lazy generic body or
every prose snippet. Native Smith examples do not constitute a sustained fuzzing
campaign. Missing/wrong-version compilers return unavailable (exit 2), test or
expected-diagnostic failures return 1, and completed checks return 0. An unrelated
compiler error, crashing compiler or negative fixture that succeeds is not a pass.

For cross-compilation, require explicit compile-only scope:

```bash
uv run python3 tests/check_zig_examples.py --optimize safe \
  --compile-only --target aarch64-linux-musl
zig test references/zig_0_17_regressions.zig -O safe \
  -target aarch64_be-linux-musl --test-no-exec
```

The latter contains comptime logical-bit/endian assertions. Neither command runs
target machine code. Use the project's actual native/emulated harness when target
execution is required. CI separates native debug/safe tests and the opposite-
endian compile-only lane and verifies the official compiler archive's checksum.

The helper tests cover cache safety, repository closure and runner classification.
Stub-compiler tests prove control flow/status handling, not Zig correctness. Source-
contract checks cover referential integrity and optional routing artifacts, not
prose quality. Keep those evidence categories separate in reports.

Optional build-cost experiment:

```bash
uv run python3 tests/measure_comptime.py --zig zig --sizes 8 32 128 \
  --samples 3 --cpu baseline
```

It records cold direct-compilation wall time and object bytes for exported runtime-
input kernels, with fresh per-sample compiler caches and rotated strategy order.
It does not measure runtime latency, peak compiler memory, configuration-cache hits
or persistent incremental rebuilds. See the comptime/performance playbooks and
matched behavioral probes. No experiment is a required ordinary-use stage.
