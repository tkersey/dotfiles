# Zig performance and measurement

Use for latency, throughput, allocation pressure, compile time, binary size,
CPU hotspots, layout, SIMD and LTO. State the workload, baseline, hypothesis,
correctness guard, exact commands, version/target/CPU/mode/allocator and relevant
noise. This can be a short result, not a mandatory report template. Report
`UNMEASURED` instead of implying a speedup without measurements.

## Separate the measured questions

Zig 0.17 changes compilation infrastructure. Measure separately:

- cold compilation with declared local/global cache state;
- warm no-change build/configuration-cache hits;
- incremental edited rebuilds in a persistent `--watch` process;
- produced-program runtime and memory behavior.

A faster warm configure step is not faster semantic analysis; a smaller object is
not lower runtime latency. The bundled comptime driver measures cold direct
`build-obj` wall time and object bytes only, with rotated strategies and fresh
per-sample caches. It does not measure the build-system configure cache, persistent
incremental compilation, peak compiler memory or runtime. Pin CPU/features when
comparing machines; native CPU detection changes can otherwise confound results.

The 0.17 incremental milestone primarily concerns x86_64 Linux and its ELF linker.
Verify backend/target support before proposing `-fincremental --watch`. Do not
promise equivalent Apple Silicon/macOS gains or enable a backend solely because
it is new. Keep usable debug information for the profiling lane; experimental
WebAssembly debug-info support is not a production profiling guarantee.

## Runtime benchmarks

Use externally supplied runtime input, warmup, repeated samples, an observable
checksum or invariant, and the same dataset and allocator across baseline and
variant. Match the production optimize mode (`fast`, `safe` or `small` in 0.17),
not an assumed Debug-versus-release comparison. Inspect generated code when the
optimizer may eliminate the work or make representations equivalent.

Decompose a cross-layer regression into substrate, wrapper, full path and
reference/optimized lanes only when that distinction helps isolate the cause.
Keep identical semantic checks and input across them.

## LTO and binary size

LTO is a release hypothesis, not a routine correctness requirement. Cross-module
inlining, visible-call specialization and dead-code removal can help or regress
an artifact. Confirm supported LLVM/linker/object-format combinations first.

```bash
zig build-exe src/main.zig -O fast -fno-lto
zig build-exe src/main.zig -O fast -flto=thin
zig build-exe src/main.zig -O fast -flto=full
zig build-exe src/main.zig -O small -flto=thin
```

Check installed help; prefer the repository harness. Use `-Dlto=...` only if the
build exposes it. Compare none/thin/full under the same workload and correctness
guard, recording artifact size, strip/debug state and compile/link time. ThinLTO
is a candidate for constrained link time/memory, not an unconditional winner.
Full LTO needs its own evidence. Do not infer program speed from artifact size.

## Allocation and CPU

Measure allocation count, allocated/freed bytes, live/peak requested bytes, leaks
and contention. SafeAllocator's checks and thread safety do not demonstrate
application throughput or race freedom. Use repository-compatible `zprof` for
allocator metrics and a platform profiler for CPU/time; inspect actual tool
compatibility rather than inventing flags after a compiler upgrade.

On Linux, a supported lane is `perf record --call-graph dwarf -- ./zig-out/bin/app`
followed by `perf report`. On macOS use Instruments Time Profiler. Use Tracy only
when supported or justified by a timeline question. Preserve DWARF/call-graph
quality separately from shipping linker/LTO choices. `zig objdump` object metadata
inspection does not automatically replace a disassembler or a CPU profiler.

## Layout, specialization and vectors

Investigate hot/cold splitting, arrays-of-structs versus structs-of-arrays, pointer
chasing, false sharing, packed access, alignment and branch behavior. Claim cache
or branch improvements only with suitable evidence. Count comptime specialization
cardinality and plan storage alongside build time and binary size.

Keep an independent scalar path for SIMD, explicit CPU features, correct alignment
and tail handling, and scalar/vector equivalence tests. Runtime array coercion is
an option where vector indexing support requires it, not a universal requirement.
Zig 0.17 still disables LLVM loop vectorization for a correctness workaround; do
not force it back on merely to improve a benchmark. Explicit vectors and automatic
loop vectorization are different mechanisms. Revisit logical `@bitCast` semantics
before treating vector packing as a memory-layout optimization.
