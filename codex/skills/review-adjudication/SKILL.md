---
name: review-adjudication
description: >-
  Discriminately adjudicate PR review comments before implementation. Treat each
  comment as a claim to test, preserve raw comment identity, build the strongest
  no-change countercase, separate valid concerns from valid proposed fixes,
  recover PR rationale with explicit `$seq` when needed, and emit a gated ledger
  that decides what to act on, rebut, defer, or investigate. Trigger for
  `$review-adjudication`, review the review, adjudicate PR comments, are these
  comments relevant, which comments matter, should we act on these comments, or
  gate review comments before implementation. Not for implementing fixes,
  writing rebuttals only, or final merge closure.
---

# Review Adjudication

## Intent

Decide which PR review comments should change code, which should be rebutted,
which are stale or out of scope, which require validation only, and which should
be reframed as a governing invariant instead of handled as isolated local fixes.

This skill is **discriminative**, not deferential. A reviewer comment is an input
claim, not an obligation. `act` is a conclusion that must be earned from current
artifact evidence.

## Default mode

Use **Compact-Gated** mode whenever the input contains real review comments.
Compact-Gated mode is mandatory because automation needs stable identity,
complete disposition coverage, and an explicit handoff gate.

Other modes are allowed only when they still satisfy the completion gate:

- **Standard**: expanded reasoning plus the full Compact-Gated tail.
- **Fast**: bucket-only output plus the completion gate; allowed for exploratory
  triage or synthetic comments, not for implementation handoff unless the gate
  passes.

## Doctrine

Operate in **DISCRIMINATIVE**, **REBUTTAL-FIRST**, **INVARIANT-SEEKING**,
**ANTI-RUBBER-STAMP**, **EVIDENCE-WEIGHTED**, and **FAIL-CLOSED** mode.

- **DISCRIMINATIVE**: separate true concerns from irrelevant, stale,
  unsupported, preference-only, misdiagnosed, or misframed comments.
- **REBUTTAL-FIRST**: for each comment, construct the strongest no-change
  countercase before deciding to act.
- **INVARIANT-SEEKING**: look for the governing invariant behind repeated local
  comments; avoid fixing the same invariant piecemeal.
- **ANTI-RUBBER-STAMP**: do not let plausibility, politeness, reviewer authority,
  or ease of implementation become acceptance evidence.
- **EVIDENCE-WEIGHTED**: rank current artifacts above memories, memories above
  intuition, and direct proof above consensus.
- **FAIL-CLOSED**: if the adjudication contract is incomplete, block
  implementation handoff rather than guessing.

## Contract

- Review comments are claims to test, not truths to obey.
- `act` is a conclusion, not the default.
- Current artifact state outranks reviewer intuition.
- Prefer current-session artifacts over memories.
- Use memories as secondary rationale support and provenance, not as the sole
  basis for acting.
- Distinguish concern validity from proposed-fix validity.
- Separate relevance from actionability.
- Preserve raw comment identity; do not let summaries replace comment IDs,
  reviewers, excerpts, or locations.
- Tail-weight outputs for CLI use.
- Do not implement fixes here.
- Do not create an implementation handoff unless the Adjudication Gate passes.

## Dependency

This skill expects `$seq` to be installed when PR rationale recovery is needed.
If `$seq` is unavailable, proceed only from current artifacts and mark PR
rationale fields as `unknown` instead of inventing intent.

## Specialist mode

For large or disputed comment sets, optionally use these read-only specialists
before final adjudication:

- `evidence_mapper`
- `soundness_auditor`
- `hazard_hunter`

Use them only to sharpen grounding, soundness, or hazard questions. They do not
replace the adjudication judgment.

When specialists are used, assign the current artifact state and exact comment
or file scope, then require the shared packet contract at
`../references/specialist-packet-contract.md`. Consume only
packet-native, scoped, evidence-bearing, current packets. Reject stale,
wrong-scope, wrapper-leaking, acknowledgement-only, or no-evidence packets and
keep them out of `act`/`rebut`/`defer` decisions.

## Required input context

When possible, build a compact context pack before adjudication:

```md
Review comments:
- raw id/thread
- reviewer
- file/location
- exact excerpt
- reviewer-suggested fix, if any

Current artifacts:
- branch/diff summary
- touched files
- relevant tests
- CI/local proof status
- PR description or stated goal

Constraints:
- intended change
- non-goals
- compatibility posture
- proof bar
```

Do not feed the whole repository by default. Add more context only when current
artifacts cannot decide grounding, scope, freshness, or intent.

## `$seq` rationale recovery

Use `$seq` when the PR why is missing, disputed, stale, or likely to change
adjudication.

Preferred ladder:

1. `plan-search`
2. `artifact-search`
3. `find-session` + `session-prompts`
4. `memory-map`
5. `memory-provenance`
6. `memory-history`

Use `$seq` to recover rationale, not to manufacture obligations. A recovered
plan can explain why a comment matters, but current artifacts still decide
whether the comment is grounded, stale, or in scope.

## Evidence ranking

1. Current diff, code, tests, CI, and local artifact state
2. Current-session artifact evidence
3. Prior-session artifact evidence
4. Memory-derived evidence
5. Reviewer intuition without artifact support

## PR Why Ledger

Summarize recovered rationale in compact fields:

- `intended_change`
- `explicit_constraints`
- `non_goals`
- `governing_invariants`
- `evidence_source`
- `rationale_freshness`
- `staleness_source`
- `confidence`

If the PR why is unavailable and it materially affects adjudication, mark the
affected comments `need-evidence` rather than acting from invented intent.

## Comment identity

Preserve raw review-comment identity. For every comment, carry:

- `comment_id` or `id/thread`
- `reviewer`
- `short_excerpt`
- `file_or_thread` / `location`
- `claim`
- `concern_validity`
- `proposed_fix_validity`
- `relevance_class`
- `disposition`
- `no_change_countercase_status`
- `governing_invariant`
- `evidence_basis`
- `reply_stance`
- `handoff_action`

If the source input lacks comment identity, record the identity gap and set
`identity_coverage: fail` in the Adjudication Gate. Do not silently synthesize
stable IDs for real PR comments.

## Required checks per comment

For every comment, assess:

1. grounding
2. materiality
3. freshness
4. diagnosis quality
5. scope fit
6. concern validity
7. proposed-fix validity
8. remediation posture
9. strongest no-change countercase
10. no-change countercase status
11. governing invariant, if any
12. minimum evidence to change mind
13. evidence basis
14. handoff action

## Act validity rule

A comment may be marked `act` only if all are true:

1. Current artifacts ground the concern.
2. The concern is material, or the user explicitly wants the nonmaterial change.
3. The strongest no-change countercase is defeated.
4. The proposed fix is valid, or the chosen handoff replaces it with a valid fix
   shape.
5. The action fits this PR's scope, constraints, and intended change.

If any item fails, do not use `act`; use `rebut`, `defer`, or `need-evidence`.
`act` requires proof, not plausibility.

## Rebuttal-first pass

Before marking a comment `act`, write the strongest plausible no-change
countercase.

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

Only mark `act` when artifact evidence defeats the no-change countercase. If the
countercase is not defeated, use `rebut`, `defer`, or `need-evidence`.

## Validation-only escape hatch

Do not mutate code just because a concern might be real. When uncertainty is
material and a validating check is the correct next step, use:

```md
disposition: need-evidence
reframe_type: validation-only
remediation_posture: validating-check-only
handoff_action: route-to-fixed-point-driver
```

Validation-only handoff may create tests, probes, logs, or inspections. It must
not implement the reviewer's requested code change unless the validation fails or
current artifacts already prove the concern.

## Governing invariant pass

After individual adjudication, cluster comments that appear to point at the same
underlying invariant, source-of-truth rule, ownership boundary, soundness
obligation, or API contract.

When multiple comments share an invariant:

- do not treat them as unrelated local fixes
- name the governing invariant
- decide whether the correct handoff is an invariant-level change
- route to `$fixed-point-driver` when the comments are coupled, contentious,
  structural, or likely to reopen one another
- route to `$accretive-implementer` only when the invariant-level agenda is
  narrow, accretive, and locally reviewable

If no invariant cluster exists, say so explicitly and set `invariant_pass: pass`
only after checking.

## Relevance classes

Use exactly one per comment:

- `material-relevant`
- `relevant-nonmaterial`
- `partially-relevant`
- `stale-or-superseded`
- `unsupported`
- `out-of-scope`
- `preference-only`

## Concern validity values

Use exactly one per comment:

- `valid`
- `partial`
- `unsupported`
- `unknown`

## Proposed-fix validity values

Use exactly one per comment:

- `valid`
- `partially-valid`
- `wrong-fix`
- `overbroad`
- `under-specified`
- `not-applicable`
- `validation-only`

## Disposition values

Use exactly one per comment:

- `act`
- `rebut`
- `defer`
- `need-evidence`

## No-change countercase status

Use exactly one per comment:

- `defeated`
- `not-defeated`
- `unresolved`

## Reply stance

For each comment, optionally record a `Reply Stance` to help later handoff to
`$logophile`:

- `acknowledge-and-fix`
- `acknowledge-and-bound`
- `rebut-with-evidence`
- `defer-with-scope`
- `ask-for-evidence`

## Acceptance skew audit

Before finalizing, audit the distribution of dispositions.

If every substantive comment is marked `act`, treat that as a warning sign, not
a victory. Emit an **All-Action Justification** with specific checks:

- `stale/superseded check`
- `unsupported check`
- `preference-only check`
- `out-of-scope check`
- `misdiagnosis check`
- `proposed-fix validity check`
- `validation-only alternative`
- `shared-invariant check`

If this block is missing, generic, or unsupported by artifact evidence, set:

```md
handoff_allowed: no
Adjudication Bottom Line: Blocked: all-action adjudication lacks justification.
```

Do not require artificial disposition diversity. Require an all-action safety
proof.

## Adjudication completion gate

Before any implementation handoff, emit an `Adjudication Gate` block.

Required fields:

- `identity_coverage`: `pass` / `fail`
- `no_change_coverage`: `pass` / `fail`
- `disposition_coverage`: `pass` / `fail`
- `proposed_fix_separation`: `pass` / `fail`
- `evidence_coverage`: `pass` / `fail`
- `invariant_pass`: `pass` / `fail`
- `acceptance_skew_audit`: `pass` / `fail`
- `handoff_allowed`: `yes` / `no`

`handoff_allowed` may be `yes` only when all required fields pass and any
all-action adjudication includes a specific All-Action Justification.

If any required field fails, the bottom line must be:

```md
Blocked: incomplete adjudication. Do not implement yet.
```

Do not route to `$accretive-implementer` or `$fixed-point-driver` from an
incomplete adjudication.

## Output contract

### Compact-Gated

Use this mode for real PR comment sets:

```md
## Review Basis
## PR Why Ledger
## Comment Ledger
| id/thread | reviewer | location | claim | concern validity | proposed fix validity | relevance | disposition | no-change status | invariant | evidence | handoff |
|---|---|---|---|---|---|---|---|---|---|---|---|

## No-Change Countercases
## Governing Invariant Ledger
## Act On
## Rebut
## Defer / Out of Scope
## Need Evidence
## Invariant-Level Handoff
## Acceptance Skew Audit
## All-Action Justification
## Adjudication Gate
## Handoff Agenda
## Adjudication Bottom Line
```

Omit `All-Action Justification` only when at least one substantive comment is not
`act`; still include `Acceptance Skew Audit`.

### Standard

Standard output may include expanded per-comment analysis, but it must end with
the full Compact-Gated tail and Adjudication Gate.

### Fast

Fast output may compress reasoning into decision buckets, but it must still
preserve comment identity, include an Acceptance Skew Audit, and emit an
Adjudication Gate. If identity or no-change coverage is missing, Fast mode must
block handoff.

## Handoff rules

- Route to `$accretive-implementer` when the accepted agenda is narrow,
  accretive, and locally reviewable.
- Route to `$fixed-point-driver` when accepted comments are coupled, contentious,
  invariant-level, structural, validation-only, or likely to reopen one another.
- Route to `$logophile` only for drafting replies, naming, or wording.
- If the correct response is no code change, do not create an implementation
  handoff.
- If the Adjudication Gate fails, do not create an implementation handoff.

## Machine-check hook

When automation is available, run the optional checker against the adjudication
output before routing implementation:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md
```

A failed checker result means the adjudication is incomplete. Re-run adjudication
with the missing fields instead of implementing.

## Hard rules

- Do not turn adjudication into implementation.
- Do not treat memory artifacts as infallible.
- Do not force action on preference-only, stale, unsupported, or out-of-scope
  comments.
- Do not mark a comment `act` merely because it is easy to fix.
- Do not mark a comment `act` merely because the reviewer is probably right.
- Do not accept a local fix when the real issue is a governing invariant.
- Do not hide uncertainty; say exactly what evidence is missing.
- Do not allow `handoff_allowed: yes` if any gate field fails.

## Resources

- [seq-rationale-ladder.md](references/seq-rationale-ladder.md)
- [adjudication-ledger.md](references/adjudication-ledger.md)
- [criticality-rubric.md](references/criticality-rubric.md)
- [adjudication-gate-contract.md](references/adjudication-gate-contract.md)
- [adjudication-output-template.md](references/adjudication-output-template.md)
- [context-pack.md](references/context-pack.md)
- [example-invocations.md](references/example-invocations.md)
- [common-routing-vocabulary.md](references/common-routing-vocabulary.md)
- [adversarial-eval-seeds.md](references/adversarial-eval-seeds.md)
