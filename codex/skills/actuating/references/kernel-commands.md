# Ledger Operational Projection

This is the current Ledger-owned internal projection of `artifact-kernel-v1`.
It does not add public `$actuating` modes or make these command names part of
ACT-AK's source-level architecture. Conforming adapters must preserve the same
transient-envelope, capability-before-effect, evidence, and derived-state laws.
For this Ledger adapter, always pass `--goal GOAL_ID`; without it, Ledger
selects frozen `legacy-actuating-v1` command semantics.

Before the first command, load `$ledger` and complete `$ledger ensure`. Use the
repository root and keep transient JSON envelopes outside reviewed subject
paths unless the Goal explicitly includes them.

## Current Ledger commands

Use `ledger --source actuation [--repo PATH] --goal GOAL_ID
COMMAND ...`. The routing table is the single command inventory.

The Evidence path is fixed at
`.ledger/actuation/artifact-kernel/evidence.jsonl`; artifact-kernel `--path` is
rejected. Frozen legacy commands without `--goal` retain their arbitrary
`--path` compatibility surface.

## Routing table

| Need | Route |
|---|---|
| Register Goal and K0 while Ledger injects its static Review Contract | `open --json FILE` |
| Register immutable successor Construction | `register-construction --json FILE` |
| Register a classified Counterexample Set | `register-counterexamples --json FILE` |
| Record review, publication, or closure-observation evidence | `append --json FILE` |
| Admit one construction-projected operation | `prepare --json FILE` |
| Consume an edit capability after exact delta reconciliation | `record --capability CAP` |
| Consume inspect/verify capability and run its verifier | `execute --capability CAP` |
| Run admitted verifier after a recorded edit | `observe --step STEP_ID` |
| Consume a pending operation without proof credit | `abort --step STEP_ID --capability CAP` |
| Fail-closed abort after capability-output loss, only if nothing changed | `abort --step STEP_ID` |
| Derive execution/review/closure state | `state` |
| Project the current closure receipt | `decide` |

## Open envelope

`open` is the only entry for a new goal. It validates and takes custody of the
Goal Contract and selected initial Construction. Ledger injects and custodies
its one built-in canonical static Review Contract; the caller supplies no Review
Contract path, bytes, digest, or materialization command.

Production is currently Phase 3, so new artifact-kernel goal admission is
build-disabled. Existing registered artifact-kernel goals remain replayable;
enable new `open` only after the Phase 4 historical-store inventory gate passes.

~~~json
{
  "schema": "actuation-open/v2",
  "protocol": "artifact-kernel-v1",
  "goal_id": "goal-1",
  "execution_authority_ref": "user:turn-42",
  "execution_authority_digest": "sha256:...",
  "mutation_allowed": true,
  "goal_contract_path": "goal-contract.json",
  "construction_contract_path": "construction-k0.json"
}
~~~

~~~bash
ledger --source actuation --goal goal-1 open --json actuation-open.json
~~~

The envelope authority fields must exactly match the Goal Contract. K0 must
belong to that Goal, use `mode: initial`, reference it, and have no Construction
predecessor. A source revision opens a fresh goal with a successor Goal Contract
and a fresh K0; do not reopen or reinterpret the predecessor goal.

## Registration envelopes

Register a successor Construction only after Counterexample classification or
when the current accepted source requires a new material construction:

~~~json
{
  "schema": "construction-registration/v1",
  "goal_id": "goal-1",
  "construction_contract_path": "construction-k1.json"
}
~~~

~~~bash
ledger --source actuation --goal goal-1 register-construction \
  --json construction-registration.json
~~~

Register each immutable classified set while no capability is pending:

~~~json
{
  "schema": "counterexample-registration/v1",
  "goal_id": "goal-1",
  "counterexample_set_path": "counterexamples-q1.json"
}
~~~

~~~bash
ledger --source actuation --goal goal-1 register-counterexamples \
  --json counterexample-registration.json
~~~

An accepted current class blocks further operation admission until a current
successor Construction covers it. A blocked class blocks closure.

## Operation envelope

Project one operation exactly from the current Construction:

~~~json
{
  "schema": "actuation-operation/v2",
  "goal_id": "goal-1",
  "construction_ref": "sha256:...",
  "step_id": "step-1",
  "effect": "edit",
  "idempotency_key": "goal-1:k0:step-1",
  "owner_boundary": "selected-owner",
  "paths": ["src/kernel.zig"],
  "proof_obligation_refs": ["proof-law-1"]
}
~~~

~~~bash
ledger --source actuation --goal goal-1 prepare --json operation.json
~~~

Ledger chooses the verifier from the cited Construction obligations and returns
raw `AKC3-*` capability material once. Persist only its digest. Do not prepare
after the effect or reuse a step, idempotency key, or capability.

For both `execute` and `observe`, Ledger validates the current subject and
pending operation under exclusive custody, then appends
`operation_observation_reserved` before starting the verifier. Its canonical
`operation-observation-reserved/v1` body binds the exact `step_id`, `effect`,
`idempotency_key`, `capability_digest`, and `subject_digest`. Replay moves to
`observation_reserved`, from which only the matching `operation_observed` or an
admitted abort is legal. A concurrent invocation therefore loses before it can
run the verifier; a timed-out or otherwise failed verifier receives no proof
credit and cannot be started again under the consumed reservation.

For `edit`:

~~~bash
# Apply only the admitted edit while the capability is live.
ledger --source actuation --goal goal-1 record --capability "$CAPABILITY"
ledger --source actuation --goal goal-1 observe --step step-1
~~~

For `inspect` or `verify`:

~~~bash
ledger --source actuation --goal goal-1 execute --capability "$CAPABILITY"
~~~

If execution must stop while the capability remains available, use
`abort --step step-1 --capability "$CAPABILITY"`. If `prepare` committed but
the capability output was lost, use `abort --step step-1`; recovery is legal
only when the subject, declared paths, and reconciled workspace are unchanged.
Neither route grants proof credit. After observation reservation, recovery is
not legal; use the capability-bound abort path to terminate the pending
operation without proof credit.

## Evidence append envelope

External evidence uses one transient wrapper:

~~~json
{
  "schema": "actuating-evidence-append/v1",
  "goal_id": "goal-1",
  "construction_ref": "sha256:...",
  "subject_digest": "sha256:...",
  "kind": "EVENT_KIND",
  "body": {}
}
~~~

~~~bash
ledger --source actuation --goal goal-1 append --json evidence.json
~~~

Externally appendable kinds are:

~~~text
review_campaign_started
review_request_bound
review_attempt_started
review_attempt_completed
review_transport_failed
publication_observed
closure_projection_observed
~~~

Use the current runtime schema for each exact event body. Each body carries the
campaign or publication binding plus the digest of the owner-validated receipt
or instruction it cites. CAS owns review-receipt validation; Ship owns
publication-receipt validation. Ledger checks only the narrow Actuating
projection needed by its fold and records the owner-issued reference. Do not
copy either owner's full schema into the Evidence event or invent a second
Actuating custody protocol.

Operation events and authoritative document registration events are
Ledger-authored consequences of their dedicated commands. Do not append them
directly.

## Review dispatch barrier

Append the current campaign start and all five request bindings before launching
the concurrent 1+4 wave. Append an attempt-start event immediately before each
dispatch and the exact terminal attempt or transport-failure receipt afterward.
Let all launched siblings terminate. Only after the barrier may one failed
request receive its single same-subject fresh recovery.

After any material subject change, append no old-subject credit. Start a fresh
campaign and bind a fresh full wave.

## Publication boundary

Call `$ship` with the current `ready-to-ship` closure receipt and the exact
transient compatibility projection:

~~~text
actuation_binding.actuation_run_id = closure_receipt.receipt_id
actuation_binding.state_fingerprint = closure_receipt.subject_digest
~~~

Actuating owns this projection. It creates no durable peer artifact and grants
no authority; Ship validates the pair against the supplied receipt and copies
it verbatim. After Ship returns a successful current `SHIP-v1`, append
`publication_observed` with its owner-issued receipt reference and the exact
closure receipt identity. Do not create or update a public PR through Ledger or
Actuating.

## Projection and replay

~~~bash
ledger --source actuation --goal goal-1 state
ledger --source actuation --goal goal-1 decide
~~~

Treat projections as disposable. Re-run them after any event for the goal or
any material subject movement. Do not write a mutable state artifact or
hand-author closure.
