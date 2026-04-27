# I/O Profiling, Storage Pathologies, and RAM-for-Speed Tradeoffs

> Most "CPU is at 30%" perf problems are I/O or memory hierarchy problems misdiagnosed. This is the checklist that separates "slow code" from "slow machine" from "wrong storage layout".

## Contents

1. [First — is this actually I/O?](#first--is-this-actually-io)
2. [I/O axes (what you measure)](#io-axes-what-you-measure)
3. [Tools by axis](#tools-by-axis)
4. [fsync — the hidden latency tax](#fsync--the-hidden-latency-tax)
5. [Small-file pathology](#small-file-pathology)
6. [Filesystem-specific gotchas](#filesystem-specific-gotchas)
7. [btrfs fragmentation playbook](#btrfs-fragmentation-playbook)
8. [Page cache, mmap, and O_DIRECT](#page-cache-mmap-and-o_direct)
9. [Network I/O](#network-io)
10. [RAM-for-speed tradeoffs — the no-brainer table](#ram-for-speed-tradeoffs--the-no-brainer-table)
11. [Prefetch / preload / pre-warm](#prefetch--preload--pre-warm)
12. [Tradeoff budget](#tradeoff-budget)

---

## First — is this actually I/O?

Before you profile disk, prove it's disk. A CPU flame that looks CPU-bound can be hiding I/O wait inside `read()` / `pread()` / allocator slowpaths. The cheap triage:

```bash
# Is the process on-CPU or sleeping?
while :; do ps -o pid,stat,%cpu,wchan= -p $PID; sleep 0.5; done
# STAT column:  R = running, D = uninterruptible (disk/NFS), S = sleeping, wchan names the kernel wait

# Aggregate: how much of wall time was the process actually on-CPU?
/usr/bin/time -v ./bin args 2>&1 | grep -E "CPU|wall"
# Percent of CPU this job got: <N%>   ← anything <80% on a single-threaded CPU-bound workload = I/O/lock wait

# Full system picture
vmstat 1          # wa column is % I/O wait
iostat -xm 1      # %util, r/s, w/s, await per device
pidstat -d 1      # per-process kB/s read/write
dstat -tcdnm 1    # compact cross-cut

# Off-CPU flamegraph — *where* we're waiting
git clone https://github.com/iovisor/bcc
sudo offcputime-bpfcc -p $PID 30 > offcpu.stacks
flamegraph.pl --color=io --title="Off-CPU" < offcpu.stacks > offcpu.svg
```

**Rule of thumb:**
- `wa` > 20% in vmstat → disk is the bottleneck, not CPU
- `await` > 10ms for NVMe → contention, queue depth too high, or fs issue
- `%CPU` < 80% on a "CPU-bound" job → not actually CPU-bound
- `D` state in `ps` → uninterruptible wait — always I/O or semaphore

---

## I/O axes (what you measure)

| Axis | Unit | Why it matters | Tool |
|------|------|----------------|------|
| IOPS (4KB) | ops/sec | Metadata-heavy / small random I/O | `fio`, `iostat` |
| Throughput | MB/s | Streaming / large sequential | `fio`, `dd`, `iostat` |
| Latency | µs–ms p50/p95/p99 | User-visible response | `fio --latency_percentiles=1`, `biolatency-bpfcc` |
| fsync latency | ms | Durability-bound workloads | `fio --fsync=1`, custom bench |
| Queue depth | # | Underutilized device vs queue saturation | `iostat -x` (avgqu-sz) |
| Read/Write mix | % | Cache effectiveness, wear | `iostat`, `iotop -a` |
| Block size | KB | Under-block = wasted IOPS; over-block = wasted bandwidth | `blktrace` |
| Random vs sequential | ratio | Seek cost on HDD, GC on SSD | `blktrace` + `btt` |
| fsync frequency | per sec | Commit pressure | `bpftrace fsync.bt` |
| Inode / dentry cache hit | % | Small-file workload cost | `/proc/sys/fs/dentry-state` |

---

## Tools by axis

### Per-device live view
```bash
iostat -xm 1                # r/s w/s rMB/s wMB/s await %util aqu-sz
dstat -tcdnm 1              # single line per second
sar -d 1                    # persistent recording (needs sysstat)
nvme smart-log /dev/<device> # NVMe health + wear
```

### Per-process I/O
```bash
sudo iotop -oPa             # processes actually doing I/O
pidstat -d 1                # kB/s per process per tick
cat /proc/$PID/io           # cumulative rchar/wchar/syscr/syscw/read_bytes/write_bytes
```

### Per-syscall
```bash
strace -c -e trace=read,write,pread64,pwrite64,fsync,openat ./bin args
strace -T -e read,write ./bin  2>&1 | head -100   # latency per call
```

### Block-level tracing (the sharp tools)
```bash
# biosnoop — every block I/O with process/latency
sudo biosnoop-bpfcc                # or: bpftrace /usr/share/bpftrace/tools/biosnoop.bt
# biolatency — histogram of I/O latency
sudo biolatency-bpfcc -m 10         # 10s, millisecond buckets
# ext4slower / xfsslower — slow fs ops
sudo ext4slower-bpfcc 5             # ops > 5ms
# Full block trace
sudo blktrace -d /dev/<device> -o trace -w 10
blkparse trace | less
btt -i trace.blktrace.0             # latency breakdown: Q→D→C
```

### Reproducible IOPS/latency benchmarks — `fio`
```bash
# 4 KiB random read IOPS (NVMe spec workload)
fio --name=rand_read --filename=/data/fio.tmp --size=8G --bs=4k \
    --iodepth=32 --rw=randread --ioengine=libaio --direct=1 \
    --runtime=30 --time_based --group_reporting \
    --latency_percentiles=1

# 1 MiB sequential write (streaming)
fio --name=seq_write --filename=/data/fio.tmp --size=8G --bs=1M \
    --iodepth=8 --rw=write --ioengine=libaio --direct=1 \
    --runtime=30 --time_based

# fsync-heavy (WAL-like)
fio --name=sync_write --filename=/data/fio.tmp --size=1G --bs=4k \
    --iodepth=1 --rw=randwrite --ioengine=sync --fsync=1 \
    --runtime=30 --time_based --latency_percentiles=1

# Mixed 70/30 OLTP-style
fio --name=oltp --filename=/data/fio.tmp --size=8G --bs=16k \
    --iodepth=16 --rw=randrw --rwmixread=70 --ioengine=libaio --direct=1 \
    --runtime=30 --time_based
```
Always include `--direct=1` when benchmarking storage itself — otherwise you're mostly measuring the page cache.

### Page-cache occupancy
```bash
# Is this file's data in cache?
pip install pcstat
pcstat /data/hot.bin

# Per-page in-core map
fincore /data/hot.bin | head

# Prewarm a file into cache
vmtouch -t /data/hot.bin     # touch pages
vmtouch -l -d /data/hot.bin  # lock in memory (background)

# Evict
vmtouch -e /data/hot.bin
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches    # nuke everything
```

---

## fsync — the hidden latency tax

`fsync()` / `fdatasync()` forces data to stable storage. On NVMe it can cost 50µs–5ms depending on flight ordering, journaling, and write-barriers. One fsync per message = your tail latency.

**Signs you're fsync-bound:**
- `biolatency-bpfcc` shows a bimodal distribution: "fast" and "slow" clusters
- `iostat -x` `%util` high but `r/s + w/s` low — fewer but slower operations
- `strace -c` ranks `fsync` with large total time but small count
- Latency scales with tail of `fdatasync` histogram

**Levers:**
1. **Coalesce:** batch N writes, one fsync. `O_APPEND`/WAL pattern writes once per batch, not per record.
2. **Defer:** group-commit windows (e.g. 5ms). Latency cost = window length, throughput gain is large.
3. **`fdatasync` vs `fsync`:** skips metadata updates; safe when file size/mtime don't matter for recovery.
4. **Write barriers / `sync_file_range(SYNC_FILE_RANGE_WRITE)`:** ask the kernel to start flushing without blocking.
5. **Filesystem choice:** ext4 `data=ordered` is the safe default; `data=journal` doubles write cost.
6. **Storage choice:** NVMe with PLP (power-loss protection) treats fsync as near-free; consumer SSDs don't.
7. **nobarrier / `data=writeback`:** **only with UPS or explicit ok-with-data-loss policy**.

**Measure fsync itself:**
```c
// isolate fsync cost in a microbench
for (int i=0;i<N;i++){
  write(fd, buf, 4096);
  clock_gettime(CLOCK_MONOTONIC, &t0);
  fdatasync(fd);
  clock_gettime(CLOCK_MONOTONIC, &t1);
  record(hist, ns(t1,t0));
}
```
`fio --fsync=1` is the canned version.

---

## Small-file pathology

"Lots of tiny files" is the single most common hidden perf problem. It looks like CPU, it's actually inode/dentry cache + metadata I/O + directory scan cost.

### Symptoms
- `readdir()` + `stat()` dominate the flame
- `vmstat` shows high `so`/`si` (swap) or `bo` (block out) with low bytes/s
- Commands that touch the tree (`du`, `ls -R`, `find`) are minutes slow the first time, seconds the second (cache warmup)
- Growth is mostly inodes, not bytes: `df -i`

### Measure
```bash
df -i /mount                                   # inode use
find /path -type f | wc -l                     # file count
find /path -type f -printf '%s\n' | awk '{s+=$1;n++}END{print "avg",s/n}'
find /path -type d -printf '%f/' | awk -F/ '{print NF}' | sort -n | uniq -c  # depth histogram

# Slowest dir ops
sudo ext4slower-bpfcc 10
sudo opensnoop-bpfcc -p $PID     # every open()
sudo execsnoop-bpfcc             # if a shell wrapper is spawning stats
```

### Remedies (in order of cheapness)
1. **Avoid scanning** — keep an index (sqlite, json, a manifest). A full-tree walk on 100k files at 4KB each costs ≥ 10s cold on btrfs even on NVMe.
2. **Bundle** — tar / zip / SQLite BLOB / one fat mmap'd file. A search indexer can store millions of small records in one SQLite DB instead of millions of files.
3. **Directory sharding** — `a/ab/abcd.bin` limits dir size; ext4 and btrfs degrade past ~10k entries per dir.
4. **Prefetch the tree** — `vmtouch -f /path` loads dentries + inodes into cache before the hot op.
5. **Increase cache pressure budget** — `sysctl vm.vfs_cache_pressure=50` (default 100) keeps dentries/inodes in cache longer.
6. **Raise `fs.file-max`** if hitting limits; raise `ulimit -n` for open fd count.
7. **Content-addressed storage** — git-like loose object + packfile split; hot data stays in loose, cold data rolls into packs.
8. **tmpfs for scratch** — if ephemeral, put it in `/dev/shm` or a dedicated tmpfs; the 2x-5x speedup for metadata-heavy scratch work is massive.

---

## Filesystem-specific gotchas

### ext4

```
/mount defaults,noatime,data=ordered,commit=5,nobarrier?   # nobarrier only with UPS
```
- `noatime` or `lazytime` — stop updating `atime` on reads (one write per read otherwise).
- `data=ordered` (default) — journal metadata, order data before commit. Good balance.
- `data=journal` — journal everything. 2x write cost, safest.
- `data=writeback` — no data ordering. Fastest, **can expose stale blocks on crash**. Rarely worth it.
- `commit=N` — journal commit every N seconds (default 5). Lowering improves recovery; raising reduces writes.

### xfs

```
/mount defaults,noatime,logbufs=8,logbsize=256k
```
- Recommended for low-variance server writes.
- `allocsize=1m` for log-file-style sequential writes prevents fragmentation.
- No online shrink; plan volume sizing.

### btrfs — has its own section below (highest chance of surprise)

### ZFS

- ARC is RAM-greedy; tune `zfs_arc_max` or suffer.
- `compression=lz4` is a near-free win for most workloads.
- Snapshots are ~free until they aren't; space amplification on heavy rewrite.
- `recordsize` matters: 128k default for bulk; 16k for database workloads.
- `sync=disabled` = bye bye durability on crash; only for scratch.

### APFS (macOS)

- Barrier semantics differ from Linux; fsync ≈ "durable rename" cost.
- Spotlight indexing chews I/O during dev; exclude project dirs (`.noindex`).

### tmpfs

- **Not durable.** Crash = gone.
- Great scratch for intermediates. Use with `/tmp` or `/dev/shm`.
- Respects `size=` mount option — don't let it swap.

---

## btrfs fragmentation playbook

btrfs is CoW — every write allocates new extents. On rewrite-heavy workloads (databases, VM images, append-heavy logs with random in-place updates) extents accumulate and reads become scatter-gather.

### Diagnose
```bash
# Per-file extent count (the key metric)
filefrag -v /path/to/db.sqlite
# Summary for a file tree
sudo filefrag /mount/**/*.sqlite | awk '{print $2, $1}' | sort -rn | head

# Per-filesystem usage + metadata pressure
sudo btrfs filesystem usage /mount
sudo btrfs filesystem df /mount        # metadata vs data allocation
sudo btrfs device stats /mount
sudo btrfs scrub status /mount
```

Thresholds:
- `> 1000` extents for a multi-MB file → degraded read throughput
- `metadata,DUP used > 80%` → run a balance
- `Data,single` approaching `total` with no free chunks → run a balance

### Fix
```bash
# Online defragment a single file
sudo btrfs filesystem defragment -r -v -czstd /path/to/file

# Defragment a subvolume
sudo btrfs filesystem defragment -r -v -czstd /mount/subvol

# Rebalance allocations (long-running; rate-limit with -dusage=)
sudo btrfs balance start -dusage=50 -musage=50 /mount

# Full resync if allocation got stuck
sudo btrfs balance start --full-balance /mount
```
Note: defragment on files with *reflinks* (snapshots, `cp --reflink`) breaks reflink sharing and can multiply disk usage. Check before running on snapshotted data.

### Prevent
```
/mount defaults,noatime,compress=zstd:1,autodefrag,ssd,discard=async,space_cache=v2
```
- `compress=zstd:1` — near-zero CPU cost; usually wins read throughput back through better cache density.
- `autodefrag` — background defrag of files with small random writes. **Bad for big files with large random writes (database files)** — reads/rewrites fragments forever. Prefer `chattr +C` on those files instead.
- `chattr +C path/db.sqlite` (set **before first write**) — disable CoW for this file. Eliminates fragmentation for in-place rewrites. Tradeoff: no checksumming for that file, no snapshot sharing post-divergence.
- `nodatacow` mount option does the same for the whole FS; rarely the right answer.
- Subvolume for DB workloads separate from the rest — lets you tune per-workload.

### Snapshot/reflink pitfalls
- Long-lived snapshots multiply space on rewrite. `btrfs subvolume list -t /mount` + `btrfs qgroup show /mount` to audit.
- Snapshots on btrfs don't make rollback "free" — they just share extents until divergence. A churning DB with 90 days of hourly snapshots will balloon.

### Filesystem-specific baselines matter

If one environment uses btrfs and another uses ext4, the `BUDGETS.md` table should carry separate rows for each filesystem. Do not compare numbers across filesystems — roll per-FS baselines.

---

## Page cache, mmap, and O_DIRECT

### Page cache is free memory

Modern Linux uses every free byte for the page cache. If your working set fits, you get RAM latency on "disk" reads. If it doesn't, you get disk latency. **So: how big is your working set, and how much cache do you have?**

```bash
# Working set indicator — how much of the cache is your files?
pcstat -terse /data/hot/*.db
# Cache headroom
free -h                        # "available" ≈ reclaimable cache + truly free
cat /proc/meminfo | egrep 'Cached|Buffers|Available'
```

### `posix_fadvise` / `madvise` — tell the kernel what you're doing

```c
// I'll read the whole file sequentially, please read ahead aggressively
posix_fadvise(fd, 0, 0, POSIX_FADV_SEQUENTIAL);

// I'll read bits of this randomly, so don't read-ahead (saves bandwidth)
posix_fadvise(fd, 0, 0, POSIX_FADV_RANDOM);

// I'm done with this range, drop it from cache (good for large scans)
posix_fadvise(fd, offset, len, POSIX_FADV_DONTNEED);

// mmap variants
madvise(addr, len, MADV_WILLNEED);    // async prefetch
madvise(addr, len, MADV_SEQUENTIAL);  // evict eagerly after read
madvise(addr, len, MADV_HUGEPAGE);    // try 2M pages (THP must allow)
madvise(addr, len, MADV_DONTNEED);    // hard drop, discards dirty private pages
```

### mmap — when to use

- Read-mostly large files (index, dictionary, dataset). OS demand-pages, shares across procs.
- Random access patterns where you don't want to manage buffering.
- Frankensearch / Tantivy use mmap heavily; grow `vm.max_map_count` if you hit its limit.

Tradeoffs:
- TLB pressure — use transparent huge pages or explicit hugepages for multi-GB maps.
- Page faults appear as "CPU" in samplers but are synchronous I/O — check `perf stat -e page-faults`.
- Writing through mmap is ergonomic but crash semantics are subtle — prefer explicit `write()` + `fsync()` for durability.

### O_DIRECT — bypass the page cache

Used when you're implementing your own cache (databases). Requires aligned buffers (usually 4KiB) and aligned offsets. Measure: with direct I/O, your code owns all the caching decisions — often slower than letting the kernel do it unless you've already invested in a real buffer pool.

### `vm.swappiness`

```
# keep anon pages in RAM longer (prefer to evict page cache instead)
sudo sysctl -w vm.swappiness=10
```
Default 60 is too aggressive for servers with large page caches; 10 is the workload-owner default.

---

## Network I/O

Not disk, but same category — kernel call with a tail. Checklist:

- **Connection pooling:** handshake cost dominates for short requests. Reuse connections (HTTP keep-alive, SQL pools, gRPC channels).
- **DNS:** a `getaddrinfo` miss can add 10–100ms. Cache, use `/etc/hosts`, or a local resolver.
- **TLS handshake:** 1 RTT with TLS 1.3, 2 RTT with 1.2. Session resumption / 0-RTT where it fits.
- **TCP tuning for bulk:** `tcp_rmem`/`tcp_wmem` and `tcp_congestion_control=bbr`; matters mostly for cross-region links.
- **Nagle vs TCP_NODELAY:** for interactive / request-response protocols, `TCP_NODELAY=1` — otherwise 40ms nagle delay on small writes.
- **Measure:**
  - `tcpdump -i any -s0 -w out.pcap host X` + Wireshark → TCP-level RTT, retransmits.
  - `ss -ti` → per-connection RTT, cwnd, retrans.
  - `nghttp -v` for HTTP/2; `curl -w "@fmt"` for per-phase breakdown.
- **Retries:** exponential backoff with jitter; cap concurrent retries; retry budgets.

---

## RAM-for-speed tradeoffs — the no-brainer table

If you have abundant RAM relative to the working set, many "slow" things are one-line fixes. This table is "when X takes Y RAM but returns Z speedup, the answer is almost always yes."

| Pattern | Cost (RAM) | Benefit | When it's a no-brainer |
|---------|-----------|---------|------------------------|
| In-process LRU on pure function | `size × entries` | O(n) → O(1) for cached calls | Hit rate > 30%, entries fit, values immutable |
| Memoize expensive request parser | 10s MiB | x2–10 throughput | Parser runs on hot path, parse is deterministic |
| Prepared-statement cache | ~100 KiB | x10–30 per repeated query | ≥ 90% of queries repeat |
| Query plan cache | ~1 MiB | x5 for cached plans | SQL workload, plan compile ≥ 1ms |
| Bloom filter pre-filter | 10 bits × n entries | O(n) IO → O(filter) miss pass | Many negative membership tests |
| mmap + prefetch entire index | `index size` | page-fault latency → amortized sequential | Index fits in RAM; read-mostly |
| Precompute inverse index | `O(input size)` | O(m × n) → O(m + n) | Lookup is a hot query, input is stable |
| Full decode cache | `decoded × entries` | Skip re-decode per access | Same row decoded > 2× |
| Connection pool | `n × (~200 KiB)` | 10s of ms saved per hit | Repeated outbound calls |
| vmtouch / lock hot files in RAM | `file size` | First access → page-cache hit | Known hot files, cold cache noise |
| Arena / bump allocator | `arena size` | Eliminates many individual frees | Burst-allocate, bulk-drop pattern |
| String interning | `unique strings × size` | Equality in O(1), cache-friendly | Repeated strings, comparison hot |
| Columnar mirror of row data | `~input size` | Vector scan for analytical queries | Mixed OLTP + analytical workload |
| Prefill DNS cache | KiB | 10–100ms per cold lookup | Outbound to known hosts |
| Keep disk-image build in tmpfs | `image size` | 3–5x faster incremental | CI scratch space that doesn't need to survive |
| Pre-warm JIT / compile / link | `hot set size` | First-request cliff disappears | Cold start p99 matters |
| Increase cgroup memory + swappiness down | n/a | Prevents page-cache eviction | Running alongside noisy neighbors |

### When it's NOT a no-brainer
- Cache wastes RAM if hit rate < 10% or you have to build a complex invalidation story.
- LRU on inherently distinct keys (UUIDs) helps nothing.
- Memoizing impure functions is a correctness bug, not a speedup.
- RAM caches inside containers: the container memory limit may kill you before the optimization helps.
- Multi-process: each worker gets its own cache unless you use shared-memory.

**Policy:** if the optimization costs < 1% of machine RAM and returns ≥ 20% on a measured hotspot, do it. If the cache is tiny relative to the host and buys a measured 30% win, it is usually the right trade.

---

## Prefetch / preload / pre-warm

### File contents
```bash
vmtouch -t /data/hot/*.db                 # read into cache
vmtouch -l -d /data/hot/*.db              # lock, daemonize (drop perms after)
```

### Directory metadata
```bash
find /large/tree -type d -exec true \; # forces stat → dentry cache hit
```

### Program text (reduce cold-start flame):
```bash
cat /proc/$PID/maps | grep 'r-xp' | awk '{print $6}' | sort -u | xargs vmtouch -t
```

### DB buffer pool
- Postgres: `pg_prewarm` extension.
- SQLite: `PRAGMA cache_size=-NNNN;` in pages (negative = KiB); `PRAGMA mmap_size=NN` for mmap-over-pager.
- Many engines auto-prewarm on startup only after the first N queries — script the warmup in CI.

### JIT / bytecode
- Node: `--require` pre-loading; V8 code cache via `node --write-environment-file`.
- Python: `-X importtime` to find slow imports; use `zipimport` / freeze binaries.
- JVM: JFR + application-class-data-sharing (AppCDS).

---

## Tradeoff budget

Before any "add more RAM to it" change, write down:

```markdown
## Tradeoff — <name>
- RAM cost at typical load: X MiB
- RAM cost at peak load:    X MiB
- Headroom on reference host: avail - X MiB = ___
- Expected benefit: p95 X ms → Y ms (Δ %)
- Invalidation story: TTL / write-through / event-based / never
- Correctness: cached output == fresh output? (pure function? deterministic? isomorphism preserved?)
- Rollback: feature-flag name, env var, or config key
- Failure mode: what happens under OOM? (LRU evicts fine; statically sized dies hard)
```

If this table isn't filled in, the cache isn't ready to ship — it's just "works on my machine" with extra steps.

---

## Cross-reference

- Kernel-level tuning that interacts with I/O: [OS-TUNING.md](OS-TUNING.md) (`vm.swappiness`, `vm.vfs_cache_pressure`, `vm.dirty_ratio`, scheduler tuning).
- How to instrument these tradeoffs: [INSTRUMENTATION.md](INSTRUMENTATION.md) (cache hit counters, fsync histograms).
- Where results land: [ARTIFACTS.md](ARTIFACTS.md) (scaling law for "with/without cache", variance envelope for fsync-bound workloads).
