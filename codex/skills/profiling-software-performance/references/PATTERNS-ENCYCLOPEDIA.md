# Symptom → Diagnosis → Fix Encyclopedia

> A lookup table from "what the user is complaining about" → "what to measure" → "what the fix probably is." Use as a first-pass before deep profiling; each entry links to the deeper reference.

## Contents

1. [Latency shape symptoms](#latency-shape-symptoms)
2. [Throughput symptoms](#throughput-symptoms)
3. [Memory symptoms](#memory-symptoms)
4. [I/O symptoms](#io-symptoms)
5. [Concurrency symptoms](#concurrency-symptoms)
6. [Cold-vs-warm symptoms](#cold-vs-warm-symptoms)
7. [Environment / deployment symptoms](#environment--deployment-symptoms)
8. [Framework-specific symptoms](#framework-specific-symptoms)
9. [How to read this table](#how-to-read-this-table)

---

## Latency shape symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **p99 is 10× p50, p95 is 2× p50** | Tail events: GC, lock, I/O, thermal throttle, context switch burst | Off-CPU flamegraph (Brendan Gregg); `perf sched`; `biolatency-bpfcc`; GC trace | Fix the tail-producing event, not the median path |
| **p50 and p99 scaled together (2×)** | Steady pressure; working-set overflow or code regression | On-CPU flame diff; sampling at higher frequency (`-F 997`); `git bisect` | Usually a code change (vs environment) — bisect |
| **p99 spikes are periodic (every N seconds)** | Scheduled job, GC cycle, compaction, page-cache writeback, metrics flush | `top -H` + timestamp; `GODEBUG=gctrace=1`; log with microsecond timestamps | Stagger, rate-limit, or move off-critical-path |
| **p99 is stable until load rises, then explodes** | Contention knee; queue saturation; open-loop vs closed-loop lie | Scaling-law harness (`scaling_law.md`); wrk2/k6/vegeta at fixed rate | Identify knee, cut contention or add backpressure |
| **First call after idle is slow, then fine** | JIT / AOT warmup, connection pool lazy-init, cache cold | Measure first-call-after-idle separately from steady-state; `performance.timerify` for Node; `cargo bench --warm-up-time` | Pre-warm, connection-keepalive, `vmtouch`, pgbouncer |
| **Bimodal histogram (two peaks)** | Fast and slow paths; fsync hit vs miss; cache hit vs miss | `biolatency-bpfcc -m 10` (millisecond buckets); `hdrhistogram`'s value_at_percentile across buckets | Collapse the slow path (cache, coalesce) or separate them at the API level |
| **Tail is correlated with tracing enabled** | Instrumentation overhead; `tracing-chrome` unbuffered writes | Disable instrumentation, re-measure; `strace -c` on the binary with tracing vs without | Gate instrumentation, buffer-writer, async-subscriber |
| **"Feels fast on dev, slow in prod"** | Data shape, scale, concurrency, storage, network differ; prod cache cold | Capture prod fingerprint + workload; compare to dev fingerprint; continuous profiler (Pyroscope/Parca) in prod | Repro locally with prod-size data; or profile in prod |
| **"Used to be fast, now slow"** | Regression (code, dependency, kernel, governor, thermal) | Fingerprint diff (first!); then git bisect with bench as the test; dep lockfile bisect | Bisect + A/B the offending commit |

---

## Throughput symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **Throughput plateaus as concurrency rises (flat)** | Contention: mutex, channel, DB connection pool, single shared writer | Scaling-law harness; tokio-console for async; `perf lock`; `pprof mutex` (Go) | Shard, lock-free, read-mostly → RwLock, connection pool size |
| **Throughput plateaus at 1-thread single-core ceiling** | Code is single-threaded; no parallelism | CPU% per core; check `num_cpus::get()` vs active threads | `rayon`, worker pool, `tokio::spawn` per unit-of-work |
| **Throughput drops past a certain concurrency** | Lock thrash (superlinear), context-switch storm, cache-line bouncing, allocator contention | Scaling table showing superlinear growth; `perf stat -e context-switches,cs`; `perf c2c` (cache coherence) | Reduce cross-thread data sharing, `jemalloc`/`mimalloc`, false-sharing padding |
| **Throughput drops over time (seconds/minutes)** | Memory bloat, cache pollution, connection leak, file-descriptor exhaustion, WAL growth | Long-running run; RSS and FD trace over time; `lsof -p <pid>` snapshots | Leak fix, periodic reset, WAL compaction |
| **Throughput per core drops as you add cores** | Memory-bandwidth bound, shared cache contention, NUMA effects | `perf stat -e cycles,instructions,cache-misses,LLC-load-misses,LLC-loads`; compute IPC and miss rate | SoA layout, prefetching, NUMA-aware allocation (`numactl --localalloc`) |
| **"I added threads and got slower"** | Amdahl / contention / allocator / false sharing | `rayon` with `install_global_handler`; check whether the hot loop has thread-local state | Thread-local everything possible; stripe allocator (jemalloc arenas) |

---

## Memory symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **Peak RSS grows unbounded** | Leak (strong ref cycle, sender not dropped, global Vec push) | `heaptrack` with leak view; `memray --live`; `valgrind --leak-check` | Fix reference cycle, drop explicitly, bounded cache |
| **Peak RSS grows then stabilizes (high)** | Caches warming, allocator hold-back, bounded LRU saturated | `smaps_rollup` Rss/Pss/Uss diff; `MALLOC_CONF=stats_print:true`; allocator-specific diag | Tune LRU size; `jemalloc` dirty page decay (`MALLOC_CONF=dirty_decay_ms:1000`) |
| **RSS grows slowly over days** | Fragmentation or cache without a bound; slow leak | Allocator profile at multiple points; track per-struct alloc count over time | Switch allocator (mimalloc is less fragmenting); bound caches |
| **Peak RSS > heap high-water (from DHAT)** | Kernel is holding pages we "freed"; or mmap region is in RSS | `smaps_rollup` vs `dhat-heap.json` size; `MALLOC_CONF=muzzy_decay_ms:0` forces return | Tune allocator page decay; use `madvise(DONTNEED)` on large unused regions |
| **Alloc rate is huge (>1 GB/s) but RSS stable** | Churn: short-lived allocations; allocator recycling fine but CPU cost is real | DHAT `total` bytes vs `max_blocks_live`; allocator CPU time in flame | Object pool, `bumpalo` arena, buffer reuse |
| **Peak RSS different on same run** | ASLR / page-cache / randomness; or non-determinism in workload | Compare `/proc/<pid>/smaps_rollup` under `taskset` isolation | Pin input, check for randomness in the code |
| **Heap profile shows 99% in one call site** | Obvious: optimize that site | DHAT call-site ranking, viewer (dh_view.html) | Buffer reuse, `SmallVec` on stack, arena |
| **Heap profile shows diffuse allocations (no hot site)** | Many small allocs everywhere; language-level (boxing, interface{}, autoboxing) | `GODEBUG=allocfreetrace=1`; escape analysis `-gcflags='all=-m=2'`; Rust `cargo +nightly build -Z print-type-sizes` | Language-specific: avoid `Box<dyn>`, avoid `any`, avoid autoboxing; use generics |

---

## I/O symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **`%CPU < 80%` but "CPU-bound"** | You're not CPU-bound — waiting on I/O or lock | `/usr/bin/time -v`; `vmstat 1 | awk '{print $16}'` for wa%; off-CPU flame | Follow the I/O trail; see IO-AND-TRADEOFFS.md §"First — is this actually I/O?" |
| **`iostat %util` close to 100%** | Disk is saturated | `iostat -xm 1` for r/s w/s await; `biolatency-bpfcc` | Batch writes, coalesce, move to faster storage, add cache |
| **High `await` with low r/s+w/s** | Queue saturation or slow media | `iostat -xm 1` `avgqu-sz`; `nvme smart-log` for SSD wear | Lower queue depth, check for SSD wear-out, different scheduler |
| **Latency bimodal at 3ms and 80ms** | fsync hit-vs-miss; check fsync cost | `biolatency-bpfcc -m 10` to see buckets; `strace -c -e fsync` ranks cost | Batch fsync, fdatasync-over-fsync, group commit |
| **Latency scales with batch size of writes, not reads** | fsync cost or write amplification | `fio --fsync=1` ceiling; compare to app; cross-ref fsync-bound triage (PROMPTS.md) | Coalesce writes, move to WAL, use PLP NVMe |
| **Directory scan slow, becomes fast on 2nd run** | Cold dentry/inode cache | `vmtouch /path`; `sudo sysctl vm.vfs_cache_pressure=50` | Pre-warm, reduce scans (index, content-addressed), shard dirs |
| **`find` takes minutes, file count is high** | Small-file pathology — too many inodes | `df -i`; `find | wc -l` | Bundle (SQLite, tar), shard, content-addressed |
| **btrfs file `filefrag` shows 1000+ extents** | CoW fragmentation from small random writes | `filefrag -v`; `btrfs filesystem usage` | `chattr +C` on DB files (before first write), `autodefrag`, targeted defrag |
| **Writes fast initially, slow after GB** | WAL/journal pressure, checkpoint not running, compaction backed up | `iostat %util` over time; DB-specific stats | Tune checkpoint/commit interval, WAL autocheckpoint |
| **Network round trips seem to multiply** | N+1 pattern at HTTP / gRPC / DB layer | `tcpdump`; `strace -e connect,sendto,recvfrom`; app-level trace | Batch queries, GraphQL/DataLoader pattern, prefetch |
| **TLS handshake dominates** | Short-lived connections; no session resumption | `curl -w "@fmt"` per-phase; `ss -ti` RTT | Connection pool, TLS session resumption, TLS 1.3, 0-RTT |

---

## Concurrency symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **`top -H` shows one thread at 100%, others idle** | Serialized work; single shared lock; main thread doing everything | per-thread profile; `perf sched`; code review at the shared-state boundary | Shard, work-steal (rayon), split the shared state |
| **Lots of threads all at ~50%** | Contention (locks, channel, allocator) | `perf lock contention -ab sleep 10`; `pprof mutex`; tokio-console | Lock-free ds, shard, `parking_lot`, `dashmap` |
| **Tokio task hangs, no CPU used** | Await holding lock; deadlock; missed waker | `tokio-console` long-poll warnings; off-CPU flame → `futex_wait` | Drop guard before `.await`; `parking_lot::RwLock` doesn't cross await safely |
| **"if let Some(x) = lock.lock().take()" hangs** | Lock guard lifetime = if-let body; inner call re-locks | code grep for guard-as-scrutinee pattern; see Case Study 5 | Extract to `let val = ... .take(); if let Some(v) = val { ... }` |
| **Unexplained occasional stall** | GC pause (Go, Java, Python); futex, page fault, thermal | `GODEBUG=gctrace=1`; `perf record --call-graph dwarf` with offcputime | GC tuning; avoid large GC-visible graphs; offload to native |
| **Cross-core invalidations hot** | False sharing; cacheline ping-pong | `perf c2c record && perf c2c report`; hardware counters `LLC-load-misses` | Cacheline padding (`#[repr(align(64))]`), move state to thread-local |

---

## Cold-vs-warm symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **Cold start: 5s, warm: 50ms** | JIT, connection pool, cache fill, mmap page-in | first-request vs steady-state measured separately | Pre-warm at deploy (AOT cache, prewarm endpoint, `pg_prewarm`) |
| **First N requests to a fresh process are slow** | JIT (V8, JVM), TLS warmup, AOT cache cold | `node --prof-process`; JFR startup flight | Pre-compile, pre-connect, pre-load |
| **Cold run is fast, 2nd run is fast, 3rd is slow** | Cache eviction, fragmentation, or a reporting artifact | Cold cache checklist: `drop_caches` before every run; consistent warmup | Pick cold OR warm, document which |
| **"My benchmark always says the first run is faster"** | Filesystem metadata cached from earlier `cargo build`; or thermal | drop_caches; `time cargo clean && cargo build`; check CPU freq during run | Consistent warmup; drop caches consistently; pin CPU freq |
| **Sporadic slow run that correlates with disk activity** | Neighbor workload (indexer, backup); kernel writeback | `iotop -oPa`; `systemd-cgtop`; `atop` with process history | Isolate machine or time-window the bench; pin CPU with `taskset` |

---

## Environment / deployment symptoms

| Symptom | Most likely cause | Diagnostic | Typical fix class |
|---------|-------------------|------------|-------------------|
| **Bench passes locally, fails in CI** | CI runner has different CPU, less RAM, shared host, different kernel | fingerprint.json diff; run bench on both; document runner in CI-REGRESSION-GATES.md §Runner match | Match runner tier (GitHub large runner; dedicated self-hosted); relax budget for CI class |
| **Prod is slower than staging with identical code** | Prod data is larger, prod clients more, prod cache cold, prod traffic shape different | Continuous profiler (Pyroscope/Parca) in prod; compare prod trace to staging | Reproduce prod data locally; profile in prod; or accept staging-as-proxy with budget multiplier |
| **Docker is N% slower than bare metal** | cgroup limits, THP, network namespace, overlayfs | `docker stats`; `cat /sys/fs/cgroup/cpu.max`; compare bare-metal fingerprint to container fingerprint | Raise limits, host-networking, bind-mount vs overlay |
| **Kubernetes pod is erratic** | Noisy neighbor, CPU quota throttling, page cache steal | `kubectl top pod`; `cpu_throttled_seconds_total` metric; `kubectl describe node` for resource pressure | CPU pinning (static CPU manager), guaranteed QoS class, raise limits |
| **Lambda / serverless cold start** | Cold container, JIT cold, mmap cold | AWS Lambda `init_duration_ms` in CloudWatch; Vercel Function cold-start metric | Provisioned concurrency; smaller deployment; move to Rust / Go for faster starts |

---

## Framework-specific symptoms

### Rust async / Tokio

| Symptom | Likely cause | Diagnostic | Fix |
|---------|--------------|------------|-----|
| "Task spawned but doesn't progress" | Runtime saturated; missed waker | tokio-console LongPoll warnings | Increase worker threads, find blocking call in async context |
| Awaiting a mutex across `.await` | Bad pattern | clippy `await_holding_lock` | Use `tokio::sync::Mutex` or drop guard before `.await` |
| `spawn_blocking` slow | Blocking pool saturated | tokio-console blocking-pool metrics | Resize pool (`max_blocking_threads`); or move to dedicated threadpool |

### Go

| Symptom | Likely cause | Diagnostic | Fix |
|---------|--------------|------------|-----|
| GC takes 50+ ms | Huge live heap | `GODEBUG=gctrace=1`; heap profile | Reduce allocs, use `sync.Pool`, pre-allocate slices |
| Goroutines stuck | Channel deadlock, select without default | `go tool pprof /debug/pprof/goroutine`; `goroutine` dump | Review channel patterns, add timeouts |
| Mutex/block profile empty | Rates not enabled | `runtime.SetMutexProfileFraction(5); runtime.SetBlockProfileRate(10_000)` | Enable at startup |

### Node / TypeScript

| Symptom | Likely cause | Diagnostic | Fix |
|---------|--------------|------------|-----|
| Event loop lag spiking | Sync CPU work in handlers; `JSON.parse` of huge payloads | `monitorEventLoopDelay`; `clinic doctor` | Move CPU to Worker, stream-parse, cache JSON |
| Promise chain stalls | `await` in loop; sequential | Code grep for `for .. await`; `clinic bubbleprof` | `Promise.all(map(fn))` or `p-limit` |
| Memory grows slowly | Closure capture, module-level cache without bound | `--heap-prof`; Chrome DevTools heap snapshot diff | Bounded Map/WeakMap; drop listeners |

### Python

| Symptom | Likely cause | Diagnostic | Fix |
|---------|--------------|------------|-----|
| GIL serialization | CPU-bound, single-process | `py-spy top` — see % in GIL | `multiprocessing`, Cython, or move CPU to native |
| `pandas` slow | `.apply` is a Python loop | `scalene`; `%timeit`; `pandas.DataFrame.info(memory_usage='deep')` | Vectorize with `np.where`, `df[col].values`, or `polars` |
| Memory grows per request | Closure capture; global Dict | `memray run --trace-python-allocators`; `objgraph.show_growth()` | Bounded dict; `WeakValueDictionary` |

### SQLite / Postgres / MySQL

| Symptom | Likely cause | Diagnostic | Fix |
|---------|--------------|------------|-----|
| Query p99 spikes | Query-plan flip; cold buffer pool | `EXPLAIN (ANALYZE, BUFFERS)`; `pg_stat_statements` | Plan hints, pinning, pre-warm |
| Writes slow under load | WAL contention, checkpoint pressure | `pg_stat_wal`; `checkpoint_completion_target` | Tune checkpoint, increase WAL size |
| Reads slow on hot table | Seq scan, missing index | `EXPLAIN`; index hints | Add index; verify with `EXPLAIN (ANALYZE, BUFFERS)` |

See DATABASE-PROFILING.md for deeper coverage.

---

## How to read this table

1. **Find your symptom row.** If unsure, start at the top of the section.
2. **Confirm the diagnostic.** Run it; compare actual to "most likely cause."
3. **If the diagnostic matches**, apply the fix class. Link to the deep reference for how-to.
4. **If it doesn't match**, look one row down (or sideways) — symptoms often overlap.

This encyclopedia is the 80% case. The deep references cover the 20%.

### Priority order when multiple symptoms overlap

When a system exhibits symptoms from 2+ rows (e.g., "p99 spikes" AND "RSS grows"):

1. Fix **leaks / unbounded growth first** — they destabilize measurements.
2. Fix **contention second** — it distorts percentiles across the whole distribution.
3. Fix **tail-producing events third** (GC, fsync, context switches).
4. Fix **steady-state work last** — it's the most measurable and most isolated.

This order also happens to match difficulty-to-measure: leaks are obvious in `smaps_rollup`; contention requires tokio-console or `perf lock`; GC requires `gctrace`; steady-state needs flamegraphs and spans.

---

## When the encyclopedia doesn't help

- Write a new row when you solve a symptom not listed here.
- Apply `◊ Paradox-Hunt` (OPERATOR-CARDS.md) when two rows seem to match but imply different fixes.
- Apply `⟂ Transpose` when the symptom is workload-specific — maybe the symptom changes when you change the axis.
- Escalate to exotic CS techniques when the symptom doesn't match anything here — cache-oblivious layouts, sublinear sketches, semiring generalizations, randomized approximations, concurrent research algorithms. See PROMPTS.md §"Escalation — stuck after 3 rounds" for the structured path.
