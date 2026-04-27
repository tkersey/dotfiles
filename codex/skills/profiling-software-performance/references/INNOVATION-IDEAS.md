# Innovation Ideas — Creative Expansions for Profiling Practice

> Idea-wizard output. Each idea scored on **Impact**, **Feasibility**, **Leverage**. Not all equally mature — some are novel tool applications, some are systems to build, some are half-baked hypotheses.

## Contents

1. [Closed-loop regression archaeology](#1-closed-loop-regression-archaeology)
2. [Perf budget as "latency debt"](#2-perf-budget-as-latency-debt)
3. [Profile-as-code DSL](#3-profile-as-code-dsl)
4. [Workload fuzzing for profiling](#4-workload-fuzzing-for-profiling)
5. [Causal profiler integration (coz) as first-class](#5-causal-profiler-integration-coz-as-first-class)
6. [Agent-swarm profiling dispatcher](#6-agent-swarm-profiling-dispatcher)
7. [Whole-machine energy accounting](#7-whole-machine-energy-accounting)
8. [Continuous perf DNA fingerprint-shift detector](#8-continuous-perf-dna-fingerprint-shift-detector)
9. [Perf PR reviewer bot](#9-perf-pr-reviewer-bot)
10. [Bisect the profile, not the bug](#10-bisect-the-profile-not-the-bug)
11. [Perfmon-as-a-unit-test](#11-perfmon-as-a-unit-test)
12. [Time-Travel Profiling (TTP)](#12-time-travel-profiling-ttp)
13. [The "Perf Story" narrative artifact](#13-the-perf-story-narrative-artifact)
14. [Real-workload shadowing](#14-real-workload-shadowing)
15. [Deterministic replay benches for flakiness-immune CI](#15-deterministic-replay-benches-for-flakiness-immune-ci)
16. [Profiling-aware code review](#16-profiling-aware-code-review)
17. [Hardware-selection as a budget question](#17-hardware-selection-as-a-budget-question)
18. [Cross-project "perf corpus" mining](#18-cross-project-perf-corpus-mining)
19. [Adversarial bench challenger](#19-adversarial-bench-challenger)
20. [LLM-assisted hotspot-to-patch loop](#20-llm-assisted-hotspot-to-patch-loop)

---

## 1. Closed-loop regression archaeology

**Impact**: high · **Feasibility**: medium · **Leverage**: high

When a gate fires, automatically:
1. Download the last-known-good profile + current profile
2. Diff the flame graphs (`difffolded.pl`)
3. Identify the red bar with the largest delta
4. `git blame` the file containing that symbol
5. Post the commit + diff + owner to the PR comment

Turns the gate from "regression exists" → "regression is likely in commit `<SHA>` touching `<file>:<line>`, owned by `<author>`" with zero human bisect.

**Build**:
- One tool in `scripts/`: takes old + new `pprof.json`, emits a ranked delta table
- Wire into `perf-gate.yml` after the comparison step
- Handle the "dependency bump" edge case by looking at Cargo.lock/package-lock diff separately

---

## 2. Perf budget as "latency debt"

**Impact**: high · **Feasibility**: medium · **Leverage**: high

Borrow financial-debt framing: every ms over budget is "debt." Track across releases:

```
BUDGETS.md → becomes LIVE dashboard
For each benchmark, track:
  - current_p95
  - budget_p95
  - debt_ms = max(0, current - budget)
  - interest_accumulated = sum of debt_ms × days_in_that_state
```

Visualize debt as a stock over time. Now "we have 470ms of latency debt" becomes an organizational number — budgets get tended like budgets, not forgotten like README files.

**Build**:
- `scripts/latency_debt.py` emits a dashboard from the history of run-ids
- Weekly cronjob posts debt trend to Slack/email
- Debt exceeding threshold creates a beads issue

---

## 3. Profile-as-code DSL

**Impact**: medium · **Feasibility**: medium · **Leverage**: high

A YAML (or Rust-macro) DSL for describing a profiling scenario:

```yaml
scenario: archive_batch_100
metric:   p95
budget_ms: 250
workload:
  distribution: zipf
  alpha: 1.0
  batch_sizes: [1, 10, 50, 100, 500, 1000]
  payload_size: { dist: lognormal, mean: 5000, sigma: 1.5 }
warmup:   { runs: 3, min_seconds: 1 }
measurement: { runs: 20, percentiles: [50, 95, 99, 99.9] }
fingerprint_required:
  cpu_model: match
  kernel_major: match
  fs: ext4|xfs|btrfs (per-fs budget applies)
profilers:
  cpu:   samply
  alloc: heaptrack
  off_cpu: offcputime-bpfcc
hypotheses:
  - name: fsync_per_msg
    falsifier: wbq_flush cumulative > 10ms
  - name: file_layout
    falsifier: archive.write_msg cumulative > 50% of e2e
```

Then `profile run scenario.yaml` does everything. The DSL becomes the single source of truth for "what does it mean to profile this thing."

**Build**:
- Start with a simple YAML schema + Python runner that shells out to existing tools
- Over time, migrate to a `profiler-kit` Rust crate

---

## 4. Workload fuzzing for profiling

**Impact**: medium · **Feasibility**: high · **Leverage**: medium

Apply fuzzing concepts to profiling: instead of "run the standard workload and profile," systematically vary workload dimensions (Zipfian α, payload size, concurrency, error rate) and find **the workload that triggers the worst p99**.

```python
for alpha in [0.5, 0.8, 1.0, 1.2, 1.5]:
    for concurrency in [1, 4, 16, 64]:
        for payload_median in [100, 1000, 10000, 100000]:
            run_bench(alpha, concurrency, payload_median)
            capture_p99()

# Find the cell with worst p99 — that's your weakness
# Profile that cell deeply (off-CPU flame, span summary)
```

Discovers non-obvious performance cliffs: "p99 balloons at α=1.2, concurrency=16, payload_median=10KB" — a specific operating point you wouldn't have hit with a single bench.

**Build**:
- Integrate with `WORKLOAD-GENERATORS.md`'s generator helpers
- Output a heatmap of p99 × workload parameters
- Highlight cells where p99 > 3× neighboring cells (cliff detection)

---

## 5. Causal profiler integration (coz) as first-class

**Impact**: high · **Feasibility**: medium · **Leverage**: high

`coz` (Curtsinger & Berger, SOSP'15) answers the question flamegraphs can't: "If I make function X N% faster, how much does the overall system speed up?" This is the ACTUAL question you care about when prioritizing optimization.

Most teams ignore coz because it needs source-code annotations. The integration idea: **auto-annotate hot paths identified by the flame graph** with `coz::progress!()` and re-run.

```
Step 1: regular samply flame → ranked hotspots
Step 2: annotate top-10 frames with coz::progress!
Step 3: coz run
Step 4: read "virtual speedup" per frame — which optimizations ACTUALLY pay off
```

Changes the prioritization from "widest frame" (may not be the critical path) to "frame whose speedup actually helps" (the actual leverage).

**Build**:
- A script that patches a Rust source tree: reads flame top-N, inserts `coz::progress!()` at the entry of each hot function
- Run coz + report virtual-speedup rank table
- Now Impact column in the hotspot table is measured, not estimated

---

## 6. Agent-swarm profiling dispatcher

**Impact**: medium · **Feasibility**: medium · **Leverage**: medium

Profiling benefits from parallel exploration — different machines profile different scenarios simultaneously. Spawn an ntm-swarm where each pane:
- Runs a different workload axis (light load / medium / heavy / bursty)
- On a different filesystem (ext4 / xfs / btrfs / tmpfs)
- Captures its own artifact bundle
- Writes to a shared `hypothesis.md` with marker-bounded sections

Then a supervisor agent aggregates. Parallelism turns 6 hours of sequential exploration into 30 minutes of swarm exploration.

**Build**:
- `profile-swarm` command using ntm patterns
- Shared state via `tests/artifacts/perf/<run-id>/swarm/`
- Each pane emits a delta block; supervisor merges (same pattern as the `operationalizing-expertise` kickoff model)

---

## 7. Whole-machine energy accounting

**Impact**: medium · **Feasibility**: medium · **Leverage**: medium

Energy (watts × seconds) is an increasingly important dimension. Modern Intel/AMD CPUs expose RAPL (Running Average Power Limit) counters:

```bash
perf stat -a -e 'power/energy-pkg/,power/energy-ram/,power/energy-cores/' ./bin args
# Joules per workload
```

Report not just latency and throughput, but **joules per request**. Useful when:
- Choosing allocator strategies (mimalloc vs jemalloc may differ on power)
- Rust async vs sync (Tokio adds CPU work, affects power)
- Quantization choices for ML inference
- Cloud cost proxy ("energy per request" correlates with billing)

Especially relevant for FinOps: a 10% latency win that costs 20% more energy is the wrong direction on operating cost.

**Build**:
- Add `power_joules` and `power_per_op` fields to `fingerprint.json` and `span_summary`
- In ARTIFACTS.md, add a per-bench energy row
- On Apple Silicon, use `powermetrics --samplers cpu_power` equivalent

---

## 8. Continuous perf DNA fingerprint-shift detector

**Impact**: high · **Feasibility**: medium · **Leverage**: very high

Every production release captures a "perf DNA" snapshot: top-50 functions by cumulative CPU, alloc rate per span, typical p95 distribution. Store as a versioned fingerprint.

When prod p99 shifts unexpectedly, diff the current DNA against the last-known-good DNA. Which functions are suddenly hotter? Which are colder? This gives you a starting point for forensics BEFORE opening a flamegraph — the high-level "what changed."

This is like structural-health monitoring for the perf profile.

**Build**:
- Continuous profiler (Pyroscope / Parca) feeds into a daily DNA snapshot
- Compare today's DNA to last week's (frame-by-frame % change)
- Alert on any frame with > 50% change in either direction
- Operational impact: catches drift even when no explicit bench shows it

---

## 9. Perf PR reviewer bot

**Impact**: high · **Feasibility**: medium · **Leverage**: very high

Every PR that touches code in the top-N hotspot list auto-gets a "perf review" comment:

```
### Perf review (automated)

You touched `record_decode` which is ranked #1 in the current hotspot table.

Expected-impact checks:
- Does this PR change the allocation pattern? [no clones added per diff] ✓
- Does this PR change the loop structure? [yes — nested depth 2 → 3] ⚠
- Does this PR touch the hot data layout? [no field reordering] ✓

Suggested action: Run `cargo bench record_decode` locally and attach results to the PR.
Perf gate will also run.
```

Mechanics:
- Maintain a list of "perf-sensitive symbols" in a yaml
- GitHub webhook on PR: intersect diff symbols with the sensitive list
- If overlap, post a comment with auto-generated checks
- Run the targeted bench on the PR (not full suite — too expensive)

This turns `extreme-software-optimization`'s "score Impact × Confidence / Effort" into something that can guide PR review automatically.

---

## 10. Bisect the profile, not the bug

**Impact**: medium · **Feasibility**: high · **Leverage**: high

Classic bisect: "find the commit that broke test X." Profile bisect: "find the commit that moved the dominant hot path."

```bash
git bisect start HEAD-100 HEAD
git bisect run scripts/profile_bisect.sh  # exits 0 if top hotspot is X, 1 otherwise
```

The test: run the bench, capture `samply` output, ask "is `fn_X` still #1?" Good → 0, bad → 1. Bisect lands on the commit that made `fn_X` lose rank (e.g., because fn_Y suddenly got much slower, or fn_X got much faster).

Uses: forensic analysis of WHEN the shape of your app changed, not just WHEN it got slower.

---

## 11. Perfmon-as-a-unit-test

**Impact**: medium · **Feasibility**: high · **Leverage**: high

Treat specific perf properties as unit tests. E.g.:

```rust
#[test]
fn archive_write_batch_100_allocs_less_than_1000_times() {
    let stats = dhat::start_profiling();
    archive_write_batch(vec![...; 100]);
    let heap = dhat::HeapStats::current();
    assert!(heap.total_blocks < 1000, "batch-100 allocated {} blocks", heap.total_blocks);
}

#[test]
fn archive_write_batch_100_completes_under_budget() {
    let t = Instant::now();
    archive_write_batch(vec![...; 100]);
    let elapsed = t.elapsed();
    assert!(elapsed < Duration::from_millis(250), "batch-100 took {:?}", elapsed);
}
```

These live in the test suite. They fail the build when alloc count or latency breaches. Unlike benches (statistical, report), these are binary pass/fail. Use for invariants — "this operation must never allocate in the hot path," "this function must return in < 10ms on reference host."

---

## 12. Time-Travel Profiling (TTP)

**Impact**: very high · **Feasibility**: low · **Leverage**: very high

Combine `rr record` with post-hoc profiling tools. Instead of profiling live (can't reproduce the exact p99 moment), record a session, then replay it while profiling:

```bash
rr record -- ./bin args              # produces a deterministic trace
# later:
rr replay -- samply record ...       # profile the replay — same timeline, different tool
rr replay -- heaptrack ...           # same timeline, different axis
```

Lets you profile multiple axes (CPU, alloc, syscalls) of the SAME execution. Currently each profiler sees a different execution (non-deterministic). TTP makes them comparable.

Not fully feasible today — rr + samply integration is rough — but a high-leverage direction.

---

## 13. The "Perf Story" narrative artifact

**Impact**: medium · **Feasibility**: high · **Leverage**: high

Every major optimization lands with a 1-page markdown narrative:

```markdown
# Perf Story: batch coalescer (round 5)

## Before
batch-100 p95 was 3491ms. The budget was 250ms. Gap: 14×.

## Hypotheses we considered
1. fsync-per-msg — rejected: wbq_flush cumulative 0us
2. coalescer-batching — supports: write_message_batch dominated at 25.4s
3. file-layout — supports: per-msg archive burst dominated profile

## What we shipped
Grouped commits into 100-entry batches before fsync. New write_message_batch_bundle
fuses N individual writes into one linearized bundle.

## Result
batch-100 p95: 3491ms → 1200ms (2.9× faster, still 4.8× gap to budget)

## What didn't work
Initial attempt used sled's merge_operator — 20% slower. Switched to in-process
aggregation.

## Where we can't win (yet)
Single-msg path latency (batch-1) is unaffected; that path needs a separate round.

## Operator cards exercised
📏 Measure, 🗂 Ledger, 🎯 Attribute, ⊞ Scale-Check, 🛡 Isomorphism
```

The narrative is the OUTPUT of a round. It's readable by people who weren't there. It's how institutional knowledge survives team churn. Also a beautiful artifact for PR descriptions, docs, and recruiting.

**Build**:
- A template in `scripts/` that runs against the latest run-id dir and prompts the engineer for the 4-5 narrative fields
- Committed to `docs/perf-stories/YYYY-MM-DD-<topic>.md`
- Indexed into a `docs/perf-stories/INDEX.md`

---

## 14. Real-workload shadowing

**Impact**: high · **Feasibility**: medium · **Leverage**: very high

Instead of synthetic workloads, dup production traffic to a shadow environment and profile it.

```
prod request → [mirror] → shadow (older code OR newer code)
                        → shadow profiler captures
```

The shadow environment:
- Receives real traffic (key distribution, bursts, sizes all correct by definition)
- Has profilers attached
- Doesn't affect prod (responses discarded)

Tools: goreplay (tees HTTP), Linkerd/Istio traffic mirroring, kafka consumer groups. The old joke "profiling in prod" becomes literal.

Classic FinOps / safety: mirror only to staging-sized fleet; budget the mirror infrastructure.

---

## 15. Deterministic replay benches for flakiness-immune CI

**Impact**: medium · **Feasibility**: high · **Leverage**: high

CI benches are flaky because runners vary. Solution: record a "benchmark recording" that plays back deterministically.

```
Setup once: run bench against prod, record all HTTP calls / DB queries / clock reads
CI: replay the recording, measure only CPU/alloc time (skip I/O waits → deterministic)
```

Since replay is deterministic, CI flakiness goes near-zero. But you're measuring compute only — network / disk contribution needs separate tracking.

Tools: `mockttp`, `vcr.py`, `wiremock`. For DB, use in-memory sqlite with a seeded state.

---

## 16. Profiling-aware code review

**Impact**: medium · **Feasibility**: high · **Leverage**: high

When reviewing a PR, auto-render:
- Hotspot table for files touched
- Flame subset for functions in the diff
- Alloc attribution for any new `Vec::new` / `Box::new` / `clone` / `to_string`

The reviewer sees the perf context alongside the logic. A casual reader who wouldn't have thought to check perf gets a surfaced signal.

Integrates with #9 (PR bot) — that focuses on gating; this focuses on enabling thoughtful review.

---

## 17. Hardware-selection as a budget question

**Impact**: high · **Feasibility**: medium · **Leverage**: medium

Turn "what instance type do we need?" from hand-waving into measurement.

```
For each instance type in candidate list:
  - Run the canonical bench
  - Capture p95 / throughput / RSS / joules
  - Compute $/unit of work

Plot: cost-per-request vs latency. Pareto frontier = hardware candidates that are not dominated.
Pick from the frontier based on priorities.
```

Makes "we need m5.2xlarge" into "these are the 3 instance types on the cost/latency Pareto frontier." Huge FinOps win if done regularly.

---

## 18. Cross-project "perf corpus" mining

**Impact**: medium · **Feasibility**: high · **Leverage**: high

Mine your historical benchmark runs across projects. Look for:
- Optimization techniques that repeatedly worked (reuse patterns)
- Hypotheses you reject in project A that return in project B (déjà vu)
- Fingerprint shifts correlated with specific kernel versions
- Benchmarks where the tail always > 5× p50 (structural vs coincidental)

Emits a meta-learning log: "Your typical p99/p50 ratio for HTTP workloads is 4.2× — today's is 12×, investigate."

Cross-project meta-learning is low-friction leverage.

---

## 19. Adversarial bench challenger

**Impact**: medium · **Feasibility**: medium · **Leverage**: medium

Every bench comparison result gets run past an adversarial agent that:
- Re-reads the bench code
- Looks for the biases in UNBIASED-BENCHMARKING.md's anti-pattern list
- Flags any that might apply
- Posts as an inline PR comment

Automated honest-gate lint. If the adversary can't find flaws, the claim is trustworthy-er.

Tie-in to `multi-model-triangulation` pattern: get Codex, Gemini, and Claude to all lint independently, only accept claim when all three pass.

---

## 20. LLM-assisted hotspot-to-patch loop

**Impact**: very high · **Feasibility**: medium · **Leverage**: very high

Close the loop between profiling and patching:

1. Profile emits hotspot_table.md
2. For each top-5 hotspot, an LLM reads the source of the hot function + the flame context
3. LLM proposes 1-3 candidate optimizations ("add `with_capacity`", "replace `clone` with `Cow`", "use `FxHashMap`")
4. For each candidate, LLM writes a PR-style diff with an explanation
5. Each diff runs through the perf gate automatically
6. Diffs that pass the gate (faster, no regression) get offered to the human as ready-to-merge

This makes the skill itself the loop, not just a way to produce the hotspot table. Humans review the candidate diffs; approved ones ship.

The user's `extreme-software-optimization` skill is already the human-driven version of this. The next step is making an LLM-assisted version as a first draft.

---

## Scoring summary

```
| # | Idea                                          | Impact | Feasibility | Leverage |
|---|-----------------------------------------------|--------|-------------|----------|
| 1 | Regression archaeology                        |   H    |      M      |    H     |
| 2 | Latency debt dashboard                        |   H    |      M      |    H     |
| 3 | Profile-as-code DSL                           |   M    |      M      |    H     |
| 4 | Workload fuzzing                              |   M    |      H      |    M     |
| 5 | Causal profiler (coz) as first-class          |   H    |      M      |    H     |
| 6 | Agent-swarm profiling dispatcher              |   M    |      M      |    M     |
| 7 | Energy accounting                             |   M    |      M      |    M     |
| 8 | Perf DNA fingerprint-shift detector           |   H    |      M      |    VH    |
| 9 | Perf PR reviewer bot                          |   H    |      M      |    VH    |
|10 | Bisect the profile                            |   M    |      H      |    H     |
|11 | Perfmon-as-unit-test                          |   M    |      H      |    H     |
|12 | Time-Travel Profiling (TTP)                   |   VH   |      L      |    VH    |
|13 | Perf Story narrative artifact                 |   M    |      H      |    H     |
|14 | Real-workload shadowing                       |   H    |      M      |    VH    |
|15 | Deterministic replay benches                  |   M    |      H      |    H     |
|16 | Profiling-aware code review                   |   M    |      H      |    H     |
|17 | Hardware selection as budget question         |   H    |      M      |    M     |
|18 | Cross-project perf corpus mining              |   M    |      H      |    H     |
|19 | Adversarial bench challenger                  |   M    |      M      |    M     |
|20 | LLM-assisted hotspot-to-patch loop            |   VH   |      M      |    VH    |
```

### Prioritization

**Ship soon** (high Impact × high Feasibility × high Leverage):
- #1 Regression archaeology
- #9 PR reviewer bot
- #11 Perfmon-as-unit-test
- #13 Perf Story artifact
- #16 Profiling-aware code review

**Build as project** (high Leverage, needs real investment):
- #2 Latency debt dashboard
- #5 Causal profiler integration
- #8 Perf DNA detector
- #14 Real-workload shadowing
- #20 LLM-assisted hotspot-to-patch loop

**Research / long-term**:
- #12 Time-Travel Profiling
- #17 Hardware selection framework

---

## How to use this list

These are NOT automatic to-dos. They are seeds. Run each through the operator cards (OPERATOR-CARDS.md):

- `⊘ Level-Split` — which axis does the idea move on?
- `⚡ Spike` — can you prototype it in a day to validate?
- `💰 Score` — Impact × Confidence / Effort — which earn their cost?
- `⊞ Scale-Check` — is the claimed leverage real at your scale?

An idea that scores ≥ 2.0 on `💰 Score` is a candidate. Apply `🪣 Bucket` to group related ideas (e.g., #1, #9, #16 all form a "PR-perf-loop" bucket and may ship together).

---

## Closing — growth mindset

Good profiling practice expands. The operator cards are the present. This file is the future. Every round, ask:
- What move did I repeat today that isn't yet in OPERATOR-CARDS.md?
- What tool would have saved me 2 hours today?
- What did I do twice that should have been done once?

Write the idea here. Later, promote it to an operator card or a real project.

The skill improves because the practice improves. The practice improves because the skill names new moves. Mutually reinforcing.
