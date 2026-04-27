# Integration With Related Skills

> This skill sits inside a larger ecosystem. When profiling hits a boundary, hand off explicitly. When another skill starts but needs a profile, come back here.
>
> Handoffs marked **external** are not bundled in this repo; verify the skill is installed before invoking it.

## Contents

1. [Skill map](#skill-map)
2. [Upstream (feeds into this skill)](#upstream-feeds-into-this-skill)
3. [Downstream (this skill feeds)](#downstream-this-skill-feeds)
4. [Adjacent (runs alongside)](#adjacent-runs-alongside)
5. [Hand-off protocols](#hand-off-protocols)

---

## Skill map

```
                                    ┌──────────────────────────────────┐
                                    │  profiling-software-performance  │
                                    │  (this skill)                    │
                                    └──────────────────────────────────┘
                                                │           │
        ┌───────────────────────────┬───────────┤           ├──────────────────┬─────────────────────┐
        │                           │           │           │                  │                     │
        ▼                           ▼           ▼           ▼                  ▼                     ▼
┌────────────┐           ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐   ┌────────────┐
│ extreme-   │           │ exotic-CS  │    │ deadlock-  │    │ process-   │    │ asupersync │   │ system-    │
│ software-  │  ←Round2  │ techniques │    │ finder-    │    │ triage     │    │ -mega-skill│   │ performance│
│ optimization│          │ (external) │    │ and-fixer  │    │            │    │            │   │ -remediation│
└────────────┘           └────────────┘    └────────────┘    └────────────┘    └────────────┘   └────────────┘

                                    ▲                   ▲
                                    │                   │
                                    │                   │
                        ┌────────────┐                   │                   ┌────────────┐
                        │  operation-│                   │                   │   sbh      │
                        │  alizing-  │                   │                   │  (disk     │
                        │  expertise │                   │                   │  pressure) │
                        └────────────┘                   │                   └────────────┘
                                                          │
                                    ┌────────────────────────────────────────┐
                                    │                                         │
                                    │        Observability / tooling          │
                                    │                                         │
                                    │   supabase       vercel:vercel-agent    │
                                    │   claude-api     vercel:ai-sdk          │
                                    │   rch            rust-cli-with-sqlite   │
                                    │                                         │
                                    └─────────────────────────────────────────┘
```

---

## Upstream (feeds into this skill)

### `operationalizing-expertise`

This skill's OPERATOR-CARDS.md is styled after `operationalizing-expertise`. When defining a new cognitive move in profiling (new operator), follow that skill's card format: symbol, definition, triggers, failure modes, prompt module, quote anchors.

### `cass` / `flywheel`

Mining past profiling sessions to seed new methodology. CASE-STUDIES.md was built this way — mine sessions for real numbers, extract lessons, attach to operator cards.

Use `cass` when:
- Starting a profile of a system where you've profiled a similar system before
- Looking for the exact command-line you used last time
- Remembering which hypothesis you rejected two months ago

```bash
cass search "samply record" --robot --limit 20
cass search "flamegraph regressed" --robot --limit 20
cass search "batch-100 p95" --robot --limit 20
```

### `planning-workflow` / `beads-workflow`

When a profiling campaign will span weeks (see CASE-STUDIES.md §Case 6), convert the ranked hotspot table into beads with dependencies. The bead graph becomes the campaign's execution plan.

---

## Downstream (this skill feeds)

### `extreme-software-optimization`

The primary downstream. This skill produces the ranked hotspot table; `extreme-software-optimization` scores it (Impact × Confidence / Effort ≥ 2.0), applies one lever at a time with isomorphism proofs, and verifies golden outputs.

Hand-off artifacts (see ARTIFACTS.md §"Hand-off summary"):
- `DEFINE.md`
- `fingerprint.json`
- `BASELINE.md`
- `hotspot_table.md` with evidence citations
- `hypothesis.md`
- `scaling_law.md`
- `golden_checksums.txt`

The handoff prompt is in PROMPTS.md §"Hand-off to extreme-software-optimization."

### Round-3+ escalation (exotic algorithms / data structures)

When standard optimization has saturated (`💰 Score` returns < 2.0 for all rows), escalate to exploring advanced CS techniques — exotic data structures, algorithmic reformulations, cache-oblivious layouts, randomized approximations. See OPERATOR-CARDS.md §"Escalation chain" for how to apply `◊ Paradox-Hunt` and `⟂ Transpose` to find a Round-3 angle.

### `deadlock-finder-and-fixer`

When profiling reveals lock contention as the dominant cause (futex waits in off-CPU flame, tokio-console showing mutex hold across `.await`), hand off to this skill for concurrency-bug-class remediation.

CASE-STUDIES.md §Case 5 (Tokio ticker_cx deadlock) is a direct example. The profile shows the pattern; the deadlock-finder skill enumerates the canonical fix templates.

### `asupersync-mega-skill`

When the profile shows Tokio as a bottleneck for a specific set of workloads (lots of short async tasks, heavy small-allocs in futures, contention on the runtime), `asupersync-mega-skill` is the Rust-async replacement migration path. Invoke after profiling has quantified the Tokio cost.

---

## Adjacent (runs alongside)

### External: `process-triage`

"A process is misbehaving on the machine" → `process-triage` decides what to do about it (kill, nice, cgroup), if that external skill is installed. "A process's code is slow under normal conditions" → this skill. They sometimes overlap (runaway process triage shows tokio-console has long polls → this skill diagnoses the code).

### `system-performance-remediation`

Machine-wide cleanup (high load average, unresponsive fleet). Use before profiling when the measurement host itself is misbehaving. OS-TUNING.md §Pre-tune verification overlaps; pick one authoritative set of commands.

### External: `sbh` (Disk pressure)

When `df -h` is near full and that's the cause of perf degradation. IO-AND-TRADEOFFS.md's small-file / btrfs sections mention this but `sbh`, when installed, is the remediation skill. Hand off when root cause is disk pressure.

### `rch`

Remote compilation (cargo / gcc / bun). When local builds are slow and that's blocking the profile run (see CASE-STUDIES.md §Case 4), use `rch exec` in `bench_baseline.sh`.

### `testing-perfect-e2e-integration-tests-with-logging-and-no-mocks`

Integration tests that are mock-free produce the most realistic workloads for profiling. When building a bench scenario, start from one of these tests rather than a synthetic harness.

### `supabase` / `supabase:supabase-postgres-best-practices`

For Postgres-backed apps on Supabase. DATABASE-PROFILING.md defers to `supabase:supabase-postgres-best-practices` for Supabase-specific Postgres tuning.

### External: `claude-api`

For LLM apps. LLM-AI-PROFILING.md is the perf-specific lens; `claude-api`, when installed, covers broader SDK usage, prompt caching design, batch API, files API. Pair them: profile with this skill, fix with `claude-api`'s guidance.

### `vercel:vercel-functions` / `vercel:ai-sdk`

Vercel-specific runtime profiling. CONTAINER-CLOUD.md §Serverless defers to these for product-specific details.

---

## Hand-off protocols

### From this skill → another

Emit the hand-off summary (see ARTIFACTS.md and PROMPTS.md §"Hand-off to..."). Structure:

```
Profile complete: <scenario> — run-id <id>
Baseline: <p95> — budget <budget> — gap <N×>
Top hotspots:
  1. ...
  2. ...
  3. ...
Supported hypothesis: <name>
Rejected: <list>
Handing off to: <next skill name>
Reason: <why this skill vs another>
Artifacts: tests/artifacts/perf/<run-id>/
```

### From another skill → this skill

When another skill needs a performance baseline (before refactor, before dependency bump, before architecture migration), it should invoke this skill via:

```
Profile [subject] to establish baseline before [change].
Scenario: [exact workload]
Metric: [p95 / throughput / RSS]
Acceptable variance: [±X%]

Return: DEFINE.md, BASELINE.md, fingerprint.json.
Do not modify code during this profile pass.
```

### Inter-skill memory

When skills hand off, the receiving skill should:
1. Verify the artifacts are on disk (not just claimed)
2. Verify fingerprint compatibility with its reference host
3. Record the hand-off in its own audit log

Losing context between skills is a common failure mode in multi-skill workflows. Path-based artifacts (`tests/artifacts/perf/<run-id>/`) are the durable medium that survives context resets.

---

## Boundaries

- This skill does NOT apply optimizations — that's `extreme-software-optimization`
- This skill does NOT handle general debugging (stack traces, logic errors) — use `gdb-for-debugging` or normal dev loop
- This skill does NOT do security review — use `security-audit-for-saas` or related
- This skill does NOT tune database schema changes — `supabase:supabase-postgres-best-practices` or `rust-cli-with-sqlite`
- This skill does NOT fix deadlocks — hand off to `deadlock-finder-and-fixer`
- This skill does NOT do one-off "how fast is it?" without a scenario — requires DEFINE.md first

When in doubt about which skill to use, the answer is almost always "profile first, remediate second." Come here, then go elsewhere.
