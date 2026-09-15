---
name: tune
description: "Optimize software and agentic systems from measured bottlenecks, latency, throughput, memory, cost, reliability, or task-quality evidence; create, edit, and diagnose Codex skill packages, including activation and behavioral regressions. Use for performance optimization, profiling, algorithmic improvements, agent effectiveness, or skill-package work, not unrelated feature development or cosmetic application edits."
---

# Tune

## Mission

Improve the measured effectiveness and efficiency of software, agentic systems,
and skill packages. Preserve protected contracts, identify the limiting mechanism,
make an attributable intervention, and verify the result. `$tune` remains the sole owner
of skill creation, direct editing, and evidence-backed behavioral tuning.

One skill owns diagnosis, selection, and authorized mutation. Keep those phases
distinct; do not hand off merely because the target is code rather than a skill.

## Select the target before the procedure

| Target | Primary evidence | Required route |
|---|---|---|
| Software: application, library, service, runtime, build, or tool implementation | Representative workload, profile, correctness oracle, resource measurements | [performance.md](performance.md) and its software guide |
| Agent system: prompts, tools, retrieval, orchestration, harness, or model configuration | Task evaluations, traces, quality, latency, cost, and failure denominators | [performance.md](performance.md) and its agent guide |
| Skill package: creation, specified package change, or behavioral diagnosis | Current package and requested delta; decision episodes when attribution is needed | Skill-package guidance below |

A mixed target loads only the guides implicated by its objective and intervention.
For example, an agent latency problem can require software profiling of a tool;
a measured skill-overhead problem can require both package authoring and agent
measurement. Reuse one objective and evidence set, not parallel dossiers. Do not
assume that a prompt edit is the remedy before locating the limiting mechanism.

Software work does not require skill discovery, activation history, a decision
receipt, or `agents/openai.yaml`. Skill creation and known package edits do not
require unrelated performance benchmarks. Ordinary feature work without a tuning
objective remains outside implicit activation.

## Public modes

Choose one intent mode, independently of target and authority:

```text
create  -> create a skill when no existing owner covers the intent
edit    -> apply a requested concrete change or known defect repair
tune    -> diagnose and improve from evidence, including performance optimization
```

Infer `create` for an uncovered skill request, `edit` for a specified change, and
`tune` for questions about behavior, effectiveness, bottlenecks, or regressions.
An explicit `$tune create`, `$tune edit`, or `$tune tune` overrides mode inference,
not target selection, authority, or validation. `create` is not a general-purpose
application generator. A specified code optimization in `edit` mode still follows
the performance route; it cannot bypass baseline or preservation checks.

`inspect`, `apply`, target kind, regression, evidence source, publication state,
and terminal result are not modes.

## Authority gates

### Mutation

`inspect` forbids file changes. Select it for analyze, audit, review,
inspect, "what should change?", proposal-only, or an explicit no-edit request.
Read existing evidence; run non-mutating observations only when authorized and
safe. Do not write benchmark files, generate outputs, invoke effectful workloads,
install tools, or create branches under inspect authority or an explicit
no-file-changes request.

`apply` authorizes changes inside the requested target surface. Select it for
create, edit, fix, update, apply, patch, optimize, or improve when the target and
objective are clear. An explicit prohibition on edits always wins. Diagnose and
freeze the expected delta before tune-mode mutation. A known direct skill edit
does not need a manufactured historical dossier.

Neither authority grants production load, paid evaluations, network access,
profiling of unrelated processes, data export, deployment, or relaxed security
controls. Use existing permissions and budgets; otherwise report the specific
blocked effect while continuing independent authorized work. Redact secrets and
private payloads from profiles, traces, fixtures, and published evidence.

### Publication

Local mutation does not authorize Git effects.

```text
commit  -> explicit commit, save-to-git, publish, ship, or PR intent
push    -> explicit remote publication intent after the intended commit succeeds
PR      -> explicit PR intent
```

One attributable experiment need not be one commit. Follow repository integration
policy; do not rewrite shared history or discard unrelated work for a benchmark.
Report a concrete blocker when requested publication cannot complete.

## Skill-package guidance

For a skill-package target, read its `SKILL.md`, `agents/openai.yaml`, and existing
decision contract first. Search for an existing owner before creating a package.
Load [create.md](create.md), [edit.md](edit.md), or [tuning.md](tuning.md) for the
selected mode. Read [authoring.md](authoring.md) before selecting or realizing a
package intervention, including proposal-only surgery. It owns progressive
disclosure, cognitive compilation, semantic-weakness selection, package integrity,
and the fresh-eyes pass. A diagnosis ending in `no-change` need not load authoring.

Load deeper references, scripts, assets, and definitions only when the mode or
change depends on them; inspect affected integrations before editing. Root owns
every skill-package edit. Retain existing Seq/Ledger ownership and privacy rules;
their skill-history adapters are not prerequisites for software benchmarks.

A supported defect in current package text can justify a direct edit. Historical
claims about activation, recurrence, influence, or outcomes require behavioral
evidence. Preserve the distinctions among activation, decision influence, and
outcome causality, and all stable contract IDs. Doctrine vocabulary alone is not
a behavioral improvement. Cognitive changes still use the conditional authoring
reference; mechanical changes do not acquire a cognitive-compilation ritual.

<a id="progressive-disclosure"></a>
Progressive disclosure: [authoring.md](authoring.md#progressive-disclosure).
<a id="cognitive-compilation"></a>
Cognitive compilation: [authoring.md](authoring.md#cognitive-compilation).
<a id="intervention-selection"></a>
Intervention selection: [authoring.md](authoring.md#intervention-selection).
<a id="decision-instrumentation"></a>
Decision instrumentation: [authoring.md](authoring.md#decision-instrumentation).
<a id="package-rules"></a>
Package rules: [authoring.md](authoring.md#package-rules).
<a id="fresh-eyes-pass"></a>
Fresh-eyes pass: [authoring.md](authoring.md#fresh-eyes-pass).
<a id="create-mode"></a>
Create mode: [create.md](create.md#create-mode).
<a id="edit-mode"></a>
Edit mode: [edit.md](edit.md#edit-mode).
<a id="tune-mode"></a>
Skill tune mode: [tuning.md](tuning.md#tune-mode).

## Common kernel

1. Resolve target, objective, mode, authority, and selected guidance.
2. Reconstruct only the operative contract: required observations, protected
   behavior, consequential decisions, authority, stopping conditions, and
   observable success/failure. For skills, include trigger and non-trigger bounds.
3. Acquire the evidence the selected route needs. For performance, establish a
   representative baseline and identify the limiting mechanism before optimizing.
4. Before mutation, freeze in the native workflow, not a new mandatory receipt:
   ```text
   expected delta: from -> to
   protected behavior and acceptance criterion
   evidence and its limits
   selected intervention and why it addresses the mechanism
   mutation authority
   ```
5. Select one dominant valid intervention per cycle, or no change. For package
   policy, semantic weakness precedes physical minimality. For performance,
   compare expected end-to-end benefit, confidence, risk, and cost; do not invent
   a universal numeric cutoff or choose by diff size alone.
6. Apply only when authorized. A coherent intervention can span multiple files.
   Preserve unrelated behavior, concurrent work, and required evidence.
7. Validate the protected contract and the strongest currently observable claim.
   Code needs a preservation argument and executed evidence; agents need outcome
   quality as well as resource measurements; packages need integrity and relevant
   behavioral probes. Tests and checklists are not automatically formal proofs.
8. Retain, revise, or discard from evidence. Re-measure and re-profile accepted
   performance changes because the bottleneck may move. Finish the authorized
   objective/set; do not stop after the first win or repeat without a discriminator.
9. Run a fresh-eyes pass over correctness, routing, authority, and claim strength;
   use the package-specific pass when editing a skill. Publish only as authorized.

If materially new evidence invalidates the expected delta or selected intervention,
return to the contract/evidence step; do not silently broaden scope during editing.
For an explicitly requested portfolio pass, select independently per target and
finish the authorized set. An available implementation or another skill is not a
reason to stop before requested validation and delivery.

## Outcome observation and stops

Run a current observation when it can exist within authority. Otherwise retain
an exact reproduction/evaluation command or query and identify what remains
unproved. Missing tooling permits bounded diagnosis, not fabricated measurements
or a claim that an unmeasured patch is faster.

A text edit proves changed text, not activation, reasoning quality, or outcomes.
A faster microbenchmark does not establish a faster system. Fewer tokens, model
calls, or steps do not establish a better agent. Do not silently trade accuracy,
ordering, numerical semantics, reliability, safety, or security for speed.
Approximation needs an existing allowance or explicit authorization with bounds.

Stop when the objective is satisfied, no worthwhile supported candidate remains,
the authorized budget is exhausted, or a concrete blocker prevents the next
necessary effect. Distinguish `no-change`, `inconclusive`, and `blocked`; do not
claim global optimality. Rejected experiments do not count as retained gains.

## Report

```text
Tuned:
- Target and objective:
- Mode: create | edit | tune
- Mutation: inspect | apply
- Expected delta and protected behavior:
- Evidence and limits:
- Selected intervention:
- Files changed:
- Validation and outcome observation:
- Before/after, variability, and tradeoffs:
- Retained/rejected experiments and stopping reason:
- Publication:
- Remaining uncertainty:
```

Omit empty or inapplicable fields. Put the useful result last after any execution
narration. When changing Tune's scope/routing, use
[performance-probes.md](references/performance-probes.md) alongside existing
package/cognitive probes; those are change-validation cases, not a startup gate
for each optimization.
