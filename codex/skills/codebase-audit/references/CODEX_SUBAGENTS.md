# Specialist Workers for Codebase Audit

Use the version-neutral worker model in `../../references/codex-specialist-worker-model.md`. Do not depend on one runtime's subagent invocation syntax or install path.

## Repository worker definitions

This dotfiles repo stores reusable audit worker TOML files under `codex/agents/`:

| Domain | Worker |
|---|---|
| security | `audit_security` |
| ux | `audit_ux` |
| performance | `audit_performance` |
| api | `audit_api` |
| copy | `audit_copy` |
| cli | `audit_cli` |

The active Codex runtime or local dotfiles setup decides how those TOML files become invokable.

## Parallel audit prompt shape

```text
Use $codebase-audit with specialist workers when supported. Run one read-only worker per requested domain, assign artifact_state_id and exact scope, require packet-native evidence-bearing outputs, then synthesize a prioritized report from valid packets and file:line evidence. If a named worker is unavailable, perform that domain lane in the root and state the fallback.
```

## Parent synthesis rules

The parent/root should launch independent domain lanes before waiting, keep workers read-only, assign `artifact_state_id`, validate against `../../references/specialist-packet-contract.md`, close stale or low-value workers, de-duplicate findings, normalize severity, preserve uncertainty under `Needs Verification`, and return a final report rather than raw transcripts.
