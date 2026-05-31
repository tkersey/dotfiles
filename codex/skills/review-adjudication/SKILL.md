---
name: review-adjudication
description: "Adjudicate PR/review comments before implementation. Treat each comment as a claim to test, recover PR rationale with $seq when needed, separate true concern from valid proposed fix, and classify act/rebut/defer/need-evidence/validate-only/proof-only/blocked. Trigger for review comments, reviewer suggestions, disputed feedback, or 'should we act on this?' before code changes."
---

# Review Adjudication

This skill decides which review comments deserve action. It is deliberately more critical than a claim validator: review comments are inputs to test, not orders to obey.

## Dependency
This skill expects `$seq` to be installed when PR rationale recovery is needed. If `$seq` is unavailable, proceed only from current artifacts and mark PR rationale fields as `unknown` instead of inventing intent.

## Doctrine
Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **ANTI-RUBBER-STAMP**, **INVARIANT-SEEKING**, **EVIDENCE-WEIGHTED**, **SCOPE-AWARE**, **STALE-PROOF**, and **RESOLVE-SELECTION** mode.

- **REBUTTAL-FIRST**: for every substantive comment, construct the strongest no-change case before accepting action.
- **ANTI-RUBBER-STAMP**: all-action outcomes are suspicious until justified.
- **INVARIANT-SEEKING**: repeated local comments may be one governing invariant.
- **EVIDENCE-WEIGHTED**: current artifacts beat reviewer authority, memory, and plausible prose.

## Doctrine alpha adjudication

This skill extracts value by refusing to treat locally valid review comments as automatically correct implementation tasks.

For each substantive comment or finding:

1. Decide whether it is a true concern.
2. Decide whether the proposed fix is valid.
3. Decide whether mutation is approved.
4. Decide whether the comment is actually a counterexample to a broader governing invariant.
5. Decide whether the correct handoff is implementation, validation-only, proof-only reply/thread resolution, no-change, blocked, or fixed-point-driver.

### Governing invariant promotion

When two or more comments touch the same state, representation, ownership boundary, proof surface, or validation path, emit a **Governing Invariant Candidate**:

```text
comment_ids:
local concerns:
governing invariant:
canonical owner:
selected resolution: local fixes | owner-level rewrite | validation-only | rebuttal/no-change | blocked
why local fixes are insufficient or sufficient:
```

Do not send a pile of locally valid comments to implementation when one owner-level rewrite is the real fix.

## $seq rationale ladder
Use `$seq` only when PR “why” is missing, ambiguous, stale, or likely to change adjudication.

Preferred ladder:
1. current artifacts and PR comments
2. `$seq plan-search` or `$seq artifact-search`
3. `$seq find-session` + `$seq session-prompts`
4. `$seq memory-map`, `$seq memory-provenance`, `$seq memory-history`
5. memory summaries only as weak supporting context

Current artifacts outrank memory. Memories are helpful recall, not proof.

## Comment ledger schema
Preserve raw comment identity:

```yaml
comment_ledger:
  - comment_id: "..."
    reviewer: "..."
    short_excerpt: "..."
    file_or_thread: "..."
    raw_claim: "..."
    proposed_fix: "..."
    rationale_match: yes | no | unknown
    evidence_basis: "..."
    no_change_countercase: "..."
    no_change_countercase_status: defeated | not-defeated | unresolved
    disposition: material-relevant | relevant-nonmaterial | partially-relevant | stale-or-superseded | unsupported | out-of-scope | preference-only
    reply_stance: acknowledge-and-fix | validate-first | rebut | defer | ask-for-evidence | resolve-without-change | blocked
    handoff_action: act | validate-only | proof-only | no-change | fixed-point-driver | blocked
```

## Acceptance skew audit
If every substantive comment is marked `act`, treat that as a warning sign. Add an **All-Action Justification** explaining why no comment was unsupported, stale, out of scope, preference-only, misdiagnosed, better handled as validation-only, or part of a shared governing invariant.

## Output contract
Use tail-weighted sections:

1. Review Context
2. PR Why Ledger
3. Comment Ledger
4. Governing Invariant Candidates
5. Acceptance Skew Audit
6. Act On
7. Rebut
8. Defer / Out of Scope
9. Need Evidence
10. Handoff Agenda
11. Adjudication Bottom Line

`Adjudication Bottom Line` must be final and list exact next action.

## Resources
- [doctrine-alpha.md](references/doctrine-alpha.md)
- [tail-proof.md](references/tail-proof.md)
- [seq-rationale-ladder.md](references/seq-rationale-ladder.md)
- [adjudication-ledger.md](references/adjudication-ledger.md)
