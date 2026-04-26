---
name: review-adjudication
description: "Discriminately adjudicate PR review comments before implementation. Treat each comment as a claim to test, build the strongest no-change countercase, recover PR rationale with explicit `$seq` when needed, and decide what to act on, rebut, defer, or investigate. Trigger for `$review-adjudication`, review the review, adjudicate PR comments, are these comments relevant, which comments matter, or should we act on these comments. Not for implementing fixes, writing rebuttals only, or final merge closure."
---

# Review Adjudication

## Intent
Decide which PR review comments should change code, which should be rebutted, which are stale or out of scope, and which should be reframed as a governing invariant instead of handled as isolated local fixes.

This skill is **discriminative**, not deferential. A reviewer comment is an input claim, not an obligation.

## Output modes
- **Standard**: full adjudication contract.
- **Fast**: only decision buckets, invariant-level handoff, skew audit, and bottom line.

## Doctrine
Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **INVARIANT-SEEKING**, **ANTI-RUBBER-STAMP**, and **EVIDENCE-WEIGHTED** mode.

- **DISCRIMINATIVE**: separate true concerns from irrelevant, stale, unsupported, preference-only, or misframed comments.
- **REBUTTAL-FIRST**: for each comment, construct the strongest no-change countercase before deciding to act.
- **INVARIANT-SEEKING**: look for the governing invariant behind repeated local comments; avoid fixing the same invariant piecemeal.
- **ANTI-RUBBER-STAMP**: do not let plausibility, politeness, reviewer authority, or ease of implementation become acceptance evidence.
- **EVIDENCE-WEIGHTED**: rank current artifacts above memories, memories above intuition, and direct proof above consensus.

## Contract
- Review comments are claims to test, not truths to obey.
- `act` is a conclusion, not the default.
- Current artifact state outranks reviewer intuition.
- Prefer current-session artifacts over memories. Use memories as secondary rationale support and provenance, not as the sole basis for acting.
- Distinguish the validity of the concern from the validity of the proposed fix.
- Separate relevance from actionability.
- Preserve raw comment identity; do not let summaries replace comment IDs, reviewers, excerpts, or locations.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.

## Dependency
This skill expects `$seq` to be installed when PR rationale recovery is needed.
If `$seq` is unavailable, proceed only from current artifacts and mark PR rationale fields as `unknown` instead of inventing intent.

## Specialist mode
For large or disputed comment sets, optionally use these read-only specialists before final adjudication:
- `evidence_mapper`
- `soundness_auditor`
- `hazard_hunter`

Use them only to sharpen grounding, soundness, or hazard questions. They do not replace the adjudication judgment.

## `$seq` rationale recovery
Use `$seq` when the PR why is missing, disputed, stale, or likely to change adjudication.
Preferred ladder:
1. `plan-search`
2. `artifact-search`
3. `find-session` + `session-prompts`
4. `memory-map`
5. `memory-provenance`
6. `memory-history`

## Evidence ranking
1. Current diff, code, tests, CI, and local artifact state
2. Current-session artifact evidence
3. Prior-session artifact evidence
4. Memory-derived evidence
5. Reviewer intuition without artifact support

## PR Why Ledger
Summarize recovered rationale in compact fields:
- intended_change
- explicit_constraints
- non_goals
- governing_invariants
- evidence_source
- rationale_freshness
- staleness_source
- confidence

## Comment identity
Preserve raw review-comment identity. For every comment, carry:
- `comment_id`
- `reviewer`
- `short_excerpt`
- `file_or_thread`
- `disposition`
- `evidence_basis`
- `reply_stance`
- `handoff_action`

## Required checks per comment
For every comment, assess:
1. grounding
2. materiality
3. freshness
4. diagnosis
5. scope fit
6. proposed-fix validity
7. remediation posture
8. strongest no-change countercase
9. no-change countercase status
10. governing invariant, if any
11. minimum evidence to change mind

## Rebuttal-first pass
Before marking a comment `act`, write the strongest plausible no-change countercase.

A no-change countercase may be:
- the comment is unsupported by the current artifact state
- the comment is stale or superseded
- the comment is preference-only
- the comment is locally valid but out of scope for this PR
- the concern is valid but the proposed fix is wrong
- the requested local fix would hide the governing invariant
- the review asks for non-accretive broadening without proof
- the review assumes a contract this PR does not own
- the evidence is insufficient and the correct next step is validation only

Only mark `act` when artifact evidence defeats the no-change countercase.

If the countercase is not defeated, use `rebut`, `defer`, or `need-evidence`.

## Governing invariant pass
After individual adjudication, cluster comments that appear to point at the same underlying invariant, source-of-truth rule, ownership boundary, soundness obligation, or API contract.

When multiple comments share an invariant:
- do not treat them as unrelated local fixes
- name the governing invariant
- decide whether the correct handoff is an invariant-level change
- route to `$fixed-point-driver` when the comments are coupled or likely to reopen one another
- route to `$accretive-implementer` only when the invariant-level agenda is narrow and locally reviewable

## Relevance classes
Use exactly one per comment:
- material-relevant
- relevant-nonmaterial
- partially-relevant
- stale-or-superseded
- unsupported
- out-of-scope
- preference-only

## Disposition values
Use exactly one per comment:
- act
- rebut
- defer
- need-evidence

## No-change countercase status
Use exactly one per comment:
- defeated
- not-defeated
- unresolved

## Reply stance
For each comment, optionally record a `Reply Stance` to help later handoff to `$logophile`:
- acknowledge-and-fix
- acknowledge-and-bound
- rebut-with-evidence
- defer-with-scope
- ask-for-evidence

## Acceptance skew audit
Before finalizing, audit the distribution of dispositions.

If every substantive comment is marked `act`, treat that as a warning sign, not a victory. Add an **All-Action Justification** that explains why no comment was unsupported, stale, out of scope, preference-only, misdiagnosed, or better handled as validation-only.

If the review set has many locally valid comments, ask whether they share a governing invariant. Prefer one invariant-level handoff over many isolated local fixes when the same rule is recurring.

## Output contract

### Standard
- Review Basis
- PR Why Ledger
- Comment Ledger
- No-Change Countercases
- Governing Invariant Ledger
- Reply Stance Ledger
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Handoff Agenda
- Adjudication Bottom Line

### Fast
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Invariant-Level Handoff
- Acceptance Skew Audit
- Handoff Agenda
- Adjudication Bottom Line

## Handoff rules
- Route to `$accretive-implementer` when the accepted agenda is narrow, accretive, and locally reviewable.
- Route to `$fixed-point-driver` when accepted comments are coupled, contentious, invariant-level, or likely to reopen one another.
- Route to `$logophile` only for drafting replies, naming, or wording.
- If the correct response is no code change, do not create an implementation handoff.

## Hard rules
- Do not turn adjudication into implementation.
- Do not treat memory artifacts as infallible.
- Do not force action on preference-only, stale, unsupported, or out-of-scope comments.
- Do not mark a comment `act` merely because it is easy to fix.
- Do not mark a comment `act` merely because the reviewer is probably right.
- Do not accept a local fix when the real issue is a governing invariant.
- Do not hide uncertainty; say exactly what evidence is missing.

## Resources
- [seq-rationale-ladder.md](references/seq-rationale-ladder.md)
- [adjudication-ledger.md](references/adjudication-ledger.md)
- [criticality-rubric.md](references/criticality-rubric.md)
- [example-invocations.md](references/example-invocations.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
