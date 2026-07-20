# Static Review Contract

Use one separately versioned `actuating-review-contract/v1` as review law. It
is not a per-goal mutable artifact and never becomes a per-run policy snapshot.
At Goal registration, bind its exact release-owned digest. Its canonical bytes
remain static release evidence rather than a copied per-goal document.

## Contract shape

~~~yaml
review_contract:
  schema: actuating-review-contract/v1
  contract_id:
  contract_digest:

  required_lenses:
    - name: standard
      role: standard
      contract_ref:
      contract_digest:
    - name: footgun-finder
      role: auxiliary
      contract_ref:
      contract_digest:
    - name: invariant-ace
      role: auxiliary
      contract_ref:
      contract_digest:
    - name: complexity-mitigator
      role: auxiliary
      contract_ref:
      contract_digest:
    - name: fresh-eyes
      role: auxiliary
      contract_ref:
      contract_digest:

  initial_wave:
    concurrent: true
    all_lenses_required: true
    non_cancelling: true

  standard_convergence:
    required_consecutive_clean_attempts: 5
    first_wave_standard_counts: true
    later_attempts_serial: true
    findings_reset_streak: true

  material_change:
    resets_all_review_credit: true

  transport_recovery:
    request_local: true
    maximum_fresh_recovery_attempts: 1

  attempt_quality:
    strong_principal_required: true
    reduced_principal_forbidden: true
    fallback_forbidden: true
    context_match_required: true
    exact_instruction_digest_required: true
~~~

Changing a lens, lens role, lens contract, clean threshold, recovery rule,
attempt-quality rule, or material-change rule creates a new static Review
Contract version. It does not require a Counterexample or Evidence schema
change.

Ledger resolves the Goal-bound digest through one append-only release registry.
Each entry fixes the exact contract bytes, ordered lens names and roles, exact
lens-contract bytes, clean threshold, and recovery bound. The v1 builder and
its lens bytes are frozen; a future version appends a new registry entry rather
than revising v1. A self-consistent caller-supplied contract is not an
alternative registry entry and fails closed.

## Campaign identity

Derive campaign identity from:

~~~text
digest(goal_id, construction_ref, subject_digest, review_contract_digest)
~~~

Review campaign state is a fold of the static contract, current Construction,
current subject, review events, and Counterexample Sets. Git publication state
is not part of campaign identity. Do not store peer mutable policy or campaign
truth.

## Initial wave

Before dispatch, bind all five requests to:

- one Goal, Construction, subject, and campaign;
- the exact selected lens contract bytes and digest;
- the exact source-bound review instruction bytes and digest;
- a unique opaque request identity and fingerprint;
- the Goal-owned compatibility authority.

Actuating owns review scope. Ledger deterministically projects the current Goal
scope and admitted subject into canonical `CAS-REVIEW-SUBJECT-v1` bytes with
exactly `allowedPaths`, `excludedPaths`, `repoRealpath`, `schema`, and
`subjectDigest`; `excludedPaths` is exactly
`[".ledger/actuation/artifact-kernel"]`. Ledger retains those bytes only as a
content-addressed supporting attachment. The descriptor is transient CAS
custody, not a fifth authoritative artifact family or peer review state.

CAS owns target identity. It validates the descriptor, repository, literal
safe path sets, live Goal-scoped subject, and exact instruction bytes; rejects
subject drift; and binds the descriptor digest into the target fingerprint.
Legacy review without a descriptor retains its frozen whole-workspace identity
and never mixes with this route.

Ledger, not the caller, builds the exact `ACTUATING-REVIEW-DISPATCH/v1` packet
from the canonical request bytes and the registry-pinned lens-contract bytes.
Its owner directive makes the pinned lens governing and prevents supplemental
instructions from overriding, weakening, or replacing it. The packet, rather
than either component alone, is the bytestring bound into CAS target identity
and the request fingerprint.

After all five exact bindings exist, invoke Ledger's transient
`dispatch-review` operation. Ledger starts standard plus four auxiliary CAS
children before waiting on any child and authors the five durable
`review_attempt_started` events. A caller cannot append an initial start event,
and no initial terminal event is admissible until all five starts exist. Every
launched sibling must reach terminal transport evidence after any finding,
start-collection failure, or later transport failure. Do not cancel siblings,
serialize a replacement wave, mutate before the wave and classification
barriers, or treat one request failure as whole-wave zero credit.

Report a completed review exactly once after both its structured receipt and
recorded process status exist. The semantic verdict, not process exit status,
owns `clean` or `findings`. Reporting does not mutate request state, grant
credit, cancel siblings, open recovery, classify findings, or authorize repair.

## Request-local recovery

A terminal attempt without a structured semantic verdict:

- contributes no semantic attempt and no clean credit;
- changes only that request to recovery-required in the derived fold;
- preserves all sibling facts and any standard suffix on the unchanged subject;
- waits for the initial dispatch barrier;
- reruns that exact request once with the same subject and request binding plus
  a fresh attempt identity;
- blocks after a second verdictless terminal result.

The failure remains in exhaustive transport history. Never rewrite it as a
finding, a clean attempt, or a whole-wave reset.

## Findings and Counterexamples

Pass every finding through `$review-fold`. It authors the current
`counterexample-set/v1`, separates fact from suggested repair, quotients
duplicates, and classifies each stable boundary-law class as accepted,
rejected, blocked, or follow-up.

Review transport and classification never select a repair or grant mutation.
An accepted class requires a current successor Construction Contract. A
blocked class blocks closure. Rejection requires evidence.

For a completed CAS receipt, Ledger authors each durable `finding_ref` from the
receipt digest, finding index, and exact canonical finding bytes. Callers and
`$review-fold` must consume those references and must not invent, reorder, or
substitute them.

## Full-wave success and convergence

The full wave succeeds only when:

- its standard attempt is clean;
- all five requests have valid terminal semantic or resolved transport facts;
- every finding is classified;
- every accepted Counterexample is excluded, rejected with evidence, or
  represented by an explicit blocker;
- the Construction, subject, and Review Contract are current.

Count the full-wave standard clean as streak one. Then run fresh standard
reviews serially until the trailing current-subject clean streak equals five.
Auxiliary attempts never add standard credit.

## Findings on an unchanged subject

A standard finding resets the standard streak immediately. If adjudication
causes no material change, preserve current auxiliary results; after the class
is rejected or otherwise resolved, fresh standard attempts may continue from
zero.

An auxiliary finding does not alter standard credit on the unchanged subject.
Its accepted Counterexample still blocks mutation until a successor
Construction is registered.

## Material change

Any material change to the correctness subject invalidates all review credit
and requires a fresh concurrent 1+4 wave. A different Goal, Construction, or
Review Contract derives a different campaign rather than inheriting credit.
The subject digest includes every repository artifact in Goal scope and
excludes only Ledger control storage and declared external evidence custody.

There is no `auxiliary-remediation` carry and no review credit across a material
subject change. Old attempts retain their historical tuples and never become
current credit by relabeling.

## Target drift during a launched wave

Terminal append inputs use the v2 completion or transport schema. After CAS
receipt admission, Ledger re-observes the live target under exclusive append
custody. If it differs from the request-bound target, Ledger writes the exact
v3 terminal schema with `observed_target_fingerprint_digest`. That terminal
fact earns neither semantic nor recovery credit; it records only that the
launched attempt ended against a stale target.

Let every launched sibling reach terminal evidence. Then append
`review-campaign-started/v3` with the existing campaign ID and one stale
witness request. Ledger authors the observed target digest, clears only derived
review state, preserves non-review Evidence and globally consumed request and
attempt identities, and requires a fresh full 1+4 binding. No prior auxiliary
result or standard clean survives the restart. A caller may not use v3 to
rename a campaign, restart while an attempt is active, or turn stale terminal
evidence into credit.

## Independence

Reviewers receive the exact subject and source-bound contracts needed to
falsify it. Do not automatically provide persuasive Universalist candidate
analysis or rationale. After review, Actuating joins classified
Counterexamples to the selected Construction and asks which claim was
falsified. This keeps architecture synthesis and review falsification
independent.
