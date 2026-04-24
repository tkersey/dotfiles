---
name: lift
description: >-
  Uber performance optimization skill: measurement-driven latency, throughput,
  memory/GC, tail-behavior, algorithmic, systems, and micro-architectural
  optimization with profile evidence, score-gated experiments, behavior proofs,
  golden-output oracles, and regression guards. Use when the user asks to
  optimize, speed up, reduce p95/p99 latency, increase throughput/QPS, lower CPU,
  memory, allocations, GC pauses, syscalls, round trips, or asks for profiling,
  bottleneck analysis, algorithmic improvement, or a benchmarked perf pass. If a
  runnable workload is unavailable, operate in explicitly labelled UNMEASURED
  mode with exact benchmark/profiling/proof commands. Zig-only CLI iteration for
  bench_stats/perf_report must be proven before shipping.
---

# Lift

## Intent

Deliver aggressive performance improvements while preserving behavior, safety,
determinism, and maintainability. Lift is the umbrella optimization skill for
product workloads, service latency, batch/offline throughput, memory pressure,
tail behavior, algorithmic complexity, data layout, concurrency, I/O, and runtime
or compiler tuning.

## Prime Directive

Profile first. Prove behavior unchanged. Change one lever at a time. Measure
before and after on the same workload. Ship only with a regression guard.

Every optimization pass must produce evidence for five questions:

1. What is the performance contract?
2. What does the baseline show?
3. What bottleneck did profiling identify?
4. Why is the proposed change behavior-preserving?
5. What measured delta and guard justify shipping?

## Double Diamond fit

Lift lives in Define -> Deliver.

- Define: write a performance contract, select a proof workload, and choose a
  correctness oracle.
- Deliver: baseline, profile, score opportunities, run tight experiments, prove
  equivalence, verify the result, and install a guard.

## Hard Rules

- Measure before and after every optimization: numbers, environment, command,
  workload, dataset, and sample count.
- Optimize the current bottleneck, not the loudest hunch. Use a profiler, trace,
  counter, or workload-specific observation.
- Require a correctness signal before and after. Never accept a perf win with a
  failing correctness gate.
- Preserve semantics unless the user explicitly approves a semantic trade-off.
- Change one lever per experiment and keep diffs reversible.
- Reject wins smaller than the noise floor unless the result is explicitly
  labelled inconclusive.
- Track second-order regressions: memory, tail latency, CPU, I/O, lock waits,
  cache size, and external cost.
- Stop and ask before raising resource or cost ceilings, unless the user asked
  for that trade-off.
- If no runnable proof workload exists, prefix the response with `UNMEASURED:`
  and provide exact commands. Do not claim wins.
- For Lift-owned CLIs, use Zig binaries only (`bench_stats`, `perf_report`) and
  prove compatibility with marker checks before use.
- After any Zig CLI contract change, update docs and release/tap propagation in
  the same pass so install guidance matches runtime behavior.

## Mode Selection

Use measured mode whenever a proof workload can run.

- **Measured mode:** run baseline and variant on the same workload. Include raw
  sample count, percentiles or throughput, profile evidence, correctness proof,
  and regression guard.
- **Unmeasured mode:** start with `UNMEASURED:`. Provide hypotheses and the exact
  commands that would generate baseline, profile, correctness, and after data.
- **Audit mode:** when the user only asks for a review, produce a ranked
  opportunity matrix and proof plan, but mark untested items as hypotheses.

## Contract Derivation

If the user did not provide a numeric target, define the contract as:

> Improve `<primary metric>` on `<workload>` versus baseline; report delta and do
> not regress `<correctness + secondary metrics>`.

Default primary metric:

- Request-like/service code: latency p95; also report p50, p99, max, throughput,
  CPU, and memory when feasible.
- Batch/offline code: throughput or wall-clock duration; also report CPU%, peak
  RSS, and I/O volume.
- Memory/GC issue: peak RSS, allocation rate, and GC pause; also report latency
  or throughput.
- Startup/cold path: cold-start wall time; separately measure steady-state.
- Tail problem: p99/max and variance drivers; treat variance reduction as the
  primary goal.

## Workload Selection

Pick the first representative runnable proof workload available:

1. User-provided reproduction command or production-like workload.
2. Existing repo benchmark, test harness, Makefile/justfile/taskfile, CI job, or
   README workflow.
3. A minimal harness around the hot path, paired with correctness checks.
4. If none can be created without product ambiguity, operate in `UNMEASURED`
   mode and specify the missing workload requirements.

## Mandatory Optimization Loop

```text
0. PREFLIGHT  -> environment, workload, correctness oracle, warmup sanity
1. BASELINE   -> repeated samples, p50/p95/p99/max or throughput/RSS/allocs
2. PROFILE    -> CPU, allocation, I/O, lock, queue, or tail evidence
3. PROVE      -> golden outputs, invariants, property tests, or differential run
4. SCORE      -> opportunity matrix: Impact x Confidence / Effort
5. IMPLEMENT  -> one lever only, smallest reversible diff
6. VERIFY     -> correctness gate, golden checksum/diff, benchmark rerun
7. REPROFILE  -> confirm bottleneck moved or score next opportunity
8. GUARD      -> benchmark budget, CI gate, monitor, or perf report
```

Default benchmark examples:

```bash
hyperfine --warmup 3 --runs 10 'command'
hyperfine --warmup 3 --runs 30 --export-json baseline.json 'command'
/usr/bin/time -v command 2>&1 | tee time.txt
```

Default behavior oracle examples:

```bash
mkdir -p golden_outputs
for input in test_inputs/*; do ./program "$input" > "golden_outputs/$(basename "$input").out"; done
sha256sum golden_outputs/* > golden_checksums.txt
sha256sum -c golden_checksums.txt
```

## Opportunity Matrix Gate

Only implement a candidate when the score is at least 2.0, unless the user
explicitly requests exploratory work.

```text
Score = (Impact x Confidence) / Effort
Impact:     1=<5%, 2=5-10%, 3=10-25%, 4=25-50%, 5=>50%
Confidence: 1=speculative, 3=plausible, 5=profile-confirmed
Effort:     1=minutes, 3=hours, 5=>1 day or high complexity
```

| Opportunity | Hotspot evidence | Impact | Confidence | Effort | Score | Decision |
|---|---:|---:|---:|---:|---:|---|
| `<change>` | `<profile/trace/counter>` |  |  |  |  | accept/reject |

## Behavior Proof Gate

For every accepted change, document an isomorphism proof before claiming success.
Use `references/behavior-proof.md` for full guidance.

```markdown
## Behavior proof: <change>
- Inputs covered:
- Old behavior:
- New behavior:
- Ordering preserved:
- Tie-breaking unchanged:
- Floating-point semantics:
- RNG/time/concurrency determinism:
- Error handling and edge cases:
- Golden outputs / differential check:
- Correctness command(s):
```

Common proof obligations:

- Batching: same operations, same effective order or explicitly stable reorder.
- Hash/index lookup: same key equivalence, same missing-key behavior, order
  preserved if observable.
- Memoization: function is pure for cache key, invalidation is correct, bounds are
  safe.
- Parallelization: operation is associative/commutative or merge order is stable;
  no data races.
- Approximation: bounded error is explicitly accepted by the user or product
  contract.

## Optimization Ladder

Move down only after higher-leverage tiers are exhausted.

1. Delete work: skip unused computation, redundant parsing, duplicate I/O.
2. Change the algorithm: reduce complexity class or exploit monotonicity.
3. Change data structures/layout: indexes, maps, heaps, SoA, contiguous buffers.
4. Improve memory behavior: preallocation, pooling, arenas, allocation removal.
5. Improve concurrency: shard, pipeline, batch, reduce contention, bound queues.
6. Reduce I/O/serialization: fewer bytes, syscalls, round trips, and copies.
7. Improve tail behavior: backpressure, timeouts, cancellation, variance control.
8. Tune micro-architecture: branch predictability, SIMD, cache lines, prefetch.
9. Tune compiler/runtime: PGO/LTO/JIT warmup/GC flags/inlining.

## Round Escalation

- **Round 0:** Measurement hygiene. Stabilize benchmark and correctness oracle.
- **Round 1:** Standard wins: N+1 elimination, batching, indexing, memoization,
  preallocation, cache bounds, JSON/serialization cleanup, log formatting removal.
- **Round 2:** Algorithmic and architectural wins: DP, graph reductions,
  streaming, partitioning, lock sharding, layout rewrites, queue/admission fixes.
- **Round 3:** Advanced/exotic wins: convex/semiring recasts, FFT/NTT, suffix
  arrays, sketches, cache-oblivious recursion, meet-in-the-middle, specialized
  indexes, PGO/LTO/SIMD.

Each round starts with a fresh profile because bottlenecks shift.

## Fast Pattern Tiers

| Tier | Pattern | When | Proof concern |
|---|---|---|---|
| 1 | N+1 -> batch | Sequential external calls | Result ordering and retry semantics |
| 1 | Linear scan -> index/hash | Repeated keyed lookup | Key equality and observable order |
| 1 | Memoization | Repeated pure computation | Cache key, invalidation, bounds |
| 1 | Buffer/prealloc reuse | Allocation in hot loop | Aliasing and lifetime safety |
| 2 | Binary search/two-pointer | Sorted or monotone data | Precondition validation |
| 2 | Prefix sums/sliding window | Repeated range queries | Static data or update semantics |
| 2 | Priority queue/top-k | Scheduling or ranking | Tie-breaking and stability |
| 3 | Arena/pool/SmallVec/SoA | Allocation or locality bound | Lifetime, ownership, memory cap |
| 3 | Bloom/sketch/HLL | Membership/counting at scale | Error bound and acceptance |
| 3 | Lock sharding/queues | Contention/tail bound | Races, fairness, backpressure |

## Language Triage Cheatsheet

| Ecosystem | First profiler | Allocation/memory | Fast grep signals |
|---|---|---|---|
| Rust/Zig/C/C++ | `perf`, flamegraph, Instruments | `heaptrack`, DHAT, massif | clones/copies, boxes, formatting, allocs |
| Go | `go tool pprof`, `go tool trace` | heap/alloc profiles, `GODEBUG=gctrace=1` | `interface{}`, `defer` in loops, `fmt.Sprintf` |
| Node/TypeScript | `clinic flame`, `node --prof` | DevTools heap, event-loop delay | JSON parse/stringify, sync fs, await-in-loop |
| Python | `py-spy`, `cProfile`, `scalene` | `memory_profiler`, `tracemalloc` | `iterrows`, string `+=`, list membership |
| JVM | JFR, async-profiler | allocation/lock events, GC logs | boxing, reflection, synchronized hot path |

## Zig CLI Iteration Repos

When iterating on the Zig-backed `bench_stats` / `perf_report` helper CLI path,
use these two repos:

- `skills-zig` (`$HOME/workspace/tk/skills-zig`): source for `bench_stats` and
  `perf_report`, build/test wiring, and release tags.
- `homebrew-tap` (`$HOME/workspace/tk/homebrew-tap`): Homebrew formula updates
  and checksum bumps for released `lift` binaries.

For Lift-owned CLIs, prove marker compatibility before use:

```bash
command -v bench_stats && bench_stats --help 2>&1 | grep -q bench_stats.zig
command -v perf_report && perf_report --help 2>&1 | grep -q perf_report.zig
bench_stats --input samples.txt --unit ms
perf_report --title "Perf pass" --owner "team" --system "service" --output /tmp/perf-report.md
```

## Brew-aware Launcher Pattern

```bash
run_lift_tool() {
  local subcommand="${1:-}"
  if [ -z "$subcommand" ]; then
    echo "usage: run_lift_tool <bench-stats|perf-report> [args...]" >&2
    return 2
  fi
  shift || true

  local bin="" marker=""
  case "$subcommand" in
    bench-stats) bin="bench_stats"; marker="bench_stats.zig" ;;
    perf-report) bin="perf_report"; marker="perf_report.zig" ;;
    *) echo "unknown lift subcommand: $subcommand" >&2; return 2 ;;
  esac

  install_lift_direct() {
    local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
    if ! command -v zig >/dev/null 2>&1; then
      echo "zig not found. Install Zig and retry." >&2
      return 1
    fi
    if [ ! -d "$repo" ]; then
      echo "skills-zig repo not found at $repo." >&2
      echo "clone it with: git clone https://github.com/tkersey/skills-zig \"$repo\"" >&2
      return 1
    fi
    (cd "$repo" && zig build -Doptimize=ReleaseSafe) || return 1
    [ -x "$repo/zig-out/bin/$bin" ] || return 1
    mkdir -p "$HOME/.local/bin"
    install -m 0755 "$repo/zig-out/bin/$bin" "$HOME/.local/bin/$bin"
  }

  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi

  if [ "$(uname -s)" = "Darwin" ]; then
    command -v brew >/dev/null 2>&1 || { echo "homebrew is required on macOS" >&2; return 1; }
    brew install tkersey/tap/lift || return 1
  else
    install_lift_direct || return 1
  fi

  if command -v "$bin" >/dev/null 2>&1 && "$bin" --help 2>&1 | grep -q "$marker"; then
    "$bin" "$@"
    return
  fi

  echo "missing compatible $bin binary after install attempt" >&2
  return 1
}
```

## Deliverable Format (Chat)

If unmeasured, prefix the response with `UNMEASURED:` and fill the sections with
an exact measurement/profiling/proof plan. Do not claim deltas.

Output these sections, numbers first:

**Performance contract**
- Metric + percentile:
- Workload command:
- Dataset:
- Environment:
- Constraints:

**Baseline**
- Samples + warmup:
- Results:
- Noise floor / variance:

**Bottleneck evidence**
- Tool + artifact:
- Hot path / contention / queue:
- Bound classification:

**Opportunity matrix**
- Candidate -> score -> decision:

**Behavior proof**
- Oracle:
- Invariants:
- Golden/differential/property check:

**Experiments**
- Hypothesis -> change -> measured delta -> decision:

**Result**
- Variant results:
- Delta vs baseline:
- Confidence:
- Trade-offs / regressions checked:

**Regression guard**
- Benchmark/budget/monitor:
- Threshold:

**Validation**
- Correctness command(s) -> pass/fail:
- Performance command(s) -> numbers:
- CLI proof if applicable:

**Residual risks / next steps**
-

`lift_compliance: mode=<measured|unmeasured|audit>; workload=<cmd>; baseline=<yes/no>; after=<yes/no>; correctness=<yes/no>; bottleneck_evidence=<yes/no>; behavior_proof=<yes/no>; score_gate=<yes/no>`

## Core References (Load on Demand)

- `references/playbook.md` — master flow, doctrine, and loop.
- `references/measurement.md` — benchmarking, statistics, noise, and reporting.
- `references/profiling-tools.md` — tool matrix and evidence artifacts.
- `references/behavior-proof.md` — golden outputs, invariants, isomorphism proof.
- `references/opportunity-matrix.md` — impact/confidence/effort score gate.
- `references/optimization-tactics.md` — tactical catalog by layer.
- `references/algorithms-and-data-structures.md` — algorithmic and structural levers.
- `references/systems-and-architecture.md` — CPU, memory, OS, network tactics.
- `references/latency-throughput-tail.md` — queueing, variance, and backpressure.
- `references/language-specific.md` — ecosystem-specific profilers and red flags.
- `references/advanced-techniques.md` — round-2/round-3 advanced patterns.
- `references/checklists.md` — fast triage and validation checklists.
- `references/anti-patterns.md` — traps to reject.

## Assets

- `assets/perf-report-template.md` — ready-to-edit measured or unmeasured report.
- `assets/experiment-log-template.md` — one-variable experiment ledger.
- `assets/isomorphism-proof-template.md` — per-change behavior proof.
- `assets/opportunity-matrix-template.md` — score-gated opportunity table.
- `assets/golden-output-manifest.md` — golden-output capture checklist.
