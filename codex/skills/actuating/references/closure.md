# Closure

`closure-decision/v1` is a live projection of one folded actuation kernel
generation. It never accepts caller-authored success flags or a previously
issued completion decision.

## Authority source

The only executable closure path is:

~~~bash
ledger doctor --source actuation
ledger state --source actuation --run RUN_ID
ledger close --source actuation --run RUN_ID
ledger decide --source actuation --run RUN_ID
~~~

The append-only `.ledger/actuation/events.jsonl` chain is authoritative.
YAML/prose summaries, saved command output, and hand-authored receipts are not.

## Fold conditions

`doctor` validates:

- `actuation-event/v1` schema;
- global monotonic sequence;
- predecessor digest continuity;
- body and event digests;
- legal per-run state transitions;
- unique run, step, obligation, and idempotency identities;
- exact verifier inheritance from cited obligations;
- single capability consumption;
- terminal obligation conservation.

`close` additionally observes the current Git repository. It succeeds only
when:

~~~text
phase == ready
pending_step == null
outstanding_obligations == []
live_artifact_digest == folded_artifact_digest
~~~

An invalid chain, stale artifact, open operation, failed verifier, or uncovered
obligation blocks closure.

## Decision projection

Before close, `decide` returns `continue` and names the fold's
`next_transition`. After close, it returns the immutable completion route bound
at `open`: `ready-to-ship` or `complete`.

~~~json
{
  "closure_decision": {
    "version": "closure-decision/v1",
    "decision_id": "sha256:...",
    "run_id": "goal-17:g0",
    "evaluated_artifact": {
      "repo": "/absolute/repo",
      "state_fingerprint": "sha256:..."
    },
    "run_digest": "sha256:...",
    "resolution_digest": null,
    "verdict": "continue | ready-to-ship | complete",
    "outcomes": {
      "goal_outcome": "continue | complete",
      "implementation_outcome": "incomplete | complete",
      "next_owner": "goal-actuating | ship | none"
    },
    "evidence_basis": [
      {"obligation_id": "tests", "step_id": "step-1"}
    ],
    "review_basis": [],
    "ship_basis": [],
    "implementation_checkpoint": null,
    "reasons": ["next-transition:prepare"]
  }
}
~~~

The decision digest covers the folded run state, verdict, outcomes, next owner,
and next transition. The run digest covers authority, source, terminal route,
repository, artifact, paths, obligations, verifier commands, discharge
bindings, step identities, idempotency identities, and any pending operation.
Each obligation is classified as `implementation`, `review`, `ship`, or
`acceptance`; `decide` routes its discharge binding into `evidence_basis`,
`review_basis`, or `ship_basis` without accepting caller-authored basis lists.

## Learning disposition after decision

Before a `ready-to-ship` handoff or terminal `complete` report, invoke
`$learnings` and retain exactly one disposition: `appended`, `duplicate-skip`,
`no-op`, or `blocked`. This checkpoint does not satisfy a kernel obligation and
does not alter the meaning of `closure-decision/v1`.

Recompute artifact currency after an append. If the canonical learning write
changes the Git artifact named by the decision, the decision becomes stale; open a
new generation with the learning path admitted and obtain a new terminal
decision. If the source store is ignored/local and the evaluated artifact is
unchanged, preserve the existing decision. A blocked learning disposition must
be reported as a source-memory closeout blocker even when the actuation fold is
otherwise terminal.

## Goal and implementation outcomes

Keep these separate:

| Fold | Verdict | Goal | Implementation | Next owner |
|---|---|---|---|---|
| Open generation | `continue` | `continue` | `incomplete` | `goal-actuating` |
| Closed `ready-to-ship` generation | `ready-to-ship` | `continue` | `complete` | `ship` |
| Closed `complete` generation | `complete` | `complete` | `complete` | `none` |

One completed operation never completes the parent goal. Only a closed terminal
generation can project `goal_outcome: complete`.

## Bare lifecycle

The ordered bare pipeline uses distinct immutable generations under one
`goal_id`:

~~~text
g0 implementation, completion=ready-to-ship
  -> close
  -> kernel decision ready-to-ship
  -> $ship
g1 review-closeout, completion=complete
  -> closure-grade review obligations
  -> close
  -> kernel decision complete
~~~

The second generation's GoalContract digest must bind the accepted SHIP-v1 and
current review source/resolution identities. It cannot relabel or reopen `g0`.
A review repair that changes the published artifact uses another
`ready-to-ship` generation; its final post-publication proof uses a new
`complete` generation.

## Review and publication evidence

`$actuating` owns review policy and resolution, `$cas` owns review transport,
and `$ship` owns publication. The kernel does not reproduce those owner
contracts. Instead, the accepted GoalContract projects every required current
proof into verifier-backed obligations before the generation opens.

Publication-bound closure must therefore include obligations for the current
SHIP binding, actuation review policy, current resolution, exact changed
artifact, fresh CAS evidence, and any repository-specific review-thread sweep.
If a required proof has no executable verifier, the generation is not
openable.

After any published head change, prior tuple-bound review observations are
stale; open a new generation with new obligation identities and current
verifiers. `$ship` remains the only public-effect owner.

## Failure behavior

- A valid `continue`, `ready-to-ship`, or `complete` decision exits zero.
- A failed executed verifier emits a transition result with `passed: false` and
  exits two.
- Malformed input, invalid state, stale artifact, replay, and unavailable
  dependencies emit `actuation-error/v1` and exit two.
- Invalid command syntax uses the standard `ledger` usage failure.
- `proof-patch` may render only a current `complete` decision whose repository
  fingerprint still matches.
