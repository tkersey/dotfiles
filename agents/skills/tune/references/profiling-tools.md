# Profiling tools and language-specific diagnosis

Read only the platform/language sections needed for the selected experiment.
Commands are starting points, not a required installed stack. Check version/help,
repository build/test instructions, permissions, output paths, and instrumentation
overhead before running. Use existing tools first; installation, privileged
profiling, external service load, and profile publication need authority.

Keep baseline/candidate environments equal. Do not benchmark an instrumented build
against an uninstrumented one or silently change optimization/safety settings.
Store generated profiles outside tracked source unless their inclusion is useful
and authorized. Profiles and heap snapshots can contain sensitive data.

## Cross-platform measurement

For an authorized local CLI experiment with known terminating commands:

```bash
hyperfine --warmup 3 --runs 20 --export-json comparison.json \
  './baseline input.fixture' './candidate input.fixture'
```

The run count is illustrative, not a statistical threshold. Omit warmups for a
cold-start objective; test cold and warm separately when both matter. Record
commands/fixtures and variance. Hyperfine measures whole-command timing, not
service request p99. Use the project's load test for service throughput/tails.
See [Hyperfine's own documentation](https://github.com/sharkdp/hyperfine).

| Need | Linux candidates | macOS candidates |
|---|---|---|
| CPU stacks | `perf record -g -- ./binary`, then `perf report` | Instruments Time Profiler; authorized `sample` capture |
| CPU/cache counters | `perf stat -- ./binary` with supported events | Instruments counters where supported |
| Allocation/retained memory | heaptrack, Massif, allocator/runtime counters | Instruments Allocations and Leaks |
| Syscalls/I/O/waits | `strace -c ./binary`, runtime tracing, authorized off-CPU tooling | Instruments System Trace / File Activity |
| Peak process memory | `/usr/bin/time -v ./binary` | `/usr/bin/time -l ./binary` |

Tool availability and capabilities differ by architecture, kernel, permissions,
and runtime. A CPU-only sample misses blocked time; correlate traces and counters.
Use utilization, saturation, and errors to distinguish resource pressure from
application work; see the [USE checklist](https://www.brendangregg.com/USEmethod/use-linux.html).
Do not weaken host profiling restrictions to make a command succeed.

## Zig

Read the pinned Zig version, `build.zig`, and available build steps first:

```bash
zig version
zig build --help
# Only when the project exposes these standard options/steps:
zig build -Doptimize=ReleaseSafe
zig build test -Doptimize=ReleaseSafe
```

Benchmark the production-representative mode on both revisions, with symbols
where supported. `ReleaseSafe` retains safety checks; `ReleaseFast`/`ReleaseSmall`
change defaults. Do not present disabling runtime safety as a lossless speedup.
Verify both production behavior and the relevant checked build. Follow the
[language reference for the pinned version](https://ziglang.org/documentation/master/#Build-Mode),
not assumed APIs from a different release.

Use native CPU/heap tools for the target platform. If allocator activity is the
mechanism, use an existing counting/tracking allocator or a small version-correct
instrumentation seam; do not introduce global allocator policy merely to profile.
Examine capacity growth, copies, arena lifetimes, error/cleanup paths, layout,
alignment, tagged-union/indirect dispatch, and comptime specialization only where
measured. Check generated code when it can resolve an actual inlining/vectorization
question. For WASM, profile the real interpreter/host, host-call boundary, memory
and serialization costs; native timing alone does not establish WASM performance.

## Rust

Use the existing release test/benchmark targets and available flamegraph tooling:

```bash
cargo test --release
cargo bench
# With cargo-flamegraph installed and its CLI verified:
cargo flamegraph -- <application-arguments>
```

Use perf/Instruments for CPU, heaptrack or existing DHAT instrumentation for
allocation, and the project's Criterion or other benchmark framework. A `.clone()`,
trait object, mutex, or default hasher is not a defect without measured relevance.
Check borrowing/ownership, collection capacity, materialization, dispatch, and
contention without weakening lifetimes, error behavior, or collision defenses.

For PGO, use matching compiler/profdata tools: instrument, run representative
training workloads, merge profiles, rebuild with profile use, then measure on
holdouts. Include LTO/code-size/compile-time effects. Follow
[rustc's PGO instructions](https://doc.rust-lang.org/rustc/profile-guided-optimization.html)
for the pinned toolchain; no fixed percentage gain is promised.

## Go

Prefer project benchmarks and pprof/trace rather than grepping for interfaces:

```bash
go test ./...
go test -run '^$' -bench . -benchmem -count 10 ./path/to/package
# Scoped to one package; writes diagnostic files:
go test -run '^$' -bench BenchmarkTarget -cpuprofile cpu.out \
  -memprofile mem.out ./path/to/package
go tool pprof cpu.out
go test -race ./...
```

Compare saved baseline/candidate benchmark samples with an available `benchstat`;
retain sample size and uncertainty. Use block/mutex profiles and execution traces
for contention/scheduling. Inspect escape analysis or GC diagnostics only when
allocation/GC is implicated. Pools, concrete types, and worker limits are candidate
changes, not rules. Race-instrumented timings are not production benchmarks.
See [Go diagnostics](https://go.dev/doc/diagnostics) and
[benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat).

## JavaScript / TypeScript

Profile the deployed runtime and emitted code, with source maps when needed:

```bash
node --cpu-prof app.js
node --heap-prof app.js
```

Use runtime-supported DevTools/performance facilities and event-loop delay,
utilization, GC, and async traces as appropriate. Browser work needs browser
profiling rather than assuming Node behavior. Preserve JIT warmup assumptions
and examine deoptimizations only with relevant evidence. Verify flags against
[Node's command-line documentation](https://nodejs.org/api/cli.html).

Investigate synchronous I/O, repeated JSON work, copying/materialization, serial
awaits, and CPU-bound callbacks. Bounded concurrency helps independent I/O; it
does not make CPU work parallel. Worker transfers, serialization, and scheduling
can exceed the work saved. Preserve stateful regex behavior, object identity,
ordering, exceptions, and cancellation. Prefer built-in tools over requiring a
particular third-party profiler or global npm install.

## Python

Use repository-prescribed Python tooling; in this repository, invoke through uv:

```bash
uv run -- python -m cProfile -o profile.pstats script.py
uv run -- python -m pstats profile.pstats
```

Use existing py-spy, Scalene, tracemalloc, or allocation tooling when the question
requires sampling, native frames, or memory attribution. Do not create a project
or install dependencies solely because a guide names a tool. The
[standard profiler documentation](https://docs.python.org/3/library/profile.html)
explains deterministic profiling; use independent timing for performance claims.

Investigate Python/native boundary costs, vectorizable loops, materialization,
repeated pure computation, object churn, and data-frame iteration when profiled.
Vectorization can allocate large temporaries or alter numeric semantics. Do not
assume regex calls always recompile, all string concatenation is quadratic, or
that a pool/GC disabling is inherently better. Match dtype, null, order, and
exception behavior when replacing data-processing operations.

## Other runtimes

Use native evidence rather than forcing one of these recipes: JVM JFR/JMH for
Java, runtime-specific .NET tooling, GPU kernel/transfer profiles, or database
query plans as applicable. Verify current commands and methodology from the
runtime's primary documentation before execution. Preserve Tune's same workload,
correctness, authority, and claim-strength requirements.
