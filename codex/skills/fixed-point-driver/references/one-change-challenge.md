# One-change challenge

Run this challenge after a candidate material fixed point and before every final closure attempt.

Also run it before escalating from `direct-closure` or `targeted` into a broader specialist lane when the only reason for escalation is uncertainty about whether one more change might matter.

Prompt:
> If you could change one thing about this changeset, what would you change?

## Rules

- Seek the single highest-leverage remaining change.
- Check the Negative Evidence Ledger before selecting a change.
- For non-trivial fixed-point runs, use the pre-closure Negative Ledger Handoff; if it is missing, run `$negative-ledger` query/map/handoff first.
- Prefer impactful accretive improvements.
- If the best remaining move is structural, say why a narrower fix is insufficient.
- If the selected move matches active negative evidence, either choose a different move or show that reopening criteria are now satisfied.
- If a `learnings` hit suggests the move failed before, treat it as candidate evidence until current-state applicability is established.
- If there is no impactful remaining change, record `no-impactful-change`.
- If the challenge produces no material candidate and proof lanes are obvious, do not fan out.
- If the challenge identifies one bounded uncertainty, prefer one specialist over a swarm.
- If the challenge identifies multiple independent uncertainty classes, reclassify to `expanded-targeted`.
- After any implemented one-change improvement, rerun full de novo review before closure.

## Ledger fields

```yaml
one_change_challenge:
  challenge_result: apply | reject | defer | escalate-to-specialist | no-impactful-change
  selected_change: "..."
  candidate_extra_change: "..."
  materiality: material | non-material | unknown
  why_now: "..."
  why_not_the_next_alternative: "..."
  posture: validating-check-only | accretive-remediation | structural-remediation | none
  verification_needed: "..."
  proof_needed: "..."
  negative_ledger_checked: queried | mapped | handoff | no-applicable-evidence | unavailable
  matched_negative_ids: []
  learning_source_ids: []
  reopening_criteria_satisfied: yes | no | n/a
  decision: apply | reject | defer | escalate-to-specialist | no-impactful-change
  reason: "..."
```

## Negative-evidence interpretation

- `negative_ledger_checked: handoff` is the preferred pre-closure state.
- `negative_ledger_checked: no-applicable-evidence` is valid only when a root-owned Negative Ledger Pass actually ran.
- `negative_ledger_checked: unavailable` does not automatically block closure, but closure must report the evidence limit.
- `matched_negative_ids` with `reopening_criteria_satisfied: no` means the selected change is not eligible unless the user explicitly accepts the risk.
- Stale or superseded negative evidence should become a proof prompt, not an exclusion rule.

## Fanout suppression role

Use the challenge to reduce unnecessary specialists:
- If no material one-change candidate appears, do not add a specialist merely to certify absence.
- If the remaining question is pure proof selection, prefer a single `verification_auditor` or root-owned verification planning.
- If the remaining question is repeated-failure history, run root-owned negative-ledger query/map first; launch `negative-ledger-mapper` only when history mapping is read-heavy.
