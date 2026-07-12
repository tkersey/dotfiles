---
name: actuating
description: "Front door for authority-bound goal execution through the actuation kernel. Bare $actuating or /goal $actuating runs implement, then $ship, then review-closeout; explicit $actuating implement stops after implementation. Explicit triage, remediation-plan, and review-closeout retain their named behavior; never infer mutation from an unqualified review request."
---

# Actuating

## Mission

Turn accepted intent into conserved obligations, capability-admitted effects,
independent observations, and a live kernel-derived closure decision.

~~~text
bare $actuating:
accepted source -> implementation generation -> $ship -> review generation -> final closure

explicit mode:
accepted source -> named mode -> its terminal output
~~~

`$actuating` routes and governs this workflow. `$goal-actuating` coordinates
execution. `$goal-grind` executes one already-selected operation. `$ship` alone
owns public PR effects.

## Modes

Bare `/goal $actuating` and bare `$actuating` select `implement -> $ship ->
review-closeout`. `$actuating implement` selects implementation only. Explicit
`triage`, `remediation-plan`, and `review-closeout` select only the named mode.

| Intent | Mode | Mutation | End |
|---|---|---:|---|
| Implement accepted work only | `implement` | Authority-bound | Local completion |
| Review, audit, or classify | `triage` | No | Review report |
| Produce a fix plan | `remediation-plan` | No | Resolution plan |
| Fix or close review findings | `review-closeout` | Resolution-bound | Ship handoff or completion |

An unqualified review request means `triage`. Require explicit fix, resolve,
address, implement, or closeout language before choosing `review-closeout`.
Planning requests route to `$plan`; there is no planning mode here.

## Executable authority

`ledger --source actuation` is the only executable actuation gate. Do not invoke
or recreate a second actuation gate.

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure`. After readiness, invoke `ledger` directly; the CLI
owns command compatibility, integrity, and failures.

The live objects are:

1. `GC-v2`, the accepted source-bound GoalContract.
2. `actuation-open/v1`, its executable projection into authority, path scope,
   terminal route, and verifier-backed obligations.
3. `actuation-operation/v1`, one selected effect with an idempotency key, owner,
   exact paths, and cited obligations.
4. The append-only `actuation-event/v1` chain, whose fold yields
   `actuation-kernel-state/v1`.
5. `closure-decision/v1`, projected by the kernel from that live fold.

`actuation-review-policy/v2`, `review-resolution/v1`, RF-v2, EF-v1, CAS
receipts, and SHIP-v1 remain owner-specific evidence. Bind their current
identities into the GoalContract and discharge their predicates through exact
verifier commands; do not copy their policy logic into the kernel.

Read [live-semantics.yaml](references/live-semantics.yaml) for canonical
vocabulary and [closure.md](references/closure.md) for the terminal projection.
The executable laws live in the event fold and its direct counterexample tests.

## Recursion-scheme architecture

`/goal` owns fixed-point iteration. The kernel performs at most one state
transition per invocation:

~~~text
coalgebra: actuation-kernel-state -> next legal transition or terminal
handler:   admitted capability -> process effect or external-edit reconciliation
algebra:   prior state + actuation-event/v1 -> next state
driver:    /goal observes and repeats, stops, or blocks
~~~

The event fold is the catamorphism. `state` and `decide` are coalgebraic
observations. The workflow is hylomorphic only because `/goal` repeatedly
unfolds and folds; `ledger --source actuation` never owns that recursion or
claims parent completion from one operation.

## Source and authority

Open a material generation only from:

- a current accepted specification whose governance result is complete; or
- a direct user goal with explicit execution authority.

A plan supplies scope and policy but not mutation authority. Review evidence
supplies liabilities but not mutation authority. Preserve separate
`source_ref`, `execution_authority_ref`, and `mutation_allowed` fields.

Project every terminal GoalContract predicate into at least one obligation with
an exact verifier command. The kernel conserves exactly the accepted
`actuation-open/v1` obligation set; the source-to-open projection remains a
human/GoalContract responsibility and must be inspected before `open`.

~~~json
{
  "schema": "actuation-open/v1",
  "run_id": "goal-17:g0",
  "goal_id": "goal-17",
  "goal_contract_digest": "sha256:...",
  "resolution_digest": null,
  "source_ref": "user:turn-42",
  "execution_authority_ref": "user:turn-42",
  "mutation_allowed": true,
  "completion": "ready-to-ship",
  "allowed_paths": ["src/kernel.zig"],
  "obligations": [
    {
      "id": "tests",
      "kind": "implementation",
      "statement": "The accepted implementation proof lane passes.",
      "verifier": ["zig", "build", "test"]
    }
  ]
}
~~~

Use `completion: ready-to-ship` for a generation whose next owner is `$ship`.
Use `completion: complete` for explicit local implementation or the final
review generation. Supply the current `resolution_digest` for review-bound
work. These values are immutable after `open`.

## One-operation law

From the repository root:

1. Open the generation once:

   ~~~bash
   ledger open --source actuation --json ACTUATION_OPEN.json
   ~~~

   The store lock sidecar must already be Git-ignored. A repo-level
   `.ledger/` ignore covers the default store.

2. Inspect `ledger state --source actuation --run RUN_ID`. Select exactly the
   operation named by `next_transition`; `/goal`, not the CLI, decides whether
   to continue.
3. Build one `actuation-operation/v1` from the selected owner boundary:

   ~~~json
   {
     "schema": "actuation-operation/v1",
     "step_id": "step-1",
     "effect": "edit",
     "idempotency_key": "goal-17:g0:step-1",
     "owner_boundary": "actuation-kernel",
     "paths": ["src/kernel.zig"],
     "obligation_refs": ["tests"]
   }
   ~~~

4. Prepare before any executable effect:

   ~~~bash
   ledger prepare --source actuation \
     --run RUN_ID \
     --json ACTUATION_OPERATION.json
   ~~~

   Hold the returned `AKC1-*` capability only in the active executor. Capture
   the result without deliberately echoing or copying the raw value into a
   durable run, evidence, or handoff artifact. The ledger persists only its
   digest; transport confidentiality remains the caller/runtime boundary.
5. For `edit`, perform only the admitted path mutation, then consume and
   observe it:

   ~~~bash
   ledger record --source actuation --run RUN_ID --capability "$CAPABILITY"
   ledger observe --source actuation --run RUN_ID --step STEP_ID
   ~~~

   For `inspect` or `verify`, use one kernel-owned execution:

   ~~~bash
   ledger execute --source actuation --run RUN_ID --capability "$CAPABILITY"
   ~~~

6. Fold tests, diffs, logs, and returned event digests through
   `$evidence-fold`. A node may be done; it may not complete the parent goal.
7. Re-read kernel state. A failed observation consumes the capability but
   leaves its obligations outstanding; select a new step with a new
   idempotency key or block.

The kernel rejects post-hoc preparation, stale pre-state, capability replay,
duplicate step or idempotency identities, verifier substitution, path escape,
simultaneous out-of-scope mutation, unchanged declared edit paths, malformed or
reordered events, verifier-side repository mutation, and closure with
outstanding obligations.

## Review law

`$actuating` owns review selection, exact lens contract and instruction
digests, standard and auxiliary roles, invalidation, repeated-review
accounting, and closeout credit. Compile those decisions into
`actuation-review-policy/v2` before the first run; read
[review-policy.md](references/review-policy.md).

Require a chain ending in at least five consecutive, distinct standard clean
attempts and a clean standard attempt on the current tuple. Bind every
registered auxiliary lens and have `$goal-actuating` launch all auxiliary
requests concurrently with the first standard attempt. Auxiliary clean results
discharge only their own current request; auxiliary findings enter RF-v2; no
auxiliary attempt or tuple transition contributes to the standard clean suffix.
Preserve prior standard credit across a changed CAS tuple only through a
policy-bound `auxiliary-remediation` carry that cites the accepted finding,
resolution, correctness observations, actuation events, and SHIP receipt while
keeping each attempt bound to its original request and tuple. Any standard
finding, contract drift, base change, or unrelated mutation resets the chain.

Require Ledger 0.7.0 or newer before executing a v2 preflight. Ledger retains
v1 validation for historical same-tuple snapshots, but new campaigns never
downgrade to v1 to avoid the chain law.

Treat the policy as executable syntax owned by `$actuating`. Before CAS
execution, require a passing policy validation decision:

~~~bash
ledger validate actuation-review-policy \
  --phase preflight --input <policy.json>
~~~

Before closeout, run the same checker with `--phase closeout` against the
current snapshot. Bind both exact commands as GoalContract review obligations.
The checker enforces stable request, binding, attempt, and lane-accounting
laws; it does not decide whether a source trigger makes a lens applicable or
replace exhaustive CAS history acquisition.

Fresh or closure-grade review uses `$cas` only to execute the opaque request
and return tuple-bound attempt, verdict, failure, and finding facts. Project
only the policy request's `request_id` and `request_fingerprint` into CAS
`workflowBinding`. Join the returned binding and target tuple back to the
pre-bound policy request; never derive lens meaning from CAS output.

Review evidence passes through `$review-fold`, which classifies and quotients
findings, then through `ledger validate review-fold` as a pure invariant
check. `review-resolution/v1` then selects at most one current owner-boundary
repair. Read [review-resolution.md](references/review-resolution.md) before
review-driven mutation.

For every accepted RF-v2 equivalence class, invoke `$universalist` at the
classified owner boundary and compile one `correctness_refinement`. Bind the
class, discrepancy, law delta, smallest owner construction, preservation
witness, and strict progress witness. Before mutation, require a passing
correctness-refinement validation decision:

~~~bash
ledger validate review-resolution \
  --phase preflight --input <resolution.json>
~~~

The checker enforces the structural class-to-refinement join. It does not
validate the entire resolution, execute witness commands, select a strategy,
grant authority, or move review semantics into CAS. `$goal-actuating` must bind
the complete current resolution and observe both witness obligations.

For a review edit:

- refresh live review sources before selection;
- bind the complete review policy and every selected request into the
  GoalContract digest before CAS execution;
- pass the policy preflight, verify the exact instruction bytes, and
  project the exact CAS command into a review obligation;
- launch the first standard request and all auxiliary requests as one
  concurrent wave against the same artifact;
- after an auxiliary-driven repair, invalidate every current request and
  preserve the standard suffix only by appending a certified non-credit carry;
- bind the current resolution, publication epoch, and evidence identities into
  the GoalContract digest;
- pass the correctness-refinement preflight and project both preservation
  and progress witness commands into verifier-backed obligations;
- project the selected resolution node into the operation's owner, exact paths,
  and verifier-backed obligations;
- prepare the capability before mutation;
- preserve cumulative finding semantics across adjacent repairs and reships;
- require fresh closure-grade CAS evidence after the final published change;
- pass the policy and correctness-refinement closeout checks, with both
  witness obligations observed, before granting review credit.

The validation verdict grants no authority. Raw review prose, a fold receipt,
a CAS record, or a suggested patch never grants mutation. `$ship` remains the
only public-effect owner. The kernel may
execute a verifier that observes those owner artifacts, but it never publishes,
classifies review prose, or invents a repair strategy.

## Lifecycle

A material generation is immutable and closes once:

~~~text
ready -> prepared -> effect_recorded -> ready -> ... -> closed
          |                  |
          +---- execute -----+
~~~

For a bare invocation:

1. open generation `g0` with `completion: ready-to-ship`;
2. discharge implementation obligations, close, and run `decide`;
3. hand the kernel decision to `$ship`;
4. open generation `g1` under the same `goal_id`, with a new GoalContract digest
   that binds SHIP and review-closeout authority;
5. discharge review/closure obligations, close, and run `decide` with
   `completion: complete`.

An explicit implementation run uses `completion: complete` and never enters
the ship branch. A review repair that must be republished closes a
`ready-to-ship` generation; final post-publication review uses a fresh
`complete` generation. Generations are append-only siblings under one goal,
not mutable lifecycle labels.

## Closure

Read [closure.md](references/closure.md), then run:

~~~bash
ledger doctor --source actuation
ledger state --source actuation --run RUN_ID
ledger close --source actuation --run RUN_ID
ledger decide --source actuation --run RUN_ID
~~~

`close` is legal only from `ready` with no pending step, no outstanding
obligation, and an unchanged live artifact. `decide` recomputes the current
artifact digest and returns:

- `continue` plus `next-transition:*` before close;
- `ready-to-ship` after a closed ship-bound generation; or
- `complete` after a closed terminal generation.

Only the latter two set implementation outcome to complete. Only terminal
`complete` sets goal outcome to complete. The generated `closure-decision/v1`
binds the repository fingerprint, folded run digest, obligation discharge
basis, terminal route, and next owner.

Before handing off `ready-to-ship` or reporting terminal `complete`, invoke
`$learnings` and retain one learning disposition. The disposition is a required
execution checkpoint, not evidence that can satisfy an actuation obligation.
If a canonical append changes the Git artifact evaluated by `decide`, that
decision becomes stale: open and close a new generation whose allowed paths include
the learning store before handoff or completion. An ignored/local source-store
write that leaves the evaluated artifact unchanged does not invalidate the
decision.

Use the JSON verdict, not prose or exit-code folklore, as the workflow result.
Malformed input, invalid transitions, unavailable state, stale artifacts, and
failed observations exit nonzero with `actuation-error/v1` or a failed
transition result. Invalid CLI syntax uses the standard `ledger` usage failure.

## Obstruction boundary

A repo-local process cannot physically intercept Codex's in-app mutation
primitive. For `edit`, the kernel therefore proves causal admission before the
effect and independently reconciles exact path movement afterward. It is not an
OS sandbox and cannot prove that an unrecorded external effect never happened.
Loss of the raw capability blocks the prepared operation; the kernel does not
reconstruct it from deterministic state. The capability is a causal replay
guard, not a claim that process arguments or session transcripts are secret.

## Stop rules

Stop when authority is missing, the GoalContract projection is incomplete, the
live artifact is stale, the selected effect does not match `next_transition`, a
capability is unavailable, an obligation lacks an executable verifier, review
resolution is open, evidence regresses, closure-grade review is stale, or a
public effect would bypass `$ship`.

## Resources

- [live-semantics.yaml](references/live-semantics.yaml) — canonical worlds,
  transitions, ownership, and laws.
- [review-policy.md](references/review-policy.md) — lens selection, exact
  request binding, lane accounting, and invalidation.
- [review-resolution.md](references/review-resolution.md) — resolution schema,
  strategy rules, and semantic balance.
- [closure.md](references/closure.md) — kernel terminal projection and lifecycle
  handoff.
- [decision-contract.yaml](references/decision-contract.yaml) — trigger and
  routing contract for audit tooling.
