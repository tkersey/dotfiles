# Prepared architectural review

Load when parallel investigation is useful or explicitly required. Parallelism is
optional unless the caller makes it an execution requirement. Several obligations
can be investigated directly; do not create workers to satisfy a count or make
optional transport a prerequisite to assessment.

## Select a usable route

Before deep preparation, inspect the available operation's schema and history
semantics: can it select a fixed prepared source, retain its complete history,
expose verifiable lineage, and support the worker lifecycle? A current-parent-only
`spawn_agent` may inherit history without being able to select that checkpoint.
Do not equate missing source selection with missing context inheritance, or an
absent wrapper with absent native capability.

When the wrapper is insufficient, load the installed `$cas` entry and its selected
[app-server guidance](../../cas/app-server.md), including its compatibility gate,
for native transport only. Use a compatible available route rather than declaring
failure from the wrapper alone. Preserve the actual model, reasoning effort,
working directory, permissions, and any explicit endpoint/transport restrictions.
Do not install, upgrade, repair, or reconfigure tooling just to obtain parallelism;
a transport announcement or successful preflight is not a completed investigation.

Establish source access and route capability before choosing parallel execution;
verify the actual checkpoint after preparation and before launching investigators.
If either fails, withhold affected launches and follow the execution-change rules
below. Respect explicit parallel, topology, and transport requirements; direct
inspection must not be presented as satisfying any of them.

## Shared preparation and verified checkpoint

The coordinator reconstructs the whole selected causal scope once and publishes
the entry contract's source-bound orientation in the transcript. Include a compact
inventory of selected obligations, their material interactions, and assignment
ownership. Existing component boundaries are hypotheses, not assignment borders.
Facts and accepted requirements cite immutable evidence; hypotheses include a
falsifier and no preselected repair or adjudicated consequence.

Bind the preparation to the exact subject, source/document identities, included
working-tree content, accepted requirement versions, selected obligations and
interactions, and installed contract versions. Record a real orientation digest
or runtime content identity; that identity covers the orientation bytes, not the
whole history or independent judgment.

Every initial parallel investigator must inherit the same complete prepared-history
checkpoint, through the orientation and preparation turn, excluding subsequent
worker findings and coordinator adjudication. Use one of these native forms:

- **Immutable seed.** Create one seed from the coordinator after preparation;
  verify its parent and retained history. Give it no assignments, findings,
  follow-ups, or results. Fork every investigator directly from that unchanged
  seed. For this form, reuse Elenctic's installed
  [native-fork transport](../../elenctic/references/native-forks.md) unchanged:
  its Campaign Brief is this orientation, its epoch is this subject binding, and
  its canonical assignment is the assignment below. This imports transport,
  history verification, and provenance, not Elenctic's campaign or GitHub effects.
- **Exact completed preparation cutoff.** When the installed native route supports
  it, fork each investigator from the same source thread ID and the same inclusive
  completed-turn cutoff containing all preparation. Bind both IDs and verify each
  returned parent against that source, not a fictional seed. The documented
  app-server `thread/fork` form uses `threadId` plus `lastTurnId`; the latter must
  not be in progress. This is an Architectonic route, not a relaxation of
  Elenctic's seed procedure. Use it only when the completed checkpoint already
  exists; do not end the task or require another user turn to manufacture one.

The [app-server protocol](https://developers.openai.com/codex/app-server/)
documents that cutoff. Installed compatibility and actual retained history govern
admission, not documentation or a version string alone. With current-turn
preparation and no usable completed cutoff, use the seed form or the direct-work
rules below; never omit the cutoff and fork the evolving parent as a substitute.

Resolve actual source IDs from the runtime and verify them; never guess from a
title, directory, or latest-session search. Before assignment, verify source-to-seed
and seed-to-worker lineage, or source-and-cutoff-to-worker lineage, as applicable.
Read the complete retained history with pagination as needed. Compare the whole
ordered observable history through the checkpoint and its content, excluding only
runtime/fork status and timing metadata; reject later findings in starting context.
Matching orientation digests or parent IDs alone do not establish that property.
A copied orientation, earlier cutoff missing preparation, fresh summary-only agent,
or unbounded evolving-parent fork is not an equivalent checkpoint.

Readback verifies observable history, not opaque reasoning internals. Never expose
raw inherited content. Shared history is orientation, not authority: each worker
revalidates its premises, including prior implementation rationales. Correlated
agreement does not add independent proof. Neither native form invokes Elenctic,
imports its file worker, Viewed/thread mutations, or grants Actuating review credit.

## Assign by obligation

Use the following information in each assignment; omit no material binding:

```text
Role: read-only Architectonic investigator, not a coordinator.
Subject and preparation identity: <exact bound snapshot and orientation identity>.
Checkpoint: <actual immutable seed ID, or source thread ID plus completed cutoff ID>.
Assignment identity: <coordinator-assigned identifier>.
Obligation / interacting law family: <accepted outcome and source>.
Causal scope and known interactions: <paths and relevant scenarios, not a file fence>.
Nomination ownership: <this decision, or the other named assignment that owns it>.
Installed contracts: <resolved Architectonic entry, investigation, and Universalist binding>.
Task: verify premises locally; trace the obligation end to end; challenge incumbent
and any admissible alternative; try to falsify retained conclusions; return the
assignment/binding identities, findings, evidence, actual check outcomes, residuals,
interaction consequences, and exact covered/uninspected obligations.
Authority: no writes/publication, coordinator entry points, spawning, or nested teams.
```

An investigator may use Universalist inline only for its owned live decision under
Architectonic composition; it must not delegate again. Shared decisions get one
nomination owner, not competing duplicate Universalist passes. Other workers
report interaction evidence to the coordinator. Do not artificially separate laws
whose validity depends on each other.

Keep at most 20 investigators active, or the caller's lower positive limit. Match
actual supported capacity; admit work on completion and replenish rather than
launching everything or imposing a limit on causal exploration. Track actual
thread/turn IDs, assignment, subject/preparation identity, and terminal state.
A timeout or transport failure is not semantic completion. On uncertain delivery
or reconnect, recover the exact turn state before retrying the same assignment;
do not infer non-delivery or launch a duplicate.

## Admission and synthesis

Read the exact terminal report. Match its worker, turn, checkpoint lineage,
preparation, subject, assignment, and contract identities. Inspect the supporting
evidence and check semantics, not merely a successful envelope or the worker's
chosen label. Reject mismatched, stale, missing, truncated, or unbound completion
as worker coverage. Keep independently verifiable facts as evidence, without
upgrading an unadmitted report to a completed assignment.

A valid complete report may contain defects, risk, or missing mandatory proof;
transport/provenance validity does not grant acceptance. A worker's scoped
completion also does not establish another worker's obligation or a cross-worker
interaction. The coordinator owns adjudication and must inspect material
interactions itself or assign a bounded follow-up tied to the same evidence.
A follow-up that receives findings is not another independent checkpoint-based
review; label its lineage and re-adjudication purpose honestly.

## Recover or change execution

When optional parallel work cannot start or continue through a compatible route,
state the specific failure and switch the unfinished obligations to direct
investigation. This is a changed execution strategy, not equivalent fork provenance.
An earlier internal choice to parallelize does not prohibit this change. Do not
turn the fallback into tool-repair loops or narrow the agreed assessment scope.

For failures after launch, retain admitted reports only while their subject and
evidence remain valid. Recover known worker/turn state where possible; explicitly
supersede affected unfinished assignments before taking them over directly. Request
interruption of this assessment's obsolete live turns when the authorized transport
permits it. Do not claim an unknown turn stopped, interfere with unrelated workers,
or treat a late report as a second authoritative owner or completed replacement.
Late/unadmitted reports are leads only, independently verified before use.

Apply the full [investigation contract](investigation.md) to every taken-over
obligation and its material interactions, rechecking subject binding and actual
check outcomes. Preparation, a worker summary, a transport receipt, or a changed
label cannot supply missing investigation. Preserve supported defects and failed
mandatory checks until evidence actually resolves them. A route change cannot
repair unavailable source evidence or discharge a mandatory verification condition.

Report the actual execution as direct, prepared-parallel, or mixed, identifying
material strategy changes and remaining gaps without a second report or ledger.
A failed optional transport need not leave architectural coverage incomplete once
all selected obligations and interactions have been genuinely investigated. If
parallelism, a topology, or a transport was explicitly required, report any unmet
execution requirement separately even when useful direct evidence is available;
do not claim the requested assessment complete or silently waive it. Continue only
inspection the caller permits; explicit prohibitions on direct work still apply.

Use the entry contract's reconciliation and output rules. Withhold a complete
assessment while any selected material obligation or interaction lacks valid
coverage; preserve verified findings alongside the missing coverage. No file count,
Viewed marker, unanimous verdict, or passed optional check substitutes for it.

Changes to material subject inputs, requirement versions, selected scope, installed
contracts, or orientation invalidate affected preparation and coverage in every
execution strategy. Do not silently patch a checkpoint or mix epochs. Reprepare
and bind a fresh checkpoint for new parallel work; previous findings are hypotheses
until revalidated. Unchanged admitted evidence need not be repeated solely because
execution changed. Recover lost provenance through exact runtime facts or use the
direct-work rules, never a title/latest-session guess. No persistent campaign ledger
or new executable is required.
