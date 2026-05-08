# Example invocations

## Compact-Gated review adjudication

```md
Use $review-adjudication in Compact-Gated mode.

Goal: determine which current PR review comments should change code before any
implementation.

Inputs:
- raw PR review comments with id/thread/reviewer/location/excerpt
- current branch vs main
- PR description / intended change
- current tests and CI status
- relevant files

Rules:
- preserve raw comment identity
- treat each comment as a claim, not an obligation
- construct the strongest no-change countercase for every comment
- separate concern validity from proposed-fix validity
- use $seq only if PR rationale is missing, disputed, stale, or likely to affect disposition
- do not implement fixes
- do not hand off implementation unless the Adjudication Gate passes

Required output:
- Review Basis
- PR Why Ledger
- Comment Ledger
- No-Change Countercases
- Governing Invariant Ledger
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Adjudication Gate
- Handoff Agenda
- Adjudication Bottom Line

Failure condition:
If identity coverage, no-change coverage, proposed-fix separation, evidence
coverage, invariant pass, or skew audit is incomplete, set `handoff_allowed: no`.
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
- emit the Adjudication Gate

Done when:
- each comment is classified
- the bottom line says what to act on, rebut, defer, or investigate
- any governing invariant behind repeated comments is named
- the handoff agenda says whether this should go to $accretive-implementer or $fixed-point-driver
- `handoff_allowed` is explicit
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
- Comment Ledger
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Adjudication Gate
- Handoff Agenda
- Adjudication Bottom Line

Do not allow implementation handoff unless the gate passes.
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
- if every comment is accepted, justify why this is not rubber-stamping
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
- if all comments are `act`, emit All-Action Justification or block handoff
```

## Validation-only uncertain review

```md
Use $review-adjudication in Compact-Gated mode.

Goal: decide whether a reviewer-reported failure mode is proven or should be
validated before code changes.

Rules:
- if the concern might be real but current artifacts do not prove it, use
  `need-evidence`
- use `reframe_type: validation-only` and `remediation_posture: validating-check-only`
- route validation-only work to $fixed-point-driver
- do not implement the proposed fix unless validation fails or current artifacts
  already prove the failure
```
