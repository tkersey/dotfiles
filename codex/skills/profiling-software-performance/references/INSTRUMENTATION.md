# Code-Level Instrumentation Patterns

> How to wire measurement into the code so profilers actually attribute time correctly, and so you can ship perf dashboards without tearing the code apart every time.

## Contents

1. [The three layers](#the-three-layers)
2. [Sentinel frames — force flamegraph attribution](#sentinel-frames--force-flamegraph-attribution)
3. [Spans & structured traces](#spans--structured-traces)
4. [Histograms & metrics](#histograms--metrics)
5. [Structured logging contract](#structured-logging-contract)
6. [Cache hit counters (for the RAM tradeoff table)](#cache-hit-counters-for-the-ram-tradeoff-table)
7. [Per-language snippets](#per-language-snippets)
8. [Gating behind an env flag](#gating-behind-an-env-flag)
9. [Custom per-pipeline profile snapshots](#custom-per-pipeline-profile-snapshots)
10. [When to use OpenTelemetry vs handwritten](#when-to-use-opentelemetry-vs-handwritten)

---

## The three layers

| Layer | Purpose | Cost when disabled |
|-------|---------|--------------------|
| Sentinel frames | Attribute sampler output to logical stages | ~0 (empty fn, inlined if requested) |
| Spans | Deterministic per-call timing, stack shape | 10-100ns per span |
| Histograms | Ship tail latency to prod dashboards | 50-200ns per record |

You want all three, layered. The sampler is cheap and coarse; histograms are cheap and aggregate; spans are expensive and deterministic.

---

## Sentinel frames — force flamegraph attribution

When the work is `parse → compile → plan → execute → commit`, add `#[inline(never)]` no-op functions named `_profile_<stage>` so the flame graph shows each stage as a distinct bar.

Rust:

```rust
#[inline(never)] pub fn _profile_parse()    { std::hint::black_box(()); }
#[inline(never)] pub fn _profile_compile()  { std::hint::black_box(()); }
#[inline(never)] pub fn _profile_plan()     { std::hint::black_box(()); }
#[inline(never)] pub fn _profile_execute()  { std::hint::black_box(()); }
#[inline(never)] pub fn _profile_btree_seek() { std::hint::black_box(()); }

fn run_query(sql: &str) -> Result<Rows> {
    _profile_parse();    let ast  = parse(sql)?;
    _profile_compile();  let prog = compile(ast)?;
    _profile_plan();     let plan = plan(prog)?;
    _profile_execute();  let rows = execute(plan)?;
    Ok(rows)
}
```

Go:
```go
//go:noinline
func _profile_stage_parse()    {}
//go:noinline
func _profile_stage_compile()  {}

func Run(sql string) (Rows, error) {
    _profile_stage_parse()
    ast, err := parse(sql); if err != nil { return nil, err }
    _profile_stage_compile()
    prog, err := compile(ast); if err != nil { return nil, err }
    ...
}
```

C/C++:
```c
__attribute__((noinline)) void _profile_parse(void)   { __asm__ volatile(""); }
__attribute__((noinline)) void _profile_compile(void) { __asm__ volatile(""); }
```

Gotcha: LTO ("thin" is fine, "fat" isn't always) may still inline these despite the hint. For truly critical cases, put the sentinel in a separate crate/object so the linker can't fuse. The `volatile` asm / `black_box` prevents dead-code elimination.

---

## Spans & structured traces

### Rust — `tracing`

```rust
use tracing::{instrument, info_span};

#[instrument(skip_all, fields(batch_size = batch.len()))]
pub fn write_message_batch(batch: &[Message]) -> Result<()> {
    let _span = info_span!("archive_batch.fsync_group").entered();
    ...
}
```

Subscriber that emits Chrome trace JSON (`traceEvents` — `chrome://tracing` / Perfetto compatible):
```rust
use tracing_chrome::ChromeLayerBuilder;
use tracing_subscriber::prelude::*;

let (chrome_layer, _guard) = ChromeLayerBuilder::new()
    .file(std::env::var("TRACE_FILE").unwrap_or("/tmp/trace.json".into()))
    .include_args(true)
    .build();
tracing_subscriber::registry().with(chrome_layer).init();
```
The resulting trace JSON opens in `chrome://tracing` / Perfetto / speedscope.

### Go

```go
import (
    "runtime/trace"
    "context"
)

func WriteBatch(ctx context.Context, batch []Message) error {
    ctx, task := trace.NewTask(ctx, "write_batch")
    defer task.End()
    defer trace.StartRegion(ctx, "fsync_group").End()
    ...
}
```
Dump: `curl -o trace.out http://host:6060/debug/pprof/trace?seconds=5; go tool trace trace.out`.

### Node

```javascript
import { performance, PerformanceObserver } from 'perf_hooks';
const obs = new PerformanceObserver(list =>
  list.getEntries().forEach(e => logger.info('span', { name: e.name, dur_ms: e.duration }))
);
obs.observe({ entryTypes: ['measure'] });

performance.mark('parse:start');
parse();
performance.mark('parse:end');
performance.measure('parse', 'parse:start', 'parse:end');
```

### Python

```python
import viztracer, time
with viztracer.log_sparse(name='parse'):
    parse(sql)
```
Or write to Chrome trace directly via `viztracer.VizTracer()`.

### C/C++ — Tracy

```cpp
#include <tracy/Tracy.hpp>
void run() {
    ZoneScopedN("parse");
    parse();
    { ZoneScopedN("compile"); compile(); }
}
```

---

## Histograms & metrics

Use `hdrhistogram` (any language) for latency — it's log-linear so tails don't cost absurd memory, and quantile queries are O(1).

### Rust

```rust
use metrics::{counter, histogram};
use hdrhistogram::Histogram;

histogram!("archive.write_batch_ms", duration.as_secs_f64() * 1000.0, "batch_size" => batch.len().to_string());
counter!("archive.write_batch_total", 1, "result" => if ok { "ok" } else { "err" });

// manual hdr for in-process tail ship-out
let mut h = Histogram::<u64>::new_with_bounds(1, 60_000_000, 3).unwrap();
h.record(elapsed.as_micros() as u64).unwrap();
tracing::info!(target: "perf.profile.span_summary",
    span_name = "archive_batch.write_messages",
    count = h.len(),
    p50 = h.value_at_quantile(0.5),
    p95 = h.value_at_quantile(0.95),
    p99 = h.value_at_quantile(0.99),
    p99_9 = h.value_at_quantile(0.999),
    max = h.max());
```

Ship to Prometheus: `metrics-exporter-prometheus` crate. Ship to OTLP: `metrics-exporter-otel`.

### Go

```go
import "github.com/prometheus/client_golang/prometheus"
var batchHist = prometheus.NewHistogramVec(
    prometheus.HistogramOpts{Name: "write_batch_ms", Buckets: prometheus.ExponentialBuckets(1, 2, 16)},
    []string{"size_bucket"})

start := time.Now()
defer func(){ batchHist.WithLabelValues(sizeBucket).Observe(float64(time.Since(start).Milliseconds())) }()
```

### Node

```javascript
import { Summary } from 'prom-client';
const batch = new Summary({ name: 'write_batch_ms', labelNames: ['size'], percentiles: [0.5,0.95,0.99,0.999] });
const end = batch.labels(sz).startTimer();
try { await write(batch); } finally { end(); }
```

### Python

```python
from prometheus_client import Histogram
H = Histogram('write_batch_ms', 'Batch write latency', buckets=(1,2,5,10,25,50,100,250,500,1000,2500,5000))
with H.time():
    write_batch(batch)
```

---

## Structured logging contract

One uniform schema across all your projects means the pipeline that builds hotspot tables can ingest any of them:

```
Target                               Fields
────────────────────────────────────────────────────────────────────
perf.profile.run_start               run_id, scenario, toolchain_version, hardware_json
perf.profile.sample_collected        run_id, sample_count, duration_sec
perf.profile.span_summary            run_id, span_name, cumulative_us, count, p50, p95, p99, p99_9, max
perf.profile.hypothesis_evaluated    run_id, name, verdict (supports|rejects), evidence
perf.profile.scaling_law             run_id, axis, sizes[], p95s[], verdict
perf.profile.run_complete            run_id, duration_sec, artifacts_written[]
```

A simple renderer walks the log file and emits `hotspot_table.md`, `scaling_law.md`, `hypothesis.md`. See `ARTIFACTS.md` for the templates.

Match these names exactly — the ingestion side depends on it.

---

## Cache hit counters (for the RAM tradeoff table)

When you add a cache from the RAM-for-speed table (see `IO-AND-TRADEOFFS.md`), instrument it so next round's profile proves whether it paid off:

```rust
struct Cache<K, V> {
    inner: LruCache<K, V>,
    hits: AtomicU64,
    misses: AtomicU64,
    evictions: AtomicU64,
}

impl<K: Hash + Eq, V: Clone> Cache<K, V> {
    pub fn get_or_insert_with(&mut self, k: K, f: impl FnOnce() -> V) -> V {
        if let Some(v) = self.inner.get(&k) {
            self.hits.fetch_add(1, Ordering::Relaxed);
            return v.clone();
        }
        self.misses.fetch_add(1, Ordering::Relaxed);
        let v = f();
        if self.inner.put(k, v.clone()).is_some() {
            self.evictions.fetch_add(1, Ordering::Relaxed);
        }
        v
    }
    pub fn snapshot(&self) -> CacheStats {
        let h = self.hits.load(Ordering::Relaxed);
        let m = self.misses.load(Ordering::Relaxed);
        let total = h + m;
        CacheStats {
            hits: h, misses: m,
            evictions: self.evictions.load(Ordering::Relaxed),
            hit_rate_bps: if total > 0 { ((h * 10_000) / total) as u32 } else { 0 }
        }
    }
}
```

Emit per-run via `perf.profile.span_summary` with `span_name = "cache.<name>"` and `p50/p95` = actual get() latency, plus a `hits/misses/evictions/hit_rate_bps` row per cache. A reusable **Baseline Reuse Ledger** format:

```
| Cache | supported | hits | misses | hit_rate_bps | target |
|-------|-----------|------|--------|--------------|--------|
| statement_parse_cache | true | 100 | 62 | 6173 | J4 |
| cursor_frame_reuse    | true | 100 | 1  | 9901 | J7 |
```

---

## Per-language snippets

### Rust — `#[tracing::instrument]` sugar + `hdrhistogram` + `pprof-rs`

```rust
use pprof::ProfilerGuardBuilder;

let guard = ProfilerGuardBuilder::default()
    .frequency(997)
    .blocklist(&["libc", "libgcc", "pthread", "vdso"])
    .build()?;

// ... do work ...

if let Ok(report) = guard.report().build() {
    let file = std::fs::File::create("cpu.pprof")?;
    report.pprof()?.encode(&mut std::io::BufWriter::new(file))?;   // analyze with `go tool pprof`
    let file = std::fs::File::create("cpu.svg")?;
    report.flamegraph(file)?;
}
```

### Go — handy function-scope helper

```go
func trackHot(name string) func() {
    start := time.Now()
    return func(){ metrics.Observe(name, time.Since(start)) }
}
func Serve(req *Req) *Resp {
    defer trackHot("serve_total")()
    ...
}
```

### Node — high-res hot-loop timing

```javascript
const now = () => Number(process.hrtime.bigint()) / 1e6;  // ms
const hist = [];
for (const item of batch) {
    const t = now();
    process(item);
    hist.push(now() - t);
}
hist.sort((a, b) => a - b);
const q = p => hist[Math.floor(hist.length * p)];
logger.info('span', { span_name: 'process', p50: q(0.5), p95: q(0.95), p99: q(0.99) });
```

### Python — `time.perf_counter_ns` hot loop

```python
from time import perf_counter_ns as ns
from hdrh.histogram import HdrHistogram
h = HdrHistogram(1, 60_000_000, 3)
for m in batch:
    t = ns()
    process(m)
    h.record_value((ns() - t) // 1000)  # µs
log.info('span', span_name='process', p50=h.get_value_at_percentile(50),
         p95=h.get_value_at_percentile(95), p99=h.get_value_at_percentile(99))
```

---

## Gating behind an env flag

Instrumentation that costs any real overhead goes behind a runtime flag so production pays nothing by default but operators can flip it on.

```rust
fn profile_enabled() -> bool {
    static ENABLED: std::sync::OnceLock<bool> = std::sync::OnceLock::new();
    *ENABLED.get_or_init(|| std::env::var("MYAPP_PROFILE").is_ok())
}

pub fn record_span(name: &str, dur: Duration) {
    if !profile_enabled() { return; }
    // ... record to hdrhistogram, emit tracing event ...
}
```

Document the profiling env flag name in your project's `docs/PROFILING.md` so operators aren't guessing.

---

## Custom per-pipeline profile snapshots

When pipeline stages are the primary optimization axis, build a lightweight binary snapshot you can materialize per run, such as a `HotPathProfileSnapshot`.

```rust
#[derive(Default, Clone)]
pub struct HotPathSnapshot {
    pub parse_ns: u64,
    pub compile_ns: u64,
    pub plan_ns: u64,
    pub execute_ns: u64,
    pub btree_seek_ns: u64,
    pub btree_seek_count: u64,
    pub record_decode_ns: u64,
    pub record_decode_count: u64,
    pub alloc_bytes: u64,
    pub cache_hits: u32, pub cache_misses: u32,
}

thread_local! {
    static SNAP: std::cell::RefCell<HotPathSnapshot> = Default::default();
}

pub fn reset() { SNAP.with(|s| *s.borrow_mut() = Default::default()); }
pub fn snapshot() -> HotPathSnapshot { SNAP.with(|s| s.borrow().clone()) }

pub fn add_parse_ns(ns: u64)   { SNAP.with(|s| s.borrow_mut().parse_ns   += ns); }
pub fn add_compile_ns(ns: u64) { SNAP.with(|s| s.borrow_mut().compile_ns += ns); }
// ...

pub fn write_artifacts(snap: &HotPathSnapshot, dir: &Path) -> std::io::Result<()> {
    serde_json::to_writer_pretty(File::create(dir.join("hotpath.json"))?, snap)?;
    std::fs::write(dir.join("summary.md"), render_markdown(snap))?;
    Ok(())
}
```

Call `reset()` between scenario runs, `snapshot()` + `write_artifacts()` at the end. The result is a tiny, deterministic, per-subsystem breakdown the next skill (`extreme-software-optimization`) can score.

---

## When to use OpenTelemetry vs handwritten

**Use OpenTelemetry (`opentelemetry-*` crates / SDKs) when:**
- Request flows cross services (spans need to propagate via W3C trace context).
- You want a single vendor-neutral export format and can wire Jaeger/Tempo/Datadog behind it.
- You already have OTel in place for logs/metrics.

**Use handwritten instrumentation when:**
- Single-process CPU-bound code. OTel adds ~microseconds per span; that's noise in request handlers and catastrophic inside hot loops.
- You want Chrome trace / Perfetto output for fast visual analysis. `tracing-chrome` is one dep vs. the OTel collector.
- You're writing numeric benchmarks — use `criterion` / `iai-callgrind`, not OTel.

**Hybrid (common):** OTel at the request boundary (HTTP/gRPC handler entry), handwritten spans + histograms inside hot paths, bridge hotspot data as OTel span attributes so one tool shows the whole story. OTel 1.x now supports profile signals for linking flame graphs to spans.

---

## Checklist before running a profile

- [ ] Sentinel frames present for each pipeline stage
- [ ] `#[tracing::instrument]` / equivalent on hot APIs
- [ ] Histograms gated behind env flag emit `perf.profile.span_summary`
- [ ] Cache hit/miss counters exposed if any caches exist
- [ ] Chrome trace / span JSON writes to `tests/artifacts/perf/<run-id>/<scenario>_spans.json`
- [ ] Instrumentation overhead measured — if > 1% of baseline, regate and re-measure
