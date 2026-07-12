---
name: goal-actuating
description: "Coordinate an accepted implementation goal or explicit review workflow through Zig actuation-kernel generations. Select one bounded operation, delegate execution to $goal-grind, fold evidence, consume review-resolution/v1, acquire CAS review evidence when required, and request a Zig closure-decision/v1 without owning publication."
---

# Goal Actuating

## Mission

Be the sole coordinator around the one-transition Zig kernel.

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
actuation-review-policy/v1
-> pre-bound exact lens request, contract digest, and instruction digest
-> passing Actuating Zig preflight decision
-> GoalContract digest and review verifier obligations
-> prepared Zig review operation
-> exact CAS command
-> live review source
-> $review-fold
-> review-resolution/v1
-> correctness_refinement for each accepted RF-v2 class
-> passing Actuating Zig correctness-refinement preflight decision
-> updated GoalContract and verifier obligations for any selected repair
-> prepared Zig repair operation
-> action evidence
-> current closure-grade review
-> passing Actuating Zig policy and correctness-refinement closeout decisions
~~~

For every fresh or closure-grade CAS review, and for same-handle timeout
recovery, pass `--timeout-ms 1800000` explicitly:

First require `cas_rer_opaque_request_binding_v1=true`,
`cas_review_history_v2=true`, and
`cas_review_scoped_instructions_v1=true` from `cas capabilities` for
closure-grade work.

~~~bash
cas review run --cwd <repo> --base <base-ref> \
  --custom-instructions @<instructions-ref> \
  --workflow-binding-json @binding.json \
  --timeout-ms 1800000 --json --fallback none
cas review list --cwd <repo> --base <base-ref> \
  --custom-instructions @<instructions-ref> \
  --workflow-binding-json @binding.json \
  --codex-thread-id <id> --json
cas review_session wait --cwd <repo> --review-thread-id <reviewThreadId> \
  --timeout-ms 1800000 --json
~~~

The binding contains only the policy request's opaque `requestId` and
`requestFingerprint`. `$goal-actuating` verifies the pinned contract manifest,
its resource digests, and the exact instruction bytes; binds the complete
policy artifact into the GoalContract digest; and joins the returned binding
and tuple to that pre-bound request. CAS output never selects or labels a lens.

Before the first CAS command, execute the exact preflight obligation:

~~~bash
zig run codex/skills/actuating/scripts/review_policy.zig -- \
  --phase preflight --input <policy.json>
~~~

Interpret the passing policy as one concurrent initial wave: dispatch the
first standard request and every auxiliary request in parallel against the
same tuple. Then continue the standard lane with fresh, ordered attempts until
it has at least five consecutive clean results. Do not serialize auxiliary
lanes behind the standard streak. Auxiliary results may introduce findings or
discharge their own request, but their attempt identities never enter
`standard_clean_attempt_ids`.

After exhaustive current CAS history has been joined into the policy snapshot,
execute the same checker with `--phase closeout`. The Zig decision checks the
stable policy algebra; `$goal-actuating` still proves that the concurrent wave
was dispatched from the pre-bound requests and that the supplied history is
exhaustive.

After `$review-fold`, require each accepted equivalence class to have exactly
one `correctness_refinement` at the classified owner boundary. Before preparing
a repair, execute:

~~~bash
zig run codex/skills/actuating/scripts/review_resolution.zig -- \
  --phase preflight --input <resolution.json>
~~~

Project the refinement's preservation and progress verifier commands into the
updated GoalContract as `correctness:<decision_id>:preservation` and
`correctness:<decision_id>:progress`, with statements and argv copied exactly.
Bind the passing RF-v2 validation decision and full resolution digest into that
contract. At closeout, rerun the same checker with `--phase closeout` against
the cumulative resolution and require passing kernel observations for both
named obligations on the current artifact and GoalContract digest. The checker
validates the refinement sub-contract, not the full resolution or witness
execution. Neither decision grants authority; the prepared actuation operation
remains the only mutation gate.

Do not admit a smaller review wait budget unless the user explicitly overrides
it. Project the exact command into the review obligation so older installed CAS
binaries cannot silently restore a shorter default. A timeout preserves the
same review attempt; recover its handle instead of starting a duplicate tuple.

The current resolution may select at most one owner node. Project that node's
ID, owner, paths, and proof requirements into the operation and obligations.
Refresh sources and open a new generation after any repair or publication
change; do not relabel a closed generation. Relaunch the first standard attempt
and every auxiliary request concurrently for the new artifact.

For publication-bearing closeout, bind the accepted SHIP-v1, resolution digest,
publication tuple, actuation review policy, and selected request identities into
the next GoalContract. `$ship` alone updates the retained PR. A final published
change invalidates earlier request and tuple bindings.

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
bypass `$ship`. Report the Zig error or projected transition without
reinterpreting it locally.
