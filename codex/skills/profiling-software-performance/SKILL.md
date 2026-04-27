---
name: profiling-software-performance
description: >-
  Rank hot paths by CPU, memory, I/O, and contention; hand the optimization skill
  a scored target list. Use when: profile, flamegraph, hotspot, bottleneck, p95/p99,
  IOPS, fsync, "why is this slow".
---

# Profiling Software Performance

> **One Rule:** Ranked evidence before any optimization. No hotspot list → no change.

## Table of Contents

One Rule · The Loop · Pre-Flight Checklist · Quick Triggers · Build Flags · Scenario Fingerprint · Samplers · Metrics · Instrumentation · OS Tuning · Hotspot Table · Cheat Sheet · Anti-Patterns · Hand-off · [Reference Index](#references)

This skill produces the input that [extreme-software-optimization](../extreme-software-optimization/SKILL.md) consumes: a **ranked hotspot table**, a **baseline fingerprint**, and a **hypothesis ledger**. It does not change code to make things faster — that's the next skill. Measurement-only instrumentation is allowed when needed to attribute cost; keep it behind an env flag, document it as profiling-only, and do not mix it with optimization changes. Stop at the hand-off.

## The Loop

```
1. DEFINE       → scenario, metric, budget, golden output — declare what "fast" means
2. ENVIRONMENT  → fingerprint host; ASK before tuning kernel/governor
3. BASELINE     → hyperfine / criterion / bench_baseline.sh → p50/p95/p99/p99.9, ops/sec, RSS
4. INSTRUMENT   → spans, histograms, sentinel frames, structured `perf.profile.*` logs
5. PROFILE      → CPU + alloc + I/O + off-CPU + contention samplers
6. INTERPRET    → ranked hotspots + scaling law + hypothesis ledger
7. HAND OFF     → extreme-software-optimization with Opportunity Matrix inputs
```

Each phase emits a concrete artifact under `tests/artifacts/perf/` (or equivalent). No artifact → phase isn't done.

---

## Pre-Flight Checklist

Run through this before touching any profiler — the most common "bad profile" root cause is skipping one of these.

- [ ] **Scenario is written down** — name, inputs, expected output, success metric (p95/throughput/RSS). "It's slow" is not a scenario.
- [ ] **Build profile is profilable** — debug info on, frame pointers on, `strip=false` (see Build Flags below).
- [ ] **Fingerprint captured** — `scripts/env_fingerprint.sh > fingerprint.json` (CPU, governor, kernel, toolchain, FS). Without this, the number isn't comparable to anything.
- [ ] **Baseline recorded** — ≥ 20 runs via `scripts/bench_baseline.sh`; variance within envelope (check with `scripts/variance_envelope.py`).
- [ ] **Same-host discipline** — no other heavy jobs, no cross-host comparisons, same power profile.
- [ ] **One lever per run** — don't change code and profiler settings together; you lose attribution.
- [ ] **Kernel tuning asked-and-approved** — `scripts/profile_init.sh` prints the plan and prompts before applying.

If any box is empty, stop and resolve it first. Profiling under a broken precondition wastes the whole session.

---

## Quick Triggers

| User says | First move |
|-----------|------------|
| "why is this slow?" | Define scenario + capture baseline before touching code |
| "optimize X" | **Refuse to optimize** until a profile identifies X as top-5 |
| "add a flamegraph" | Check debug symbols + frame pointers are on, then `samply` / `cargo flamegraph` / `py-spy` |
| "it uses too much memory" | Pick peak RSS *or* heap high-watermark; they're different measurements |
| "disk is the bottleneck" / "IOPS" / "fsync is slow" | Prove it first (`vmstat` wa, `/usr/bin/time -v` %CPU, off-CPU flame), then `iostat -xm 1`, `biolatency-bpfcc`, `fio` — see [IO-AND-TRADEOFFS.md](references/IO-AND-TRADEOFFS.md) |
| "too many small files" / "btrfs is fragmented" | `df -i`, `filefrag`, `btrfs filesystem usage`, then the small-file + btrfs playbooks in [IO-AND-TRADEOFFS.md](references/IO-AND-TRADEOFFS.md) |
| "could we cache this in RAM?" | Use the RAM-for-speed tradeoff table (headroom × hit rate × invalidation story) in [IO-AND-TRADEOFFS.md](references/IO-AND-TRADEOFFS.md) |
| "it's slower in prod" | Reach for continuous profiling (Pyroscope / Parca) or an on-demand `pprof` endpoint |
| "no numbers, just feels slow" | Build a minimal repro scenario *first*; profiling noise without a scenario |

---

## Build Flags That Unbreak Profilers

Release builds strip the symbols profilers need. **Always add a `profiling` (or `release-perf`) profile** — never profile the size-optimized release binary.

**Rust** (`Cargo.toml`):
```toml
[profile.release-perf]          # or "profiling"
inherits = "release"
opt-level = 3
lto = "thin"
codegen-units = 1
debug = "line-tables-only"      # cheap, preserves frames; use `true` for deepest unwinds
strip = false
```
```bash
export RUSTFLAGS="-C force-frame-pointers=yes"
cargo build --profile release-perf
```

**Go**: `go build -gcflags='all=-N -l'` kills inlining — only for deep attribution; otherwise leave optimized and rely on `pprof` DWARF.

**C/C++**: `-O2 -g -fno-omit-frame-pointer -gdwarf-4`.

**Node**: run with `--cpu-prof --heap-prof`; add `NODE_OPTIONS="--inspect=0.0.0.0:9229"` for DevTools.

**Python**: no flag changes — `py-spy` / `memray` / `scalene` attach to the running interpreter.

---

## Scenario Fingerprint (required)

Every profile run must carry this header (see [ARTIFACTS.md](references/ARTIFACTS.md) for the template). Without it the number is not comparable to anything:

```
CPU model + cores + SMT state + governor + no_turbo
RAM size + swap
Storage + filesystem + mount options
Kernel version
Toolchain version (rustc, go, node, python)
Build profile (opt-level, lto, codegen-units, debug, panic)
Workload isolation (taskset, cgroup, rch, bare)
Cold vs warm cache
Run ID + git SHA + timestamp
```

The bundled `scripts/bench_baseline.sh` captures this into `fingerprint.json` per run — copy that pattern into the project under measurement.

---

## Sampler Picks (default first, others only if first fails)

| Language | Default | Alloc | Live attach | Notes |
|----------|---------|-------|-------------|-------|
| Rust | `samply record ./bin` | `heaptrack` or `dhat` | `samply` / `pprof-rs` | `cargo flamegraph` is fine; `samply` is the 2025 default — opens in Firefox Profiler |
| Go | `go test -cpuprofile` / `/debug/pprof/profile` | `/debug/pprof/heap` | built-in pprof | `SetMutexProfileFraction(5)` + `SetBlockProfileRate(10_000)` — off by default |
| Node/TS | `--cpu-prof` → Chrome DevTools | `--heap-prof` / `clinic heapprofiler` | `clinic doctor` then `flame` | `clinic doctor` tells you whether it's CPU, event loop, GC, or I/O |
| Python | `py-spy record -o f.svg --pid $PID` | `memray run` (replaces memory_profiler) | `py-spy top --pid $PID` | `scalene` for line-level CPU+RAM; `austin` lowest overhead |
| C/C++ | `perf record -g --call-graph dwarf` | `heaptrack` / `massif --pages-as-heap` | `perf top` | `Tracy` if you own the source and want frame-time visualization |

Full install + flags per language: [LANGUAGE-GUIDES.md](references/LANGUAGE-GUIDES.md).

---

## Metrics You Report (not optional)

```
latency:    p50, p95, p99, p99.9, p99.99, max  (flag p99.9/p99.99 as conservative if samples < 1000)
throughput: ops/sec + bytes/sec
memory:     peak RSS (`/usr/bin/time -v`), heap high-water (allocator), PSS via smaps_rollup
cpu:        avg process CPU% + per-core
scaling:    p95 ratio vs 1-unit baseline across 1/10/50/100/500/1000
```

**Variance envelope** (same-host):
- ≤ 10% p95 drift → noise, ignore
- \> 10% → investigate
- \> 20% or 3 consecutive > 10% → escalate

---

## Instrumentation Shortlist

Add these *before* profiling, keep them behind an env flag:

| Lang | Where | What |
|------|-------|------|
| Rust | hot path | `#[tracing::instrument(skip_all, fields(...))]`; `#[inline(never)] fn _profile_<stage>()` sentinels for flamegraph attribution |
| Rust | metrics | `metrics::histogram!("stage_ms", dur.as_secs_f64()*1e3)`; `hdrhistogram` for tails |
| Go | handlers | `pprof.SetGoroutineLabels`, `trace.StartRegion`, `pprof.Do` |
| Node | hot call | `performance.timerify(fn)`, `monitorEventLoopDelay({resolution:20})` |
| Python | loop | `@viztracer.log_sparse` or `tracemalloc.start()` + `take_snapshot()` |
| C/C++ | frame | `Tracy` `ZoneScoped`; `USDT` probes for `bpftrace` |

Structured logging contract (`scripts/render_hotspot_table.py` accepts either naming):
```
perf.profile.run_start             { scenario, rust_version, hardware }
perf.profile.sample_collected      { sample_count, duration_sec }
perf.profile.span_summary          { span | span_name, cumulative_us, count,
                                     p50_us | p50, p95_us | p95,
                                     category, evidence }
perf.profile.hypothesis_evaluated  { name, verdict: "supports"|"rejects", evidence }
perf.profile.run_complete          { duration_sec, artifacts_written }
```

Full guidance: [INSTRUMENTATION.md](references/INSTRUMENTATION.md).

---

## OS Tuning (ASK FIRST)

These kernel knobs visibly affect numbers but require sudo and change global state. **Always present the list and ask "apply these?" before running.** Revert commands are in [OS-TUNING.md](references/OS-TUNING.md).

Minimum set for Linux profiling accuracy:
```bash
sudo sysctl -w kernel.perf_event_paranoid=-1   # or 1 for user-space profiling
sudo sysctl -w kernel.kptr_restrict=0          # resolve kernel symbols in stacks
sudo sysctl -w kernel.nmi_watchdog=0           # frees a PMU counter
sudo cpupower frequency-set -g performance     # no P-state jitter
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
taskset -c 2,3 ./bin                           # pin to isolated cores (needs isolcpus= boot flag)
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches   # cold-cache runs only
```

macOS: SIP cripples dtrace; prefer `samply`, `xctrace record`, `sample <pid>`, `spindump`. Full matrix + restore commands in [OS-TUNING.md](references/OS-TUNING.md).

---

## Hotspot Table (the hand-off artifact)

```markdown
| Rank | Location           | Metric        | Value   | Category | Evidence            |
|------|--------------------|---------------|---------|----------|---------------------|
| 1    | record_decode      | cumulative    | 841ms   | CPU      | flame_1.svg:0.23    |
| 2    | parser_ast_churn   | cumulative    | 627ms   | CPU/alloc| dhat-heap.json#L412 |
| 3    | flush_async_commits| wait          | 82ms    | I/O      | span_summary.json   |
| 4    | btree_seek         | count*avg     | 3063×x  | CPU      | perf.data           |
| 5    | page_lock_wait     | cumulative    | 0ns     | lock     | off-cpu.svg         |
```

Each row must cite an artifact path — no unreferenced claims.

Also ship a **hypothesis ledger** — name each candidate explanation, mark `supports` / `rejects` with evidence:
```
coalescer batching : rejects — write_message_batch dominates at 25.4s vs flush 0.87s
fsync per msg       : rejects — wbq_flush cumulative 0 vs flush_async_commits 873ms
file layout         : supports — per-msg archive burst dominates profile (25.4s)
lock thrash         : rejects — scaling is sublinear through batch-1000
```

---

## Workflow Cheat Sheet

```bash
# Rust
cargo bench -p <crate> --bench <name> -- --save-baseline before
samply record --save-only -o cpu.json -- ./target/release-perf/bin
heaptrack ./target/release-perf/bin

# Go
go test -bench=. -cpuprofile=cpu.p -memprofile=mem.p -benchmem
go tool pprof -http=:8080 cpu.p
go tool trace trace.out

# Node
node --cpu-prof --cpu-prof-dir=./prof app.js
clinic doctor -- node app.js
autocannon -c 100 -d 30 http://localhost:3000

# Python
py-spy record -o flame.svg --pid $PID --duration 30
memray run --live-remote prog.py
scalene --cpu --memory prog.py

# Wall-clock A/B
hyperfine --warmup 3 --runs 20 --export-json r.json 'cmdA' 'cmdB'
```

---

## Anti-Patterns

| ✗ | Why |
|---|-----|
| Profile the release build | `opt-level="z"` + `strip=true` = no frames → useless flames |
| "Feels slow" without a scenario | No scenario = no comparable baseline = every rerun is random |
| One run, one number | Variance envelope needs ≥ 20 runs; publish p50/p95/p99 or don't publish |
| Mix sampler + code change | Can't attribute — one lever per run |
| Compare prepared-vs-ad-hoc | "Benchmark truthfulness" — normalize API usage before trusting a head-to-head result |
| Report only `time ./bin` | Missing tails; user wire-time (p99) usually ≠ mean |
| Tune kernel without asking | Global state change; get approval, record revert |
| Optimize before hand-off | This skill stops at the hotspot table — hand to extreme-software-optimization |

---

## Hand-off

When the hotspot table + hypothesis ledger + baseline fingerprint are in place, stop.

Say to the user:
> Baseline captured. Top 5 hotspots ranked with evidence in `tests/artifacts/perf/<run-id>/`. Ready for extreme-software-optimization to score targets (Impact × Confidence / Effort ≥ 2.0) and apply one lever at a time.

That's the contract.

---

## References

### Core methodology & artifacts
| Need | File |
|------|------|
| Phase-by-phase methodology (DEFINE → HAND OFF) | [METHODOLOGY.md](references/METHODOLOGY.md) |
| Rust / Go / TS / Python / C++ specifics | [LANGUAGE-GUIDES.md](references/LANGUAGE-GUIDES.md) |
| I/O profiling, IOPS, fsync, btrfs fragmentation, small-file pathology, RAM-for-speed tradeoffs | [IO-AND-TRADEOFFS.md](references/IO-AND-TRADEOFFS.md) |
| Linux + macOS tuning with revert commands | [OS-TUNING.md](references/OS-TUNING.md) |
| Code-level instrumentation patterns | [INSTRUMENTATION.md](references/INSTRUMENTATION.md) |
| BUDGETS.md / fingerprint / hotspot table templates | [ARTIFACTS.md](references/ARTIFACTS.md) |

### Operator library & prompts
| Need | File |
|------|------|
| 19 operator cards (Level-Split, Recode, Measure, Spike, Attribute, Ledger, …) | [OPERATOR-CARDS.md](references/OPERATOR-CARDS.md) |
| "THE EXACT PROMPT" modules per operator / scenario | [PROMPTS.md](references/PROMPTS.md) |
| Symptom → diagnosis → fix encyclopedia | [PATTERNS-ENCYCLOPEDIA.md](references/PATTERNS-ENCYCLOPEDIA.md) |
| Case studies and reusable templates | [CASE-STUDIES.md](references/CASE-STUDIES.md) |

### Reading & interpretation
| Need | File |
|------|------|
| Canonical flame graph reading guide | [FLAMEGRAPH-READING.md](references/FLAMEGRAPH-READING.md) |
| p50/p95/p99 discipline, CV, MAD, bootstrap CIs | [STATISTICAL-RIGOR.md](references/STATISTICAL-RIGOR.md) |
| Honest-gate benchmarks, 5 levels of fairness, apples-to-oranges when correct | [UNBIASED-BENCHMARKING.md](references/UNBIASED-BENCHMARKING.md) |
| 14-question pre/during/post benchmark gate (with attestation artifact) | [HONEST-GATE-CHECKLIST.md](references/HONEST-GATE-CHECKLIST.md) |
| Which dimensions must MATCH vs which IS the comparison's point | [APPLES-TO-APPLES-MATRIX.md](references/APPLES-TO-APPLES-MATRIX.md) |
| Three orthogonal angles must agree before acting on a hypothesis | [TRIANGULATION-RECIPE.md](references/TRIANGULATION-RECIPE.md) |
| Cache hierarchy timing, AoS vs SoA, false sharing | [CACHE-HIERARCHY.md](references/CACHE-HIERARCHY.md) |

### Systems & tools
| Need | File |
|------|------|
| GDB/strace/perf poor-man's-profiler + rr + eBPF | [GDB-STRACE-SYSTEMS-PROFILING.md](references/GDB-STRACE-SYSTEMS-PROFILING.md) |
| Database query-plan profiling (Postgres/SQLite/MySQL) | [DATABASE-PROFILING.md](references/DATABASE-PROFILING.md) |
| LLM/AI profiling: TTFT/TPOT/cache hit rate | [LLM-AI-PROFILING.md](references/LLM-AI-PROFILING.md) |
| GPU/accelerator profiling (CUDA/ROCm/Metal) | [GPU-ACCELERATOR.md](references/GPU-ACCELERATOR.md) |
| Container / K8s / serverless / edge / Wasm profiling | [CONTAINER-CLOUD.md](references/CONTAINER-CLOUD.md) |
| Zipfian / Poisson / replay workload generators | [WORKLOAD-GENERATORS.md](references/WORKLOAD-GENERATORS.md) |

### CI, skill hand-off, and creative expansion
| Need | File |
|------|------|
| GitHub Actions regression gates, runner match, comparators | [CI-REGRESSION-GATES.md](references/CI-REGRESSION-GATES.md) |
| Skill map and hand-off protocols | [CROSS-SKILL.md](references/CROSS-SKILL.md) |
| 20 scored innovation ideas (Impact × Feasibility × Leverage) | [INNOVATION-IDEAS.md](references/INNOVATION-IDEAS.md) |

### Scripts
| Need | File |
|------|------|
| Capture fingerprint.json per run | [scripts/env_fingerprint.sh](scripts/env_fingerprint.sh) |
| Canonical hyperfine baseline wrapper | [scripts/bench_baseline.sh](scripts/bench_baseline.sh) |
| User-gated OS-tuning initializer with revert | [scripts/profile_init.sh](scripts/profile_init.sh) |
| Render ranked hotspot table from perf.profile.* JSONL | [scripts/render_hotspot_table.py](scripts/render_hotspot_table.py) |
| Check variance envelope (≤10% drift) across runs | [scripts/variance_envelope.py](scripts/variance_envelope.py) |
| CI regression comparator (baseline vs candidate p95) | [scripts/ci_compare.sh](scripts/ci_compare.sh) |
| Static bias scan of bench JSON / harness source | [scripts/bias_audit.py](scripts/bias_audit.py) |
| Walk the 14 honest-gate questions interactively, emit signed attestation | [scripts/honest_gate.sh](scripts/honest_gate.sh) |
