---
name: hylo
description: "Compile real Codex sessions and repo-local Ledger evidence into portable replay campaigns, run blind repeated attempts in reconstructed or generated environments, grade outcomes with evidence-bound rubrics, append attempts and grades to `.ledger/hylo/events.jsonl`, and derive comparable progress/frontier views. Use for `$hylo`, self-replay, experience-driven evaluation, session-derived training environments, replay-and-grade loops, repeated agent or skill improvement on real historical requests, or tracking whether responses improve across controlled reruns."
---

# Hylo

## Mission

Turn lived execution history into a renewable improvement substrate.

```text
unfold(session evidence + Ledger evidence) -> portable replay scenarios
interpret(scenario, target version)         -> attempt trace
grade(trace, rubric version)                -> evidence-bound grade
fold(append-only events)                    -> progress frontier
select(frontier)                            -> next replay, mutation, repair, or stop
```

Hylo is not a static benchmark and does not train model weights. It repeatedly
exercises an agent, skill, prompt, workflow, or model configuration against
real work, records what happened, and supports evidence-bound behavioral
improvement.

## Ownership

Keep these boundaries explicit:

```text
$seq       selects and freezes historical session evidence
$cas       owns controlled thread or transcript replay lifecycle
$retrace   owns bounded historical-decision experiments and epistemic claims
$ghost     may export a portable behavior contract
$emulator  may instantiate or mutate synthetic worlds from that contract
$hylo      owns campaigns, splits, rubrics, grade lineage, iteration, and progress
$tune      diagnoses a target-skill delta from Hylo evidence
$refine    edits a target skill only after an explicit apply gate
$learnings captures a durable cross-task lesson, not every grade
```

`$goal-grind` executes one capability already prepared by `$goal-actuating`.
It is not a campaign runner and must not create Hylo authority or loop itself.

## Core artifacts

Use three portable contracts:

```text
hylo-campaign/v1  target, source corpus, rubric, replay policy, stop policy
hylo-scenario/v1  one source-governed request, world, oracle, and split
hylo-event/v1     append-only campaign, attempt, grade, feedback, and close evidence
```

Derive `hylo-progress/v1` from events. Never store a progress summary as peer
truth or hand-edit it.

Read [contracts.md](references/contracts.md) before creating a campaign or
writing events. Read [grading-and-progression.md](references/grading-and-progression.md)
when selecting graders, comparing target versions, or declaring improvement.

## Ledger boundary

Before the first native Ledger command in a workflow, load `$ledger` and
complete `$ledger ensure` once. Use native Ledger sources only for the evidence
they own.

Probe the required source before compiling or running a campaign:

```bash
ledger --version
ledger --source hylo --help
```

Require Ledger `>= 0.6.1`, and confirm that Hylo help advertises
`snapshot-target` as well as `validate-campaign`, `append`, `doctor`, and
`progress`. `$ledger ensure` establishes command availability, not this version
floor. If either check fails, stop before creating or mutating a campaign and
report that the native source must be upgraded. Never route Hylo grades through
`learnings`, `negative-ledger`, `actuation`, `synesthesia`, or `universalist`
merely to obtain append semantics.

The native Hylo source is the exclusive mutation owner for:

```text
<repo>/.ledger/hylo/events.jsonl
```

Use it directly:

```bash
ledger --source hylo doctor --repo <repo>
ledger --source hylo snapshot-target --repo <repo> --revision INDEX --input <roots.json>
ledger --source hylo append --repo <repo> --json <intent.json>
ledger --source hylo progress --repo <repo> --campaign-id <id> --format markdown
```

Ledger adds sequence numbers, campaign lineage, timestamps, canonical body
digests, and global plus per-campaign hash chains. Do not write the JSONL
directly.

## Modes

Choose exactly one mode per invocation:

```text
compile   select source episodes and produce a portable campaign
run       execute selected scenarios and record attempt evidence
grade     apply a frozen rubric to recorded attempts
iterate   perform one bounded run -> grade -> next-route cycle
report    derive progress, frontier, and comparability limits
doctor    validate campaign artifacts or the event chain
```

`iterate` performs one cycle unless the user explicitly requests persistent
goal execution. A terminal request does not authorize target edits, external
effects, or unbounded model spend.

## Request shape

Prefer:

```yaml
hylo_request:
  mode: compile | run | grade | iterate | report | doctor
  target:
    kind: skill | agent | prompt | workflow | model_configuration
    id:
    fingerprint:
  source:
    session_ids: []
    query:
    root: ~/.codex/sessions
    exclusions: [current_session, injected_skill_text, quoted_transcripts]
  campaign_id:
  scenario_budget:
  repeat_count:
  privacy: sanitized | local_full
  replay_fidelity: transcript_only | workspace_snapshot | controlled_replay | synthetic_mutation
  target_change_authority: none | propose | apply_via_owner
  publication_authority: none | commit
```

Default to `sanitized`, exclude the current session, and keep target change and
publication authority at `none` unless the user explicitly grants more.

## Workflow

### 1. Freeze the source corpus

Probe the installed Seq surface first:

```bash
seq --version
seq capabilities --format json
seq decision-capsule --help
```

Use the narrowest lifted command: `decision-capsule`, `turns`,
`session-detail`, `skill-decision-audit`, or another advertised surface. Do not
parse raw session JSONL when Seq owns the fact. Record the corpus window,
session IDs, exclusions, Seq version, and corpus fingerprint.

Separate source material into:

```text
visible_input      request and context available to the replay target
hidden_reference  original response, later outcome, private oracle data
world_evidence    repo revision, files, tools, permissions, external state
outcome_evidence  tests, review findings, user feedback, side effects
```

Never expose hidden reference material to a blind attempt.

### 2. Compile replay syntax

Create `campaign.json` and `scenarios.jsonl` using the portable contracts.
Each scenario must bind:

- source refs and fingerprints;
- an evidence-bound redaction receipt before session text is persisted;
- user request and visible context;
- a versioned replay adapter, snapshot, setup plan, toolchain, fixtures, and
  reconstructability limits;
- enforceable filesystem, network, and external-effect boundaries;
- deterministic oracles and trace invariants;
- optional model/human rubric dimensions;
- split: `practice`, `holdout`, or `challenge`;
- mutation parent and preserved invariants when generated.

Freeze every scenario ID, split, and canonical fingerprint into the campaign's
`scenario_manifest`. Admit the complete manifest before the first attempt; an
unadmitted scenario is not an optional case.

Treat missing historical state as explicit missingness. Do not fabricate an
exact world. Use `$ghost` when a reusable language-neutral behavior contract is
needed; use `$emulator` for generated or mutated worlds.

Validate before running:

```bash
ledger --source hylo validate-campaign --campaign <campaign.json>
```

### 3. Establish two baselines

First ingest and grade the response that actually occurred as a
`historical_baseline`. Use later outcome, tests, review findings, user feedback,
and trace evidence to expose its strengths and failure frontier. The original
response is evidence, not a golden answer.

Historical grades are diagnostic and never comparison-eligible: the exact
model state, workspace, or environment may be unavailable. Then record at
least one blind `replay_baseline` attempt of the historical
target/configuration before any candidate attempt for the same scenario. Grade
practice baselines immediately. Keep holdout and challenge results quarantined
until the candidate change is frozen; their baseline attempts may be recorded
first and graded afterward. That controlled replay establishes the comparable
denominator without choosing it after observing the candidate.

Use CAS/Retrace when historical lineage matters; use an explicitly declared
adapter for reconstructed or synthetic environments. Record origin, role,
target, environment, replay-policy, trace, and artifact fingerprints.

A replay is a new execution. It is not the source model's hidden reasoning and
must not be described as recovered chain of thought.

Historical attempts use explicit `exact`, `partial`, or `unavailable`
provenance and do not borrow replay environment or policy fingerprints. For a
Git-backed controlled target, use the native `snapshot-target` command to bind
the replay to an immutable revision or the staged `INDEX` projection.

### 4. Grade evidence

Apply graders in this order:

1. state assertions, tests, schemas, and side-effect checks;
2. trace invariants, forbidden actions, budgets, and permission checks;
3. calibrated model judgment where deterministic checks cannot express quality;
4. human judgment for ambiguous, high-stakes, or rubric-calibration cases.

Bind every grade to attempt, target, rubric, environment, replay policy, judge,
per-dimension grader, oracle result, and evidence refs. Freeze judge and
dimension authority in campaign syntax and oracle authority in scenario syntax
before any replay; native Ledger rejects declared drift. That is declaration
consistency, not authentication: deterministic and trace graders need
independently inspectable execution receipts, and human grades need human
confirmation. Keep dimension scores visible. Native Ledger recomputes the
scalar and pass/fail status from the frozen policy; a caller-authored mismatch
is invalid.

### 5. Fold progress and select the next frontier

Derive the current view:

```bash
ledger --source hylo progress \
  --repo <repo> --campaign-id <id> --format json
```

Prefer the smallest next action that can change the observed failure:

```text
replay same scenario for reliability
shrink or clarify a counterexample
add a missing deterministic oracle
repair an environment reconstruction gap
propose one target change through its owner skill
promote an unseen holdout scenario
stop because the frontier is empty or the budget is exhausted
```

When a target skill appears deficient, emit evidence suitable for `$tune`.
When change authority is `apply_via_owner`, route the smallest bounded repair
through the target owner (`$tune` -> `$refine` for skills, the repository's
normal implementation workflow for code, or `$goal-actuating` for a prepared
goal operation). Hylo remains the campaign controller; it does not bypass the
owner's apply gate.

After applying a candidate change through its owner:

1. use only failing practice evidence as repair motivation; never tune against
   holdout or challenge results inside the same campaign;
2. stage exactly the authorized paths and record the verified
   `git-index:HEAD` diff, before/after target fingerprints, owner, and
   validation evidence as `change_recorded`;
3. before every candidate attempt, rederive the recorded staged-diff
   fingerprint, require tracked and untracked cleanliness across every target
   root, and snapshot `INDEX`; drift invalidates the change and requires a new
   owner-routed `change_recorded` event;
4. rerun every practice scenario, then reveal and grade the quarantined
   baseline plus candidate results for untouched blind holdout/challenge cases;
   after an eligible holdout or challenge grade is recorded, the campaign is
   sealed against further repair;
5. repair only a practice failure. A holdout or challenge miss requires
   rejection or a new campaign with untouched cases; never adapt this candidate
   from the exposed result;
6. require the latest configured repeat cohort for every frozen scenario to
   pass; older successes cannot hide a newer failure;
7. when `publication_authority=commit`, review the unchanged staged diff, run the
   repo-required learning disposition, stage only campaign-owned changes, and
   create the commit;
8. append `publication_recorded` with the change ID, commit SHA, committed
   paths, target fingerprint, validation refs, and eligible promotion-grade
   IDs.

Ledger rejects publication unless the commit's target projection exactly
equals the snapshot graded during promotion. Overlapping edits after grading
therefore invalidate publication rather than silently riding the old grades.

The invocation must grant commit authority explicitly. Do not infer it from
`iterate`, “improve,” or a terminal/persistent request. Pushing remains outside
the Hylo v1 publication authority.

### 6. Rebaseline honestly

Start a new campaign when the rubric semantics, visibility policy, or required
environment observations change. Do not splice incomparable epochs into one
trend. A target-only change may remain in the same campaign when all comparison
fingerprints stay fixed.

## Improvement gate

Claim improvement only when all hold:

- source and split membership are fixed;
- candidate attempts were blind to hidden references;
- rubric, environment, replay policy, and required observations are comparable;
- critical invariant violations did not increase;
- the claimed dimension or pass-rate delta is derived from eligible events;
- baseline and candidate grader configurations are identical;
- holdout evidence supports generalization when the claim extends beyond practice cases;
- uncertainty and sample size are reported.

Otherwise report `practice_gain`, `incomparable`, `insufficient_evidence`, or
`regression` rather than `improved`.

## Stop conditions

Stop the campaign when any configured condition fires:

```text
verified frontier empty at required reliability
holdout threshold met with zero critical violations
no measurable delta across an operator-declared patience window
budget, latency, or attempt cap reached
grader or environment validity fails
target change requires missing authority
human-owned ambiguity blocks a meaningful next scenario
```

An empty practice frontier without holdout evidence is not general capability.

## Output

```text
Hylo:
- mode / campaign / target fingerprint
- source corpus / exclusions / split counts
- replay fidelity / environment limitations
- attempts / eligible grades / critical violations
- comparable deltas / holdout result / uncertainty
- current frontier
- event-chain head / progress fingerprint
- next route: replay | mutate | repair-environment | handoff-tune | rebaseline | stop | blocked
```

## Hard rules

- No scenario without source lineage or an explicit synthetic parent.
- No blind attempt may see the source response, later outcome, or hidden oracle.
- No grade without attempt evidence and a frozen rubric fingerprint.
- No model judge may be the sole authority for safety-critical behavior.
- No comparison across changed grade, environment, or visibility semantics.
- No progress claim from practice cases alone when generalization is claimed.
- No target edit without explicit authority and the target owner's workflow.
- No attempt before the complete frozen scenario manifest is admitted.
- No holdout or challenge evidence may motivate a repair in the same campaign.
- No new repair after an eligible holdout or challenge grade has been exposed.
- No candidate comparison without a like-for-like controlled replay baseline.
- No candidate attempt before the matching replay-baseline attempt.
- No commit without explicit campaign publication authority and a passing blind promotion gate.
- No promotion from cherry-picked historical passes; the latest repeat cohort must pass.
- No publication unless committed target bytes equal the promoted target snapshot.
- No staging unrelated paths; do not force-add locally excluded Hylo Ledger artifacts.
- No raw capabilities, secrets, private reasoning, or unredacted sensitive data in campaign artifacts or events.
- No hand-editing `.ledger/hylo/events.jsonl`.
- No fallback store writer when the native Hylo source is unavailable.
- No infinite self-improvement claim: report the observed campaign boundary and stop rule.
