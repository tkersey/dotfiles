# Dominant Move Brief Templates

Use one canonical brief shape based on final state.

## Dominant move

```text
# Dominant Move Brief

## Artifact State
- label:
- relevant surfaces:
- current evidence:
- constraints:

## Verdict
- state: dominant-move
- confidence:
- selected move:
- target lane:

## Why This Move Dominates
- governing reason:
- material axis:
- latent frame used:
- accretive payoff:

## Alternatives Rejected
- alternative:
  - why it loses:
  - what evidence could revive it:

## First Proof Signal
- check:
- expected result:
- failure would imply:
- executor needed:

## Minimum Viable Diff
- likely touched surfaces:
- smallest useful implementation:
- non-goals:
- reversibility:

## Risks and Assumptions
- known risks:
- assumptions:
- residual uncertainty:
- decision gates:

## Recommended Executor
- executor: fixed-point-driver | human | none | other
- why:
- handoff readiness: ready | partial | not-ready

## Do Next
- owner:
- action:
- why:
- state: dominant-move
```

Do not call this an execution result. A validated move is not a validated patch.

## No dominant move

```text
# Dominant Move Brief

## Verdict
- state: no-dominant-move
- confidence:

## Why No Candidate Dominates
- reason:
- closest contender:
- competing contender:
- unresolved tradeoff:

## What Would Break The Tie
- fastest discriminating check:
- expected decision unlocked:
- executor needed:

## Do Next
- owner:
- action:
- why:
- state: no-dominant-move
```

## Insufficient evidence

```text
# Dominant Move Brief

## Verdict
- state: needs-evidence
- confidence:

## Missing Evidence
- missing fact:
- why it matters:
- decision it controls:

## Fastest Discriminating Check
- check:
- expected outcomes:
- how each outcome routes:

## Do Next
- owner:
- action:
- why:
- state: needs-evidence
```

## Needs decision

```text
# Dominant Move Brief

## Verdict
- state: needs-decision
- confidence:

## Decision Required
- decision:
- options:
- tradeoff:
- why the skill cannot decide from repo evidence alone:

## Do Next
- owner: user
- action:
- why:
- state: needs-decision
```

## Blocked

```text
# Dominant Move Brief

## Verdict
- state: blocked
- confidence:

## Blocker
- blocker:
- missing access/tool/context:
- impact:

## Do Next
- owner:
- action:
- why:
- state: blocked
```

## Recommended executor rules

Recommend `fixed-point-driver` when the move touches correctness, safety, reliability, compatibility, security, or critical invariants; the implementation needs de novo adversarial review; the patch needs verification closure; the proof signal requires tests, traces, benchmarks, or multi-pass validation; or the user wants the artifact driven to readiness.

Recommend `human` when the next step is a product choice, the tradeoff is subjective or organizational, the executor needs authority outside code, or the change requires judgment about roadmap, API policy, or compatibility promises.

Recommend `none` when the final state is `no-dominant-move`, the next step is evidence gathering, or execution would be premature.

Never auto-invoke the executor from this skill.
