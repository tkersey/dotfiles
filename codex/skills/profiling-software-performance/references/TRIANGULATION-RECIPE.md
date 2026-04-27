# Triangulation Recipe — Three Angles Must Agree Before You Act

> Adapted from the `operationalizing-expertise` triangulated-kernel pattern. Apply when you have a profiling hypothesis: never act on a single signal — require three orthogonal measurements to converge. Items where 3/3 agree go in the kernel and become actionable. Items where 2/3 agree go in the disputed appendix. Items where 1/3 agree are discarded as likely artifacts of one tool's bias.

## Contents

- [The pattern, in one diagram](#the-pattern-in-one-diagram)
- [Why three (not one, not two, not five)](#why-three-not-one-not-two-not-five)
- [Choosing your three angles](#choosing-your-three-angles)
- [Worked example: "DB writes are slow"](#worked-example-db-writes-are-slow)
- [Worked example: "Memory leak"](#worked-example-memory-leak)
- [Worked example: "Container is slow"](#worked-example-container-is-slow)
- [The triangulation ledger format](#the-triangulation-ledger-format)
- [What to do when angles disagree](#what-to-do-when-angles-disagree)

---

## The pattern, in one diagram

```
                       Hypothesis: "X is the bottleneck"
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
   Angle A                      Angle B                      Angle C
   (e.g. CPU sample)        (e.g. allocator profile)    (e.g. off-CPU + I/O)
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     ▼
                              All three agree?
                                     │
                ┌────────── Yes ─────┴───── No ──────────┐
                │                                          │
                ▼                                          ▼
            KERNEL                                      DISPUTED
       (act on it)                       (publish in appendix; do not act yet)
```

This is the same shape as operationalizing-expertise's three-LLM consensus. The substitution: instead of three independent models distilling a corpus, you use three independent profilers measuring the same workload.

---

## Why three (not one, not two, not five)

- **One signal lies.** Every profiler has bias: sampling profilers under-count short fast functions; allocator profilers miss leaks below their granularity; off-CPU profiles miss work that runs hot. A single tool gives you a *view*, not the *system*.
- **Two signals can collude.** If both signals come from the same instrumentation framework (e.g., perf-based CPU + perf-based off-CPU), they share systematic errors. Two-out-of-two is one-out-of-one in disguise.
- **Three orthogonal angles** force the bias of any one tool to be outvoted. If three angles built on independent mechanisms agree, the conclusion is robust to instrument-level error.
- **Five+ is over-engineering.** Marginal signal per added angle drops fast; cost of running and reconciling rises. Three is the cheapest set that beats single-tool bias.

---

## Choosing your three angles

The angles must be **orthogonal in mechanism**, not just orthogonal in name. A good triangulation set has at most one tool per row:

| Mechanism | Examples |
|---|---|
| **Statistical sampling of CPU** | `perf record -F 99 -g`, `samply`, `py-spy`, Go pprof CPU |
| **Compiler-instrumented call trace** | gcc `-pg` + gprof, valgrind callgrind, `tracing` spans |
| **Allocator counting** | heaptrack, dhat, `pprof -alloc_objects`, valgrind massif |
| **Off-CPU / scheduler trace** | `perf sched`, `bpftrace` runqueue, off-cpu flame graph |
| **I/O syscall trace** | `strace -T -c`, `iotop`, `biolatency-bpfcc`, `iostat -xm` |
| **Lock / contention** | `perf lock`, mutex-profiling allocator, `tokio-console` |
| **Hardware PMU** | `perf stat -e cache-misses,cycles,branch-misses` |
| **Kernel-side trace** | `bpftrace`, ftrace, USDT probes |

Pick **one tool from three different mechanism rows** for your triangulation set. Two `perf` invocations from the same machine count as one mechanism, not two.

---

## Worked example: "DB writes are slow"

You suspect writes are bottlenecked, but on what?

| Angle | Tool | Observation |
|---|---|---|
| A: CPU sample | `samply` flamegraph | 41% of samples in `wal_append_record` |
| B: Off-CPU | `bpftrace` runqlat | 80% of wall time waiting on `fdatasync` |
| C: Syscall trace | `strace -c -p PID` | `fdatasync` is 3 of top-5 syscalls by total time |

Three angles converge on **fsync as the bottleneck, not WAL append CPU.** The CPU flamegraph is misleading on its own — it shows where CPU went, but the workload spent most wall time *waiting*. Hand-off to extreme-software-optimization with the hypothesis "fsync coalescing or `synchronous=NORMAL`."

If only A and B agreed but C showed `read` syscalls dominating, you'd be in the disputed appendix — investigate further before acting.

---

## Worked example: "Memory leak"

| Angle | Tool | Observation |
|---|---|---|
| A: RSS over time | `/usr/bin/time -v` + `smaps_rollup` | RSS grows linearly with request count |
| B: Allocator profile | `heaptrack` / `dhat` | One allocation site holds 600MB at peak |
| C: Drop / free trace | `valgrind --tool=massif --pages-as-heap` | Same site, no matching free |

Three angles agree → kernel: this site leaks. Hand off.

If A and B agreed but C showed frees do happen, you're in disputed: probably **fragmentation**, not a true leak. Different fix.

---

## Worked example: "Container is slow"

| Angle | Tool | Observation |
|---|---|---|
| A: CPU steal in container | `mpstat -P ALL 1` (look at `%steal`) | 12% steal time |
| B: Cgroup throttling | `cat /sys/fs/cgroup/cpu.stat` (`nr_throttled`) | 200 throttle events / sec |
| C: Wall vs CPU profile | `samply record` + `time` wall clock | wall ≫ CPU; large gap |

Three angles agree → kernel: **CPU is being taken away by the orchestrator, not consumed by the workload.** Defer optimization; raise the limit instead. Hand back to user without an extreme-software-optimization invocation — the hot path is fine.

---

## The triangulation ledger format

Add a section to your `hypothesis.md` ledger for triangulation. Each row tracks one hypothesis × three angles:

```markdown
## Triangulation Ledger

### H1: fsync per record is the cost driver

| Angle | Tool / file              | Verdict   | Evidence path                  |
|-------|--------------------------|-----------|--------------------------------|
| A     | samply flame             | supports  | flames/cpu.svg:0.41 wal_append |
| B     | bpftrace runqlat         | supports  | offcpu/runq.json#L120          |
| C     | strace -c                | supports  | strace/strace_summary.txt:L8   |
| Result| **3/3 → KERNEL**         |           | hand off to extreme-software-optimization |

### H2: writer thread contention

| Angle | Tool / file              | Verdict   | Evidence path                  |
|-------|--------------------------|-----------|--------------------------------|
| A     | samply flame             | rejects   | no lock fns in top-50          |
| B     | perf lock record         | supports  | one mutex, 12% wait time       |
| C     | tokio-console            | supports  | one task starved 80ms p99      |
| Result| **2/3 → DISPUTED**       |           | investigate; angle A may be misleading due to sampling |
```

Pair with the hotspot table; the ledger explains *why* a row is on the table at all.

---

## What to do when angles disagree

A 2/3 split is information, not a problem. Workflow:

1. **Identify the dissenting angle.** Which tool says no?
2. **Check that tool's known biases.** A sampling profiler at 99 Hz can miss spikes shorter than ~10ms. An allocator profile sees only allocations, not OS-level mmaps. A syscall trace is blind to user-space spinning.
3. **Add a fourth angle if cheap.** A different sampling rate, or a different framework, can break the tie.
4. **If still split:** publish in the disputed appendix. Do not act on disputed hypotheses without further evidence — false positive optimizations waste a week and erode trust in the next round.

The point is *honesty about uncertainty*. Single-tool conviction is the most expensive mistake in profiling.

---

**See also:** [STATISTICAL-RIGOR.md](STATISTICAL-RIGOR.md) for sample-size and confidence-interval methodology, [OPERATOR-CARDS.md](OPERATOR-CARDS.md) for the 🔺 Triangulate operator card, [ARTIFACTS.md](ARTIFACTS.md) for `hypothesis.md` ledger template.
