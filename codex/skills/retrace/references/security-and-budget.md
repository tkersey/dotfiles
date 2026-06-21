# Security, Privacy, and Budget

## Default policy

```text
ephemeral forks
read-only permission profile
network disabled
approval requests denied
dynamic tools disabled unless explicitly needed
one turn per fork
bounded tokens and timeout
cleanup after receipt capture
```

## Sensitive context

Historical sessions may contain:

```text
credentials
private code
customer data
personal messages
tool outputs
paths and account information
```

Do not export raw transcripts to receipts.

Use refs, hashes, and bounded excerpts.

## Fork permissions

Prefer a named read-only profile.

Fail closed when the runtime cannot prove the effective permission profile.

Do not combine incompatible `permissions` and legacy `sandbox` overrides.

## Tools

Default tool access:

```text
none for transcript-only
read-only for exact workspace
```

No shell command may mutate delivery or external systems.

Block `thread/shellCommand`, which is unsandboxed.

## Budget

```yaml
budgets:
  max_forks: 4
  max_turns_per_fork: 1
  max_total_tokens:
  per_fork_timeout_ms:
  total_timeout_ms:
```

Stop on budget exhaustion.

Partial receipts remain evidence with `status=budget_exhausted`.

## Cleanup

Ephemeral forks should disappear with runtime teardown.

For persisted compatibility fallbacks:

```text
interrupt active turn
archive or delete fork thread
remove temporary worktree
remove event logs according to retention policy
record cleanup status
```
