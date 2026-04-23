---
name: verification-closure
description: Use this skill to decide whether the current artifact set is actually ready by consuming a canonical Closure Handoff Packet, running the narrowest decisive checks, and assigning a grounded readiness state. Trigger for requests like verify this patch is ready, run closure gates, decide if the branch reached a material fixed point, or close the loop on the current artifact state. Do not trigger for broad redesign or de novo code review without a closure question.
---

# Verification Closure

Use this for **proof and gating**, not for broad redesign or first-pass review.

## Output modes
- **Standard**: full gate ledger.
- **Fast**: highest-value gates, readiness, and reopen trigger only.

## CLI-tail-weighted reporting
- Keep evidence inputs and ledgers terse.
- Put the highest open gate in **Reopen Trigger**.
- End with **Closure Bottom Line**.

## Global doctrine
Operate in **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **REFINEMENT-AWARE**, **MECHANISTIC**, **TRACEABLE**, **MATERIAL**, **FIXED-POINT**, **CANONICAL**, and **LEDGER-AWARE** mode.

## Gate discipline
- Treat reviewer and specialist outputs as signals, not proof.
- Treat unresolved **material soundness** as a hard closure gate.
- Treat unresolved critical invariants, material foot-guns, and material complexity hazards as closure gates.
- If evidence conflicts, run the narrowest resolving check.

## Handoff intake
Start by validating the Closure Handoff Packet.
Assign `Handoff Contract Status` as:
- `complete`
- `incomplete`
- `stale`

If the packet is stale or incomplete, say so before evaluating readiness.

## Output contract
### Standard
Use concise sections in this order:
- Handoff Contract Status
- Verification Target
- Evidence Inputs
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
- Closure Gate Ledger
- Readiness
- Reopen Trigger
- Closure Bottom Line

## Reopen Trigger
- Name the **single highest open gate**.
- Say whether it wants `validating-check-only`, `accretive-remediation`, or `structural-remediation`.
- If there is no open gate, say `reopen: none`.

## Hard rules
- Never upgrade claims beyond the evidence.
- Never let passing checks stand in for unresolved material soundness.
- Never call the artifact set `ready` while a hard closure gate remains open.
- Never reopen the loop without naming the exact gate and narrowest next move.

## Resources
- [closure-gates.md](references/closure-gates.md)
- [handoff-intake-checklist.md](references/handoff-intake-checklist.md)
- [specialist-briefing-intake.md](references/specialist-briefing-intake.md)
- [closure-handoff-contract.md](references/closure-handoff-contract.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](references/common-soundness.md)
- [common-ledgers.md](references/common-ledgers.md)
- [common-cli-reporting.md](references/common-cli-reporting.md)
