---
name: actuating
description: "Execute accepted implementation and review work through Actuating Artifact Kernel v1. Use bare $actuating for implementation, Ship publication, and review convergence; use explicit implement, triage, remediation-plan, or review-closeout for their bounded routes. Bind artifact-kernel-v1 goals to Goal Contract v3, Counterexample Sets, Construction Contracts, and the Evidence Ledger; keep legacy-actuating-v1 goals on frozen legacy semantics and never mix protocols."
---

# Actuating

Turn accepted intent into a lawful construction, capability-admitted effects,
independent falsification evidence, and derived closure.

## Authority kernel

Use exactly four authoritative per-goal artifact families:

1. `goal-contract/v3` — accepted truth and authority, compiled by
   `$goal-contract`.
2. `counterexample-set/v1` — classified witnessed falsifications, authored by
   `$review-fold`.
3. `construction-contract/v1` — the one selected architecture and proof plan,
   authored by `$actuating` using `$universalist`.
4. `actuating-evidence-event/v1` — domain-owned observations in Ledger's
   append-only envelope.

The Goal Contract is the sole semantic-authority artifact, the Counterexample
Set is the sole classified-bug artifact, the Construction Contract is the sole
architecture-selection artifact, and the Evidence Ledger is the sole mutable
per-goal truth. Read [artifact-kernel.md](references/artifact-kernel.md) for the
owner map and its exact downstream contracts.

For an artifact-kernel goal, Ledger's Construction-bound handlers admit and
execute projected operations; they never select architecture. `$ship` alone
owns public effects. Plans, reviews, validators, and Construction Contracts do
not independently grant mutation.

## Protocol boundary

Bind each goal immutably to `artifact-kernel-v1` or `legacy-actuating-v1` in the
canonical Evidence Ledger. Production remains at migration Phase 3: replay
existing registered artifact-kernel goals, but keep new artifact-kernel goal
admission build-disabled. Phase 4 remains blocked until an
operator-authoritative inventory covers every historical custom legacy store.

Never mix protocols, writers, artifacts, review credit, or closure rules in one
goal. Use the repository-local Ledger admission boundary described in
[artifact-kernel.md](references/artifact-kernel.md); never hand-write its
binding or infer a protocol from nearby documents.

For a Ledger-admitted legacy goal, use only the frozen
[legacy-actuating-v1 owner workflow](references/legacy-actuating-v1.md). It
owns the legacy coordinator, executor, policy, resolution, semantics, decision,
and closure references. Those surfaces remain readable through their stated
compatibility window and are never artifact-kernel inputs or authority.

## Public modes

| Intent | Route | Mutation | Terminal result |
|---|---|---:|---|
| Bare `$actuating` or `/goal $actuating` | implement -> Ship -> review-closeout | Authority-bound | Derived `complete` |
| `$actuating implement` | implementation only | Authority-bound | Local derived `complete` |
| `$actuating triage` | acquire and classify review | Forbidden | Counterexample Set and report |
| `$actuating remediation-plan` | propose successor construction | Forbidden | Non-executable Construction Contract |
| `$actuating review-closeout` | repair, ablate, Ship when required, re-review | Resolution-bound | Derived `complete` |

An unqualified request to review, inspect, audit, or classify selects `triage`.
Require explicit implement, fix, resolve, address, or closeout intent before
mutation.

Bare mode preserves this lifecycle:

~~~text
Goal Contract -> Construction -> capability-bound realization -> ready-to-ship
-> Ship -> concurrent 1+4 review -> Counterexamples/successor Construction
-> fresh convergence -> five consecutive standard cleans -> complete
~~~

`implement` stops before Ship and review. `triage` never mutates.
`remediation-plan` proposes but cannot execute a successor Construction.
`review-closeout` realizes accepted Counterexamples, retires residue, publishes
when required, and obtains fresh review convergence.

## Owner-directed procedure

1. Compile source semantics, scope, compatibility, laws, and accepted authority
   with [$goal-contract](../goal-contract/SKILL.md). Do not select architecture
   there.
2. Select `K0`, or a review-derived immutable successor, under
   [construction-contract.md](references/construction-contract.md). No finding
   authorizes a patch directly.
3. Before the first native Ledger command, load `$ledger` and complete
   `$ledger ensure`. Follow the exact transient envelopes and one-operation
   capability sequence in [kernel-commands.md](references/kernel-commands.md).
4. Follow the one static [Review Contract](references/review-contract.md).
   Route every finding through [$review-fold](../review-fold/SKILL.md) before
   any successor Construction or mutation.
5. Replay and derive state or closure under
   [closure.md](references/closure.md). Never persist peer campaign, streak,
   kernel-state, or closure truth.

The executor may perform only the Construction-projected effect on admitted
paths and report observations. It may not choose a repair, broaden scope,
change proof strategy, publish, or claim parent completion. Any material
review-subject change invalidates all review credit; no carry crosses subjects.

## Publication

Only [$ship](../ship/SKILL.md) may create, update, promote, or otherwise mutate
a public PR or tracker. For `artifact-kernel-v1`, Actuating projects a current
`ready-to-ship` closure receipt into SHIP-v1's exact opaque compatibility pair:

~~~text
actuation_binding.actuation_run_id = closure_receipt.receipt_id
actuation_binding.state_fingerprint = closure_receipt.subject_digest
~~~

Ship validates and copies the pair verbatim; it does not derive or revise the
values. The pair is transient external-evidence binding, not a fifth artifact
family or mutation authority. Actuating records the returned current `SHIP-v1`
receipt as publication evidence.

## Closure and learning

Use only `continue`, `ready-to-ship`, `complete`, or `blocked` from the current
deterministic closure projection. `$proof-patch` may render a current terminal
receipt but never grants closure.

Complete delivery closure and handoff before the `$ledger` source-memory
checkpoint. Optional learning or admission failure does not roll back code
closure; a later tracked subject change re-enters the ordinary proof and review
lifecycle.

## Fail closed

Block on stale or missing source authority, protocol mixing, stale Goal,
Construction, subject, or review identity, unresolved accepted or blocked
Counterexamples, capability replay or substitution, scope escape, incomplete
proof or retirement, unresolved review recovery, insufficient current-subject
clean attempts, invalid or substituted publication evidence, a public effect
outside Ship, or learning made delivery-critical. Missing or no-longer-current
Ship evidence after complete publication-required proof projects
`ready-to-ship`; it is not itself a blocker.
