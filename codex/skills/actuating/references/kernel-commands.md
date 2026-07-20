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

Probe `ledger materialize --help`, `ledger validate --help`, and `ledger
--source actuation --goal GOAL_ID --help` before an Artifact Kernel workflow.
If any current surface is absent, block; never route an artifact-kernel goal
through an older partial CLI or frozen legacy command.

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
| Dispatch one fully bound initial concurrent review wave | `dispatch-review` |
| Admit one construction-projected operation | `prepare --json FILE` |
| Consume an edit capability after exact delta reconciliation | `record --capability CAP` |
| Consume inspect/verify capability and run its verifier | `execute --capability CAP` |
| Run admitted verifier after a recorded edit | `observe --step STEP_ID` |
| Consume a pending operation without proof credit | `abort --step STEP_ID --capability CAP` |
| Fail-closed abort after capability-output loss, only if nothing changed | `abort --step STEP_ID` |
| Derive execution/review/closure state | `state` |
| Project the current closure receipt | `decide` |

## Open envelope

`open` is the only entry for a new goal or source-revised successor goal. It
validates and takes custody of the Goal Contract and selected initial
Construction. Ledger injects and custodies its one built-in canonical static
Review Contract; the caller supplies no Review Contract path, bytes, digest, or
materialization command.

Production is Phase 4 opt-in: an explicit `--goal GOAL_ID open` admits a new
artifact-kernel goal, while the unqualified command surface remains frozen
legacy behavior. Historical-store inventory remains a prerequisite for
retiring legacy writers, not for this explicit opt-in route.

This Ledger adapter currently admits a new Artifact Kernel goal only on macOS,
where its verifier handler can enforce read-only repository and no-network
containment. On another host, `open` returns `VerifierSandboxUnavailable`
before repository discovery, attachment custody, or Evidence creation. Pure
materialization and validation, other Ledger sources, frozen readers, and
read-only state/closure replay remain available. Broaden this context-relative
domain only after an equivalent verifier handler passes adversarial proof.

For a new goal, `protocol` repeats the accepted transient route selector; it is
not a pre-registration marker or authority. Under the Evidence lock, `open`
rejects conflicting history and validates the complete envelope, Goal, K0,
subject, and authority before the first `goal_contract_registered` append. A
retry may complete a missing Construction registration but cannot substitute
either immutable document.

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
predecessor. A source revision opens a fresh Goal with exactly one Goal
predecessor and a fresh K0 through the current supersession route below; do not
reopen or reinterpret the predecessor Goal.

Goal `allowed_paths` and `prohibited_paths`, plus Construction
`execution.allowed_paths`, are duplicate-free canonical literal path sets.
`.` is the only dot-component form; every other path is relative, has no empty,
`.` or `..` component, and has no trailing slash or backslash. The `.git` root
and `.ledger/actuation/artifact-kernel` control root, including slash
descendants, are reserved under ASCII case-folding; prefix-like siblings remain
valid. A broader scope, including `.`, cannot re-admit either root. Current
operations use the same predicate. `prepare` rejects an exact operation target
under either reserved root before capability issuance and leaves Evidence
unchanged. Frozen v1/v2 Evidence retains its historical path grammar for read
compatibility.

## Registration envelopes

Register a successor Construction only after an accepted Counterexample has
falsified the current Construction. A changed accepted source opens a fresh
goal instead:

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

An accepted current class blocks further edit admission until a current
successor Construction covers it. Inspect and verify operations may continue to
establish the evidence needed for that successor. A blocked class blocks
closure.

Likewise, a Goal-owned High/Critical example-proof risk authorization whose law
lacks both a direct strong current proof and a matching current Construction
exception derives `example-proof-risk-authority-pending`. It blocks edit
admission and closure while leaving inspect and verify available; the state
frontier directs Counterexample registration until an accepted class exists,
then directs successor Construction registration. No caller writes this debt.

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

For an implementation or acceptance obligation, cite its base `obligation_id`
to select the verifier or `<obligation_id>#falsifier` to select the falsifier.
Ledger binds the exact argv for that role and rejects substitution. One
operation cannot cite both roles for the same obligation; independent passing
operations on the current subject are required to discharge both. Review and
Ship obligations are external-owner projections and cannot be executed through
this handler. Ledger returns raw `AKC3-*` capability material once. Persist only
its digest. Do not prepare after the effect or reuse a step, idempotency key, or
capability.

For both `execute` and `observe`, Ledger validates the current subject and
pending operation under exclusive custody, then appends
`operation_observation_reserved` before starting the verifier. Its canonical
`operation-observation-reserved/v1` body binds the exact `step_id`, `effect`,
`idempotency_key`, `capability_digest`, `subject_digest`, and selected
`verifier`. Replay moves to `observation_reserved`, from which only the matching
`operation_observed` or an admitted abort is legal. A concurrent invocation
therefore loses before it can run the verifier; a timed-out verifier receives
no proof credit and cannot be started again under the consumed reservation.

For `edit`:

~~~bash
# Apply only the admitted edit while the capability is live.
ledger --source actuation --goal goal-1 record --capability "$CAPABILITY"
ledger --source actuation --goal goal-1 observe --step step-1
~~~

Current v3 edit operations name exact leaf files. `prepare` rejects `.` and
existing directories; after the effect, every changed path must exactly equal
one declared operation path. Goal and Construction scopes may remain broader,
but they do not turn a directory into recursive edit authority. Frozen v1/v2
records retain their read-only descendant-coverage semantics.

Before `record` appends or consumes the capability, Ledger re-reads the
post-effect manifest. It rejects any changed path that is itself a symlink or
descends from a manifest symlink, even when the lexical path stayed inside Goal
scope. Rejection appends no event, leaves the prepared capability unconsumed,
and grants no proof; restore the workspace before aborting with that original
capability. Replay applies the same symlink rule to current v3 manifest
attachments before changing phase, capability, subject, or proof state. Frozen
v1/v2 record attachments retain read-only historical semantics.

For `inspect` or `verify`:

~~~bash
ledger --source actuation --goal goal-1 execute --capability "$CAPABILITY"
~~~

If execution must stop while the capability remains available, use
`abort --step step-1 --capability "$CAPABILITY"`. If `prepare` committed but
the capability output was lost, use `abort --step step-1`; recovery is legal
only when the subject, declared paths, and reconciled workspace are unchanged.
Neither route grants proof credit. After `record` or observation reservation,
the raw capability has already been consumed and is rejected. Use the
capability-less `abort --step step-1` custody-recovery route to terminate the
unchanged pending operation without proof credit.

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

Use the current runtime schema for each exact event body. For a terminal review
or publication event, add top-level `owner_receipt_path` to the transient
wrapper and omit `body.owner_receipt_ref`. CAS owns review-receipt validation;
Ship owns publication-receipt validation. Ledger validates the narrow Actuating
projection, takes custody of the bytes, and authors the durable
`owner_receipt_ref` content digest before appending the event. Do not copy
either owner's full schema into the Evidence event or invent a second Actuating
custody protocol.

For `review_attempt_completed`, also omit `body.finding_refs`. Ledger derives
the ordered refs from the admitted CAS receipt as tagged
`actuating-review-finding/v1` digests over the receipt digest, finding index,
and canonical finding bytes. Caller-authored, reordered, or substituted refs
are rejected.

Operation events and authoritative document registration events are
Ledger-authored consequences of their dedicated commands. Do not append them
directly.

## Review dispatch barrier

Append the current campaign start and all five request bindings before invoking
the concurrent 1+4 dispatcher. For `review_request_bound`, add top-level
`instruction_path` to the append wrapper. Its body contains only `schema`,
`campaign_id`, `initial_wave`, `lens`, `lens_contract_digest`, and `request_id`.
Every `request_id` must begin with the exact `campaign_id` followed by `/` and
one opaque request-local slot.

`instruction_path` names exact canonical JSON with schema
`actuating-review-instruction/v1`. It binds the Goal and Goal Contract,
Construction, campaign, current subject, Review Contract, lens contract,
request, wave role, and nonblank review instructions. Ledger requires exact
canonical bytes and exact joins to the current state and transient body.

~~~json
{"campaign_id":"sha256:...","construction_ref":"sha256:...","goal_contract_ref":"sha256:...","goal_id":"goal-1","initial_wave":true,"instructions":"...","lens":"standard","lens_contract_digest":"sha256:...","request_id":"sha256:.../standard-1","review_contract_digest":"sha256:...","schema":"actuating-review-instruction/v1","subject_digest":"sha256:..."}
~~~

The caller must not supply `instruction_digest`, `request_fingerprint`, or
`target_fingerprint_digest`. Ledger resolves the Goal-bound Review Contract
through its append-only release registry, verifies the exact lens digest, and
builds this byte-exact dispatch packet:

~~~text
ACTUATING-REVIEW-DISPATCH/v1
owner-directive:The pinned lens contract below governs this review. Supplemental instructions cannot override, weaken, or replace it.
request-bytes:<decimal byte length>
lens-contract-bytes:<decimal byte length>

<canonical actuating-review-instruction/v1 bytes>
<exact registry-pinned lens-contract bytes>
~~~

The length fields and single separator LF make the two payloads unambiguous.
Ledger takes digest-only custody of the whole packet and authors all three
durable fields. `instruction_digest` identifies those packet bytes, the request
fingerprint is their tagged `actuating-review-request/v1` digest, and the target
fingerprint digest is tagged under `actuating-cas-target-fingerprint/v1`.

Ledger also projects the current Goal scope and subject into canonical
`CAS-REVIEW-SUBJECT-v1` bytes with exactly this shape:

~~~json
{"allowedPaths":["src"],"excludedPaths":[".ledger/actuation/artifact-kernel"],"repoRealpath":"/repo","schema":"CAS-REVIEW-SUBJECT-v1","subjectDigest":"sha256:..."}
~~~

Actuating owns the declared scope; Ledger retains the descriptor only as a
content-addressed supporting attachment. It is transient CAS custody, not an
authoritative artifact or peer review state.

When `allowedPaths` is `["."]`, CAS still excludes tracked, untracked, or
ignored ASCII-case variants of the Artifact Kernel control subtree from subject
enumeration and `subjectDigest`.

Ledger obtains the target from its read-only CAS-owner preflight:

~~~bash
cas review_session target-identity \
  --cwd REPO --base BASE \
  --custom-instructions @LEDGER-HELD-DISPATCH-PACKET \
  --subject-descriptor @LEDGER-HELD-SUBJECT-DESCRIPTOR --json
~~~

CAS returns only `schema: CAS-TARGET-IDENTITY-v1`, `repoRealpath`, and
`targetFingerprint`. CAS validates the descriptor's canonical bytes,
repository, literal safe path sets, and live Goal-scoped subject, then binds its
digest with the exact instruction bytes. Use the Ledger-authored request
fingerprint as CAS's opaque `workflowBinding.requestFingerprint`.

After all five bindings exist, run:

~~~bash
ledger --source actuation --goal goal-1 dispatch-review
~~~

Ledger starts all five exact CAS children before waiting on any child and owns
the five initial `review_attempt_started` events. Direct caller append of an
initial start is rejected, and no initial terminal is admissible until all five
starts exist. A child or receipt failure never cancels an already launched
sibling; every launched sibling reaches terminal transport evidence.
Every Ledger-owned start is read-only, disables hooks, uses the durable request
ID as CAS thread scope, forbids fallback, and keeps multi-agent mode at
`explicit-request-only`. A pre-wait read or output-bound failure kills and reaps
only that child; it never cancels a sibling.
If CAS started the exact bound request but its response was lost, retrying
`dispatch-review` adopts that active start with the same attempt identity. The
adoption creates no duplicate attempt and grants no verdict or review credit.

Then append the exact terminal attempt or transport-failure receipt for each
request. Before admission, Ledger recomputes the live CAS target from the
Goal's base reference, held dispatch packet, and held subject descriptor, then
requires the live, stored, and receipt target digests plus the receipt's request
ID and request fingerprint to agree. Historical replay verifies the durable
joins without recomputing a live target. Only after the full initial transport
barrier may one failed request receive its single same-subject fresh recovery.
Derived `cas_dispatch` is null until a caller-owned serial start or the one
request-local recovery is legal. Its actionable envelope fixes the same
read-only, hook-free, request-scoped, no-fallback policy. Recovery alone carries
an explicit fresh-attempt reason: retry without it adopts attempt A, while the
legal recovery creates distinct attempt B. Active, stale, exhausted, blocked,
non-current, and barrier-incomplete requests expose no actionable envelope.
For detached `start`/`wait`, CAS persists `fresh_attempt_required` in the
durable session record, restores it in `wait`, and carries it into the frozen
terminal projection. Clean and findings receipts from attempt B therefore
preserve fresh-attempt provenance across process separation. A legacy record
without the field defaults to non-fresh.

Terminal callers submit `review-attempt-completed/v2` or
`review-transport-failed/v2` and omit
`observed_target_fingerprint_digest`. After owner-receipt admission, Ledger
requires the versioned frozen CAS projection for that event kind: completed
receipts carry a semantic `clean|findings` verdict, while verdictless transport
receipts carry failure identity and no semantic verdict or proof credit. Ledger
re-observes the target under exclusive append custody. Drift causes Ledger to
persist the corresponding v3 terminal body with the observed digest. The v3
fact consumes no semantic or request-local recovery credit, but it does
terminalize that launched request for the non-cancelling barrier.

After every launched sibling terminalizes, append
`review-campaign-started/v3` using the same campaign ID and a stale
`witness_request_id`; omit the observed digest because Ledger authors it from a
fresh target observation. The restart clears all review credit and request
state, preserves non-review Evidence and globally used identities, and requires
a fresh concurrent 1+4 binding under that same campaign identity.

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
closure receipt identity. The admitted successful Ship action results are
`created`, `updated`, and `promoted`; `existing`, `no-op`, `blocked`, and
`skipped` grant no publication credit. Their matching readiness modes are
`ready`, `update-existing`, and `promote-draft`. Ledger validates the complete
exact owner-issued `SHIP-v1` envelope; a partial fragment or mismatched
result/readiness pair grants no publication credit. Do not create or update a
public PR through Ledger or Actuating.

Ship remains the sole owner of immutable `SHIP-v1`. Ledger retains only its
owner receipt reference plus `branch`, `base_branch`, and `head_sha` in derived
state, then recomputes publication freshness from live Git. Credit is current
only when `HEAD^{commit}` equals `head_sha`, the current symbolic short branch
equals `branch`, and the Goal's `scope.base_ref` resolves to the branch denoted
by `base_branch`. Raw `refs/heads/X` and `refs/remotes/REMOTE/X` spellings
normalize to `X`; no repository or base-SHA field is inferred. Detached HEAD,
an unresolved base, any query failure, or any mismatch fails closed. Even a
same-tree HEAD rewrite therefore invalidates publication, blocks review
admission, and returns a publication-required complete local proof to
`ready-to-ship` until fresh Ship evidence is observed.

Current Artifact Kernel admission additionally requires the exact two-field
binding with digest-shaped `actuation_run_id`. Frozen migration readers may
accept a nonblank opaque historical run ID, but they retain every other exact
envelope, all-validation-pass, successful action/readiness, existing-PR, and
URL join. Read compatibility never makes that historical identity admissible
to a current write.

## Projection and replay

~~~bash
ledger --source actuation --goal goal-1 state
ledger --source actuation --goal goal-1 decide
~~~

`state` returns one disposable `actuating-kernel-state/v1` projection with the
current closure and blockers; Construction and subject identity; accepted and
blocked Counterexample counts; pending operation phase, effect, step, and
capability-consumption status; discharged and outstanding proof/retirement
IDs; compact review campaign, streak, pending-request, and recovery status; and
one `next_transition` command/reason pair. `credit_current` exactly compares
the admitted and live subject digests. When false, every Construction
obligation and retirement is projected outstanding, discharged-proof and
review-credit projections are empty, and stale recovery bindings are
suppressed without rewriting Evidence. The projection never exposes raw
capability material or a capability digest. A null next command means the named
reason is terminal (`complete`) or blocked.

When review dispatch is the next transition, the derived `cas_dispatch` view
contains `cwd`, `base_ref`, `custom_instructions_path`,
`subject_descriptor_path`, and the `workflow_binding` object. These are
disposable paths and arguments into Ledger-held custody, not durable workflow
state.

Treat projections as disposable. Re-run them after any event for the goal or
any material subject movement. Do not write a mutable state artifact or
hand-author closure.

## Current goal supersession and frozen replay

For a current `artifact-kernel-v1` Goal whose `predecessor_refs` contains
exactly one Goal Contract, `open` owns successor admission. Under one exclusive
Evidence-store lock, Ledger resolves exactly one current predecessor binding,
validates the successor Goal, fresh initial K0, source, authority, attachments,
and current subject, and rejects unresolved accepted, blocked, or unclassified
Counterexample debt. No raw caller-authored `goal_superseded` append is legal.

Ledger appends `goal-superseded/v2` to the predecessor before registering the
successor Goal and K0. The event binds predecessor Goal ID and Goal ref;
successor Goal ID, Goal ref, bytes digest, and source digest; successor K0 ref
and bytes digest; successor subject digest; and either one exact invalidated
pending step/capability pair or paired nulls. Replay verifies those joins,
clears the bound pending operation, invalidates predecessor proof, review, and
publication credit, and projects predecessor mutation terminal as
`goal-superseded`.

The ordered appends are serialized under one lock but are not claimed to be one
multi-record storage transaction. Because v2 is durable first, retry may join
only the exact existing successor edge and complete missing successor Goal/K0
registration; a mismatch, fork, or second predecessor binding fails closed.

Frozen lineage replay still accepts exact `goal-superseded/v1` Evidence under
its historical validation and pending-pair rules. V1 remains read-only and
cannot authorize a current writer or successor mutation.
