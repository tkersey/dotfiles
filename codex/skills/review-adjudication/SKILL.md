---
name: review-adjudication
description: "Adjudicate PR review comments for actual relevance before implementation. Treat each comment as a claim to test against the diff, code, tests, invariants, and recovered PR rationale. Use explicit `$seq` to recover the PR why from current sessions and memories when intent is unclear, disputed, or stale. Trigger for `$review-adjudication`, review the review, adjudicate PR comments, are these comments relevant, which comments matter, or should we act on these comments. Not for implementing fixes, writing rebuttals only, or final merge closure."
---

# Review Adjudication

## Intent
Decide which review comments should change code, which should be rebutted, which are stale or out of scope, and what evidence is still missing before implementation begins.

## Output modes
- **Standard**: full adjudication contract.
- **Fast**: only dispositions and handoff.

## Contract
- Review comments are claims to test, not truths to obey.
- Current artifact state outranks reviewer intuition.
- Prefer current-session artifacts over memories. Use memories as secondary rationale support and provenance, not as the sole basis for acting.
- Distinguish the validity of the concern from the validity of the proposed fix.
- Separate relevance from actionability.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.

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

## PR Why Ledger
Summarize recovered rationale in compact fields:
- intended_change
- explicit_constraints
- evidence_source
- rationale_freshness
- staleness_source
- confidence

## Required checks per comment
For every comment, assess:
1. grounding
2. materiality
3. freshness
4. diagnosis
5. scope fit
6. remediation posture
7. minimum evidence to change mind

## Relevance classes
Use exactly one per comment:
- material-relevant
- relevant-nonmaterial
- partially-relevant
- stale-or-superseded
- unsupported
- out-of-scope
- preference-only

## Reply stance
For each comment, optionally record a `Reply Stance` to help later handoff to `$logophile`:
- acknowledge-and-fix
- acknowledge-and-bound
- rebut-with-evidence
- defer-with-scope
- ask-for-evidence

## Output contract
### Standard
- Review Basis
- PR Why Ledger
- Comment Ledger
- Reply Stance Ledger
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Handoff Agenda
- Adjudication Bottom Line

### Fast
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Handoff Agenda
- Adjudication Bottom Line

## Handoff rules
- Route to `$accretive-implementer` when the accepted agenda is narrow and locally reviewable.
- Route to `$fixed-point-driver` when accepted comments are coupled, contentious, or likely to reopen one another.

## Hard rules
- Do not turn adjudication into implementation.
- Do not treat memory artifacts as infallible.
- Do not force action on preference-only or stale comments.
- Do not hide uncertainty; say exactly what evidence is missing.

## Resources
- [seq-rationale-ladder.md](references/seq-rationale-ladder.md)
- [adjudication-ledger.md](references/adjudication-ledger.md)
- [example-invocations.md](references/example-invocations.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
