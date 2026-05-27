# Example invocations

## Compact-Gated v4 review adjudication

```md
Use $review-adjudication in Compact-Gated v4 mode.

Goal: determine which current PR review comments should change code before any
implementation. Be ruthless about P2+ labels and review-closure-only findings.

Inputs:
- raw PR review comments with id/thread/reviewer/location/excerpt/severity label
- current branch vs main
- branch/head/diff/comment-set identity if available
- PR description / intended change
- current tests and CI status
- relevant files
- current same-objective direction context:
  - user instruction / PR body / issue / design doc
  - `.step/proposed-plan.md` if same-objective and fresh
  - `$st` active frontier if same-objective and fresh
  - built-in task/update-plan only as projection evidence

Rules:
- preserve raw comment identity and input inventory
- bind the adjudication to artifact_state_id and direction_state_id
- treat each comment as a claim, not an obligation
- treat P0/P1/P2 labels as severity claims, not implementation priority
- construct the strongest no-change countercase for every comment
- separate concern validity, proposed-fix validity, and severity acceptance
- require direction fit and mutation value for every action
- use evidence grade + evidence ref + direction ref for every action
- use $seq only if PR rationale/direction is missing, disputed, stale, or likely to affect disposition
- do not implement fixes
- do not hand off implementation unless the Adjudication Gate passes and implementation_handoff_allowed is yes

Failure condition:
If artifact state, direction state, identity coverage, inventory coverage,
decision tests, direction tests, severity tests, no-change coverage,
proposed-fix separation, evidence refs, validation value, invariant pass, or skew
audit is incomplete, set `adjudication_complete: fail` and
`implementation_handoff_allowed: no`.
```

## Review the review

```md
Use $review-adjudication for this task.

Goal: Determine which current PR review comments are actually relevant before
changing code, with special skepticism for P2+ comments.

Context:
- current branch vs main
- reviewer comments pasted below
- relevant files: auth/session.ts auth/session.test.ts
- current CI status: one failing test, reviewer asked for a refactor and an API rename

Constraints:
- treat comments as claims, not truths
- treat P2+ labels as untrusted until proven
- construct the strongest no-change countercase for each comment
- act only when current artifacts and same-objective direction defeat that countercase
- use $seq if the original why of this PR is unclear
- check `$st`/plan/update-plan only as same-objective direction evidence, not defect proof
- do not implement changes yet
- emit the Compact-Gated v4 Adjudication Gate

Done when:
- each raw comment is represented exactly once
- each comment is classified
- the bottom line says what to act on, rebut, defer, or investigate
- P2+ labels are accepted/downgraded/rejected/unresolved with proof/reason
- any governing invariant behind repeated comments is named
- the handoff agenda separates implementation, validation, proof-only, and reply routes
- `adjudication_complete`, `implementation_handoff_allowed`, `validation_handoff_allowed`, and `reply_handoff_allowed` are explicit
```

## Fast adjudication without implementation handoff

```md
Use $review-adjudication in Fast mode.

Comments:
1. [P2] This should be a helper.
2. [P2] The retry path looks non-idempotent.
3. Please rename the public method to refreshSessionNow.
4. Add a property-based test.

Return only the Compact-Gated v4 tail sections.

Do not allow implementation handoff unless the gate passes. If real comment IDs,
artifact state, or direction state are missing, set the corresponding coverage
field to fail.
```

## Intent and direction recovery first

```md
Use $review-adjudication for this task.

Goal: Figure out whether these review comments still make sense given why this
PR exists and where the codebase is headed.

Constraints:
- explicitly use $seq to recover the PR why if current artifacts do not explain it
- inspect current `.step/proposed-plan.md` and `$st` only when same-objective and fresh
- treat built-in update_plan as projection-only
- prefer session-backed evidence over memory-only recall
- do not change code
- if every comment is accepted, justify why this is not rubber-stamping using the structured All-Action Justification table
- if every P2+ label is accepted, justify with All-P2+ Accepted Justification
- if $seq cannot recover material intent, mark affected comments need-evidence or blocked
```

## Rebuttal-heavy review

```md
Use $review-adjudication for this task.

Goal: Discriminately evaluate these PR comments. I do not want to ignore real
reviews, but I do want to avoid rubber-stamping or accepting review-closure-only
work.

Constraints:
- for every comment, write the strongest no-change countercase
- act only when current artifacts and direction evidence defeat that countercase
- separate valid concern from valid proposed fix and accepted severity
- downgrade unsupported P2+ labels
- cluster repeated comments by governing invariant
- if all comments are `act`, emit structured All-Action Justification or block implementation handoff
```

## Validation-only uncertain review

```md
Use $review-adjudication in Compact-Gated v4 mode.

Goal: decide whether a reviewer-reported failure mode is proven or should be
validated before code changes.

Rules:
- if the concern might be real but current artifacts do not prove it, use
  `need-evidence`
- use `proposed_fix_validity: validation-only`
- use `mutation_value: validation-material`
- state why validation would change accepted criticality, direction fit, merge
  safety, invariant handoff, or implementation scope
- route validation-only work to $fixed-point-driver
- set `implementation_handoff_allowed: no` unless some separate `act` item is artifact-backed
- do not implement the proposed fix unless validation fails or current artifacts
  already prove the failure
```

## Anti-laundering resolve selection

```md
Use $review-adjudication in Compact-Gated v4 mode.

Goal: refine these PR review comments to the subset that is actually worth
resolving before implementation, validation, or thread cleanup.

Rules:
- preserve raw comment identity and input inventory
- emit exactly one Resolve Selection row per ledger row
- include `proof ref` and `route rationale` for every Resolve Selection row
- run a Resolve Countercases pass that challenges the selected downstream route
- use `address` only for artifact-backed, direction-aligned `act` rows with
  implementation-grade accepted criticality
- use `validate-only` only for proof-first uncertainty with validation-material value
- use `resolve-thread-only` only for stale/already-fixed/review-closure-only
  comments with concrete proof
- use `do-not-address` for preserved no-change, preference-only, out-of-scope,
  direction-conflicting, review-closure-only, or low-value rows
- make Handoff Agenda buckets exactly match Resolve Selection decisions
- if every row is `address` or `validate-only`, emit structured All-Selected Justification
- do not route narrow-local work to $fixed-point-driver without coupled/invariant/structural/contentious/likely-to-reopen rationale
```
