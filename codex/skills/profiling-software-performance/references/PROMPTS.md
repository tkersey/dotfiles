# THE EXACT PROMPTS — Profiling Workflow Library

> Copy-paste-ready prompts for every stage of the profiling loop. Each prompt encodes a workflow and includes commentary on why each prompt is shaped the way it is.

The pattern is lifted from `sw/PROMPTS.md` — skills are instructions for YOU, and reusable prompts make that self-instruction concrete.

## Contents

1. [Kickoff — start a profiling session](#kickoff--start-a-profiling-session)
2. [DEFINE — get the scenario on paper](#define--get-the-scenario-on-paper)
3. [Environment prep — tune the host safely](#environment-prep--tune-the-host-safely)
4. [Baseline — capture the number](#baseline--capture-the-number)
5. [Instrumentation pass](#instrumentation-pass)
6. [Profile run](#profile-run)
7. [Interpret — build the hotspot table](#interpret--build-the-hotspot-table)
8. [Hypothesis ledger](#hypothesis-ledger)
9. [Scaling-law harness](#scaling-law-harness)
10. [Regression hunt](#regression-hunt)
11. [Cache-tradeoff design](#cache-tradeoff-design)
12. [btrfs-specific triage](#btrfs-specific-triage)
13. [fsync-bound triage](#fsync-bound-triage)
14. [Off-CPU / wait investigation](#off-cpu--wait-investigation)
15. [Hand-off to extreme-software-optimization](#hand-off-to-extreme-software-optimization)
16. [Escalation — stuck after 3 rounds](#escalation--stuck-after-3-rounds)
17. [Multi-agent profiling swarm kickoff](#multi-agent-profiling-swarm-kickoff)
18. [CI perf gate writer](#ci-perf-gate-writer)
19. [Cross-filesystem matrix](#cross-filesystem-matrix)
20. [Regression root-cause bisect](#regression-root-cause-bisect)

---

## Kickoff — start a profiling session

When the user says "can you profile X / it feels slow / why is this taking so long."

```
Start a profiling session for [SUBJECT].

Before anything else, write DEFINE.md with:
  1. Scenario — the exact reproducible workload
  2. Metric — p50 / p95 / p99 / p99.9 latency, throughput, peak RSS, IOPS
  3. Budget — the number "fast enough" must beat
  4. Golden output — how we confirm behavior unchanged
  5. Scope boundary — what's out of scope

Do not run a profiler until DEFINE.md is committed.
Apply [OPERATOR: ⊘ Level-Split] first if the complaint is "slow" without an axis.
Link to references/METHODOLOGY.md Phase 1 for the template.
```

**Why this works**
- Refuses to profile before a scenario is pinned, preventing "optimize something I thought was slow" waste
- Names the operator so the step is audit-able
- Anchors to a file on disk that defines the format

---

## DEFINE — get the scenario on paper

When the user is vague. Run this to force the four questions.

```
I need DEFINE.md for a profiling session. You have answered in English, I need numbers.

For each of these, give me a single-sentence answer:
  1. Scenario — one paragraph; exact command or RPC; workload size; cache state
  2. Metric — pick ONE primary: p95 / p99 / throughput / RSS / IOPS
  3. Budget — a number. If you can't commit, pick (current p95) × 0.5.
  4. Golden output — sha256 file, property test names, or diff recipe

If any answer is "it depends" or "probably", refuse and ask for a number.
```

**Why this works**
- Resists "it depends" — the most common failure mode at kickoff
- Forces a fallback budget when the user won't commit

---

## Environment prep — tune the host safely

Before any "accurate" measurement.

```
Before the baseline run, prepare the host:

1. Capture pre-tune state to /tmp/pre-tune.sysctl (see OS-TUNING.md §Restore block).
2. Show me the proposed tuning changes in a table: key, old, new, why.
3. Ask me "apply these? [y/N]" and wait for y.
4. On y, apply; re-capture state to tuning.json; reference it in fingerprint.json.
5. Remind me of the revert commands at the bottom of the run log.

Tuning targets: perf_event_paranoid=-1, kptr_restrict=0, nmi_watchdog=0, governor=performance, no_turbo=1, smt=off, ptrace_scope=0.
```

**Why this works**
- Forces a human-in-the-loop confirmation on global system changes
- Makes revert trivially findable
- Persists the tuning state in the fingerprint for reproducibility

---

## Baseline — capture the number

```
Capture BASELINE.md for [scenario].

Runs:
- samples ≥ 20, warmup ≥ 3
- isolated core (taskset -c 2,3) if the host has isolcpus
- record metrics: p50, p95, p99, p99.9, p99.99, max, throughput, peak RSS, heap high-water

Report card format per BASELINE.md template in references/ARTIFACTS.md.
Include the variance snapshot: 5 reruns, p95 drift max %.
Label p99.9 / p99.99 "conservative" if samples < 1000.

Tool choice:
- CLI: hyperfine --warmup 3 --runs 20 --export-json baseline.json
- Rust bench: cargo bench -- --save-baseline before
- Go bench: go test -bench=. -count=10 | tee before.txt
- HTTP server: wrk2 -R <rate> or vegeta at fixed rate (open loop; closed loop lies about tails)
- Python: pytest-benchmark
```

**Why this works**
- Enforces the variance envelope check before numbers are published
- Picks open-loop load generators for servers, cutting the most common p99 lie
- Makes p99.9 honesty explicit when samples are small

---

## Instrumentation pass

When the pure sampler can't answer "which logical stage is hot."

```
Add instrumentation for pipeline [name] behind env flag [NAME_PROFILE=1]:

Three layers, in order:
1. Sentinel frames: `#[inline(never)] fn _profile_<stage>() { std::hint::black_box(()) }` (Rust), //go:noinline empty fn (Go), __attribute__((noinline)) (C)
2. Spans: tracing::instrument (Rust), runtime/trace StartRegion (Go), performance.mark/measure (Node), viztracer log_sparse (Python), Tracy ZoneScoped (C++)
3. Histograms: hdrhistogram recording to perf.profile.span_summary structured log

Chrome trace output to tests/artifacts/perf/<run-id>/<scenario>_spans.json.
Measure instrumentation overhead: if > 1% of baseline p95, gate more aggressively.

No changes without an env flag — prod pays zero.
```

**Why this works**
- Layers are additive, not exclusive
- Env-flag gate is non-negotiable → prevents accidental prod overhead
- Overhead measurement prevents Heisenberg effects

---

## Profile run

```
Run the [axis] profile on [scenario], build profile [release-perf].

CPU axis  → samply record -- ./target/release-perf/bin ...   (preferred 2026 default)
           — or cargo flamegraph --profile release-perf --bin ...
Alloc    → heaptrack ./bin   or dhat::Profiler::new_heap()
I/O      → biolatency-bpfcc, biosnoop-bpfcc, fio (for ceiling)
Off-CPU  → offcputime-bpfcc + flamegraph.pl --color=io  (reveals I/O and lock waits)
Contention → tokio-console (Rust async), go tool pprof /debug/pprof/mutex (Go), perf lock contention (Linux)
Syscalls → strace -c -e trace=read,write,pread64,pwrite64,fsync (a sharp, underused tool)

Checklist (apply [OPERATOR: 📜 Fingerprint]):
- host matches fingerprint.json from BASELINE.md
- build profile != size-optimized release (no opt-level="z" for profiling)
- symbols present (line-tables-only minimum; debug=true for deepest unwinding)
- frame pointers forced (RUSTFLAGS="-C force-frame-pointers=yes")
- instrumentation env flag present
- ≥ 3 warmups, ≥ 20 samples
- one sampler at a time — do not stack perf record + heaptrack

Artifacts land under tests/artifacts/perf/<run-id>/.
```

**Why this works**
- Matches profiler to symptom class (not "always samply")
- Calls out the most common footguns (release opt-level="z", missing FP) in the checklist
- Forces the fingerprint match

---

## Interpret — build the hotspot table

```
Interpret the profile at tests/artifacts/perf/<run-id>/.

Produce three markdown files in that directory:

1. hotspot_table.md — ranked; each row must cite an artifact path. Columns:
   | Rank | Location | Metric | Value | Category (CPU|alloc|I/O|lock|GC|net) | Evidence |
   Also include the Baseline Reuse Ledger if caches are present.

2. scaling_law.md — if the scenario has a scale axis (batch size, QPS, payload):
   table of p50/p95/p99 at 1/10/50/100/500/1000 × base.
   Emit the "multiple vs baseline" AND the "amortized per unit" columns.
   Verdict: linear / sublinear / superlinear; implication for batch threshold.

3. hypothesis.md — every candidate cause, marked supports/rejects with evidence.
   New candidates raised this round: list.
   To-revisit next round: list.

[OPERATOR: 🎯 Attribute] applies to every row of hotspot_table.md — climb out of library frames.
```

**Why this works**
- Triage artifacts persist across rounds; the tables become the audit trail
- Forces evidence citations
- Mirrors the standard profile report structure

---

## Hypothesis ledger

```
Update hypothesis.md for [run-id].

For each existing hypothesis:
- re-verdict with fresh evidence (supports / rejects / pending)
- cite the artifact that proves the verdict
- if the verdict is "rejects", add "do-not-revive-unless: [what new data would change this]"

New candidates this round: add with "pending" verdict and the first experiment that would falsify.

At the bottom, maintain two lists:
- "Zombies killed this round" (newly rejected)
- "To revisit next round" (pending that weren't tested yet)

[OPERATOR: 🗂 Ledger]  [OPERATOR: † Theory-Kill]
```

**Why this works**
- Prevents zombie hypotheses from burning next sprint's time
- The "do-not-revive-unless" clause creates the trip-wire

---

## Scaling-law harness

```
Build a scaling-law harness for [scenario].

Emit a sweep over [axis] at 1, 10, 50, 100, 500, 1000 × base.
For each point:
- samples ≥ 12 (ok for p95, flag p99.9 as conservative)
- same fingerprint (drift-fail the whole sweep if host changes mid-run)
- capture p50, p95, p99

Output scaling_law.md with:
- "multiple vs baseline" column (e.g., batch-100 is 128.82× batch-1 p95)
- "amortized per unit" column (e.g., batch-100 amortizes to 1.288× batch-1/message)
- verdict: sublinear / linear / superlinear; transition point if nonmonotonic

Interpret:
- linear + small constant → no leverage in changing scale
- sublinear at large N only → coalescing wins above a threshold (identify it)
- superlinear at moderate N → lock thrash, alloc cliff, or GC pressure — escalate
```

**Why this works**
- The shape is often the finding; spot superlinearity early
- Forces the "transition point" identification which is usually the actual engineering target

---

## Regression hunt

When a CI gate fires or the user says "it got slower."

```
Regression hunt for [scenario] — p95 went from X to Y.

1. Confirm fingerprints match across the two runs (both runs' fingerprint.json diffed).
2. If fingerprints differ on CPU / kernel / filesystem / governor / SMT / build_profile — NOT a code regression; re-do under a matching host before assigning code blame.
3. git bisect runs the baseline harness with --bisect-run: [exact command].
4. Start range: last known-good SHA; end range: first bad SHA.
5. Land at the offending commit; apply [OPERATOR: 🎯 Attribute] + [OPERATOR: 🧪 A/B].
6. If the commit is a dependency bump (Cargo.lock / package-lock.json / go.sum), bisect the upstream between their tags.
7. Rejected-cause entries go to hypothesis.md (the ledger remembers what you ruled out).
```

**Why this works**
- Gates on fingerprint equality before blaming code — catches most false regressions
- Handles dependency bumps (a surprisingly common hidden cause)
- Records the negative result

---

## Cache-tradeoff design

When the RAM-for-speed table suggests a cache is warranted.

```
Propose cache [name] for hotspot [row] (see hotspot_table.md).

Write a tradeoff block in the PR description:
- RAM cost at typical load / peak load
- Headroom on reference host
- Expected p95 Δ (before / after) with justification from the profile
- Invalidation story: TTL / write-through / event-based / never
- Correctness: is the cached value a pure-function of (key, version)?
- Rollback: env var name, config key, or feature flag
- Failure mode: what happens under OOM? (LRU evicts fine; statically sized dies hard)

Instrumentation requirement: cache.<name>.hits / misses / evictions / hit_rate_bps
emitted to perf.profile.span_summary with span_name == "cache.<name>".

Next-round verification: profile must show the cache hit rate > 30% OR the optimization rolls back.
```

**Why this works**
- Forces the tradeoff table that the cache proposer should have written anyway
- Builds the verification before the code, so round-N+1 can't hide a bad decision

---

## btrfs-specific triage

```
The scenario workload lives on btrfs. Run the CoW / fragmentation triage:

1. filefrag -v <hot files> → table of extents per file
2. sudo btrfs filesystem usage <mount>
3. sudo btrfs filesystem df <mount> (metadata vs data pressure)
4. If DB-style workload with random in-place rewrites and > 1000 extents:
   decision tree:
   (a) was `chattr +C` set BEFORE first write? — confirm via `lsattr`
   (b) if no → copy the file to a staging path with +C, swap in (atomic rename), re-run
   (c) consider autodefrag mount flag OR targeted `btrfs filesystem defragment -r -czstd`
5. Emit a per-FS baseline row in BUDGETS.md; btrfs numbers are not directly comparable to ext4/xfs — use the per-FS matrix

Warn: `btrfs filesystem defragment` breaks reflink sharing on snapshotted files.
```

**Why this works**
- Codifies the "btrfs on SSD still isn't free" lesson: keep separate budget rows for btrfs and ext4 instead of comparing across filesystems.
- Guards the reflink footgun

---

## fsync-bound triage

```
Diagnose fsync-bound behavior for [scenario].

1. biolatency-bpfcc for 30s while workload runs.
   If the histogram is bimodal (two peaks), fsync is the tail.
2. strace -c -e trace=fsync,fdatasync,sync_file_range ./bin — rank fsync cost.
3. Measure raw fsync ceiling with fio:
   fio --name=sync_write --filename=/data/fio.tmp --size=1G --bs=4k \
       --iodepth=1 --rw=randwrite --ioengine=sync --fsync=1 \
       --runtime=30 --time_based --latency_percentiles=1
4. Compare app fsync p95 to ceiling:
   - If app ~= ceiling → storage-bound; levers are batching or stronger storage (PLP NVMe)
   - If app >> ceiling → wasted fsync work; apply coalescing, fdatasync-over-fsync, group commit

Coalescing lever:
- Group-commit window of 2-10ms trades latency for throughput (measure both).
- Respect durability invariants; never `nobarrier` unless UPS + written-policy accepts loss.
```

**Why this works**
- The "ceiling comparison" tells you whether you're fighting code or physics
- The fio canary is reproducible and comparable across hosts

---

## Off-CPU / wait investigation

```
On-CPU flame looks flat or "too clean" but latency is bad. Run off-CPU:

1. sudo offcputime-bpfcc -p $PID 30 > offcpu.stacks
2. flamegraph.pl --color=io < offcpu.stacks > off-cpu.svg
3. Classify the dominant waits:
   - futex_wait → lock contention (follow up with tokio-console or mutex profile)
   - io_schedule → disk I/O (back to biosnoop / biolatency)
   - epoll_wait → event-loop idle (good)
   - page_fault → working set > RAM, mmap page-in
4. If dominant wait is futex, add [OPERATOR: 🎯 Attribute] climb to find which lock,
   then: sharded lock / lock-free / different data structure / parking_lot.

Canonical ref: Brendan Gregg, Off-CPU Flame Graphs.
```

**Why this works**
- Separates "CPU is cheap but I'm blocked" from "CPU is expensive"
- Names the classification buckets so the next step is obvious

---

## Hand-off to extreme-software-optimization

```
Profile complete. Hand off to extreme-software-optimization.

Verify, in order:
- [ ] DEFINE.md exists with scenario, metric, budget, golden, scope, envelope
- [ ] fingerprint.json captured; tuning.json captured if kernel tuned
- [ ] BASELINE.md filled (p50/p95/p99/p99.9, samples, throughput, RSS)
- [ ] hotspot_table.md has ≥ 3 rows, each citing an artifact
- [ ] scaling_law.md filled if scenario has a scale axis
- [ ] hypothesis.md has every candidate marked supports / rejects
- [ ] golden_checksums.txt written
- [ ] variance snapshot: 5 reruns on same host, max drift ≤ 10%

Then emit this summary to the user (verbatim):

  Profile complete: <scenario> — run-id <id>
  Baseline: <p95> — budget <budget> — gap <N×>
  Top 3 hotspots (rank, location, category):
    1. <loc> — <value> — <cat>
    2. <loc> — <value> — <cat>
    3. <loc> — <value> — <cat>
  Supported hypothesis: <name>
  Rejected hypotheses: <list>
  Ready for extreme-software-optimization to score (Impact × Confidence / Effort ≥ 2.0).
  Artifacts: tests/artifacts/perf/<run-id>/

Apply [OPERATOR: 💰 Score] inside extreme-software-optimization, not here.
```

**Why this works**
- Strict verification list stops the hand-off from being premature
- The summary format is what `extreme-software-optimization` expects as input
- The `[OPERATOR: 💰 Score]` reminder marks the skill boundary

---

## Escalation — stuck after 3 rounds

```
After 3 rounds, no row in hotspot_table.md scores ≥ 2.0. Escalate.

Apply in order:
1. [OPERATOR: ⊞ Scale-Check] — compute the theoretical ceiling; how close is p95 to it?
2. [OPERATOR: ◊ Paradox-Hunt] — list any measurement that surprised you but was rationalized away.
3. [OPERATOR: ⟂ Transpose] — profile the same code under a different workload axis; new hotspots?
4. If still stuck, reach for exotic CS techniques: cache-oblivious layouts, sketches / sublinear approximations (HyperLogLog, Count-Min, Bloom), semiring generalizations, concurrent lock-free data structures from research (Harris linked list, Michael-Scott queue), matroid / submodular structure in the problem.
5. Consider non-profile optimizations: PGO, BOLT, LTO=fat, different allocator (mimalloc, jemalloc), target-cpu=native.
6. If hypothesis ledger still has unknowns, drop one round of [OPERATOR: ⚡ Spike] per unknown.

Document the escalation decision in round-log.md so future-you knows what was tried.
```

**Why this works**
- Provides a structured exit when iteration has saturated
- Names concrete Round-3 technique classes rather than asking for a vague escalation

---

## Multi-agent profiling swarm kickoff

When spinning up an `ntm` swarm for a big profiling push.

```
KICKOFF: [run-id] — profiling push on [scenario]

## Triangulated kernel (shared, do NOT modify)
See references/OPERATOR-CARDS.md §"The operator algebra" in the skill.

## Your role: [Baseline captor | Hotspot ranker | Hypothesis forger | Adversarial critic | Leverage gate]

**Primary operators** (per role table in OPERATOR-CARDS.md):
- Baseline captor: 🔒 🛡 📜 📏
- Hotspot ranker: 🎯 ⊘ 𝓛
- Hypothesis forger: 🗂 ◊ ⟂
- Adversarial critic: ⊞ ΔE †
- Leverage gate: 💰 🪣 🧪

**You MUST**:
1. Cite an artifact path for every claim.
2. Mark every hypothesis you touch in hypothesis.md.
3. Reply with subject `DELTA[<role>]: <summary>` and a ```delta``` block.

## Research question
[one-sentence]

## Context
[2-4 sentences, including reference to BUDGETS.md]

## Excerpt
[paste the relevant hotspot_table.md rows with artifact pointers]

## Requested outputs
- [per role, specific]
```

**Why this works**
- Mirrors the `operationalizing-expertise` / `brenner` kickoff format, now profiling-specialized
- Keeps the operator algebra as the shared root so agents can't drift

---

## CI perf gate writer

```
Write a CI perf gate for [project] against BUDGETS.md.

Platform: GitHub Actions

Gate design:
1. Trigger on PR to main.
2. Run bench_baseline.sh on the reference-matching runner (document in CI-REGRESSION-GATES.md §Runner match).
3. Compare against the main-branch baseline via:
   - Rust: cargo bench -- --baseline main; cargo criterion compare --threshold 10%
   - Go: benchstat main.txt pr.txt ; fail if any bench > 10% slower at p<0.05
   - Custom: hyperfine --export-json + jq p95 delta < 10%
4. On regression, post a PR comment with:
   - the offending benchmark name
   - p95 before vs after + Δ%
   - artifact URL (flamegraph + span_summary)
5. Also run cross-filesystem matrix job nightly (ext4 / xfs / btrfs / tmpfs); update the matrix row.

Output:
- .github/workflows/perf-gate.yml
- scripts/ci_compare.sh
- BUDGETS.md referenced in the gate
```

**Why this works**
- Pairs the gate with an artifact the author can actually look at (flame SVG)
- Includes the cross-filesystem story because that's where surprise regressions hide

---

## Cross-filesystem matrix

Reusable cross-filesystem fsync matrix prompt.

```
Run the cross-filesystem matrix for [scenario]:

Loopback ext4 (data=ordered)     → Linux runner
Loopback ext4 (data=journal)     → Linux runner
Loopback xfs                     → Linux runner
Loopback btrfs                   → Linux runner
tmpfs                            → Linux runner  (canary only)
APFS                             → macOS runner

Probes per FS:
- single-message write latency p50/p95/p99
- batch-100 write latency p50/p95/p99
- crash-after-flush_async_commits durability check (SIGKILL, reopen, verify)

Emit matrix as BUDGETS.md table. Document explicitly:
- ext4/xfs: the Linux baseline
- btrfs: supported-but-slower — use the btrfs row, not the ext4 row, for btrfs hosts
- tmpfs: CPU canary only, NOT a durability measurement
- APFS: barrier semantics differ; compare within platform

Do not treat this as the host-tuning done; it's a portability sentinel.
```

**Why this works**
- Prevents the single most common bad comparison (ext4 test bench vs btrfs prod host)
- Encodes the known-good baseline choices per FS

---

## Regression root-cause bisect

When `git bisect` has landed on a SHA but the diff is "unclear cause."

```
git bisect landed on [SHA]. Diff spans [N files]. Root-cause bisect:

1. Apply [OPERATOR: 🎯 Attribute]: which of the changed files is on the hot path?
   Cross-ref: hotspot_table.md from the run that detected the regression.
2. For each changed file on hot path, test a scoped rollback in a temporary worktree or throwaway branch and rerun bench; do not overwrite the shared worktree.
3. If one revert restores baseline: that file is the cause; investigate within the diff.
4. If no single revert restores: interaction between files; bisect pairs.
5. If all reverts restore but "all together" is slow: compiler-level interaction (inlining, codegen ordering). Try:
   - toggle -C codegen-units=1
   - diff asm with `cargo asm` or `objdump -d`
   - rebuild with PGO on both SHAs
6. If still ambiguous, regress is environmental; re-check fingerprint.json across the bisect range.

Log each step to regression_bisect.md so the diagnosis is reproducible.
```

**Why this works**
- Distinguishes "single file" vs "interaction" vs "codegen" causes
- Handles the nasty case where no single revert fixes it (happens more often than people think)

---

## Quick search

```bash
# find the prompt for a workflow stage
grep -n '^## ' .claude/skills/profiling-software-performance/references/PROMPTS.md

# find operator references
grep -n 'OPERATOR:' .claude/skills/profiling-software-performance/references/PROMPTS.md
```

---

## Why prompts are first-class

Borrowed from `sw/MINDSET.md`: skills are instructions to *you*. If the right prompt is this file away, the right prompt gets used. If it's in someone's head, it doesn't.

Every new workflow you catch yourself running twice → add a prompt here.
