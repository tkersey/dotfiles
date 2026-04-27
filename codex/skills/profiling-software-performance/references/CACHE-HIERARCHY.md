# The Memory Hierarchy — Reasoning About Cache, TLB, and Bandwidth

> The gap between L1 cache and DRAM is ~100×. Between DRAM and NVMe ~100×. Between NVMe and the network ~100×. Understanding these gaps lets you reason about "what's the ceiling" when a profiler says "CPU is 50% used."

## Contents

1. [The ratios you should memorize](#the-ratios-you-should-memorize)
2. [Cache-miss profiling tools](#cache-miss-profiling-tools)
3. [TLB pressure and huge pages](#tlb-pressure-and-huge-pages)
4. [Data layout: AoS vs SoA, cacheline padding, false sharing](#data-layout-aos-vs-soa-cacheline-padding-false-sharing)
5. [Memory bandwidth ceilings](#memory-bandwidth-ceilings)
6. [NUMA effects](#numa-effects)
7. [Applying this to Rust / C++ / Go data structures](#applying-this-to-rust--c--go-data-structures)
8. [Prefetching](#prefetching)
9. [Practical checklist](#practical-checklist)

---

## The ratios you should memorize

Ballpark latencies (modern x86 server, 2020s):

```
L1 cache hit                      ~1 ns        1-4 cycles
L2 cache hit                      ~3 ns        ~12 cycles
L3 cache hit                      ~12 ns       ~40 cycles
DRAM (local)                      ~80-120 ns   ~250 cycles
DRAM (remote NUMA)                ~150-200 ns  ~500 cycles
NVMe SSD (4 KiB read)             ~50-100 µs   ~1000× DRAM
Network (local RTT)               ~100-500 µs  ~10000× DRAM
Network (cross-region)            ~20-100 ms
Disk rotational seek              ~5-10 ms     (legacy — rarely encountered 2025+)
fsync (durable write)             ~50 µs-5 ms  varies with storage
```

Throughput ceilings (single socket, 2020s server):

```
L1 throughput                     ~1 TB/s per core   (loads only)
L2 throughput                     ~500 GB/s per core
L3 throughput                     ~300 GB/s per CPU
DRAM bandwidth                    ~100-400 GB/s per socket (DDR5 wider)
PCIe 4.0 x16                      ~32 GB/s unidirectional
NVMe (Gen4 x4)                    ~7 GB/s sequential; ~1M IOPS random 4K
10 GbE                            ~1.25 GB/s
100 GbE                           ~12.5 GB/s
```

**The memorize-it rule**: each level of the hierarchy is roughly 10-100× slower than the one above. If your profiler says you're "memory bound" but your working set should fit in L2, something else is going on (false sharing, indirect access pattern, prefetcher defeat).

---

## Cache-miss profiling tools

### `perf stat -e` — hardware counters

```bash
perf stat -e cycles,instructions,cache-references,cache-misses,\
L1-dcache-loads,L1-dcache-load-misses,\
LLC-loads,LLC-load-misses,\
dTLB-loads,dTLB-load-misses \
./bin args

# Output (example):
#   123,456,789 cycles
#    87,654,321 instructions        # 0.71 IPC
#     5,432,100 cache-references
#       234,567 cache-misses        # 4.32% of cache-refs
#    45,678,901 L1-dcache-loads
#       987,654 L1-dcache-load-misses  # 2.16% of L1 loads
#       123,456 LLC-loads
#        45,678 LLC-load-misses     # 37% of LLC loads
#     2,345,678 dTLB-loads
#        12,345 dTLB-load-misses    # 0.53% of dTLB loads
```

Interpret:
- **IPC (instructions per cycle)**: < 1.0 suggests stalls (memory, branch miss). Modern Intel/AMD chips can do IPC > 3 for compute-bound code.
- **L1 miss rate > 5%**: working set doesn't fit in L1 (32 KiB typical). Consider blocking / tiling.
- **LLC miss rate > 20%**: working set doesn't fit in L3 (32-128 MiB). Going to DRAM.
- **dTLB miss rate > 1%**: large sparse memory access. Huge pages may help.

### `perf c2c` — cache coherence profiler

Finds false sharing. On multicore, if thread A writes to `obj.counter_a` and thread B writes to `obj.counter_b`, both fields share a cacheline → ping-pong.

```bash
sudo perf c2c record -a -- sleep 30
sudo perf c2c report
```

Look for "HITM" (Hit Modified) events — lines showing one core reading a cacheline that another core modified. High HITM rate = false sharing or true contention.

### `valgrind --tool=cachegrind`

```bash
valgrind --tool=cachegrind --cache-sim=yes ./bin args
cg_annotate cachegrind.out.*
```

Simulated cache (not real hardware counters). Slow (~50× overhead) but deterministic and attributable per-line. Use on small inputs.

### `likwid` (Linux, Intel/AMD)

```bash
likwid-perfctr -C 0-3 -g MEM ./bin args
# Groups: FLOPS_DP, MEM, CACHE, TLB, L2, L3, UNCORE_MEM, ...
```

Per-CPU hardware counters with named metric groups — easier than raw `perf stat` lists.

---

## TLB pressure and huge pages

The TLB (Translation Lookaside Buffer) caches virtual→physical page translations. Default page size = 4 KiB. A 1 GiB working set needs 262,144 entries; a typical TLB has only ~1500. Misses fall back to page-table walks (costly).

### Symptoms of TLB pressure

- `perf stat` dTLB-load-miss rate > 1%
- Performance scales with number of pages touched, not bytes
- Adding `MADV_HUGEPAGE` / explicit hugepages gives 10-30% speedup

### Huge pages

2 MiB pages (x86):
- 512× larger than 4 KiB → 512× fewer TLB entries needed for the same range
- Enable: Transparent Huge Pages (THP) is kernel-managed; explicit hugepages are reserved

```bash
# THP mode
cat /sys/kernel/mm/transparent_hugepage/enabled
# [always] madvise never

# Usually "madvise" is safest — app must explicitly ask via madvise(MADV_HUGEPAGE)

# For large buffer pools (DB, ML inference), explicit hugepages:
sudo sysctl -w vm.nr_hugepages=1024   # reserve 2 GiB as huge pages
```

### When THP hurts

- Memory pressure + THP defrag → stalls as kernel tries to compact
- Small or sparsely used regions → wasted memory (promoted to 2 MiB when only a few KB used)

For jittery latency targets, some teams set `madvise` mode and enable only for known-large mappings.

### 1 GiB pages (huge huge pages)

Available via `HugeTLB` pools; used by DBs (MySQL, Oracle). Not worth for most apps.

---

## Data layout: AoS vs SoA, cacheline padding, false sharing

### Array of Structs (AoS) vs Struct of Arrays (SoA)

```rust
// AoS — one struct per element, fields interleaved
struct Point { x: f32, y: f32, z: f32 }
let points: Vec<Point>;

// SoA — one Vec per field
struct Points { xs: Vec<f32>, ys: Vec<f32>, zs: Vec<f32> }
```

| Use case | Better |
|----------|--------|
| Iterate all fields of each element (render a point) | AoS |
| Iterate only one field (sum all x) | SoA — 3× better cache utilization |
| SIMD over one field | SoA — aligned vector loads |
| Small struct, few fields | AoS — simpler |

### Cacheline size

x86: 64 bytes. ARM: 64 or 128 bytes. Align hot structs to cacheline to avoid one struct spanning two lines.

```rust
#[repr(align(64))]
struct HotStruct {
    // ...
}
```

### False sharing

Two logically independent hot fields on the same cacheline → cores invalidate each other's L1 copy.

```rust
// BAD: one cacheline holds both counters; two threads writing = cacheline ping-pong
struct Counters {
    counter_a: AtomicU64,  // thread A writes
    counter_b: AtomicU64,  // thread B writes
}

// GOOD: pad to separate cachelines
#[repr(align(64))]
struct PaddedCounter(AtomicU64);

struct Counters {
    counter_a: PaddedCounter,
    counter_b: PaddedCounter,
}
```

C / C++:
```c
struct __attribute__((aligned(64))) counter_t { uint64_t v; char pad[56]; };
```

Detection: `perf c2c` HITM rate on the struct → pad.

### Array padding at the end

When splitting work across threads, each thread may write a different struct in the same array. If `sizeof(T) < 64`, adjacent threads collide.

```rust
use std::mem::size_of;
assert!(size_of::<MyThreadState>() >= 64);  // prevent false sharing between consecutive entries
```

Or use `CachePadded<T>` from `crossbeam-utils`.

---

## Memory bandwidth ceilings

Calculate your ceiling:
```
DDR5-6400 dual-channel: 64 GB/s theoretical
Real: ~80% = 50 GB/s

Your workload processes N bytes at rate R ops/sec.
Bytes/sec = N * R. If close to 50 GB/s, you're memory-bound — no CPU optimization will help.
```

### Memory-bandwidth-bound workload characteristics

- High IPC is impossible (stalls on memory waits)
- Adding cores doesn't help (bandwidth is socket-wide)
- Smaller working set OR different access pattern (sequential vs random) can

### Sequential vs random

Sequential reads = prefetcher works = close to peak bandwidth.
Random reads = prefetcher defeats itself = 5-10× slower bandwidth (but hides under latency budget for small working sets).

```
# Measure
perf stat -e L1-dcache-loads,L1-dcache-load-misses -- ./seq_sum
# vs
perf stat -e L1-dcache-loads,L1-dcache-load-misses -- ./random_sum
```

### `fio` has a memory variant

```bash
fio --name=mem --ioengine=mmap --filename=/dev/shm/test --size=4G \
    --bs=4k --rw=read --direct=1
```

Measures mmap memory throughput — useful for DB buffer-pool-style workloads.

### `stream` benchmark (McCalpin)

The canonical memory-bandwidth microbench. Compile with:
```bash
gcc -O3 -DSTREAM_ARRAY_SIZE=10000000 stream.c -o stream
./stream
# Copy, Scale, Add, Triad — each reports GB/s
```

Compare to your workload's inferred bandwidth to see how close to ceiling you are.

---

## NUMA effects

Multi-socket systems (or big single-socket with NUMA nodes) have:
- local memory — fast
- remote memory — 1.5-2× slower

### Diagnosis

```bash
numactl --hardware      # nodes and their CPUs
# node 0 cpus: 0-15
# node 1 cpus: 16-31
# node distances: 0→0 10, 0→1 21

numastat              # per-process numa hit/miss
```

### Fixes

```bash
# Pin a process to a single numa node
numactl --cpunodebind=0 --membind=0 ./bin

# Check actual memory placement
numastat -p $PID
# Watch for "other_node" high values → many remote accesses
```

Programmatic (Rust with `libc`):
```rust
use libc::{set_mempolicy, MPOL_BIND};
// ... (see numa crate)
```

### NUMA-aware allocation

Database / ML inference engines often:
- Shard data across numa nodes
- Pin worker threads to numa-local cores
- Use `mbind` to bind memory regions to a specific node

For single-socket, modern CPUs: skip NUMA tuning. For 2-socket+: mandatory.

---

## Applying this to Rust / C++ / Go data structures

### Rust

| Data structure | Cache-friendliness |
|----------------|-------------------|
| `Vec<T>` | Excellent — contiguous, sequential access is peak BW |
| `Box<[T]>` | Same as Vec |
| `SmallVec<[T; N]>` | Excellent — inline up to N, then Vec |
| `VecDeque<T>` | Good — circular buffer, still contiguous |
| `HashMap<K,V>` (SipHash default) | Medium — buckets are contiguous but chains scatter |
| `HashMap<K,V>` (ahash / FxHash) | Better — faster hash reduces chain length |
| `BTreeMap<K,V>` | Medium — nodes are small, OK cache locality |
| `Vec<Box<T>>` | Poor — pointer chase; breaks prefetcher |
| `LinkedList<T>` | Worst — always use Vec or VecDeque |
| `Arc<T>` / `Rc<T>` | Adds indirection — ~1 cacheline miss per access |

### C++

Same story: `std::vector` > `std::deque` > `std::list` for cache.

`std::unordered_map` in libstdc++ uses chaining via pointer — poor. `boost::unordered_flat_map` or `absl::flat_hash_map` (Abseil Swiss Table) are flat and much better.

### Go

- Slices: contiguous, excellent.
- Maps: Go's builtin map is cacheline-optimized buckets but still has chains.
- `interface{}` / `any`: boxing → pointer chase → cache misses. Avoid in hot loops (CASE STUDIES §Go for concrete example).

---

## Prefetching

Modern CPUs auto-prefetch sequential / strided access. Random indirections defeat them.

### Software prefetch

```c
#include <x86intrin.h>
for (int i = 0; i < n; i++) {
    _mm_prefetch((const char*)&arr[i + 16], _MM_HINT_T0);  // prefetch 16 ahead
    process(arr[i]);
}
```

Rarely pays; the hardware prefetcher is usually better. Where it helps: linked structures with predictable next-pointers, pointer-chased lookups.

Rust:
```rust
use std::intrinsics::prefetch_read_data;
unsafe { prefetch_read_data(&arr[i + 16] as *const _, 3); }  // 3 = T0 (all caches)
```

Measure both: prefetching adds instructions; net win only if miss cost > added instructions.

### Software "pre-scan" prefetch

A cleaner pattern is to pre-scan sequence A so that hash lookups for sequence B are warm:

```rust
// Cold cache, sparse lookups — slow
for item in items {
    let meta = lookup_table.get(&item.key);  // cache miss per lookup
    process(item, meta);
}

// Pre-scan the keys in a tight loop first — prefetcher warms up
let keys: Vec<_> = items.iter().map(|x| x.key).collect();
for k in &keys { let _ = lookup_table.get(k); }  // warm
for (item, k) in items.iter().zip(&keys) {
    let meta = lookup_table.get(k);  // now warm
    process(item, meta);
}
```

Only pays when working set fits in cache and the loop is tight.

---

## Practical checklist

Before claiming "the code is CPU-bound":

- [ ] `perf stat` IPC — if < 1.0, you're stalling; investigate cache / branch / deps
- [ ] LLC miss rate < 20% (else memory-bound; smaller working set or SoA)
- [ ] dTLB miss rate < 1% (else TLB-bound; consider hugepages)
- [ ] No `perf c2c` HITM (else false sharing)
- [ ] Memory bandwidth used < 80% of stream benchmark (else BW-bound)
- [ ] NUMA-local (if multi-socket; `numastat -p`)

If all green and you're still slow, you're CPU-bound for real. Move on to algorithmic work.

### Quick diagnostic one-liner

```bash
perf stat -e task-clock,cycles,instructions,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses,dTLB-load-misses,context-switches -- ./bin args 2>&1 | tee perf-stat.txt
```

Eyeball:
- IPC = instructions / cycles
- L1 miss rate = L1-misses / L1-loads
- LLC miss rate = LLC-misses / LLC-loads
- dTLB miss rate = dTLB-misses / L1-loads (rough)

If these ratios look bad, follow the sections above.
