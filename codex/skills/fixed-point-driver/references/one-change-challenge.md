# One-change challenge

Run this challenge after a candidate material fixed point and before every final closure attempt.

Prompt:
> If you could change one thing about this changeset, what would you change?

## Rules
- seek the single highest-leverage remaining change
- check the Negative Evidence Ledger before selecting a change; if needed, run `$negative-ledger` query/map first
- prefer impactful accretive improvements
- if the best remaining move is structural, say why a narrower fix is insufficient
- if the selected move matches active negative evidence, either choose a different move or show that reopening criteria are now satisfied
- if a `learnings` hit suggests the move failed before, treat it as candidate evidence until current-state applicability is established
- if there is no impactful remaining change, record `no-impactful-change`
- after any implemented one-change improvement, rerun full de novo review before closure

## Ledger fields
- `challenge_result`
- `selected_change`
- `why_now`
- `why_not_the_next_alternative`
- `posture`
- `verification_needed`
- `negative_evidence_checked`
- `matched_negative_ids`
- `learning_source_ids`
- `reopening_criteria_satisfied`
