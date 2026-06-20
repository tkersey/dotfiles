# Fixed-Point Driver Integration

Use `$negative-ledger` as a routine companion for non-trivial fixed-point campaigns.

## Preflight

1. Establish `artifact_state_id`.
2. Run `ledger doctor` when store integrity matters.
3. Run root-owned `ledger map` before route selection.
4. Carry active, stale, reopened, superseded, and accepted-risk evidence into the campaign.
5. Convert active entries into narrow exclusion cards.
6. Convert stale/reopened entries into proof prompts.

## During the Loop

- Before a one-change challenge, check the candidate route against active ledger evidence.
- Fuzzy overlap may suggest investigation but cannot block.
- After witnessed failure, regression, revert, no-effect result, or proof-wound recurrence, run the ledger capture decision.
- Use `ledger status` when current artifact changes invalidate or reopen old evidence.

## Memory Admission

After canonical capture or lifecycle transition, run `ledger export --id NEG-* --format memory-note`, apply the negative-ledger memory admission gate, and append with `memory-note` only when the record has future cross-run value.

Memory admission is not required for campaign correctness and must not block closure when the canonical ledger is valid.
