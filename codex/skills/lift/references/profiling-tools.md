# Profiling Tool Matrix

## Goal

Pick one primary profiler and one secondary signal. Save artifacts so the
performance claim is reviewable.

## Universal Signals

| Question | Tool/examples | Evidence |
|---|---|---|
| Where is CPU time? | sampling profile, flamegraph, `perf report` | hot frames/stacks |
| Where are allocations? | heap profile, allocation trace | alloc rate, types, call sites |
| Why is tail high? | trace, queue depth, p99 slices | waits, HOL blocking, retries |
| Is I/O dominant? | syscall/network tracing | bytes, waits, round trips |
| Is contention dominant? | lock/block/mutex profile | wait time, lock owner/hot locks |
| Is hardware limiting? | counters | cache misses, branch misses, cycles |

## Rust / C / C++ / Zig

```bash
cargo flamegraph --release -- <args>
perf record -g -- command && perf report
perf stat -d -- command
heaptrack command && heaptrack_gui heaptrack.*.zst
valgrind --tool=massif command
strace -c command
```

Look for clones/copies, hot allocation, default hashers, formatting in hot paths,
pointer chasing, small repeated syscalls, and synchronization in tight loops.

## Go

```bash
go test -bench . -benchmem ./...
go test -bench BenchmarkName -cpuprofile cpu.pprof -memprofile mem.pprof
go tool pprof -http :0 cpu.pprof
go test -run TestName -trace trace.out && go tool trace trace.out
go build -gcflags='-m -m' ./... 2>&1 | grep 'escapes to heap'
GODEBUG=gctrace=1 ./binary
```

Also inspect block and mutex profiles for contention.

## Node.js / TypeScript

```bash
node --prof app.js && node --prof-process isolate-*.log > profile.txt
node --inspect app.js
clinic doctor -- node app.js
clinic flame -- node app.js
clinic bubbleprof -- node app.js
```

Look for synchronous filesystem calls, JSON parse/stringify loops, await-in-loop,
object spreading in hot paths, and event-loop delay.

## Python

```bash
python -m cProfile -s cumtime script.py > profile.txt
py-spy record -o profile.svg -- python script.py
py-spy top --pid <pid>
scalene script.py
python -m memory_profiler script.py
```

Look for `iterrows`, list membership, string concatenation, repeated regex
compilation, object churn, global/attribute lookup in hot loops, and non-vectorized
numeric work.

## JVM

```bash
# JFR
java -XX:StartFlightRecording=filename=recording.jfr,dumponexit=true -jar app.jar

# async-profiler examples
./profiler.sh -e cpu -d 30 -f cpu.svg <pid>
./profiler.sh -e alloc -d 30 -f alloc.svg <pid>
./profiler.sh -e lock -d 30 -f lock.svg <pid>
```

Look for boxing, reflection, synchronized hot paths, allocation churn, GC pauses,
and JIT warmup artifacts.

## Databases and Services

- Query plans: `EXPLAIN` / `EXPLAIN ANALYZE`.
- N+1 detection: count queries per request and repeated identical lookups.
- Network: round trips, payload size, retry rate, connection pool waits.
- Queues: queue depth, service time, utilization, consumer lag.

## Evidence Artifact Checklist

- profile command and timestamp
- flamegraph/profile path
- top 5 hot frames or waits
- bound classification
- candidate opportunity mapping from evidence to change
