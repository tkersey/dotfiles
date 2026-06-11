# Companion Skill Ledger

The Companion Skill Ledger makes named stage use auditable instead of implicit.

```md
| Companion | Status | Evidence |
|---|---|---|
| `parse` | used / not-needed / unavailable / blocked | architecture fingerprint status; effect on owner graph or reason skipped |
| `review-adjudication` | used / not-needed / root-equivalent / unavailable | one phrase |
| `accretive-implementer` | used / root-equivalent / not-needed / unavailable | right_sized_route=<route>; surface_budget=<budget>; ablation_status=<status>; proof_required=<summary> |
| `adversarial-reviewer` | used / root-equivalent / not-needed / unavailable | one phrase |
| `verification-closure` | used / root-equivalent / not-needed / unavailable | one phrase |
| `negative-ledger` | queried / mapped / captured / handoff / no-applicable-evidence / unavailable | one phrase |
| `learnings` | recalled / captured / not-material / unavailable | one phrase |
| `simplify-refactor` | used / root-equivalent / not-needed / unavailable | one phrase |
```

`root-equivalent` means root performed the skill doctrine without a distinct auditable invocation.

Do not mark `negative-ledger` as `root-equivalent`; use its concrete status.

Do not mark `parse` as `root-equivalent`; the distinction that matters is whether a collector-backed architecture fingerprint was consumed.

## Accretive implementer row

When fixed-point routes mutation to `accretive-implementer`, the evidence cell must include these four fields:

```text
right_sized_route=
surface_budget=
ablation_status=
proof_required=
```

Allowed `right_sized_route` values:

```text
no-change | validate-only | delete-collapse-canonicalize | mutate-existing-owner | add-new-surface | routed | blocked
```

Allowed `surface_budget` values:

```text
zero_or_negative | bounded_positive | explicit_expansion | not-applicable | unknown
```

Allowed `ablation_status` values:

```text
not-required | local-preflight | external-clearance-required | blocked
```

If `surface_budget=unknown` or `ablation_status=blocked`, mutation through `accretive-implementer` is not ready.

A companion row is insufficient unless it is backed by an `implementation_handoff` packet or a root-equivalent handoff with the same fields. Use `accretive-implementer-handoff.md`.
