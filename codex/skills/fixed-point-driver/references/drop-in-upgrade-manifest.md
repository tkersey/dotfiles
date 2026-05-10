# Fixed-Point Driver Negative-Ledger Upgrade Manifest

This drop-in replacement implements the requested fixed-point-driver changes.

## Main intent

- Make `negative-ledger` routine/default-on for non-trivial fixed-point runs.
- Preserve proof-gated fixed-point closure.
- Reduce unnecessary specialist fanout through lanes and budget exceptions.
- Make companion skill usage auditable.
- Add value receipts for every specialist packet.
- Add negative-evidence closure gates so repeated failed routes cannot silently pass closure.

## Files included

- `codex/skills/fixed-point-driver/SKILL.md`
- `codex/skills/fixed-point-driver/references/common-ledgers.md`
- `codex/skills/fixed-point-driver/references/closure-handoff-contract.md`
- `codex/skills/fixed-point-driver/references/closure-handoff-template.md`
- `codex/skills/fixed-point-driver/references/one-change-challenge.md`
- `codex/skills/fixed-point-driver/references/negative-ledger-pass.md`
- `codex/skills/fixed-point-driver/references/lane-and-specialist-budget.md`
- `codex/skills/fixed-point-driver/references/companion-skill-ledger.md`
- `codex/skills/fixed-point-driver/references/specialist-value-receipt.md`
- `codex/skills/negative-ledger/references/fixed-point-integration.md`
- `codex/skills/verification-closure/SKILL.md`
- `codex/skills/verification-closure/references/closure-handoff-contract.md`
- `codex/skills/verification-closure/references/closure-gates.md`
- `codex/skills/verification-closure/references/specialist-briefing-intake.md`

## Install

From repo root:

```bash
unzip fixed-point-driver-negative-ledger-dropin.zip
git diff -- codex/skills/fixed-point-driver codex/skills/negative-ledger/references/fixed-point-integration.md codex/skills/verification-closure
```

## Expected audit improvements

Future `$seq` audits should be able to measure:

- negative-ledger pass count by phase and mode
- no-applicable-negative-evidence count
- active exclusions and reopened negative evidence
- companion skill status distribution
- specialist count by lane
- budget exceptions
- specialist value-positive rate
- negative-ledger-mapper value-positive rate
- negative evidence closure gate outcomes
