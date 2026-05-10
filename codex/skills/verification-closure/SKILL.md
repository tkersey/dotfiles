---
name: verification-closure
description: Use this skill to decide whether the current artifact set is actually ready by consuming a canonical Closure Handoff Packet, running the narrowest decisive checks, validating specialist value receipts, checking active negative evidence and reopening criteria, and assigning a grounded readiness state. Trigger for requests like verify this patch is ready, run closure gates, decide if the branch reached a material fixed point, or close the loop on the current artifact state. Do not trigger for broad redesign or de novo code review without a closure question.
---

# Verification Closure

Use this for **proof and gating**, not for broad redesign or first-pass review.

## Output modes
- **Standard**: full gate ledger.
- **Fast**: highest-value gates, negative-evidence closure state, readiness, and reopen trigger only.

## CLI-tail-weighted reporting
- Keep evidence inputs and ledgers terse.
- Put the highest open gate in **Reopen Trigger**.
- End with **Closure Bottom Line**.

## Global doctrine
Operate in **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **TRACEABLE**, **MATERIAL**, **FIXED-POINT**, **CANONICAL**, **LEDGER-AWARE**, **NEGATIVE-EVIDENCE-AWARE**, and **REOPENABLE** mode.

## Gate discipline

- Treat reviewer and specialist outputs as signals, not proof.
- Treat unresolved **material soundness** as a hard closure gate.
- Treat unresolved critical invariants, material foot-guns, and material complexity hazards as closure gates.
- Treat active, applicable negative evidence as a closure gate when the current route repeats a disconfirmed path without satisfying reopening criteria.
- Treat `learnings` hits as candidate evidence until witness and current-state applicability are checked.
- If evidence conflicts, run the narrowest resolving check.
- If negative-ledger or learnings tooling is unavailable, decide whether the missing source is material to closure; report `blocked` or `unavailable` rather than silently ignoring it.

## Handoff intake

Start by validating the Closure Handoff Packet.

Assign `Handoff Contract Status` as:
- `complete`
- `incomplete`
- `stale`

A complete packet includes:
- Artifact State ID
- Companion Skill Ledger
- Routing and Budget Ledger
- Verification Ledger
- Negative Ledger Pass
- Negative Evidence Ledger
- Negative Ledger Handoff
- Specialist Briefing Ledger
- Specialist Value Receipts
- Closure Gate Preview
- Requested Closure Questions

If the packet is stale or incomplete, say so before evaluating readiness. If the missing part is not material, closure may proceed with a stated limitation; otherwise mark readiness not-ready or conditionally ready.

## Specialist value intake

Validate every specialist packet and value receipt:
- packet status is recorded
- artifact state ID matches or packet is marked stale/superseded
- scope matches or packet is marked wrong-scope
- value receipt exists for accepted and rejected packets
- `value: positive` is justified by route change, finding addition, proof change, or risk retirement

Do not let specialist value receipts become proof. Use them to decide which signals shaped the route and which gates still require root-owned evidence.

## Negative evidence closure gate

Always evaluate:

```yaml
negative_evidence_closure_gate:
  status: satisfied | open | blocked | unavailable
  active_exclusions_count: 0
  repeated_failed_route_used: yes | no
  reopening_criteria_satisfied: yes | no | n/a
  learnings_hits_applicability_checked: yes | no | n/a
  reason: "..."
```

Status rules:
- `satisfied`: no active applicable negative evidence blocks the route, or reopening criteria are satisfied with proof.
- `open`: active applicable negative evidence conflicts with the current route and reopening criteria are not satisfied.
- `blocked`: relevant evidence exists but cannot be checked due to missing logs, inaccessible learnings, unavailable repo history, or incomplete handoff.
- `unavailable`: negative-ledger/learnings tooling is unavailable and no in-session evidence can check the relevant source; report the limitation.

Never call the artifact set `ready` while this gate is `open` or `blocked`.

## Output contract

### Standard

Use concise sections in this order:
- Handoff Contract Status
- Verification Target
- Evidence Inputs
- Companion and Budget Intake
- Specialist Value Intake
- Negative Evidence Closure Gate
- Closure Gate Ledger
- Evidence Run
- Results
- Residual Risks
- Fixed-Point Test
- Readiness
- Reopen Trigger
- Closure Bottom Line

### Fast

Use concise sections in this order:
- Handoff Contract Status
- Negative Evidence Closure Gate
- Closure Gate Ledger
- Readiness
- Reopen Trigger
- Closure Bottom Line

## Reopen Trigger

- Name the **single highest open gate**.
- Say whether it wants `validating-check-only`, `accretive-remediation`, `structural-remediation`, `negative-ledger-reopen`, or `negative-ledger-capture`.
- If there is no open gate, say `reopen: none`.

## Hard rules

- Never upgrade claims beyond the evidence.
- Never let passing checks stand in for unresolved material soundness.
- Never let passing checks stand in for an open active negative-evidence gate.
- Never call the artifact set `ready` while a hard closure gate remains open.
- Never use a `learnings` hit as an exclusion rule without checking evidence and current-state applicability.
- Never ignore an active negative evidence entry; mark it active, stale, superseded, reopened, accepted-risk, or not applicable.
- Never reopen the loop without naming the exact gate and narrowest next move.
- Never treat specialist value receipts as proof commands or pass/fail verdicts.

## Resources
- [closure-gates.md](references/closure-gates.md)
- [handoff-intake-checklist.md](references/handoff-intake-checklist.md)
- [specialist-briefing-intake.md](references/specialist-briefing-intake.md)
- [closure-handoff-contract.md](references/closure-handoff-contract.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](references/common-soundness.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
