# Negative Ledger resource digest

generated_at: <YYYY-MM-DDTHH-MM-SSZ>
source: <learnings query | negative-ledger handoff | fixed-point ledger | manual digest>
scope: <repo / path family / task family / workflow>

Use this file as a short-lived evidence packet for Codex memory consolidation. Copy it into:

```text
~/.codex/memories/extensions/negative-ledger/resources/YYYY-MM-DDTHH-MM-SS-negative-ledger-digest.md
```

Do not use this template filename inside `resources/`; real resource files should have a timestamp prefix.

## Promote

### <short route constraint title>

- learning_ids:
  - <lrn-...>
- repo: <owner/repo or local repo slug>
- paths:
  - <path or path-family>
- hypothesis: <narrow failed hypothesis>
- attempted_change: <concrete attempted implementation/decision/route>
- observed_outcome: <what happened>
- failure_class: <no-effect | local-regression | global-regression | unsound | too-complex | stale | unknown>
- evidence_anchor: <command, benchmark, test, revert, review, trace, diff, learning id, or ledger ref>
- applicability_conditions:
  - <condition under which the old failure still binds>
- exclusion_rule: <narrow rule; do not ban a broad strategy family>
- reopening_criteria:
  - <condition/proof required before retrying or suppressing the route differently>
- next_search_hint: <adjacent promising route or proof obligation>
- memory_target: <memory_summary | MEMORY | skill | none>
- confidence: <high | medium | low>

## Watchlist

### <candidate title>

- learning_ids:
  - <lrn-...>
- missing_evidence: <what witness/applicability/reopening detail is missing>
- why_not_promoted: <why this should not affect durable memory yet>
- confirmation_needed: <specific evidence that would make it promotable>
- possible_reopening_test: <optional test/check if stale or potentially reopened>

## Do not promote

- <learning id / signal>: <why it remains evidence-only, stale, too broad, already codified, or noise>
