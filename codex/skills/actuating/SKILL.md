---
name: actuating
description: "Front door for authority-bound goal execution. Bare $actuating or /goal $actuating runs implement, then $ship, then review-closeout; explicit $actuating implement stops after implementation. Explicit triage, remediation-plan, and review-closeout retain their named behavior; never infer mutation from an unqualified review request."
---

# Actuating

## Mission

Turn accepted intent into an authority-bound run, selected work, current
evidence, and a live closure decision.

~~~text
bare $actuating:
accepted source -> implement -> $ship -> review-closeout -> final closure

explicit mode:
accepted source -> named mode -> its terminal output
~~~

`$actuating` routes and governs this workflow. `$goal-actuating` coordinates
execution. `$goal-grind` executes one already-selected step. `$ship` alone owns
public PR effects.

## Modes

Bare `/goal $actuating` and bare `$actuating` select the ordered default
pipeline: `implement -> $ship -> review-closeout`. `$actuating implement`
selects implementation only and stops at its closure decision. Explicit
`triage`, `remediation-plan`, and `review-closeout` select only the named mode.

| Intent | Mode | Mutation | End |
|---|---|---:|---|
| Implement accepted work only | `implement` | Authorized by the run | Implementation closure |
| Review, audit, or classify | `triage` | No | Review report |
| Produce a fix plan | `remediation-plan` | No | Resolution plan |
| Fix or close review findings | `review-closeout` | Only through a selected resolution node | Closure decision |

An unqualified review request means `triage`. Require explicit fix, resolve,
address, implement, or closeout language before choosing `review-closeout`.
Planning requests route to `$plan`; there is no planning mode inside this
skill.

## Canonical objects

Only three actuation control objects are live:

1. `actuation-run/v1` binds source, authority, artifact state, selected steps,
   evidence references, immutable invocation intent, lifecycle phase,
   implementation provenance, review requirements, and public-effect intent.
2. `review-resolution/v1` converts classified findings into owner-boundary
   strategies and admits at most one current work node; other owner decisions
   remain pending.
3. `closure-decision/v1` recomputes the result from the current repository,
   run, resolution, evidence folds, CAS records, and optional ship record.

Read [live-semantics.yaml](references/live-semantics.yaml) for the canonical
runtime vocabulary and policy. Behavioral laws live in the gate and its direct
counterexample tests; prose may explain them but must not create another
authority surface.

Every run records the original invocation profile in `lifecycle`:

~~~yaml
lifecycle:
  invocation_profile: bare-pipeline | explicit-implement | explicit-triage | explicit-remediation-plan | explicit-review-closeout
  phase: implement | review-closeout
  generation: 0
  implementation_checkpoint: null
~~~

The profile never changes. A bare run alone may advance from generation 0
implementation to generation 1 review closeout, and only through the
gate-derived implementation checkpoint. Explicit implementation always keeps
publication false and cannot accept SHIP input or enter review closeout.

## Source and authority

Start a run only from:

- a current accepted specification whose governance result is complete; or
- a direct user goal with explicit execution authority.

A plan handoff supplies scope and policy but does not grant mutation by itself.
A review artifact supplies evidence but never execution authority. A
gate-only specification result cannot authorize execution.

Keep these fields separate:

~~~text
scope_source_ref
execution_authority_ref
mutation_allowed
public_effects_allowed
~~~

Unsupported durable claims, fencing, independent worktrees, or serialized
cross-plan integration block the run. Do not simulate a controller.

## Step law

Before a material mutation:

1. Bind the run to the current repo, base, branch, head, and live-state fingerprint.
   Preserve that first binding as `artifact_initial` and its per-path state map
   as `artifact_initial_path_states`; every first step begins there and every
   later step begins at the prior post-state.
2. Select exactly one step and tag it with its lifecycle phase.
3. Keep selection and mutation fan-in with the lead; advisory scouting,
   classification, and proof checks may fan out.
4. From the repository root, validate the run through `uv` so the checked-in
   non-executable tool and its YAML dependency are handled explicitly:

   ~~~bash
   uv run --with pyyaml python \
     codex/skills/actuating/tools/actuating_gate.py validate-run \
     --run RUN.yaml \
     --repo .
   ~~~

   Add `--resolution RESOLUTION.yaml` for a review-derived edit and repeat
   `--evidence EF.json` for every completed predecessor.

Before any selected action, copy the gate-derived `step-admission/v1` into the
step. It binds the original invocation profile, phase, immutable predecessor
prefix, state before, effect, owner, paths, verifier, and lead selection. Every
completed `inspect`, `edit`, or `verify` action preserves that receipt
unchanged. A terminal record without it is unreachable and blocks.

For a review-derived edit, pass the current resolution to `validate-run`; its one
selected node must exactly match the selected step's ID, owner, paths, and
verifier. Before mutation, copy the gate-derived `review_admission/v1` into the
selected step's `review_admission`. That immutable receipt seals the full
`review-resolution/v1`, admission-time source/path/hunk observations, any
required current SHIP receipt, and its canonical digest. Preserve the receipt
unchanged on completion and cite `review-admission:<admission_digest>` in EF-v1
`review_refs`; `step-admission/v1` binds its digest, so the two receipts form one
admission relation rather than parallel authorities. A later resolution cannot relabel an admitted edit. When
admitting a step after prior work, also pass every referenced EF-v1 with
`--evidence`. A dangling reference cannot authorize continuation.

After the action:

1. Record changed paths and the new artifact binding.
2. Fold current evidence through `$evidence-fold`.
3. Attach that evidence to the completed step.
4. Continue only after the run validates again.

Each step names one executable `effect` (`inspect`, `edit`, or `verify`), exact
paths, and a falsifiable `verifier`. CAS acquisition, review folding, and
resolution construction are coordinator work, not executable step effects. One
direct edit may remain uncommitted and must exactly match the initial-to-live
path delta. Every iterative edit advances through a descendant commit whose
exact diff equals that step's changed paths. A non-edit preserves the complete
artifact binding. EF-v1 independently reports the same paths and shows the
verifier in its passed-command evidence. Only a prior step whose verdict is
`continue` may admit a following step.

A step may finish or block. It cannot complete the parent goal; only
`closure-decision/v1` owns goal completion.

Direct work is one ordinary selected step. Iterative work is a chain of
selected and completed steps. Resume state lives in the run through the current
step, lifecycle checkpoint, and performed-side-effect identifiers.

## Review law

Fresh or closure-grade workflow review uses `$cas`. Review evidence passes
through `$review-fold`, which only classifies and quotients findings.
Declared run source references must exactly equal the RF-v2 source identities;
triage supplies those folds directly with repeatable `--review-fold` inputs and
cannot complete from a source name alone.

`review-resolution/v1` then consumes each RF-v2 equivalence class through
exactly one decision, groups repair work by owner boundary, and selects:

- `local-repair`;
- `replacement-kernel`; or
- `blocked`.

Read [review-resolution.md](references/review-resolution.md) before resolving
review findings. Raw review prose, a review-fold receipt, a CAS record, or a
suggested repair never grants mutation.

CAS closure accepts only producer-observed standard review attempts. Specialized
routing in RF-v2 remains classification metadata; caller-supplied lens labels
never grant review credit. Standard closure requires three distinct ordered
clean attempts after the latest artifact, review contract, or resolution change.

## Semantic accounting

Audit every abstraction participating in a touched owner-boundary invariant,
including unchanged nearby abstractions.

Use `retain`, `retire`, `collapse`, `delegate`, or `replace`. `retain` requires
a named live obligation.

The gate observes the live diff and binds that identity into review admission;
the continuous admitted step chain supplies path and transition provenance.
It validates the declared abstraction, liability, addition, and retirement
account against that live state. Every declared added construct names a live
obligation and a distinct displaced construct. The gate does not yet perform
language-aware discovery of omitted constructs, so do not claim that it
independently proves net semantic shrinkage.

Closure rejects split decisions for one RF-v2 equivalence class, uncovered
liabilities, incomplete retirements, remaining dominated constructs, and
declared proof-surface growth without an accepted obligation.

`local-repair` may not add a protocol, state, helper abstraction, or
wound-specific test family. Use `replacement-kernel` when local patches would
distribute one cause or preserve dominated machinery.

## Closure

Read [closure.md](references/closure.md) before material completion.

Run:

~~~bash
uv run --with pyyaml python \
  codex/skills/actuating/tools/actuating_gate.py decide \
  --run RUN.yaml \
  --resolution RESOLUTION.yaml \
  --evidence EF.json \
  --repo .
~~~

The gate discovers the installed list action, prefers `cas review list`, and
acquires the complete live envelope itself with the run-bound base and Codex
thread ID. An explicitly advertised `cas review_session list` is the only
fallback. Saved envelopes and individual record files are non-authoritative and
cannot close the run.

The gate reads live repository state and actual evidence. It does not accept
success flags, opaque proof references, scalar clean counts, or replayable
completion approvals.

Separate:

~~~text
goal_outcome
implementation_outcome
next_owner
~~~

For no-code modes, the goal may complete while implementation is
`not-applicable`. For material work, emit the final proof-patch only after a
current closure decision. In the bare pipeline, implementation closure returns
`ready-to-ship`; `$ship` acts, then the same append-only run records the
gate-derived checkpoint described in [closure.md](references/closure.md) and
enters `review-closeout`. A fresh review run that merely reuses the ID is
invalid. Clean review closeout selects no synthetic step. Explicit
`implement` does not infer publication and stops at implementation closure.

`complete`, `ready-to-ship`, and valid `continue` decisions exit zero. Blocked,
malformed, or unavailable-dependency decisions exit two; the JSON verdict is
the workflow result.

## Stop rules

Stop when authority or artifact binding is stale, a selected step is missing,
the prior action lacks current evidence, review resolution is missing, the
standard review contract is invalid, the clean CAS suffix is short, semantic balance is
open, verification regresses, or a public effect would bypass `$ship`.

Use these stable verdicts:

~~~text
actuation verdict: blocked-run-missing
actuation verdict: blocked-run-stale
actuation verdict: blocked-step-missing
actuation verdict: blocked-evidence-fold-missing
actuation verdict: blocked-review-resolution-missing
actuation verdict: blocked-closure
~~~

## Resources

- [live-semantics.yaml](references/live-semantics.yaml) — canonical vocabulary,
  ownership, triggers, and runtime policy.
- [review-resolution.md](references/review-resolution.md) — resolution schema,
  strategy rules, and semantic balance.
- [closure.md](references/closure.md) — evidence joins, CAS suffix, outcomes,
  and ship re-entry.
- [decision-contract.yaml](references/decision-contract.yaml) — trigger and
  routing contract for audit tooling.
