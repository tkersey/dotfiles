# Example invocations

## Surface-Budgeted v5 review adjudication

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

Goal: determine which current PR review comments should change code before any
implementation.

Inputs:
- raw PR review comments with id/thread/reviewer/location/excerpt
- current branch vs main
- branch/head/diff/comment-set identity if available
- PR description / intended change
- current tests and CI status
- relevant files

Rules:
- preserve raw comment identity and input inventory
- bind the adjudication to artifact_state_id
- treat each comment as a claim, not an obligation
- construct the strongest no-change countercase for every comment
- separate concern validity from proposed-fix validity
- use evidence grade + evidence ref for every action
- use $seq only if PR rationale is missing, disputed, stale, or likely to affect disposition
- do not implement fixes
- do not hand off implementation unless the Adjudication Gate passes and implementation_handoff_allowed is yes

Required output:
- Review Basis
- Comment Inventory
- PR Why Ledger
- Comment Ledger
- Decision Tests
- No-Change Countercases
- Governing Invariant Ledger
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Resolve Selection
- Adjudication Gate
- Handoff Agenda
- Adjudication Bottom Line

Failure condition:
If artifact state, identity coverage, inventory coverage, decision tests,
no-change coverage, proposed-fix separation, evidence refs, invariant pass, or
skew audit is incomplete, set `adjudication_complete: fail` and
`implementation_handoff_allowed: no`.
```

## Review the review

```md
Use $review-adjudication for this task.

Goal: Determine which current PR review comments are actually relevant before
changing code.

Context:
- current branch vs main
- reviewer comments pasted below
- relevant files: auth/session.ts auth/session.test.ts
- current CI status: one failing test, reviewer asked for a refactor and an API rename

Constraints:
- treat comments as claims, not truths
- construct the strongest no-change countercase for each comment
- use $seq if the original why of this PR is unclear
- do not implement changes yet
- emit the Surface-Budgeted v5 Adjudication Gate

Done when:
- each raw comment is represented exactly once
- each comment is classified
- the bottom line says what to act on, rebut, defer, or investigate
- any governing invariant behind repeated comments is named
- the handoff agenda separates implementation, validation, and reply routes
- `adjudication_complete`, `implementation_handoff_allowed`, `validation_handoff_allowed`, and `reply_handoff_allowed` are explicit
```

## Fast adjudication without implementation handoff

```md
Use $review-adjudication in Fast mode.

Comments:
1. This should be a helper.
2. The retry path looks non-idempotent.
3. Please rename the public method to refreshSessionNow.
4. Add a property-based test.

Return only:
- Comment Inventory
- Comment Ledger
- Decision Tests
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Resolve Selection
- Adjudication Gate
- Handoff Agenda
- Adjudication Bottom Line

Do not allow implementation handoff unless the gate passes. If real comment IDs
are missing, set identity_coverage to fail.
```

## Intent recovery first

```md
Use $review-adjudication for this task.

Goal: Figure out whether these review comments still make sense given why this
PR exists.

Constraints:
- explicitly use $seq to recover the PR why from sessions and memories
- prefer session-backed evidence over memory-only recall
- do not change code
- if every comment is accepted, justify why this is not rubber-stamping using the structured All-Action Justification table
- if $seq cannot recover material intent, mark affected comments need-evidence
```

## Rebuttal-heavy review

```md
Use $review-adjudication for this task.

Goal: Discriminately evaluate these PR comments. I do not want to ignore real
reviews, but I do want to avoid rubber-stamping.

Constraints:
- for every comment, write the strongest no-change countercase
- act only when current artifacts defeat that countercase
- separate valid concern from valid proposed fix
- cluster repeated comments by governing invariant
- if all comments are `act`, emit structured All-Action Justification or block implementation handoff
```

## Validation-only uncertain review

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

Goal: decide whether a reviewer-reported failure mode is proven or should be
validated before code changes.

Rules:
- if the concern might be real but current artifacts do not prove it, use
  `need-evidence`
- use `proposed_fix_validity: validation-only`
- use `reframe_type: validation-only` and `remediation_posture: validating-check-only`
- route validation-only work to $fixed-point-driver
- set `implementation_handoff_allowed: no` unless some separate `act` item is artifact-backed
- do not implement the proposed fix unless validation fails or current artifacts
  already prove the failure
```


## Resolve-selection invocation

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

Goal: select which PR review comments should be addressed, validated only,
resolved with proof only, rebutted/deferred, or blocked before any `$resolve`,
`$fixed-point-driver`, `$ship`, or thread cleanup workflow.

Rules:
- preserve raw comment identity and input inventory
- bind the adjudication to the current artifact_state_id
- separate adjudication disposition from downstream resolve decision
- use `address` only for artifact-backed `act` rows
- use `validate-only` for proof-first uncertainty
- use `resolve-thread-only` for stale/already-fixed comments that need a
  proof-bearing reply but no code change
- do not route `resolve-thread-only`, `do-not-address`, or `blocked` items as
  implementation work
- emit the full Adjudication Gate with `resolve_selection_coverage`
```

## Anti-laundering resolve selection

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

Goal: refine these PR review comments to the subset that is actually worth
resolving before implementation, validation, or thread cleanup.

Rules:
- preserve raw comment identity and input inventory
- emit exactly one Resolve Selection row per ledger row
- include `proof ref` and `route rationale` for every Resolve Selection row
- run a Resolve Countercases pass that challenges the selected downstream route
- use `address` only for artifact-backed `act` rows
- use `validate-only` only for proof-first uncertainty
- use `resolve-thread-only` only for stale/already-fixed comments with concrete proof
- use `do-not-address` for preserved no-change, preference-only, out-of-scope, or low-value rows
- make Handoff Agenda buckets exactly match Resolve Selection decisions
- if every row is `address` or `validate-only`, emit structured All-Selected Justification
- do not route narrow-local work to $fixed-point-driver without coupled/invariant/structural/contentious/likely-to-reopen rationale
```

## Handoff-agenda consistency check

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

After the Comment Ledger and Resolve Selection, produce a Handoff Agenda whose
buckets are exact projections:

- items selected for implementation = all and only `address` rows
- validation-only items = all and only `validate-only` rows
- proof-only thread-resolution items = all and only `resolve-thread-only` rows
- items not selected = all and only `do-not-address` rows
- blocked items = all and only `blocked` rows

Do not use "all". Use explicit comment IDs.
```


## Resolution-warranted invocation

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

Goal: adjudicate these review/CAS claims and issue the minimum active warrants
required for the next workflow.

Rules:
- no mutation without a `mutate-code` Resolution Warrant
- no validation probe without an `add-validation-only` warrant
- no thread cleanup without a `resolve-thread` warrant
- every warrant must bind artifact_state_id, claim id, permitted scope,
  forbidden actions, evidence refs, proof required, and expiry
- Handoff Agenda must be a projection of Resolve Selection and Resolution Warrants
```

## Surface-budgeted review resolution

```md
Use $review-adjudication in Surface-Budgeted v5 mode.

Goal: decide which review comments deserve code, and for each `address` item
issue a Resolution Warrant plus Surface Budget Ledger row. Prefer deletion,
reuse, duplicate-path collapse, and refactor before additive code. Route to
$fixed-point-driver with Surface Budget Preflight and require Surface Delta
Receipts after patch groups.
```
