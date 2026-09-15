# Measured performance optimization

Use for software or agent-system optimization, including a specified optimization
in `edit` mode. Tune's authority and protected-contract rules always apply.
Before the first experiment, read only the relevant guide:
[software-performance.md](references/software-performance.md) for code and
[agent-performance.md](references/agent-performance.md) for agents. Mixed changes
use both only where required. Skill-package edits additionally retain authoring
rules, not a second optimizer or a second experiment dossier.

## Frame and baseline

State the workload/task distribution, performance objective, guardrails, and
stopping criterion. Prefer the user's acceptance target; otherwise record a
reasonable provisional target, not an invented requirement. Preserve mandated
checks and existing failures separately. Do not fix unrelated failures or
silently credit their disappearance to optimization.

Capture source revision, build/runtime/model configuration, fixtures, environment,
commands, and raw observations sufficient to reproduce the comparison. Measure
the relevant resource: wall time, throughput, peak/live memory, allocations,
I/O, cost, or quality. Do not require every metric for every task. Include startup
or cold-cache cases when material rather than warming away the actual problem.

Reuse benchmark/evaluation infrastructure. Add a small substantive harness only
when measurement cannot otherwise answer the question. No mandatory benchmark
framework, dashboard, score file, or new ledger. If execution is unavailable,
retain a concrete command/fixture plan and separate hypotheses from observations.
An unmeasured authorized patch remains explicitly unverified, not an accepted gain.

## Locate the limiting mechanism

Profile the objective, not a language stereotype. Distinguish on-CPU work from
allocation/GC, memory stalls, I/O, locks, queueing, external/model service time,
and orchestration dependencies. Use representative production traces when safely
available or a reproducible local workload. Do not run live load without authority.
A flamegraph's width reflects sampled attribution; stack depth alone is not proof
of call overhead. Correlate profiles with traces/counters and the target metric.

Inspect scaling across relevant input sizes and distributions. A rare request
class can govern p99; an allocation or off-CPU problem need not be a top CPU
hotspot. Search/grep can nominate code to inspect, never prove it is expensive.

Before low-level tuning, ask whether work can be eliminated through a different
algorithm, representation, query plan, materialization boundary, or dependency
structure. Use [optimization-techniques.md](references/optimization-techniques.md)
when selecting transformations, and its advanced reference when the structure
warrants one. Advanced methods are available in the first cycle; rounds do not
unlock them. Existing architecture/escalation skills keep their own triggers.

## Select an experiment

Compare plausible opportunities using the native report or a small table:

| Mechanism/location | Evidence and workload share | Expected end-to-end benefit | Preservation obligation | Effort/risk | Discriminator |
|---|---|---|---|---|---|
| Observed limiting operation | Profile/trace or complexity witness | Measured scope or bounded estimate | Required observations | Implementation and operational cost | Test that could reject it |

No fixed score threshold, top-five restriction, or compulsory candidate count.
Use an Amdahl-style bound for an applicable serial latency component:
`speedup = 1 / ((1 - f) + f / s)`, with measured fraction `f` and proposed local
speedup `s`. Do not apply this formula blindly to queueing, throughput, memory,
overlapping work, or a workload changed by the intervention.

Select one attributable lever per experiment. Several coordinated edits can
realize one lever. Separate unrelated refactors; allow necessary refactoring or
representation change when it is the optimization. For interacting levers, first
establish isolated effects when practical, then test the combination and record
the attribution limit. Freeze success/guardrails before inspecting the result.

## Validate and adjudicate

Run the target guide's correctness/quality checks and repeat a comparable
before/after measurement. Keep baseline and candidate artifacts distinct. Never
verify only the saved baseline and call that candidate validation. Do not change
the oracle, workload, thresholds, or failure denominator to make a candidate pass.

Use enough observations to distinguish a material effect from noise. Alternate
or randomize comparison order where practical; retain raw samples, variation,
and uncertainty. Ten or thirty process runs do not substantiate a precise
service p99. Report sample size and the unit sampled. Avoid cherry-picked best
runs, hidden failures, and comparing different machines/builds as a code effect.

Accept only an improvement supported on the declared objective while guardrails
hold. Treat a tradeoff as such and obtain authority for a changed contract. Keep
an inconclusive candidate separate from the accepted baseline. Revert only
session-owned unsuccessful changes when authorized; otherwise report the exact
pending disposition without clobbering concurrent work.

## Iterate, guard, deliver

After acceptance, re-baseline and re-profile the changed system. Validate the
cumulative candidate against the original baseline on representative and stress
cases; successive local wins can interact. Continue while the objective, evidence,
remaining opportunities, and authority justify work. Do not stop at an arbitrary
round count, or keep escalating complexity solely because a round elapsed.

Preserve a reproducible regression benchmark and relevant correctness/quality
cases using the project's existing mechanism. Set noise-aware thresholds from
the actual workload and CI environment, not a universal percentage. Separate
slow/noisy scheduled checks from stable per-change checks when appropriate.
Document rollback with state/schema compatibility, not merely `git revert` when
external state has changed. Production rollout/monitoring needs its own authority.

Report original/final results, environment, commands, uncertainty, protected
behavior, rejected attempts, tradeoffs, and remaining bottleneck through Tune's
existing report. This procedure proves neither global optimality nor efficacy
on unmeasured workloads.
