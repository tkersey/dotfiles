# Profiling Operator Cards

> Cognitive moves you apply during a profiling session. Each card has a symbol, definition, triggers, failure modes, and a copy-paste prompt module. Composition rules follow at the bottom.

The pattern is lifted from `operationalizing-expertise` — making the skill itself the **triangulated kernel** for the profiling methodology.

## Contents

1. [Why operator cards](#why-operator-cards)
2. [The operator algebra (at a glance)](#the-operator-algebra-at-a-glance)
3. [Decomposition operators](#decomposition-operators)
4. [Evidence operators](#evidence-operators)
5. [Hygiene operators](#hygiene-operators)
6. [Hypothesis operators](#hypothesis-operators)
7. [Leverage operators](#leverage-operators)
8. [Guard operators](#guard-operators)
9. [Composition rules](#composition-rules)
10. [Role assignment](#role-assignment)

---

## Why operator cards

Profiling is not "run flamegraph, look at bars." It's a chain of decisions where each step can go wrong. Names + symbols make the moves audit-able across sessions and across agents. When you catch yourself doing something you don't have an operator for — write a new card.

Every operator must have:
- **Symbol** — a memorable glyph (think ✂ for cutting hypotheses)
- **Name** — 2-3 words
- **Definition** — one sentence
- **When-to-use triggers** — ≥3 concrete situations
- **Failure modes** — ≥2 ways it goes wrong
- **Prompt module** — copy-paste text an agent can execute

## The operator algebra (at a glance)

```
Decomposition:   ⊘ Level-Split       𝓛 Recode          ≡ Invariant-Extract
Evidence:        📏 Measure           ⚡ Spike           🎯 Attribute
Hygiene:         ⊞ Scale-Check        ΔE Anomaly-Q      † Theory-Kill
Hypothesis:      🗂 Ledger            ◊ Paradox         ⟂ Transpose
Leverage:        💰 Score             🪣 Bucket         🧪 A/B
Guards:          🛡 Isomorphism       🔒 Golden         📜 Fingerprint

Default chains:
  Start → 🛡 → 📜 → 📏 → ⊘ → 🎯 → 🗂 → 💰 → (hand-off to extreme-software-optimization)
  Regression → 📜 → 📏 → ⊞ → ΔE → †
  Escalation → ⊞ → ◊ → ⟂ → 🧪
```

---

## Decomposition operators

### ⊘ Level-Split

**Definition**: Separate a blended "slow" complaint into typed levels (CPU vs alloc vs I/O vs lock vs GC vs network).

**Triggers**:
- User says "it's slow" without specifying axis
- Flamegraph looks flat / evenly distributed → not actually CPU-bound
- `/usr/bin/time -v` %CPU < 80% on a "CPU-bound" job (see IO-AND-TRADEOFFS.md §"First — is this actually I/O?")
- Memory growth language mixed with latency language

**Failure modes**:
- Optimizing CPU when contention dominates → wasted work, no user-visible gain
- Conflating allocation rate with peak RSS → chase fragmentation when rate is the issue
- Treating p50 regression as p99 regression → totally different root causes

**Prompt module**:
```text
[OPERATOR: ⊘ Level-Split]
1) Which axis is the complaint? CPU / wall-clock / alloc rate / peak memory / I/O wait / lock contention / GC / network / cold-start / tail latency.
2) State *evidence* for the chosen axis (vmstat wa%, /usr/bin/time %CPU, flamegraph balance, symptom language).
3) If evidence is ambiguous, split into 2+ sub-complaints with separate evidence each.

Output: a table { axis, evidence, proposed-sampler }.
```

---

### 𝓛 Recode

**Definition**: Restate the hot work in a different representation (bytes moved, cache lines fetched, syscalls issued, pages faulted) to reveal structure the flamegraph hides.

**Triggers**:
- Flamegraph shows a generic framework function (`core::iter`, `Promise.then`, `pandas.apply`)
- Top frame is an allocator (`malloc`, `mi_alloc`)
- Time is clearly being spent, but "where" is a dull name

**Failure modes**:
- Staying in the language-level representation when physics dominate (TLB, cache, NUMA)
- Treating an allocation hotspot as an "alloc problem" when it's really a data-layout problem

**Prompt module**:
```text
[OPERATOR: 𝓛 Recode]
1) Translate the top frame into bytes/sec, pages/sec, syscalls/sec, alloc ops/sec — whichever makes the number concrete.
2) Compare to the theoretical ceiling (memory bandwidth, syscall rate on the host, network BW).
3) Decide: are we near the ceiling (physics-limited) or orders of magnitude below (inefficient)?

Output: "<frame> is doing X <unit>/s; host ceiling is Y; gap is Z%".
```

---

### ≡ Invariant-Extract

**Definition**: Identify which behaviors must stay identical across optimization rounds (ordering, floating-point, RNG seeds, crash semantics).

**Triggers**:
- About to apply an optimization that might reorder work
- Multi-threaded change contemplated
- RNG, hashmap iteration order, or IEEE-754 semantics are in play

**Failure modes**:
- Finding a "speedup" that actually changed output
- Missing a subtle invariant (e.g., WAL ordering for crash recovery)

**Prompt module**:
```text
[OPERATOR: ≡ Invariant-Extract]
List invariants that MUST hold after optimization:
- Output ordering: [strict / sort-key / none]
- Tie-breaking: [how]
- Floating-point: [bit-identical / bounded-error / N/A]
- RNG: [same seed → same output / N/A]
- Crash semantics: [what writes must survive, in what order]
- Externally visible side effects: [logs, metrics, spans — bit-identical or not]

Store invariants in DEFINE.md so next round can check.
```

---

## Evidence operators

### 📏 Measure

**Definition**: Replace a qualitative claim with a numeric one. No optimization proceeds without a measurement card.

**Triggers**:
- Someone says "this is fast enough" or "this is slow"
- A PR claims "X% improvement" without a runs-and-percentiles table
- Budget violation suspected

**Failure modes**:
- Measuring once → calling it done (variance invisible)
- Measuring mean → tail hidden
- Measuring warm when user experience is cold (or vice versa)

**Prompt module**:
```text
[OPERATOR: 📏 Measure]
Emit a BASELINE.md card:
- scenario, metric, budget (from DEFINE.md)
- samples ≥ 20
- p50 / p95 / p99 / p99.9 / max / throughput / peak RSS
- variance snapshot: 5 reruns, max drift %

Label p99.9/p99.99 *conservative* if samples < 1000.
```

---

### ⚡ Spike

**Definition**: Deploy a deliberate **spike** — a 10-60 minute experiment to kill or confirm a specific hypothesis before committing to a full change.

**Triggers**:
- Two or more hypotheses look plausible
- Proposed change costs > 1 engineering-day
- Cheap disprove-ability ("I could just try X")

**Failure modes**:
- Letting the spike turn into production code ("it works, let's ship")
- Spike on top of spike without cleanup

**Prompt module**:
```text
[OPERATOR: ⚡ Spike]
1) Write the hypothesis in one sentence.
2) Design the cheapest experiment that would *falsify* it (not confirm).
3) Time-box: ≤ 60 min. If over, stop and rescope.
4) Record verdict in hypothesis.md; merge or archive the spike branch, and delete it only with explicit user approval.
```

---

### 🎯 Attribute

**Definition**: Tie a sample to a concrete code location + responsibility line.

**Triggers**:
- Flamegraph bar identified but no plan to act
- Vendor / stdlib frame dominates (need to climb out)
- Multi-version binary — ambiguous stack trace

**Failure modes**:
- Attributing to the *callee* when the fix belongs to the *caller* (stop calling it, not fix it)
- Attributing to a leaf that's inlined from a much bigger function

**Prompt module**:
```text
[OPERATOR: 🎯 Attribute]
For each of the top 5 bars:
- file:line of caller and callee
- responsible owner (module / team / bead)
- is the frame *doing* work or *calling* work? (inlining status)
- earliest node up the stack where we have design freedom

Log to hotspot_table.md with evidence path.
```

---

## Hygiene operators

### ⊞ Scale-Check

**Definition**: Verify orders-of-magnitude plausibility before trusting a number.

**Triggers**:
- Result seems "too good" (2000× speedup on a fix that shouldn't do much)
- Result seems impossible given hardware (throughput > memory bandwidth)
- Scaling diverges from expected shape (linear → superlinear on a log-log plot)

**Failure modes**:
- Celebrating a measurement artifact (caching, compiler eliminated the loop, JIT warmup)
- Missing cross-host drift (different CPU, filesystem, kernel → incomparable)

**Prompt module**:
```text
[OPERATOR: ⊞ Scale-Check]
Before accepting any >2× improvement:
1) Compute the theoretical ceiling (memory BW, syscall rate, IOPS, cache).
2) Rerun with `black_box` / volatile marks on every input/output to defeat DCE.
3) Rerun cold (drop_caches) if claim is "cache reuse".
4) Rerun on 2 distinct commits (baseline SHA + change SHA) to pin down git.

Any speedup unexplained by a mechanism is a measurement bug until proven.
```

---

### ΔE Anomaly-Quarantine

**Definition**: Isolate outlier samples explicitly instead of dropping them silently or averaging them away.

**Triggers**:
- One p99.9 sample 10× the p50
- A single run dominates the variance envelope
- The flame looks clean but the span histogram is bimodal

**Failure modes**:
- Averaging outliers into the mean → hides the bug that matters most for users
- Dropping outliers permanently → loses the signal for next round

**Prompt module**:
```text
[OPERATOR: ΔE Anomaly-Quarantine]
When a sample is > 3σ from median:
- DO NOT average it away.
- Log the raw sample, timestamp, and machine state (GC pause? I/O spike? context switch?).
- Move to anomaly_register.md with a classification: [GC-pause / IO-stall / lock-wait / unknown].
- Separate metric: "steady-state p95" vs "outlier-inclusive p99.9".
```

---

### † Theory-Kill

**Definition**: When evidence rejects a hypothesis, cross it out in writing (hypothesis.md) before moving on.

**Triggers**:
- New data contradicts old assumption
- A team member keeps proposing a refuted idea
- Your own "but maybe…" is re-animating a zombie hypothesis

**Failure modes**:
- Zombie hypotheses that eat next sprint
- Deleting (vs crossing-out) rejected hypotheses — lose the "we tried this" signal

**Prompt module**:
```text
[OPERATOR: † Theory-Kill]
For each rejected hypothesis in hypothesis.md, mark with:
- verdict: "rejects"
- evidence (artifact path + data)
- do-not-revive-unless: [what new evidence would resurrect it]

Review the ledger at the start of every round so zombies stay dead.
```

---

## Hypothesis operators

### 🗂 Ledger

**Definition**: Maintain the hypothesis ledger — every candidate explanation, with supports/rejects and evidence, persisted across rounds.

**Triggers**:
- Starting a new profiling round
- Discovering a new candidate cause mid-profile
- Wrapping up a round (re-read + mark)

**Failure modes**:
- Ledger drift: hypotheses proposed but never re-visited
- No "new candidates raised this round" section → next round can't learn

**Prompt module**:
```text
[OPERATOR: 🗂 Ledger]
Update hypothesis.md each round:
- supports / rejects / pending
- evidence artifact path
- new candidates this round
- zombies to kill (see †)
- to-revisit next round, with what data would change the verdict
```

---

### ◊ Paradox-Hunt

**Definition**: Use contradictions as beacons — the places where profile-driven beliefs clash with reality are the best next targets.

**Triggers**:
- Micro-bench says 10× but macro-bench says 1.1×
- Cache-hit ratio high but p99 latency still bad
- Prod and dev fingerprints equal, but numbers differ 10×

**Failure modes**:
- Dismissing the paradox ("must be a one-off")
- Treating paradox as puzzle to *explain away*, not as evidence that one of your beliefs is wrong

**Prompt module**:
```text
[OPERATOR: ◊ Paradox-Hunt]
When two measurements disagree:
1) State both facts with artifacts.
2) Enumerate every belief that would have to be true for BOTH facts.
3) Pick the cheapest experiment that distinguishes them.
4) Run; the paradox is resolved iff one fact was wrong, or iff there's a missing variable. Record which.
```

---

### ⟂ Transpose

**Definition**: Change the axis of the experiment — profile a different workload, different dataset shape, different client, different host — to separate what-about-the-code from what-about-this-particular-case.

**Triggers**:
- Workload is suspected of being unrepresentative
- Profile looks different across Zipfian-vs-uniform key distributions
- "Works on dev, slow in prod" language

**Failure modes**:
- Transposing once → declaring the system understood
- Transposing along a non-meaningful axis (e.g., swapping empty-input for empty-input)

**Prompt module**:
```text
[OPERATOR: ⟂ Transpose]
Rerun the profile with one of these axes flipped:
- workload distribution (Zipfian α=0.5 vs α=1.0 vs uniform)
- payload size (1k, 10k, 100k, 1M)
- concurrency (1, 4, 16, 64 workers)
- host (reference vs prod vs CI runner)
- cache state (cold / warm / hot)

Compare the two profiles side-by-side; new hotspots = new learning.
```

---

## Leverage operators

### 💰 Score

**Definition**: For each candidate in the hotspot table, compute Impact × Confidence / Effort. Hand off only rows ≥ 2.0.

**Triggers**:
- About to call `extreme-software-optimization`
- Multiple competing optimization ideas
- Budget conversation with the user / team

**Failure modes**:
- Scoring by gut instead of from evidence columns
- Scoring without a budget (why are we doing this, again?)

**Prompt module**:
```text
[OPERATOR: 💰 Score]
For each hotspot row:
- Impact (1-5): 5=>50% of total time, 4=25-50%, 3=10-25%, 2=5-10%, 1=<5%
- Confidence (1-5): 5=profiler+instrument agree, 3=one source, 1=speculative
- Effort (1-5): 5=>1day, 3=hours, 1=minutes
- Score = Impact × Confidence / Effort
- Recommendation: apply iff ≥ 2.0, escalate iff < 2.0 for top-5.
```

---

### 🪣 Bucket

**Definition**: Group similar optimizations into a single "bucket" so you ship them as one change and one measurement, not N scattered commits.

**Triggers**:
- 5 tiny wins that are all "remove unnecessary clones"
- Many related string-handling hotspots
- Cross-cutting pattern (e.g., "memoize all parse-y things")

**Failure modes**:
- Bucket too big → cannot isolate regressions
- Bucket spans different isomorphism concerns → hard to prove unchanged behavior

**Prompt module**:
```text
[OPERATOR: 🪣 Bucket]
Group candidate rows iff:
- same optimization technique
- same isomorphism proof
- same rollback path
- total effort still ≤ 1 day

Name the bucket (e.g., "parse-cache-hits-round-2"); commit as one change with one measurement.
```

---

### 🧪 A/B

**Definition**: Run old-vs-new as a controlled A/B, not as a before-and-after across separate runs.

**Triggers**:
- Machine-state noise suspected (thermal drift, neighbor noise)
- Comparing commit SHAs across time
- Cross-filesystem comparisons

**Failure modes**:
- Running A before B → thermal / cache drift contaminates
- A/B that ignores warmup order

**Prompt module**:
```text
[OPERATOR: 🧪 A/B]
1) Interleave runs: ABABAB… or ABBA-blocked.
2) Compare via hyperfine's built-in stats OR `benchstat` (Go) / criterion `--baseline` (Rust).
3) Minimum 20 iterations per side.
4) Require non-overlapping CIs or p < 0.05 for "real" win.
```

---

## Guard operators

### 🛡 Isomorphism

**Definition**: Every optimization must carry a written proof that observable behavior is unchanged.

**Triggers**:
- Any code change with a performance motivation
- Reordering, parallelizing, caching — anywhere output *could* change

**Failure modes**:
- "Looks equivalent" without golden verification
- Proof written but `sha256sum -c` not actually run

**Prompt module**:
```text
[OPERATOR: 🛡 Isomorphism]
For every performance change, append to proof.md:
- "What changes / what doesn't"
- ordering / tie-break / float / RNG / crash semantics (re ≡ Invariant-Extract)
- `sha256sum -c golden_checksums.txt` → ✓ / ✗
- golden test suite pass
- property tests pass (if applicable)

No row ships without green checks.
```

---

### 🔒 Golden

**Definition**: Capture outputs on the pre-optimization commit and lock them with sha256 before touching code.

**Triggers**:
- Start of any optimization round
- Before adopting a new compiler / toolchain version

**Failure modes**:
- Capturing golden *after* the first experimental change (lose reference)
- Golden that covers happy path only, missing edge cases

**Prompt module**:
```text
[OPERATOR: 🔒 Golden]
1) Checkout baseline commit.
2) Run the *full* workload set (including edge cases, cold-cache, empties, max-size).
3) `sha256sum golden_outputs/* > golden_checksums.txt`.
4) Commit the checksums file; reference it from DEFINE.md.
```

---

### 📜 Fingerprint

**Definition**: Capture host + toolchain + build profile into `fingerprint.json` every run. A comparison that crosses fingerprint boundaries is not valid.

**Triggers**:
- Every profile run
- Before making "this is X% faster" claims

**Failure modes**:
- Invisible kernel upgrade between runs
- Hidden Rosetta / NUMA / cgroup differences
- Comparing macOS / Linux numbers as if comparable

**Prompt module**:
```text
[OPERATOR: 📜 Fingerprint]
See ARTIFACTS.md §fingerprint.json for the exact schema.
Diff fingerprint.json against the prior run. Fields that MUST match for a valid A/B:
  cpu_model, kernel major, filesystem, governor, no_turbo, smt, build_profile.*
If any differ, annotate the comparison as cross-fingerprint (advisory only).
```

---

## Composition rules

1. **Order matters.** `🛡 Isomorphism` + `🔒 Golden` + `📜 Fingerprint` are pre-flight — always before `📏 Measure`.
2. **Loops exist.** `🎯 Attribute` → `⚡ Spike` → `†/🗂` → back to `🎯` for the next rank.
3. **Skip what doesn't fit.** A read-only query engine has no `≡ Invariant-Extract` for RNG.
4. **Name the operator when applied.** Commit messages / hypothesis entries begin with the operator symbol.
5. **New session? Run `🔒 + 📜` twice** — once to capture pre-tuning state, once after tuning. Document both.

### Default diagnostic chain

```
🔒 Golden  →  📜 Fingerprint  →  📏 Measure  →  ⊘ Level-Split  →  𝓛 Recode
→  🎯 Attribute  →  🗂 Ledger  →  ⚡ Spike (as needed)  →  ⊞ Scale-Check
→  💰 Score  →  🪣 Bucket  →  hand-off to extreme-software-optimization
```

### Regression-hunt chain

```
📜 Fingerprint (diff)  →  📏 Measure (both SHAs)  →  ⊞ Scale-Check  →  ΔE Anomaly-Q
→  🧪 A/B  →  🗂 Ledger (add rejected cause)  →  †
```

### Escalation chain (standard rounds exhausted, score < 2.0 everywhere)

```
⊞ Scale-Check  →  ◊ Paradox-Hunt  →  ⟂ Transpose  →  𝓛 Recode (deeper: bytes/sec ceiling)
→  (cross-ref ADVANCED.md from extreme-software-optimization for Round-2 techniques)
```

---

## Role assignment

When running a multi-agent profiling session (e.g., `ntm` swarm, `modes-of-reasoning-project-analysis`):

| Role | Primary operators |
|------|-------------------|
| **Baseline captor** | 🔒 🛡 📜 📏 |
| **Hotspot ranker** | 🎯 ⊘ 𝓛 |
| **Hypothesis forger** | 🗂 ◊ ⟂ |
| **Adversarial critic** | ⊞ ΔE † |
| **Leverage gate** | 💰 🪣 🧪 |

Each agent receives their role's operator cards verbatim in the kickoff message, matching the `operationalizing-expertise` pattern.

---

## Writing a new operator card

When you notice a recurring profiling move not on this list, add a card. Requirements:

- Symbol not already used in the registry above
- Definition ≤ 1 sentence
- ≥ 3 triggers, ≥ 2 failure modes
- Prompt module that starts with `[OPERATOR: <symbol> <name>]`
- Log anchor — a case study reference or artifact path where this operator paid off

Update the algebra diagram and the default chains when a new operator joins.

---

## Operators inherited from operationalizing-expertise

The cards below port four cognitive moves from `operationalizing-expertise` into the profiling domain. They sit alongside the original operator algebra; use the canonical chain `🗣 → 📚 → 🔺 → 📐` when transitioning a finding from raw data into something the optimization skill can act on.

### 🗣 Quote-Bank

**Definition**: Anchor every claim in your hotspot table to a specific evidence path (file:line:offset).

**Triggers**:
- Hotspot row about to be written without an `evidence:` field
- Reviewer asks "where did you get that number?"
- Hand-off bundle being assembled for extreme-software-optimization

**Failure modes**:
- Vague evidence ("flame graph showed it") — six months later you cannot find the flame
- Quote-bank entries not paired with run-id, so they don't survive code refactor

**Prompt module**:
```
[OPERATOR: 🗣 Quote-Bank] For every row in the hotspot table, attach an
evidence anchor of the form <run_id>/<artifact_filename>[:<offset_or_line>].
Reject any row without an anchor. Examples:
  - flames/cpu.svg:0.41
  - span_summary.json#L120
  - perf.data#sample_4221
  - strace_summary.txt:L8
```

### 📚 Corpus-Mine

**Definition**: Before a fresh profiling session, mine prior session artifacts (perf archives, hypothesis ledgers, hotspot tables) for the same symptom signature.

**Triggers**:
- Symptom feels familiar — has any past session profiled this codepath?
- Project is not new — there should be priors to consult
- The same hot function name appears across multiple recent sessions

**Failure modes**:
- Re-profiling a path the team already optimized last quarter
- Missing a prior conclusion that was archived but not consolidated

**Prompt module**:
```
[OPERATOR: 📚 Corpus-Mine] Before instrumenting, search:
  1. tests/artifacts/perf/**/*.md   (past hotspot tables)
  2. tests/artifacts/perf/**/hypothesis.md  (past ledgers)
  3. cass session history for "<symptom phrase>"
For each match, summarize: scenario, top-3 hotspots, what was fixed, what
remained on the table. Use this to skip redundant work and to avoid
re-investigating already-rejected hypotheses.
```

### 🔺 Triangulate

**Definition**: Refuse to act on any hypothesis until three orthogonal measurement angles agree (3/3 → kernel; 2/3 → disputed appendix; 1/3 → discard).

**Triggers**:
- A single profiler has produced a striking result
- About to recommend an optimization based on one tool
- Reviewer asks "have you confirmed this from another angle?"

**Failure modes**:
- Two angles from the same mechanism (perf-CPU + perf-off-cpu both share PMU bias)
- "I'll just trust the flame graph" — bias not characterized
- Skipping triangulation under deadline pressure produces false-positive optimizations

**Prompt module**:
```
[OPERATOR: 🔺 Triangulate] For hypothesis H about hotspot X, identify three
orthogonal measurement angles from different mechanism rows in
TRIANGULATION-RECIPE.md (e.g., CPU sample + off-CPU + syscall). Run all three.
Record verdict (supports/rejects) per angle in a triangulation ledger row.
Only promote to hotspot table if 3/3 supports.
```

See [TRIANGULATION-RECIPE.md](TRIANGULATION-RECIPE.md) for the full pattern, mechanism rows, and three worked examples.

### 📐 Validator-Emit

**Definition**: After identifying a hotspot, emit a post-optimization validator script that codifies what "fixed" means, before handing off.

**Triggers**:
- About to hand off a hotspot to extreme-software-optimization
- Optimization PR coming back with the question "did it actually work?"
- Multiple optimization attempts have toggled the same hotspot

**Failure modes**:
- Validator measures the wrong thing (e.g., total time, when the regression was specifically on p99 of one workload)
- No validator → optimization shipped without proof, regresses two months later

**Prompt module**:
```
[OPERATOR: 📐 Validator-Emit] For each row in the hotspot table, emit a
validator command that:
  1. Re-runs the bench harness with the same scenario + fingerprint
  2. Asserts the specific metric improved (e.g., p95 of span X reduced ≥ N%)
  3. Asserts no other top-5 hotspot regressed > 10%
  4. Returns non-zero if either fails
Save validators alongside the hotspot table at:
  tests/artifacts/perf/<run-id>/validators/<hotspot_name>.sh
The optimization PR must run the validator and attach output.
```

### Composition: the kernel-formation chain

When transitioning from raw observation to actionable hand-off:

```
👁 HAL → 📚 Corpus-Mine → 📏 Measure → 🔺 Triangulate → 🗣 Quote-Bank → 💰 Score → 📐 Validator-Emit → hand-off
```

This is the operationalizing-expertise discipline applied end-to-end:
- **Observation** is anchored (👁)
- **Prior work** is consulted before re-doing it (📚)
- **Multiple angles** must agree (🔺)
- **Claims have receipts** (🗣)
- **Hand-off includes proof spec** for the next step (📐)
