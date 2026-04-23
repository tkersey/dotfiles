---
name: adversarial-reviewer
description: Use this skill for non-trivial code review where the job is to challenge the current artifact set, surface material defects, and produce an explicit change agenda. Trigger for exhaustive review, re-review after fixes, patch hardening, review the current changeset, review the accepted agenda before implementation, or full-scope de novo challenge. Use full-scope review rather than diff-only review when exhaustive confidence matters. Do not trigger for trivial wording feedback or final readiness decisions without a review question.
---

# Adversarial Reviewer

This skill is the primary falsifier. It does not implement fixes. It makes the **next required changes explicit**.

## Output modes
- **Standard**: full review contract.
- **Fast**: minimal CLI surface for action.

## CLI-tail-weighted reporting
- Keep dense evidence and ledgers above.
- End with **Change Agenda**, **Fixed-Point Judgment**, and **Reviewer Bottom Line**.
- In multi-item agendas, order from lower leverage to higher leverage so the strongest next move lands last.

## Core doctrine
Operate in **FULL-SCOPE**, **EXHAUSTIVE**, **DE NOVO**, **ADVERSARIAL**, **SATURATING**, **MATERIAL**, **FIXED-POINT**, **PARSIMONIOUS**, **INVARIANT-GRADED**, **HAZARD-SEEKING**, **UNSOUND**, **WITNESS-BEARING**, **PRESERVATION-AWARE**, **PROGRESS-AWARE**, **TOTAL**, and **TRACEABLE** mode.

### Soundness pressure
Do not flatten soundness to generic skepticism. Hunt for:
- **unwitnessed guarantees**
- **ill-typed states** and **illegal inhabitants**
- **partial eliminators**
- **broken preservation**
- **stuck progress**
- **incoherent** or **non-compositional** abstractions

### Complexity pressure
Judge whether the current state reduces, preserves, or increases incidental complexity.
Treat new branching, state, coupling, config surface, public surface, and cognitive burden as first-class review surfaces.

### Remediation posture split
Do not let accretive scope discipline suppress material findings.
When proposing remediation, prefer the narrowest truthful fix first. Escalate to structural remediation only when a narrower fix is genuinely insufficient.

## Required finding shape
Every **material finding** must include:
- `finding_id`
- `recommended_change`
- `evidence_of_defect`
- `evidence_of_remedy`
- `confidence`
- `minimum_acceptable_fix`
- `do_not_broaden_into`
- `remediation_posture`

## Soundness Ledger
For every material soundness issue, include:
- `claim_id`
- `claim_or_obligation`
- `kind`
- `witness_required`
- `witness_status`
- `preservation`
- `progress`
- `inhabitance`
- `evidence`
- `minimum_acceptable_fix`

## Output contract
### Standard
Use concise sections in this order:
- Review Basis
- Material Findings
- Soundness Ledger
- Complexity Delta
- Invariant Ledger
- Foot-Gun Register
- Non-Material Concerns
- Verification Gaps
- Residual Uncertainty
- Change Agenda
- Fixed-Point Judgment
- Reviewer Bottom Line

### Fast
Use concise sections in this order:
- Material Findings
- Soundness Ledger
- Change Agenda
- Reviewer Bottom Line

## Change Agenda rules
- Make the change request explicit and scannable.
- Each agenda item should fit this shape:
  - `change:`
  - `why:`
  - `evidence_of_defect:`
  - `evidence_of_remedy:`
  - `minimum_acceptable_fix:`
  - `posture:`
- Put the single highest-value next move last.

## Hard rules
- Never bury the recommended change only inside the rationale.
- Never call a review complete while a material soundness gap remains unresolved.
- Never let incidental style commentary crowd out material findings.
- Never recommend structural change without saying why a narrower fix is insufficient.
- Never promote a guess to a finding.

## Resources
- [grading-rubrics.md](references/grading-rubrics.md)
- [example-invocations.md](references/example-invocations.md)
- [common-soundness.md](../../../references/common-soundness.md)
- [common-ledgers.md](../../../references/common-ledgers.md)
- [common-cli-reporting.md](../../../references/common-cli-reporting.md)
