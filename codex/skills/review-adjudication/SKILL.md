---
name: review-adjudication
description: "Adjudicate PR review comments for actual relevance before implementation. Treat each comment as a claim to test against the diff, code, tests, invariants, and recovered PR rationale. Use explicit `$seq` to recover the PR why from current sessions and memories when intent is unclear, disputed, or stale. Triggers: `$review-adjudication`, review the review, adjudicate PR comments, are these comments relevant, which comments matter, should we act on these comments. Not for implementing fixes, writing rebuttals only, or final merge closure."
---

# Review Adjudication

## Intent
Decide which review comments should change code, which should be rebutted, which are stale or out of scope, and what evidence is still missing before any implementation work begins.

## Contract
- Review comments are claims to test, not truths to obey.
- Current artifact state outranks reviewer intuition.
- PR rationale matters. When the why is unclear, disputed, stale, or only partially remembered, explicitly invoke `$seq` before adjudicating.
- Prefer current-session artifacts over memories. Use memories as secondary rationale support and provenance, not as the sole basis for acting.
- Materiality beats verbosity. Focus first on comments that change correctness, invariants, soundness, hazards, public contracts, tests, or meaningful complexity.
- Distinguish the validity of the concern from the validity of the proposed fix. A reviewer can be right about the risk and wrong about the remedy.
- Separate relevance from actionability. A comment can be relevant but non-material, partially relevant, or blocked on evidence.
- Tail-weight outputs for CLI use. Put the highest-value disposition and handoff at the end.
- Do not implement fixes unless the user explicitly asks. Produce a handoff agenda for `$accretive-implementer` or `$fixed-point-driver`.

## Use when
- The user wants to know which PR review comments actually matter.
- The user wants to review the review before changing code.
- The rationale or original plan behind a changeset is unclear and may affect whether a comment is valid.
- A PR has mixed comments spanning correctness, style, scope, abstraction, tests, and architecture.

## Not for
- Implementing accepted changes directly.
- Final readiness or merge closure.
- Pure wording polish of PR responses.
- Broad patch review when there are no review comments to adjudicate.

## Core doctrine
Operate in CLAIM-TESTING, RATIONALE-RECOVERING, MATERIALITY-FIRST, SOUNDNESS-AWARE, and TAIL-WEIGHTED mode.

### CLAIM-TESTING
- For each comment, ask what would have to be true for this comment to be correct.
- Test the comment against the current diff, code, tests, logs, invariants, and known rationale.
- Distinguish unsupported comments from comments with weak but real evidence.

### RATIONALE-RECOVERING
- Use `$seq` when the PR why is missing, disputed, or likely to change the adjudication.
- Recover intent from current sessions first, then prior sessions, then memory artifacts.
- Treat recovered rationale as evidence with freshness and provenance, not as untouchable truth.

### MATERIALITY-FIRST
- Prioritize correctness, invariants, soundness, hazard reduction, and public-contract integrity above taste.
- Down-rank preference-only comments unless the surrounding repo conventions clearly make them binding.

### SOUNDNESS-AWARE
- Flag comments whose concern points at unwitnessed guarantees, illegal states, partial handlers, refinement leaks, or incoherent abstractions.
- Also flag comments that are themselves unsound, stale, or not actually derivable from the current artifact state.

### TAIL-WEIGHTED
- Keep dense evidence and ledgers above.
- End with a crisp disposition summary and the exact handoff agenda.

## Required checks for each comment
For every comment, assess:
1. Grounding: Is it supported by the diff, code, tests, logs, or recovered rationale?
2. Materiality: Does it matter for correctness, soundness, hazards, public contract, tests, or meaningful complexity?
3. Freshness: Is it current, stale, or superseded by later changes?
4. Diagnosis: Is the concern correct, partially correct, or misdiagnosed?
5. Scope fit: Is it in scope for this PR?
6. Remediation posture:
   - no-change
   - rebut
   - validating-check-only
   - accretive-remediation
   - structural-remediation
7. Minimum evidence to change mind: What additional check or artifact would overturn the current judgment?

## Relevance classes
Use exactly one per comment:
- material-relevant
- relevant-nonmaterial
- partially-relevant
- stale-or-superseded
- unsupported
- out-of-scope
- preference-only

## Workflow

### 1) Scope the adjudication
Capture:
- the current branch or changeset
- the review comments
- the affected files and tests
- any user-stated goal or constraints

### 2) Recover the PR why with `$seq` when needed
Use `$seq` when any of these are true:
- the original plan or intent is missing
- the user asks why a change exists
- a comment may be valid only under one intended scope
- memories or prior discussions might explain a now-surprising design choice
- the review may be stale relative to later changes

Preferred `$seq` ladder:
1. `plan-search` for finalized plan artifacts and explicit plan blocks.
2. `artifact-search` for broad artifact forensics when you need rationale but do not yet know the exact artifact.
3. `find-session` + `session-prompts` when you need the exact prompts or decisions from a session.
4. `memory-map` for broad topic routing.
5. `memory-provenance` for why a memory exists now.
6. `memory-history` for how a memory thread changed over time.

Memory routing defaults:
- Use `memory_summary.md` first for broad navigational recall.
- Use `MEMORY.md` first for durable guidance, reusable decisions, or task-family history.
- Prefer session-backed evidence over memory-only recall when the question is specifically about this PR.

If `$seq` is unavailable, say so explicitly and continue with current-session evidence only. Do not pretend the rationale was recovered.

### 3) Build a PR Why Ledger
Summarize the recovered rationale in compact fields:
- intended change
- explicit constraints
- evidence source
- freshness
- confidence

### 4) Adjudicate each comment
For each comment, produce:
- comment id
- relevance class
- disposition
- grounding
- rationale match
- diagnosis quality
- materiality
- remediation posture
- minimum evidence to change mind

### 5) Produce the handoff agenda
If accepted comments are independent or narrowly scoped, prepare an `$accretive-implementer` agenda.
If accepted comments are coupled, cross-cutting, or likely to reopen one another, prepare a `$fixed-point-driver` agenda instead.

### 6) Tail-weight the output
End with the high-value surface in this exact order:
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Handoff Agenda
- Adjudication Bottom Line

## Output shape

### Standard
- Review Basis
- PR Why Ledger
- Comment Ledger

Then end with:
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Handoff Agenda
- Adjudication Bottom Line

### Fast
Use when the user wants only the actionable result:
- Act On
- Rebut
- Defer / Out of Scope
- Need Evidence
- Handoff Agenda
- Adjudication Bottom Line

## Handoff rules
- Route to `$accretive-implementer` when the accepted agenda is narrow, accretive, and locally reviewable.
- Route to `$fixed-point-driver` when accepted comments are numerous, coupled, materially contentious, or likely to require repeated re-review.
- If the right answer is to do nothing, say that directly.

## Refusal-to-drift rules
- Do not turn adjudication into implementation.
- Do not treat memory artifacts as infallible.
- Do not over-weight reviewer confidence.
- Do not force action on preference-only or stale comments.
- Do not hide uncertainty; say exactly what evidence is missing.
