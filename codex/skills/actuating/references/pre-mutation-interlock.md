# Actuating Pre-Mutation Interlock

## Purpose

This file replaces the old transaction-controller/APMA path with a simpler rule:
`$actuating` may not pretend it owns durable coordination that is no longer
available in this workspace.

The old APMA/claim/lease path is retired. Keep the `apma-v1.example.json` asset
only as a compatibility tombstone so older audits do not silently resolve to a
missing file.

## Current rule

Before a material change, `$actuating` must have one of:

```text
valid FUSION-v1 receipt for one simple direct action
current ALSR-v1 + HYL-v1 + HSR-v1 receipt chain
```

If the work needs durable claims, fencing, external worktrees, serialized
integration, or multi-plan coordination, the local workflow must stop.

```text
actuation verdict: blocked-unsupported-controller
```

## Why

The old failure shape was:

```text
plan pressure
-> local decomposition
-> patch attempts
-> retrospective control language
-> completion claim
```

The required shape is now:

```text
approved source
-> selected work item or safe frontier
-> material action
-> current evidence fold
-> terminal ATCG decision
```

## Unsupported authority path

Do not hand-author APMA-v1, claim ids, leases, coordination tokens, or serialized
integration receipts. If another tool later reintroduces real coordination, it
must come with its own validator and an explicit handoff contract.

## Direct implementation fallback

Direct implementation can be valid when no coordination is needed, but it must
not be presented as a fenced `$actuating` run. Use an explicit transition:

```text
$actuating blocked: unsupported durable coordination requirement.
Leaving $actuating before any direct implementation.
No actuation authority is claimed for subsequent edits.
```

## Falsifier

The interlock is working when future audits show:

```text
mutations_without_unfold = 0
continuations_without_fold = 0
completion_without_ATCG = 0
local edits claiming retired APMA authority = 0
```
