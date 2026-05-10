# Plan: Specialist Packet Reliability Contract

## Summary

Implement the specialist packet reliability plan that came from the recent `$seq`, `$grill-me`, and `$plan` sequence. The governing invariant is that specialist outputs are accepted only when they are scoped, evidence-bearing, current for the active artifact state, and packet-native; stale, malformed, wrapper-leaking, acknowledgement-only, or low-value outputs must be rejected or closed without blocking local proof.

## Implementation

- step=create shared specialist packet contract; owner=implementer; success_criteria=`codex/skills/references/specialist-packet-contract.md` defines required fields, evidence floor, stale handling, rejection classes, value receipts, wait/progress bounds, and root-owned proof authority.
- step=patch fixed-point and closure skills; owner=implementer; success_criteria=`fixed-point-driver` and `verification-closure` reference the shared contract and preserve artifact-state, value-receipt, negative-evidence, and root-owned proof gates.
- step=patch specialist-spawning skills; owner=implementer; success_criteria=`codebase-audit`, `codebase-archaeology`, `spec-pipeline`, `review-adjudication`, and `negative-ledger` require packet-native, scoped, evidence-bearing Codex-native specialist outputs where they spawn or consume specialists.
- step=run fixed-point review and one-change challenge; owner=implementer; success_criteria=no material contract gaps remain across all touched skill surfaces and no stale or malformed packet path can be treated as closure evidence.
- step=validate skill docs and corpus; owner=implementer; success_criteria=quick validation for every touched skill, relevant corpus validation if available, `$st` projection checks, and `git diff --check` pass.
- step=run full local proof bundle; owner=implementer; success_criteria=all available builds, lints, and tests for this repo change set pass or any unavailable lane has an exact blocker.
- step=ship validated change set; owner=implementer; success_criteria=`$ship` opens or updates a PR with concise validation proof and reports exact status without merging.

## Locked Decisions

- Scope all five failure modes: capacity saturation, late or missing packets, malformed transport/wrapper leakage, low-value acknowledgements, and timebox races where useful packets arrive too late.
- Optimize for more useful packets over minimum latency, but make waits progress-bound rather than indefinite.
- Use skill-contract hardening only; do not add new runtime tooling.
- Require at least one artifact reference for an accepted specialist packet.
- Keep the contract shared and reference it from Codex-native specialist skills instead of duplicating a divergent local schema in each skill.
- Treat root-owned local verification as authoritative; specialist packets are routing and risk signals, not final proof.

## Validation

- `uv run --with pyyaml -- python3 codex/skills/.system/skill-creator/scripts/quick_validate.py <touched-skill>`
- `uv run --with pyyaml -- python3 codex/skills/.system/validators/validate_skill_corpus.py codex/skills`
- `st doctor --file .step/st-plan.jsonl`
- `st prime --file .step/st-plan.jsonl`
- `st assert-projection --file .step/st-plan.jsonl`
- `git diff --check`
