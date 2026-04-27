# GDB, strace, /proc — Profiling Without a Sampler

> When your profiler won't attach, when the process hangs, when you need specific function-call counts — reach for gdb, strace, and /proc. This reference integrates patterns from the `gdb-for-debugging` skill with profiling-specific usage.

Cross-ref: the `gdb-for-debugging` skill is the deeper manual for GDB itself. This file covers how to use the same tools as profiling instruments.

## Contents

1. [When samplers fail](#when-samplers-fail)
2. [Live stack sampling with GDB](#live-stack-sampling-with-gdb)
3. [`/proc/PID/stack` — the cheapest stack reading](#procpidstack--the-cheapest-stack-reading)
4. [gcore — snapshot a running process](#gcore--snapshot-a-running-process)
5. [strace as a profiler](#strace-as-a-profiler)
6. [GDB breakpoint-counts as an instrumentation trick](#gdb-breakpoint-counts-as-an-instrumentation-trick)
7. [rr as a reverse-profiler](#rr-as-a-reverse-profiler)
8. [uprobes and USDT probes](#uprobes-and-usdt-probes)
9. [eBPF one-liners for profiling](#ebpf-one-liners-for-profiling)
10. [Process is spinning — how to diagnose](#process-is-spinning--how-to-diagnose)
11. [Process is stuck — how to diagnose](#process-is-stuck--how-to-diagnose)
12. [When to hand off to `gdb-for-debugging`](#when-to-hand-off-to-gdb-for-debugging)

---

## When samplers fail

Reasons you can't use samply/perf/py-spy:

- Container without privileged capabilities (common)
- Rootless environment (GitHub Actions, serverless)
- Distro without kernel-headers-matching perf
- Symbol-stripped binary where flamegraph is unreadable anyway
- Target is a long-running daemon you cannot restart
- You want precise call *counts* not statistical time
- Process is hung (on-CPU sampling gives nothing)

For these, the classic systems-debug toolkit shines.

---

## Live stack sampling with GDB

"Poor man's profiler" — hand-rolled sampling with GDB:

```bash
#!/bin/bash
# poor_mans_profiler.sh <pid> [samples] [interval_s]
PID=$1
N=${2:-30}
INTERVAL=${3:-1}

for i in $(seq 1 $N); do
    gdb -batch -p $PID \
        -ex "set pagination 0" \
        -ex "thread apply all bt" \
        2>/dev/null
    sleep $INTERVAL
done | awk '
/^Thread/        { thread=$0 }
/^\#[0-9]+/      { print $4 " " $5 }  # function name
' | sort | uniq -c | sort -rn | head -30
```

Attaches briefly (milliseconds), samples every thread's stack, aggregates. Works anywhere GDB can attach. Output: top-N function names by sample count — the stack-frame sampling flamegraph's predecessor.

Make it smarter with full stack aggregation:

```bash
for i in $(seq 1 30); do
    gdb -batch -p $PID -ex "thread apply all bt" 2>/dev/null \
        | grep -E '^#[0-9]+' \
        | awk '{print $2}' \
        | paste -sd';'
    sleep 0.5
done | sort | uniq -c | sort -rn > folded.txt

# Convert to flamegraph
flamegraph.pl < folded.txt > flame.svg
```

### Caveats

- **GDB pauses the process for each sample.** At 1 Hz over 30 seconds, you steal ~1% CPU time. Faster sampling = higher overhead.
- **Symbols must be resolvable by GDB** — same symbol-info requirements as normal profiling.
- **Non-cooperating runtimes** (JIT'd JVM, V8) show opaque frames — GDB doesn't know the JIT's frame format.

---

## `/proc/PID/stack` — the cheapest stack reading

Linux exposes each thread's current kernel-mode stack at `/proc/PID/task/TID/stack`. Reading costs no process pause.

```bash
# Sample one thread's kernel-stack
for i in $(seq 1 100); do
    cat /proc/$PID/stack
    echo '---'
    sleep 0.05
done > kernel-stacks.txt
```

Shows what the thread is *waiting* on (futex, io_uring_enter, schedule). Often enough to diagnose whether it's:
- `futex_wait` — lock contention
- `io_schedule` — disk I/O
- `poll_schedule_timeout` — epoll idle
- `pipe_read` / `net_rx_action` — I/O of a specific kind

For user-mode stack, the process has to be traced — `/proc/PID/stack` is kernel-only. For user-mode sampling, use GDB or samply/perf.

---

## gcore — snapshot a running process

```bash
gcore -o /tmp/myproc $PID
# Generates /tmp/myproc.PID — a core dump
# Analyze offline with gdb
gdb -c /tmp/myproc.PID ./mybinary
(gdb) thread apply all bt full
(gdb) info proc mappings    # memory layout
(gdb) info threads
```

Use when you want to freeze a moment in time without killing the process. gcore blocks the process briefly (usually < 1s for a few-GB process). For post-mortem analysis without incident-reproduction.

Applications:
- Capture a snapshot during a p99 tail event (trigger from metrics)
- Capture before and after a suspected leak window (diff the heaps offline)
- Capture for handoff to another team member / machine

---

## strace as a profiler

`strace -c` is a syscall-level sampling profiler:

```bash
strace -c ./bin args
# or attach:
strace -c -p $PID   # Ctrl-C to stop and get summary

# Output:
# % time     seconds  usecs/call     calls    errors syscall
# ------ ----------- ----------- --------- --------- ----------------
#  68.12    0.234567         117      2000           read
#  23.45    0.081234          81      1000           write
#   5.12    0.017777         177       100           fsync
#   3.31    0.011234          22       500           epoll_wait
```

Interpret:
- **% time** — fraction of syscall-wait wall time per call
- **usecs/call** — average latency per call of this syscall
- **calls** — count
- **errors** — how often the syscall failed

If `read` is 68% of syscall time, the bottleneck is I/O read — go to biolatency / iostat.

### Per-syscall latency histograms

```bash
strace -T -e read,write,fsync ./bin 2>&1 | \
    awk '/</ { gsub(/[<>]/, ""); print $NF }' | \
    sort -n | \
    awk '
    { a[NR]=$1 }
    END {
        n=NR
        print "p50", a[int(n*0.5)]
        print "p95", a[int(n*0.95)]
        print "p99", a[int(n*0.99)]
        print "max", a[n]
    }'
```

### Overhead warning

strace slows the process 5-30× because every syscall is trapped. Use for **investigation**, not for measuring production latency. For low-overhead equivalent, use `bpftrace` / `perf trace`.

---

## GDB breakpoint-counts as an instrumentation trick

GDB can attach a command list to a breakpoint. Use to count function calls or log arguments without recompiling:

```gdb
(gdb) break my_hot_fn
(gdb) commands 1
> silent
> printf "called %d\n", ++$count
> continue
> end
(gdb) continue
```

Now the process runs normally (slower — each breakpoint costs a ptrace roundtrip) and you get a live count.

More useful: log specific arguments:
```gdb
(gdb) break open
(gdb) commands 2
> silent
> printf "open(%s, %d)\n", $rdi, $rsi
> continue
> end
```

Or log the return value:
```gdb
(gdb) break my_hot_fn
(gdb) commands 1
> silent
> finish
> printf "returned %d\n", $rax
> end
```

Use carefully — each breakpoint hit is a context switch. Rate-limit by conditional breakpoints:
```gdb
(gdb) break my_hot_fn if some_counter % 100 == 0
```

---

## rr as a reverse-profiler

[rr](https://rr-project.org/) records and replays execution deterministically. Profile a reproduced bug:

```bash
rr record ./bin args              # records to /tmp/rr-traces/bin-0
rr replay                          # replay inside gdb
(rr) continue
(rr) reverse-continue             # step BACKWARD through execution
```

Counter-intuitive uses as profiling:
- **Find WHERE a value got bad**: watchpoint on the bad variable, `reverse-continue`, lands at the modifying instruction.
- **Profile a rare bug reproducibly**: record once, replay 100× to sample stacks at the offending window.
- **Eliminate heisenberg effects**: sampling during replay doesn't affect the recorded timeline.

Record-time overhead: 2-3× slower than native. Replay is fast and deterministic.

---

## uprobes and USDT probes

### uprobes (kernel-dynamic, no recompile)

```bash
# Attach to a user-space function by address
sudo perf probe -x /path/to/bin 'my_hot_fn'
sudo perf record -e probe_bin:my_hot_fn -aR sleep 10
sudo perf script > probe_events.txt
```

With `bpftrace`:
```bash
sudo bpftrace -e '
  uprobe:/path/to/bin:my_hot_fn { @[ustack] = count(); }
  interval:s:10 { exit(); }
'
```

### USDT (User Statically Defined Tracepoints)

Tools like Postgres, MySQL, MongoDB, Ruby, Python expose USDT probes. List them:
```bash
bpftrace -l 'usdt:/usr/lib64/libpython3.11.so.1.0:*'
bpftrace -l 'usdt:/usr/local/pgsql/bin/postgres:*'
```

Attach without code changes:
```bash
sudo bpftrace -e '
  usdt:/usr/local/pgsql/bin/postgres:transaction__commit { @[pid] = count(); }
'
```

---

## eBPF one-liners for profiling

### CPU sampling (flamegraph source)
```bash
sudo bpftrace -e 'profile:hz:99 /pid==1234/ { @[ustack] = count(); }'
```

### Off-CPU (who's blocked, for how long)
```bash
sudo offcputime-bpfcc -p 1234 30 > offcpu.stacks
flamegraph.pl --color=io < offcpu.stacks > offcpu.svg
```

### Block I/O latency histogram
```bash
sudo biolatency-bpfcc -m 10     # per-millisecond buckets, 10s
```

### fsync latency
```bash
sudo bpftrace -e '
  tracepoint:syscalls:sys_enter_fsync { @start[tid] = nsecs; }
  tracepoint:syscalls:sys_exit_fsync  /@start[tid]/ {
    @lat = hist((nsecs - @start[tid]) / 1000000);   // ms
    delete(@start[tid]);
  }
'
```

### Page faults attributable to process
```bash
sudo bpftrace -e '
  tracepoint:exceptions:page_fault_user /pid==1234/ { @[ustack] = count(); }
'
```

### syscall counts per-process
```bash
sudo syscount-bpfcc -p 1234 -d 10
```

---

## Process is spinning — how to diagnose

Symptom: one thread pegged at 100% CPU, app output stopped, no visible progress.

```bash
# Step 1: identify which thread
top -H -p $PID             # note the offending TID
# or: ps -T -p $PID -o tid,pcpu,comm | sort -rnk2

# Step 2: sample its user-stack
for i in $(seq 1 10); do
    sudo gdb -batch -p $TID -ex 'bt' 2>/dev/null
    sleep 0.1
done | sort | uniq -c | sort -rn | head

# Step 3: if stack repeats on one function → infinite loop / tight retry
# Step 4: if stack rotates through a call graph → burning CPU legitimately
# Step 5: /proc/$PID/stack to check kernel side
cat /proc/$PID/task/$TID/stack
```

Pattern: a thread stuck in `__read_nocancel` for minutes = blocked on a pipe/socket that never returns. A thread cycling through `try_lock; sleep; try_lock` = spin-retry bug.

---

## Process is stuck — how to diagnose

Symptom: zero CPU on any thread, app does nothing.

```bash
# Step 1: Is the process even alive?
ps -p $PID              # exists?
cat /proc/$PID/status | grep State
# 'S' = sleeping (normal)
# 'D' = uninterruptible disk sleep → I/O
# 'Z' = zombie, long dead

# Step 2: what are all threads waiting on?
for tid in $(ls /proc/$PID/task); do
    echo "=== TID $tid ==="
    cat /proc/$PID/task/$tid/stack
done

# Step 3: if stacks show futex_wait, lock contention — find the owner
#   attach with GDB and `info threads`, look at mutex owners

# Step 4: if stacks show io_schedule, disk is the culprit
#   iostat -xm 1 to confirm
```

Pattern: all threads in `futex_wait` on different futexes → deadlock. All threads in `futex_wait` on the same futex → contention, find the holder.

The "if let lock.lock().take()" Case 5 deadlock from CASE-STUDIES.md would show:
- Thread A in `futex_wait` on mutex X
- Thread B in `futex_wait` on mutex X
- No one holding mutex X but there's a parked waker somewhere

This is where `tokio-console` (async) or `gdb-for-debugging` (threaded) with manual mutex inspection wins.

---

## When to hand off to `gdb-for-debugging`

- Understanding WHY a process is in a given state → debugging, not profiling
- Setting up complex scripted breakpoints with commands / conditions
- Reverse debugging / rr-based root-cause analysis
- Reading C++ / Rust complex types in live memory
- Post-mortem core-dump analysis beyond `thread apply all bt`

This skill covers gdb-as-profiler. The adjacent skill covers gdb-as-debugger. They share tools but have different goals.

Boundary:
- If the question is "is it slow?" → this skill
- If the question is "why did it crash?" → `gdb-for-debugging`
- If the question is "is it in a bad state?" → use `gdb-for-debugging`, capture state, bring the findings back here for optimization

### Integration pattern

```
1. Profile (this skill) identifies a hot path you cannot explain with sampling alone
2. Hand off to gdb-for-debugging to capture live state (gcore, watchpoints, rr)
3. Post-mortem analysis reveals the semantic cause (e.g., specific key triggering cache miss)
4. Return here to refine the workload / add instrumentation / optimize
```

Both skills use the same toolchain; pick the framing that matches your current question.

---

## Checklist

- [ ] Have you tried sampler-based profiling first? (samply, perf, py-spy)
- [ ] If not, why? (Stripped symbols? Can't install? Process hung?)
- [ ] Match the technique to the question: count vs sample vs wait-stack vs snapshot
- [ ] Document overhead — strace slows 10×, GDB pauses per sample, gcore freezes briefly
- [ ] For spins / hangs: sample user-stack AND kernel-stack
- [ ] For hidden semantics: rr record + replay with watchpoints
- [ ] For protocol-level latency: strace -T on the specific syscalls
- [ ] Hand off state (core dump, rr trace) to `gdb-for-debugging` when the question shifts from "slow" to "why wrong."
