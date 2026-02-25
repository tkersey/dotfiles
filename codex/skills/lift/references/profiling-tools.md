# Profiling Tool Matrix

## Goal

Pick one primary profiler plus one secondary signal (allocs, lock wait, I/O wait, queue depth). Capture artifacts so results are reviewable.

## Common choices by ecosystem

### Go

- CPU: `go test -bench ... -cpuprofile cpu.pprof` -> `go tool pprof -http :0 cpu.pprof`
- Heap/allocs: `-memprofile mem.pprof` (and compare alloc rate)
- Concurrency: `-blockprofile block.pprof`, `-mutexprofile mutex.pprof`

### Rust / C / C++ / Zig (Linux)

- CPU sampling: `perf record -g -- <cmd>` -> `perf report` / flamegraph
- Counters: `perf stat -- <cmd>` (LLC misses, branch misses, cycles)
- Memory/allocs: `heaptrack` (when feasible)

### macOS (native + mixed stacks)

- CPU sampling: Instruments "Time Profiler"
- System: Instruments "System Trace" / "File Activity" for I/O

### JVM (Java/Kotlin)

- CPU + allocations + locks: JFR (Flight Recorder)
- Flamegraphs: async-profiler (`cpu`, `alloc`, `lock` modes)

### Node.js

- CPU: `clinic flame -- node <script>` (preferred)
- Alternatives: `0x`, `node --prof`
- Memory: `clinic heap`, heap snapshots

### Python

- CPU sampling: `py-spy top` / `py-spy record -o profile.svg -- <cmd>`
- Combined CPU+mem: `scalene` (higher overhead)
- Alloc tracing: `memray` (excellent for allocation hot paths)

## Evidence artifacts to capture

- Workload command (exact)
- Baseline and variant numbers (same runner, same env)
- Profiling command(s)
- Artifact paths (pprof file, svg, trace file, etc.)
- One-sentence bottleneck summary (what is hot, and why)

## Quick heuristics

- If p95/p99 spikes: look for queueing, lock wait, GC pauses, or I/O jitter.
- If throughput drops under concurrency: look for contention, false sharing, or allocator pressure.
- If microbench improves but macro doesn't: Amdahl's law or the bottleneck moved.
