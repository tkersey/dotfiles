# Companion Skill Ledger

The Companion Skill Ledger makes named stage use auditable instead of implicit.

## Shape

```md
| Companion | Status | Evidence |
|---|---|---|
| `review-adjudication` | used / not-needed / root-equivalent / unavailable | one phrase |
| `accretive-implementer` | used / root-equivalent / not-needed / unavailable | one phrase |
| `adversarial-reviewer` | used / root-equivalent / not-needed / unavailable | one phrase |
| `verification-closure` | used / root-equivalent / not-needed / unavailable | one phrase |
| `negative-ledger` | queried / mapped / captured / handoff / no-applicable-evidence / unavailable | one phrase |
| `learnings` | recalled / captured / not-material / unavailable | one phrase |
```

## Status rules

- `used`: explicit invocation, output packet, or contract-shaped section exists.
- `root-equivalent`: root performed the skill doctrine without a distinct auditable invocation.
- `not-needed`: task shape did not require the stage; include the reason.
- `unavailable`: registry/path/tooling was unavailable; include the exact reason.
- `queried`, `mapped`, `captured`, `handoff`: negative-ledger modes that count as visible use.
- `no-applicable-evidence`: a root-owned Negative Ledger Pass ran and found no active applicable evidence.
- `not-material`: learnings capture or durable writeback was considered but did not pass the quality gate.

## Negative-ledger special rule

Do not mark `negative-ledger` as `root-equivalent`. Use the concrete status:
- `queried`
- `mapped`
- `captured`
- `handoff`
- `no-applicable-evidence`
- `unavailable`

This keeps future `$seq` audits from collapsing routine negative-evidence handling into invisible doctrine.
