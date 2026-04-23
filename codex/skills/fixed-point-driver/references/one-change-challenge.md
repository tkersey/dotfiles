# One-change challenge

Run this challenge after a candidate material fixed point and before every final closure attempt.

Prompt:
> If you could change one thing about this changeset, what would you change?

## Rules
- seek the single highest-leverage remaining change
- prefer impactful accretive improvements
- if the best remaining move is structural, say why a narrower fix is insufficient
- if there is no impactful remaining change, record `no-impactful-change`
- after any implemented one-change improvement, rerun full de novo review before closure

## Ledger fields
- `challenge_result`
- `selected_change`
- `why_now`
- `why_not_the_next_alternative`
- `posture`
- `verification_needed`
