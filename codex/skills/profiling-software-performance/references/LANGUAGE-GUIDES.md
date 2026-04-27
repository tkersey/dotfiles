# Language-Specific Profiling Guides

> Install, flags, run commands, gotchas. One section per language. Pick the default tool unless you have a specific reason.

## Contents

1. [Rust](#rust)
2. [Go](#go)
3. [Node / TypeScript](#node--typescript)
4. [Python](#python)
5. [C / C++](#c--c)
6. [Cross-language benchmarking](#cross-language-benchmarking)
7. [Continuous profiling (prod)](#continuous-profiling-prod)

---

## Rust

### Build profile — non-negotiable

```toml
# Cargo.toml — add a dedicated perf profile, do NOT profile the size-optimized release
[profile.release-perf]        # or name it "profiling"
inherits = "release"
opt-level = 3
lto = "thin"
codegen-units = 1
debug = "line-tables-only"    # ~5% size, keeps frames. Use `true` for deepest unwinding.
strip = false

# If your regular release uses opt-level = "z" (size), the perf profile MUST override it.
```

```bash
export RUSTFLAGS="-C force-frame-pointers=yes"
cargo build --profile release-perf
```

### Defaults

```bash
cargo install samply cargo-flamegraph cargo-pgo cargo-instruments
# CPU — preferred 2025 default
samply record -- ./target/release-perf/bin args
# opens Firefox Profiler URL; call tree + flame graph + stack chart

# CPU — alternative (perf-based; Linux only)
cargo flamegraph --profile release-perf --bin <name> -- args
# writes flamegraph.svg in cwd

# Macro benchmarks
cargo bench -- --save-baseline before
# baseline A; make one change; then:
cargo bench -- --baseline before

# Micro — instruction-count stable for CI
cargo add --dev iai-callgrind
cargo install iai-callgrind-runner
cargo bench --bench micro     # no warmup noise, CI-reproducible

# Allocation
heaptrack ./target/release-perf/bin args
heaptrack --analyze heaptrack.bin.gz.*
# OR in-process:
cargo add dhat --optional   # enable with feature = "dhat-heap"
# wrap main: let _p = dhat::Profiler::new_heap();
# writes dhat-heap.json; view in https://nnethercote.github.io/dh_view.html

# Async / Tokio
cargo add console-subscriber
# console_subscriber::init(); at the top of main
RUSTFLAGS="--cfg tokio_unstable" cargo build --profile release-perf
tokio-console               # in another pane

# In-process pprof-compatible (no perf privs needed)
cargo add pprof --features flamegraph,protobuf-codec
# pprof::ProfilerGuardBuilder::default().frequency(997).build();
# on shutdown: guard.report().build()?.flamegraph(file);

# Causal profiling — which speedup would actually help?
LD_PRELOAD=libcoz.so ./target/release-perf/bin   # annotate with coz::progress!();

# PGO (after other levers exhausted)
cargo install cargo-pgo
cargo pgo build && ./target/.../bin <representative-workload>
cargo pgo optimize
```

### Criterion template (from cass)

```rust
// benches/common.rs
pub fn configure_criterion() -> Criterion {
    Criterion::default()
        .sample_size(50)
        .measurement_time(Duration::from_secs(3))
        .warm_up_time(Duration::from_secs(1))
        .noise_threshold(0.03)
        .confidence_level(0.95)
        .without_plots()
}
```

### Gotchas

- **LTO strips symbols** — `lto="thin"` is OK; `lto="fat"` kills cross-crate inlining info.
- **`[profile.release] opt-level = "z"`** (common in size-optimized release profiles) produces unprofilable binaries. Always build the `release-perf` profile for measurement.
- **`panic = "abort"`** skips unwinding; `backtrace` + panic-path profiling needs `panic = "unwind"`.
- **`Arc` / generics across crate boundaries** can be inlined invisibly. Use `#[inline(never)]` sentinels (INSTRUMENTATION.md §Frame sentinels) for pipeline stages.
- **`tokio` sampled at the top**: looks flat; most time is in `poll()`. Use `tokio-console` to see per-task time, not the flamegraph.

---

## Go

### Defaults

```bash
# Bench-driven
go test -bench=. -benchmem -count=10 \
        -cpuprofile=cpu.p -memprofile=mem.p \
        -blockprofile=blk.p -mutexprofile=mtx.p \
        ./...
go tool pprof -http=:8080 cpu.p         # browser UI
go tool pprof -alloc_space mem.p        # allocations by size
go tool pprof -top mtx.p | head         # contention ranks

# Live server
import _ "net/http/pprof"
go func() { log.Println(http.ListenAndServe("localhost:6060", nil)) }()
go tool pprof http://host:6060/debug/pprof/profile?seconds=30
go tool pprof http://host:6060/debug/pprof/heap
go tool pprof http://host:6060/debug/pprof/goroutine

# Runtime trace — scheduler + GC + syscalls on one timeline
curl -o trace.out http://host:6060/debug/pprof/trace?seconds=5
go tool trace trace.out

# Escape analysis — find heap escapes
go build -gcflags='all=-m=2' 2>&1 | grep "escapes to heap"

# Data races (use in CI, 10-20x slowdown)
go test -race ./...

# A/B benchmark comparison
go install golang.org/x/perf/cmd/benchstat@latest
benchstat old.txt new.txt     # t-test + delta

# Diagnose GC pressure
GODEBUG=gctrace=1 ./bin               # per-GC log
GODEBUG=schedtrace=1000 ./bin         # scheduler every 1s
GODEBUG=allocfreetrace=1 ./bin        # very verbose
```

### Rates that are off by default

```go
import "runtime"
runtime.SetBlockProfileRate(10_000)     // ns between blocking events sampled
runtime.SetMutexProfileFraction(5)      // 1/5 contention events
```

### Gotchas

- Block / mutex profiles are empty by default — enable rates above or you'll wonder why there's no contention data.
- `pprof` HTTP listener exposed to the internet = remote code execution. Bind to `127.0.0.1` or a unix socket.
- `go tool pprof` consumes pprof profiles; `go tool trace` consumes execution traces from `runtime/trace` or `/debug/pprof/trace?seconds=N`.
- `benchstat` is the only trusted A/B verdict; eyeballing bench output leads you astray on noisy runs.

---

## Node / TypeScript

### Defaults

```bash
# Built-in V8 profilers (no deps, ship-safe)
node --cpu-prof --cpu-prof-dir=./prof app.js      # *.cpuprofile (drop into Chrome DevTools)
node --heap-prof --heap-prof-dir=./prof app.js    # *.heapprofile
node --prof app.js                                # legacy V8 tick; process with:
node --prof-process isolate-*.log > profile.txt

# Connect Chrome DevTools live
node --inspect=0.0.0.0:9229 app.js
# open chrome://inspect

# clinic suite — the one-stop flow
npm i -g clinic autocannon
clinic doctor   -- node app.js    # diagnoses which axis is the problem
clinic flame    -- node app.js    # CPU flame
clinic bubbleprof -- node app.js  # async ops timeline
clinic heapprofiler -- node app.js

# 0x — a sharper V8 tick flame
npm i -g 0x && 0x app.js

# Load gen
autocannon -c 100 -d 30 http://localhost:3000
k6 run script.js                                  # scripted scenarios
```

### Production-safe event-loop metrics

```javascript
import { monitorEventLoopDelay, performance, PerformanceObserver } from 'perf_hooks';

const h = monitorEventLoopDelay({ resolution: 20 });
h.enable();
setInterval(() => {
  console.log('p99 event loop delay', h.percentile(99));
  h.reset();
}, 1000);

// Wrap a function so every call shows up as a perf entry
const slow = performance.timerify(slowFn);

// Observe GC events
new PerformanceObserver((list) =>
  list.getEntries().forEach((e) => console.log(e.name, e.duration))
).observe({ entryTypes: ['gc'] });
```

### Gotchas

- `for (const x of arr) await f(x)` is sequential. Use `Promise.all(arr.map(f))` or `p-limit` for bounded concurrency.
- `JSON.parse` on huge payloads is single-threaded main-loop work; stream with `stream-json` or offload to a Worker.
- `clinic doctor` is the triage tool — run it FIRST. It tells you if your bottleneck is CPU, event loop, GC, or I/O. Then pick the right deeper tool.
- TypedArrays (`Float64Array`) are materially faster than `Array<number>` for numeric hot loops.

---

## Python

### Defaults

```bash
# Attach live, zero code change, < 0.1% overhead — START HERE
pipx install py-spy
py-spy record -o flame.svg --pid $PID --duration 30
py-spy top --pid $PID

# Line-level CPU + memory + GPU + energy in one tool
pipx install scalene
scalene --cpu --memory prog.py
# produces HTML; shows Python vs native time per line

# Memory — Bloomberg's current best-in-class, replaces memory_profiler
pipx install memray
memray run --live prog.py                 # live TUI
memray run prog.py && memray flamegraph memray-prog.bin
memray run --trace-python-allocators prog.py

# Lowest overhead frame sampler (TUI pair)
apt install austin || pipx install austin-dist
austin -o out.austin python prog.py
austin-tui out.austin

# Timeline / Chrome tracing
pipx install viztracer
viztracer prog.py
vizviewer result.json

# Multi-threaded / asyncio clock-accurate profiler
pip install yappi
# yappi.start(); ... ; yappi.get_func_stats().print_all()

# Deterministic baseline (stdlib + visualizer)
python -m cProfile -o p.prof prog.py
snakeviz p.prof

# Per-line
pip install line_profiler
# add @profile decorator, then:
kernprof -l -v prog.py
```

### Gotchas

- `cProfile` overhead skews I/O-bound code — use `py-spy` or `austin` for those.
- `memory_profiler` is abandoned; use `memray` (or `tracemalloc` for in-process).
- Attach-mode (`py-spy --pid`, `memray attach`) needs `kernel.yama.ptrace_scope ≤ 1` (`sudo sysctl -w kernel.yama.ptrace_scope=1`).
- For `pandas` hot loops: `df.apply()` is a Python-level loop; prefer vectorized `df[col].where(...)` or pure NumPy.
- The GIL means CPU-bound work never sees >1 core without `multiprocessing` / `concurrent.futures.ProcessPoolExecutor`.

---

## C / C++

### Build flags

```
-O2 -g -fno-omit-frame-pointer -gdwarf-4     # perf + symbols
# or -O3 if your perf work targets production numbers
```

### Defaults

```bash
# Sampling + flamegraph
perf record -F 997 -g --call-graph dwarf -- ./bin
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# Valgrind suite
valgrind --tool=callgrind ./bin && kcachegrind callgrind.out.*
valgrind --tool=cachegrind ./bin
valgrind --tool=massif --pages-as-heap=yes ./bin && ms_print massif.out.*

# Heap allocation
heaptrack ./bin && heaptrack_gui heaptrack.bin.*

# gperftools
CPUPROFILE=cpu.prof LD_PRELOAD=libprofiler.so ./bin
pprof --web ./bin cpu.prof

HEAPPROFILE=heap.prof LD_PRELOAD=libtcmalloc.so ./bin
pprof --web ./bin heap.prof

# jemalloc profiling
MALLOC_CONF=prof:true,prof_active:true,lg_prof_sample:19,prof_prefix:jeprof.out ./bin
jeprof --svg ./bin jeprof.out.*.heap > heap.svg

# Tracy — compile-in frame profiler (best frame-latency visualizer)
# add Tracy client to app; run Tracy server GUI

# Intel VTune / AMD uProf
vtune -collect hotspots -r r ./bin
AMDuProfCLI collect --config tbp --output-dir r ./bin

# Micro-benchmark A/B diff with PMU counters
poop 'cmdA' 'cmdB'           # github.com/andrewrk/poop
```

### Gotchas

- `-fno-omit-frame-pointer` is essential; otherwise DWARF unwinding is the only stack source and it's slow/huge.
- `valgrind` emulates; callgrind slows 20-100x; use for attribution, not wall-clock tuning.
- `massif --pages-as-heap=yes` measures true peak RSS; the default option measures allocator heap only.
- `bpftrace -e 'profile:hz:99 /pid == PID/ { @[ustack] = count(); }' 10` is a sharp one-liner that beats setting up perf for ad-hoc sampling.

---

## Cross-language benchmarking

| Use | Tool | Command |
|-----|------|---------|
| CLI wall-clock A/B | hyperfine | `hyperfine --warmup 3 --runs 20 --export-json r.json 'cmdA' 'cmdB'` |
| HTTP open-loop | wrk2 | `wrk2 -t4 -c100 -d30s -R 5000 http://x` (constant rate → real p99) |
| HTTP scripted | k6 | `k6 run --vus 50 --duration 30s s.js` |
| HTTP Node-ergonomic | autocannon | `autocannon -c 100 -d 30 http://x` |
| HTTP constant rate | vegeta | `echo GET http://x | vegeta attack -rate=1000/s -duration=30s | vegeta report` |
| HTTP TUI | oha | `oha -n 10000 -c 100 http://x` |
| Go A/B | benchstat | `benchstat old.txt new.txt` |
| Rust A/B | criterion | `--save-baseline before / --baseline before` |
| Rust CI-stable | iai-callgrind | instruction count, zero variance |
| JS micro | mitata | sub-ns resolution |
| Python A/B | pytest-benchmark | `pytest --benchmark-only` |

**Closed vs open loop:** `wrk` is closed-loop (each virtual user waits for its response before sending the next). Under overload this *hides* p99 latency because requests pile up on the client, not the server. Use `wrk2` or `vegeta` at a fixed rate for accurate tail latency.

---

## Continuous profiling (prod)

| Tool | Source | Overhead | Ingest |
|------|--------|----------|--------|
| Pyroscope (Grafana) | eBPF + agents | < 1% | Grafana UI |
| Parca (Polar Signals) | eBPF | < 1% | pprof-native UI |
| Grafana Cloud Profiles | eBPF | < 1% | Grafana |
| Datadog Continuous Profiler | JFR-style | 1-5% | Datadog |
| Sentry Profiling | sampled | < 1% | Sentry |
| Elastic Universal Profiling | eBPF | < 1% | Kibana |

Reach for continuous profiling when: (a) bug only reproduces under prod load, (b) tail latency drifts without a clear code change, (c) you have many services and don't know which owns the p99. Do NOT use it for microbench tuning — the sampling rate is too low.

### pyroscope.ebpf (Alloy) — quickest on-prem path

```
# Alloy config fragment
pyroscope.ebpf "default" {
  forward_to = [pyroscope.write.remote.receiver]
  targets_from = discovery.process.all
}
pyroscope.write "remote" {
  endpoint { url = "http://pyroscope:4040" }
}
```
