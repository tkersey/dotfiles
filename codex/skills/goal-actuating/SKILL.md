---
name: goal-actuating
description: "Coordinate an accepted implementation goal or explicit review workflow through actuation-kernel generations. Select one bounded operation, delegate execution to $goal-grind, fold evidence, consume review-resolution/v1, acquire CAS review evidence when required, and request a kernel-derived closure-decision/v1 without owning publication."
---

# Goal Actuating

## Mission

Be the sole coordinator around the one-transition actuation kernel.

~~~text
accepted source + GoalContract
-> actuation-open/v1
-> ledger --source actuation
-> one selected operation
-> $goal-grind
-> $evidence-fold
-> next_transition
-> close + closure-decision/v1
~~~

This skill coordinates. It does not redefine accepted semantics, execute a
second validator, duplicate the selected-operation executor, claim node success
as goal completion, or publish.

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure`. After readiness, invoke `ledger` directly; do not
proxy individual kernel transitions through a skill helper.

## Modes

~~~yaml
goal_actuating_mode:
  mode: implement | triage | remediation-plan | review-closeout
  execution: none | direct | iterative
  review: none | existing-source | cas-fresh | cas-closeout
  closure: no-code-output | local-completion | ship-handoff | blocked
~~~

Unqualified review means `triage`. Only explicit fix, address, resolve,
implement, or closeout intent selects `review-closeout`.

Bare `$actuating` and `/goal $actuating` use an implementation generation with
`completion: ready-to-ship`, then `$ship`, then a review generation with
`completion: complete`. `$actuating implement` uses one `complete` generation
and stops before publication.

## Generation ownership

Project the accepted GoalContract into `actuation-open/v1` with:

- one generation-specific `run_id` and stable parent `goal_id`;
- current source and execution authority references;
- exact allowed repository paths;
- immutable `mutation_allowed` and `completion` values;
- every terminal predicate represented by an obligation with an exact verifier
  and `implementation`, `review`, `ship`, or `acceptance` proof kind.

Inspect the projection before opening it. `ledger --source actuation` conserves
the supplied obligation set but cannot infer an omitted user predicate.

## Coordination loop

1. If source authority or artifact state is stale, block.
2. Use `$goal-workgraph` only when decomposition changes execution. Advice never
   grants mutation.
3. Open the generation once with `ledger open --source actuation`.
4. Read `ledger state --source actuation --run RUN_ID`.
5. If `next_transition=prepare`, select exactly one ready owner node and create
   one `actuation-operation/v1` with a fresh idempotency key, exact paths, and
   outstanding obligation references.
6. Run `ledger prepare --source actuation`; keep the returned raw capability
   only in the active executor.
7. Invoke `$goal-grind` once. It must consume the capability through `record`
   plus `observe`, or through `execute`.
8. Fold event digests, tests, diffs, logs, and current artifact state through
   `$evidence-fold`.
9. Read kernel state again and follow only its projected `next_transition`.
10. When the projection is `close`, close the generation and run
    `ledger decide --source actuation --run RUN_ID`.

`/goal` owns repetition and the stop decision. The CLI performs at most one
transition per invocation, and `$goal-grind` performs exactly one selected
operation.

## Review handoff

For review work, preserve this ownership order:

~~~text
actuation-review-policy/v2
-> pre-bound exact lens request, contract digest, and instruction digest
-> passing policy preflight decision
-> GoalContract digest and review verifier obligations
-> prepared review operation
-> exact CAS command
-> live review source
-> $review-fold
-> review-resolution/v1
-> cumulative stable boundary-law components
-> owner-boundary-synthesis/v1 for each component
-> correctness_refinement for each accepted RF-v2 class
-> passing refinement-and-synthesis preflight decision
-> updated GoalContract and verifier obligations for any selected repair
-> prepared repair operation
-> action evidence
-> current closure-grade review
-> passing policy and refinement-and-synthesis closeout decisions
~~~

For every fresh or closure-grade CAS review, and for same-handle timeout
recovery, pass `--timeout-ms 2700000` explicitly for the 45-minute real-review
wait budget:

First require `cas_rer_opaque_request_binding_v1=true`,
`cas_review_history_v2=true`, and
`cas_review_scoped_instructions_v1=true` from `cas capabilities` for
closure-grade work. Require Ledger 0.7.0 or newer before validating a v2 policy.
Require Ledger 0.9.0 or newer before admitting an owner-synthesized review
repair.

~~~bash
cas review run --cwd <repo> --base <base-ref> \
  --custom-instructions @<instructions-ref> \
  --workflow-binding-json @binding.json \
  --timeout-ms 2700000 --json --fallback none
cas review list --cwd <repo> --base <base-ref> \
  --custom-instructions @<instructions-ref> \
  --workflow-binding-json @binding.json \
  --codex-thread-id <id> --json
cas review_session wait --cwd <repo> --review-thread-id <reviewThreadId> \
  --timeout-ms 2700000 --json
~~~

The binding contains only the policy request's opaque `requestId` and
`requestFingerprint`. `$goal-actuating` verifies the pinned contract manifest,
its resource digests, and the exact instruction bytes; binds the complete
policy artifact into the GoalContract digest; and joins the returned binding
and tuple to that pre-bound request. CAS output never selects or labels a lens.

Before the first CAS command, execute the exact preflight obligation:

~~~bash
ledger validate actuation-review-policy \
  --phase preflight --input <policy.json>
~~~

Interpret the passing policy as one concurrent initial wave: dispatch the
first standard request and every auxiliary request in parallel against the
same tuple. Never cancel, interrupt, terminate, or stop a sibling request
because another lens returned clean, findings, or a transport failure. Keep the
preflight-bound resolution digest unchanged and collect terminal transport
evidence from every launched dispatch before retrying a failed request. Keep the
resolution barrier closed until every policy request has a valid terminal
`clean` or `findings` fact and every finding has entered RF-v2. Only then build
a new resolution or prepare review-driven mutation.

Start an independent artifact monitor before dispatch when the Actuation
verifier or executor may buffer stdout. For each request, wait until its complete
receipt JSON and recorded process exit status (`rc`) both exist, then report that
review immediately and exactly once. Read semantic status and findings only from
`.reviewVerdict`; treat `rc` as command or transport status.
Do not wait for sibling requests or the aggregate executor to return before
reporting a completed review. This reporting observation neither changes
request state nor opens the initial dispatch, failed-request recovery, RF-v2,
adjudication, or mutation barriers. Apply the same reporting rule to
request-local recovery and later serial standard attempts.

Apply this request-local transition table exactly:

| CAS fact | Request transition | Standard projection | Next action |
| --- | --- | --- | --- |
| valid `clean` | that request becomes `clean` | append only when the request is standard | keep siblings running |
| valid `findings` | that request becomes `findings-folded` after RF-v2 | reset only when the request is standard | keep siblings running |
| terminal `review_failed` with no structured tuple verdict | only that request becomes `rerun-required`; retain the fact only in exhaustive CAS history | unchanged; the failed dispatch earns no credit | keep siblings running, then rerun only that request on the unchanged tuple with `--fresh-attempt <source-bound-reason>` after the initial dispatch barrier |
| timeout with a live attempt | request state remains pending | unchanged | recover the same handle |
| named artifact, contract, registry, base, resolution, or publication invalidation | all current requests become stale | carry or reset under the existing v2 law | launch one new full concurrent wave |

A verdictless failure terminates one dispatch handle, not the policy request.
Do not describe the whole wave as zero-credit, decrement or clear prior standard
credit, redispatch valid siblings on the same tuple, or serialize a replacement
campaign. Capacity pressure changes neither the concurrency law nor request
accounting. If the exact-request recovery dispatch also terminates without a
structured verdict, leave the request `rerun-required` and block rather than
retrying indefinitely or restarting the campaign.

After the resolution barrier and any required adjudication, continue the
standard lane with fresh, ordered attempts until it has at least five
consecutive clean results. Do not serialize auxiliary lanes behind the standard
streak. Auxiliary attempt identities never enter `standard_clean_attempt_ids`.

For an initial v2 preflight, require an empty `standard_clean_chain`. After an
auxiliary-only repair and SHIP update, allow the next preflight to retain the
prior ordered standard history and clean projection only when it appends one
`auxiliary-remediation` carry from the last clean standard attempt to the new
artifact. Bind the prior auxiliary request IDs and folds, current resolution
digest, correctness decisions, observed preservation and progress obligations,
actuation event refs, and SHIP-v1 receipt. Keep every new current request
`selected-pending`. The carry is a transition, not a review attempt, and never
increments the clean count.

After exhaustive current CAS history has been joined into the policy snapshot,
execute the same checker with `--phase closeout`. The validation decision checks the
stable policy algebra; `$goal-actuating` still proves that the concurrent wave
was dispatched from the pre-bound requests and that the supplied history is
exhaustive across every standard request epoch retained in the chain. Append
current standard terminal facts in their actual order, including findings;
require the current request attempts to equal the chain's current-tuple rows,
and require the chain to end with a clean standard attempt on the current tuple.

After `$review-fold`, join every current accepted class to the current goal's
retained resolution and synthesis history. Form structural components from
stable source and target worlds, carriers, operations, observations, and
governing laws. Implementation-specific owner names are component members, not
component identity. A generation, tuple, commit, publication, source batch, or
attempt suffix is provenance, never a new structural identity.

Invoke `$universalist` once per cumulative component and materialize one
`owner-boundary-synthesis/v1` before selecting repair strategy. The synthesis
must record recurrence after repair, multiple owners for one law, proposed
semantic machinery, displacement of multiple abstractions, and symptom repairs
after a replacement kernel. `reuse-owner` requires no such pressure;
`converge-kernel` owns the replacement construction and structural obligations;
`separate-laws` requires a concrete obstruction and routes back to component
splitting plus any necessary RF-v2 owner or law correction without mutation;
insufficient evidence blocks.

Then require each accepted equivalence class to have exactly one
`correctness_refinement` bound to that synthesis. A class-local construction
cannot independently select a repair. Before preparing a repair, execute:

~~~bash
ledger validate review-resolution \
  --phase preflight --input <resolution.json>
~~~

Project the refinement's preservation and progress verifier commands into the
updated GoalContract as `correctness:<decision_id>:preservation` and
`correctness:<decision_id>:progress`, with statements and argv copied exactly.
Project each synthesis install, collapse, delegation, and retirement verifier
as `synthesis:<synthesis_id>:<obligation-index>`. Bind the passing RF-v2
validation decision, synthesis identities, and full resolution digest into that
contract. At closeout, rerun the same checker with `--phase closeout` against
the cumulative resolution and require passing kernel observations for every
correctness and synthesis obligation on the current artifact and GoalContract
digest. The checker validates the refinement-and-synthesis sub-contract,
including component identity, strategy binding, selected-node ownership, and
declared closeout observations. It does not validate the full resolution,
dereference history or observation receipts, or execute witness commands.
Neither decision grants authority; the prepared actuation operation remains
the only mutation gate.

Do not admit a smaller review wait budget unless the user explicitly overrides
it. Project the exact command into the review obligation so older installed CAS
binaries cannot silently restore a shorter default. A timeout preserves the
same review attempt; recover its handle instead of starting a duplicate tuple.

The current resolution may select at most one synthesis-owned node, and a
repair-bearing mutation preflight must select exactly one. Project its
synthesis ID, node ID, canonical owner, paths, and proof requirements into the
operation and obligations. `$goal-grind` receives that selection but never
reinterprets its synthesis disposition or repair strategy.

Refresh sources and open a new generation after any repair or publication
change; a finding by itself does not create that transition, and a closed
generation is never relabeled. Relaunch the first standard attempt and every
auxiliary request concurrently for the new artifact. Reset the chain unless
the entire change is the certified auxiliary remediation represented by the
carry; standard findings, contract or registry drift, base movement, and
unrelated edits always reset it.

For publication-bearing closeout, bind the accepted SHIP-v1, resolution digest,
publication tuple, actuation review policy, and selected request identities into
the next GoalContract. `$ship` alone updates the retained PR. A final published
change always invalidates earlier current-request and auxiliary evidence. It
preserves earlier standard convergence credit only through the v2 carry while
leaving every retained attempt bound to its original request and tuple.

## Lifecycle handoff

A closed `ready-to-ship` generation yields:

~~~text
goal_outcome: continue
implementation_outcome: complete
next_owner: ship
~~~

Pass that decision to `$ship`. After a successful SHIP-v1, open a new review
generation under the same `goal_id`; do not mutate the closed implementation
generation.

A closed `complete` generation yields terminal goal completion. Only then may
`$proof-patch` render the human proof.

## Stop rules

Stop when the GoalContract projection is incomplete, an obligation has no
executable verifier, authority is stale, the live artifact diverges from the
fold, the next transition cannot be performed, the raw capability is lost, a
review resolution remains open, evidence regresses, or a public effect would
bypass `$ship`. Report the kernel error or projected transition without
reinterpreting it locally.
