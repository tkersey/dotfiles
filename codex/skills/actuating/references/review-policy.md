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
  version: actuation-review-policy/v1
  policy_id:
  run_id:
  goal_contract_digest:
  resolution_digest:
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
mutates no storage. `preflight` rejects review evidence and requires every
request to be pending. `closeout` checks registry/request bijection, exact
referenced contract and instruction bytes, opaque binding and artifact
identity, source quality, distinct attempts, disjoint lane accounting, and
terminal request states.

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
result before starting an auxiliary lane. Run later standard attempts as fresh,
distinct, ordered attempts until the current clean suffix reaches
`standard_required_clean_runs`, which must be at least five. Each command
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

## Lane accounting

~~~text
valid auxiliary clean           -> satisfy that auxiliary request; standard count unchanged
valid auxiliary findings        -> require RF-v2 fold; accepted artifact changes invalidate current requests
invalid clean                    -> no credit; rerun the exact current request
invalid findings                 -> candidate-pressure until owner-boundary validation and a valid rerun
selected-pending                 -> blocks closeout
valid standard clean             -> append one distinct ordered attempt ID
standard findings or code change -> reset the current standard clean suffix
~~~

Only distinct, current, ordered standard attempts contribute to
`standard_clean_attempt_ids`. Auxiliary attempts never contribute: auxiliary
clean results only discharge their execution obligation, while auxiliary
findings enter RF-v2. The policy artifact, not CAS history or lock state,
determines whether the required clean suffix and every auxiliary request are
satisfied.

The closeout checker requires `standard_clean_attempt_ids` to equal the exact
trailing required clean suffix; it rejects duplicate attempt identity,
cross-lane credit, stale artifact bindings, open auxiliary states, and any
invalidation reason.

## Invalidation

Invalidate affected review requests when any bound artifact identity,
contract byte, instruction byte, contract ID, policy selection, resolution
digest, or publication epoch changes. Recover timeouts through the same CAS
handle; do not turn recovery into another independent attempt.

Any accepted artifact change invalidates the standard suffix and every
auxiliary request. Relaunch the full concurrent wave against the new artifact;
no auxiliary result from the preceding artifact survives as closeout evidence.

Adding a lens, renaming a lens, changing a contract, or changing the required
clean count must require zero CAS schema or implementation changes.
