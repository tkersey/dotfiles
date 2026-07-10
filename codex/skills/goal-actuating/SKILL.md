---
name: goal-actuating
description: "Coordinate an accepted implementation goal or explicit review workflow through actuation-run/v1. Select one bounded step, delegate its execution to $goal-grind, fold evidence, consume review-resolution/v1, acquire CAS review evidence when required, and request closure-decision/v1 without owning publication."
---

# Goal Actuating

## Mission

Be the sole coordinator for an authority-bound run.

~~~text
accepted source + GoalContract
-> actuation-run/v1
-> select one step
-> $goal-grind action
-> $evidence-fold
-> update run
-> $ship
-> review-closeout
-> final closure-decision/v1
~~~

This skill coordinates. It does not redefine accepted semantics, implement raw
review prose, duplicate the selected-step executor, derive final proof prose,
or publish.

## Inputs

- an accepted implementation spec or direct user goal;
- a source-bound GoalContract;
- an accepted plan handoff when one exists;
- optional topology advice from `$agent-loop-schemes`;
- current review evidence and `review-resolution/v1` for review work.

Treat the accepted source as immutable authority. A plan handoff is policy and
scope, not mutation permission.

## Modes

~~~yaml
goal_actuating_mode:
  mode: implement | triage | remediation-plan | review-closeout
  persistence: update_plan | goal-artifacts
  execution: none | direct | iterative
  review: none | existing-source | cas-fresh | cas-closeout
  parallelism: none | scout-fanout | review-class-fanout | proof-fanout
  closure: no-code-output | local-completion | ship-handoff | blocked
~~~

Unqualified review means `triage`. Only explicit fix, address, resolve,
implement, or closeout intent selects `review-closeout`.

Bare `$actuating` and `/goal $actuating` run the ordered lifecycle `implement ->
$ship -> review-closeout -> final closure`. `$actuating implement` runs only the
implementation phase. Ship handoff is therefore a continuation point, not a
terminal result, for a bare invocation. The original invocation profile is an
immutable run field; publication intent cannot relabel an explicit implement
run into the bare pipeline.

## Run ownership

Create or refresh `actuation-run/v1` with:

- source and execution authority references;
- immutable invocation profile, current phase, generation, and implementation
  checkpoint;
- current repo, base, branch, head, live-state fingerprint, and initial
  per-path state map;
- allowed paths and effect boundaries;
- direct or iterative execution kind;
- current selected step, completed step chain, and evidence references;
- review requirement, source references, Codex thread ID for CAS closeout, and
  publication intent.

Before mutation, validate the run with `$actuating`'s gate. Direct work is a
one-step run; it is not an exceptional control path.

## Coordination loop

1. If source authority or artifact binding is stale, block.
2. If topology changes execution and no advice exists, request normalized step
   topology from `$agent-loop-schemes`.
3. Project a WorkGraph only when decomposition matters.
4. Select exactly one ready node as lead.
5. Record the phase-tagged selection in the run, validate it, and embed the
   gate-derived `step-admission/v1` before action.
6. Invoke `$goal-grind` once for each selected leaf.
7. Integrate accepted action results in deterministic order.
8. Run `$evidence-fold` over tests, diffs, logs, and artifact state.
9. Attach the evidence to the completed step and refresh the artifact binding.
10. Continue only when the updated run validates.

No step may claim parent completion. A node result of done means only that the
node is closed.

## Review handoff

For review work, preserve the order and artifacts required by `$actuating`'s
Review law: CAS evidence, RF-v2 classification, current resolution, admitted
selected node, embedded `review-admission/v1`, action evidence, and
closure-grade review. For publication-bearing closeout, first preserve the
complete SHIP-v1 as `review.ship_receipt`. Let the gate validate that receipt
and derive the specialized review admission plus the generic step admission;
embed both in the selected edit before mutation, bind the review digest through
the generic receipt, and require EF-v1 to cite the review digest.
Preserve `review-closeout` while review is required; changing the mode cannot
retire admission history. A terminal resolution may name only nodes observed in
completed admitted edits. `$actuating` alone
defines lens derivation, CAS eligibility, semantic balance, and closure. This
coordinator schedules those owners without restating their rules.

## Parallelism

Allowed:

- read-only scouting over independent areas;
- classification fanout after review findings are quotiented;
- proof checks over independent commands.

Mutation is serial through the one selected node. Replacement-kernel work stays
at its owner boundary instead of being divided into comment-sized patches.

The lead owns scope, selection, fan-in, integration, resolution, review
accounting, and closure. Subagents remain advisory until folded and may not
publish or complete the goal.

## Closure

For a bare invocation, hand implementation to `$ship`, resume with
`review-closeout` in the same append-only run, and only then ask `$actuating` for the final
`closure-decision/v1`; a valid SHIP-v1 returns control here with goal
`continue`, implementation `complete`, this coordinator as next owner, and a
gate-derived implementation checkpoint. Copy that checkpoint into the run,
advance its phase and generation, and retain `artifact_initial`, every
implementation step, and every evidence reference. Never construct a fresh
review run that merely shares the ID. A clean review epoch adds no synthetic
step. Do
not duplicate or precompute final closure conditions. If an admitted
publication-bearing review edit completes, obtain its current resolved refold,
accept `ready-to-ship`, replace `review.ship_receipt` through `$ship`, and only
then resume another edit or final CAS. The replacement must update the same PR
URL retained in the prior admission; a newly created PR does not continue the
review epoch. Only a
current final closure may feed `$proof-patch`. Explicit implementation-only work
stops before ship, and local completion for other workflows skips the ship
branch.

## Stop rules

Stop whenever the current run validator, resolution validator, evidence fold,
or closure gate blocks. Do not reinterpret the failure locally.

## Output

~~~text
Goal Actuation:
- run ID and current artifact binding
- mode and execution kind
- selected/completed step
- evidence-fold verdict
- closure decision or next owner
- blockers and residual risk
~~~
