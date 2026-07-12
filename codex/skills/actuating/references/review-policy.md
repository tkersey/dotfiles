# Actuating Review Policy

`$actuating` owns review selection, pinned lens contracts, exact instructions,
lane state, invalidation, repeated-review accounting, and closeout credit.
`$cas` receives only opaque request identity and the instructions it
transports.

## Policy artifact

Create one policy identity before the first review run. Materialize immutable
JSON snapshots of its current state for preflight and closeout checks:

~~~yaml
actuation_review_policy:
  version: actuation-review-policy/v2
  policy_id:
  run_id:
  goal_contract_digest:
  resolution_digest:
  review_contract_ref:
  review_contract_digest:
  artifact:
    repo:
    base_ref:
    base_sha:
    head_sha:
    state_fingerprint:
  standard_required_clean_runs: 5
  required_lenses: [standard, footgun-finder, invariant-ace, complexity-mitigator, fresh-eyes]
  requests:
    - request_id:
      request_fingerprint: null | sha256:...
      lens: standard | footgun-finder | invariant-ace | complexity-mitigator | fresh-eyes
      role: standard | auxiliary
      selection_reason:
      contract_id: null | string
      contract_ref: null | path
      contract_digest: null | sha256:...
      instructions_ref: null | path
      instruction_digest: null | sha256:...
      state: selected-pending | clean | findings-folded | candidate-pressure | blocked | rerun-required
      attempts:
        - workflow_binding:
            requestId:
            requestFingerprint:
          review_attempt_id:
          review_thread_id:
          review_turn_id:
          base_sha:
          head_sha:
          target_fingerprint:
          context_identity_matches: true | false
          principal_kind:
          principal_reduced: true | false
          fallback_used: true | false
          principal_source:
          verdict_status: clean | findings
          finding_count:
          record_ref:
      review_fold_refs: []
  standard_clean_chain:
    standard_attempts:
      - artifact:
          repo:
          base_ref:
          base_sha:
          head_sha:
          state_fingerprint:
        goal_contract_digest:
        resolution_digest:
        review_contract_digest:
        request_id:
        request_fingerprint:
        contract_id:
        contract_digest:
        instruction_digest:
        attempt:
          workflow_binding:
            requestId:
            requestFingerprint:
          review_attempt_id:
          review_thread_id:
          review_turn_id:
          base_sha:
          head_sha:
          target_fingerprint:
          context_identity_matches: true | false
          principal_kind:
          principal_reduced: true | false
          fallback_used: true | false
          principal_source:
          verdict_status: clean | findings
          finding_count:
          record_ref:
    carry_transitions:
      - kind: auxiliary-remediation
        from_attempt_id:
        to_artifact:
          repo:
          base_ref:
          base_sha:
          head_sha:
          state_fingerprint:
        from_goal_contract_digest:
        to_goal_contract_digest:
        resolution_digest:
        source_auxiliary_request_ids: []
        review_fold_refs: []
        correctness_decision_refs: []
        preservation_observation_refs: []
        progress_observation_refs: []
        actuation_event_refs: []
        ship_ref:
  standard_clean_attempt_ids: []
  invalidation_reasons: []
~~~

Run the Actuating-owned validator at both proof boundaries:

~~~bash
ledger validate actuation-review-policy \
  --phase preflight --input <policy.json>
ledger validate actuation-review-policy \
  --phase closeout --input <policy.json>
~~~

It emits `actuation-review-policy-decision/v1`, grants no authority, and
mutates no storage. New campaigns require Ledger 0.7.0 or newer and emit
`actuation-review-policy/v2`. The validator retains v1 compatibility with its
original same-tuple suffix law; a v1 snapshot cannot carry credit across a
tuple change. `preflight` requires every current request to be pending but may
accept a v2 chain carried from the immediately preceding artifact. `closeout`
checks registry/request bijection, exact referenced contract and instruction
bytes, opaque binding and artifact identity, source quality, distinct attempts,
chain topology, disjoint lane accounting, and terminal request states.

`review_contract_ref` is the exact persisted aggregate manifest for the policy
semantics that must remain stable across a carry: policy version, required
standard-clean count, ordered lens registry, every lens role, contract ID, and
contract digest. Exclude artifact identity, resolution identity, request IDs,
instruction bytes, and request fingerprints because those are epoch-specific.
Set `review_contract_digest` to the SHA-256 of the manifest's exact bytes and
bind its digest verifier into the GoalContract. Every historical standard row
must carry that same digest; contract or registry drift therefore resets the
chain instead of masquerading as auxiliary remediation.

`standard_clean_chain.standard_attempts` is the exhaustive ordered projection
of valid standard terminal facts retained for streak accounting. Preserve each
fact's original request identity, contract identity, GoalContract and
resolution digests, and CAS tuple. Include `findings` attempts because they
break the trailing clean suffix. The rows for the current artifact must equal
the current standard request's `attempts` exactly; historical rows never move
into or impersonate the current request.

`carry_transitions` contains only non-credit edges between adjacent standard
attempt epochs whose tuples differ. A carry must start from a clean standard
attempt, keep repo/base identity stable, change head and state fingerprint,
preserve the aggregate review contract and standard contract, and bind the
auxiliary request IDs, RF-v2 folds, resolution digest, correctness decisions,
observed preservation and progress obligations, actuation events, and SHIP-v1
receipt that produced the next artifact. The edge preserves the suffix length;
it never adds an attempt ID.

The policy checker validates this chain algebra and the presence, identity, and
joins of its cited fields; it does not open RF-v2, resolution, actuation, or
SHIP artifacts and rediscover their semantics. `$goal-actuating` must verify
those exact referenced artifacts, prove that the repair contains no unrelated
mutation, and bind those verifier commands into the GoalContract before the
carry receives credit.

For a selected request, `request_fingerprint` equals `instruction_digest`: the SHA-256 of the exact
persisted UTF-8 bytes at `instructions_ref`. The pre-bound policy row and
GoalContract digest bind those bytes to policy version, artifact identity,
resolution digest, lens, role, selection reason, contract ID, and contract
digest. Project only `request_id` and `request_fingerprint` into CAS
`workflowBinding` as `requestId` and `requestFingerprint`. CAS treats both
strings as opaque.

Bind the complete policy artifact into the GoalContract digest before running
CAS. Project the exact CAS command and the instruction-digest verifier into the
review obligation. Post-run labels, reconstructed prompts, and legacy semantic
bindings cannot satisfy that obligation.

Every registry row is selected and fully bound. Closure-grade review has no
auxiliary non-selection state.

## Lens registry and selection

| Lens | Role | Contract | Required focus |
| --- | --- | --- | --- |
| `standard` | standard | `standard-review-v1` | General correctness in every closure-grade campaign |
| `footgun-finder` | auxiliary | `footgun-lens-v1` | API, CLI, config, default, fallback, cleanup, permission, example, and workflow affordances |
| `invariant-ace` | auxiliary | `invariant-gate-v1` | State ownership, validation, transitions, identity, authority, replay, idempotency, and impossible-state claims |
| `complexity-mitigator` | auxiliary | `complexity-preflight-v1` | Boolean soup, mixed responsibilities, repeated owner-boundary churn, and comprehension-heavy cross-file state |
| `fresh-eyes` | auxiliary | `fresh-eyes-lens-v1` | Whole-target reinspection for blunders, mistakes, errors, oversights, omissions, problems, misconceptions, bugs, and related defects |

The selected lens skill is the instruction authority. Resolve its operative
contract and every referenced resource it requires into a manifest, persist
that manifest at `contract_ref`, and set `contract_digest` to the SHA-256 of
its exact bytes. Render the review-only request from that pinned contract,
persist the instruction bytes, and hash them before CAS execution. Before the
run and after exhaustive history acquisition, verify the manifest digest,
every resource digest named by the manifest, and the instruction digest.
RF-v2 routing obligations and changed surfaces refine request-specific scope;
they never suppress a registered auxiliary lens. Increment `contract_id`
whenever the operative lens contract changes.

Use this wrapper when materializing each selected request:

~~~text
Use $<lens> as the review-only lens for this exact review target.
Contract: <contract-id> (<contract-digest>).
Request: <request-id>.
Review target: <repo>, from <base-sha> through <head-sha> (base ref <base-ref>).
Follow the selected lens contract completely. Do not implement or choose a repair.
Return findings through the native structured review result; return zero findings only after completing the lens.
~~~

The filled wrapper is part of the persisted instruction bytes. Add any
request-specific scope needed by the selected lens before hashing; never append
instructions after the digest is bound. Naming a lens without pinning and
verifying its operative contract does not satisfy a selected request.

Copy the current registry names into `required_lenses` during source-to-open
inspection. The validator is deliberately registry-generic: it proves a
bijection between that bound list and the request rows without hard-coding
today's lens names. Every policy snapshot binds all five current registry
entries exactly once. `request_id` values are unique within the policy, and
every request begins `selected-pending`.

## Application law

Before execution, require `cas_rer_opaque_request_binding_v1=true`,
`cas_review_history_v2=true`, and
`cas_review_scoped_instructions_v1=true` from `cas capabilities`. An older
dispatcher may still drive exploratory reviews, but it cannot satisfy this
policy's bound closeout requests.

Launch every auxiliary request concurrently with the first standard attempt as
one dispatch wave against the same bound artifact. Do not wait for a standard
result before starting an auxiliary lane. A semantic verdict or verdictless
transport failure never cancels a sibling request: clean and findings are
terminal policy facts, while `review_failed` without a structured tuple verdict
is terminal only for its dispatch handle. Finish the entire launched wave before
retrying a failed request, and finish exact-request recovery before any
review-driven mutation. Keep the resolution digest bound at preflight unchanged
while collecting that wave; append review fold references to terminal semantic
request rows, then construct or update the resolution after exhaustive history
is available and no request remains `rerun-required`. Run later standard
attempts as fresh, distinct, ordered attempts until the v2 chain's trailing
clean suffix reaches `standard_required_clean_runs`, which must be at least
five, and ends with a clean standard attempt on the current tuple. Each command
carries:

~~~bash
cas review run --cwd <repo> --base <base-ref> \
  --custom-instructions @<instructions-ref> \
  --workflow-binding-json @<opaque-binding.json> \
  --timeout-ms 1800000 --json --fallback none
cas review list --cwd <repo> --base <base-ref> \
  --custom-instructions @<instructions-ref> \
  --workflow-binding-json @<opaque-binding.json> \
  --codex-thread-id <id> --json
~~~

After terminal evidence, add `--fresh-attempt <source-bound-reason>` for each
additional standard attempt. Reusing cached terminal evidence does not create a
distinct attempt.

After the run and exhaustive `CAS-LIST-v2` acquisition, `$actuating` joins four
identities:

1. the pre-bound policy request;
2. the actuation event that executed the exact command;
3. the echoed opaque binding and current CAS tuple;
4. the RF-v2 fold for any findings.

Append only valid joined terminal `clean` or `findings` facts to the request's
ordered `attempts`. Invalid, incomplete, reduced, fallback, or mismatched facts
remain observable in CAS history but never enter the credit projection. The
separate exhaustive-history obligation prevents omission from manufacturing a
clean suffix.

The join is valid only when request ID/fingerprint, base, head, target
fingerprint, attempt identity, contract digest, instruction digest, and current
artifact all agree and CAS reports `contextIdentityMatches=true`. Closure-grade
credit additionally requires `principal_kind=strong`,
`principal_reduced=false`, and `fallback_used=false`. `$actuating` evaluates
those source facts; `contextIdentityMatches` is identity evidence, not a credit
decision. An unbound, mismatched, stale, incomplete, reduced, fallback, or
pre-0.2.75 binding is `invalid-proof` for closeout.

### Verdictless transport failure

Treat a terminal CAS `review_failed` fact with
`tupleVerdictExists=false` as request-local transport evidence, never as a
semantic `clean` or `findings` attempt. Keep it in exhaustive CAS history but do
not append it to `requests[].attempts` or `standard_clean_chain`. Set only its
bound request to `rerun-required`; leave every sibling request, retained valid
attempt, and `standard_clean_attempt_ids` unchanged.

Let every other dispatch from the initial wave reach terminal transport
evidence. Then rerun only the failed request with the same request binding and
unchanged tuple, using `--fresh-attempt <source-bound-reason>` so CAS creates a
new independent attempt instead of returning the existing terminal fact. A valid
replacement verdict follows the ordinary lane rule. If that recovery dispatch
also terminates verdictless, leave the request `rerun-required` and block rather
than retrying indefinitely. It never authorizes sibling cancellation, whole-wave
zeroing, or a sequential replacement campaign. A full replacement wave is legal
only after a named invalidation changes the policy epoch, and that wave remains
concurrent.

## Lane accounting

~~~text
valid auxiliary clean                -> satisfy that current auxiliary request; standard count unchanged
valid auxiliary findings             -> fold and terminalize that request; keep siblings running; standard count unchanged
verdictless review_failed             -> failed request only is rerun-required; no attempt or credit; siblings and standard suffix unchanged
same-tuple failed-request recovery    -> after the initial dispatch barrier, rerun that exact request only
certified auxiliary-remediation carry -> preserve the standard suffix; add no credit; rerun the full current wave
invalid clean                         -> no credit; rerun the exact current request
invalid findings                      -> candidate-pressure until owner-boundary validation and a valid rerun
selected-pending                      -> blocks closeout
valid standard clean                  -> append one distinct ordered standard attempt ID
valid standard findings               -> append the finding fact and reset the trailing standard clean suffix
unrelated or uncertified tuple change -> reset the chain
~~~

Only distinct, ordered standard `clean` facts contribute to
`standard_clean_attempt_ids`. They may retain their original earlier tuples
only when every intervening tuple transition is a valid carry. Auxiliary
attempts and carry transitions never contribute: auxiliary clean results only
discharge their execution obligation, while auxiliary findings enter RF-v2.
An auxiliary findings result is terminal discovery evidence, not a zero-credit
standard result. It neither breaks the standard suffix nor changes another
request's state.
The policy artifact, not CAS history or lock state, determines whether the
required clean suffix and every current auxiliary request are satisfied.

The closeout checker requires `standard_clean_attempt_ids` to equal the exact
trailing required suffix derived from `standard_clean_chain`. It rejects
duplicate attempt identity, cross-lane credit, missing or extraneous carry
edges, standard findings inside that suffix, contract drift, a chain that does
not end clean on the current tuple, open current auxiliary states, and any
invalidation reason.

## Invalidation

The accepted repair, not the finding, creates the tuple transition. A terminal
finding does not change the bound artifact or resolution identity, invalidate
the current policy snapshot, or cancel any sibling request. Keep the
preflight-bound `resolution_digest` through the collection barrier; after every
launched request is terminal, fold and adjudicate the complete wave and bind
any resulting resolution to the repair generation and next review epoch.

A verdictless transport failure likewise creates no invalidation. It changes
only its request to `rerun-required`, preserves the current tuple and standard
projection, and must be recovered before the resolution barrier can open.

Invalidate every current request when any bound artifact identity, instruction
byte, resolution digest, or publication epoch changes. No auxiliary result from
the preceding artifact survives as closeout evidence; relaunch the full
concurrent wave against the new artifact. Recover timeouts through the same CAS
handle and do not turn recovery into another independent attempt.

Reset `standard_clean_chain` when the review-contract manifest changes, a
standard attempt reports findings, the base identity changes, the artifact
change contains any unclassified or unrelated mutation, or the transition
lacks any required auxiliary-resolution, correctness, actuation, or SHIP
evidence. A caller-authored reason or boolean exemption cannot preserve credit.

The sole artifact-change exception is a v2 `auxiliary-remediation` carry. At the
next artifact's preflight, retain the prior exhaustive standard history and its
exact clean projection, append one dangling carry from the last clean standard
attempt to the new current artifact, and keep every new current request pending.
At closeout, append the new tuple's exhaustive standard attempts, require the
carry to connect to the first new row, recompute the trailing clean projection,
and require at least one clean standard attempt plus all auxiliary evidence on
the current tuple. Multiple auxiliary repairs may compose only as a chain of
individually certified carries separated by standard attempts.

Adding a lens, renaming a lens, changing a contract, or changing the required
clean count must require zero CAS schema or implementation changes.
