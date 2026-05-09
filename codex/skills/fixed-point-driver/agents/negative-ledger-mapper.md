# negative-ledger-mapper moved

The active `negative-ledger-mapper` subagent is now defined in:

```text
codex/skills/negative-ledger/agents/negative-ledger-mapper.md
```

This compatibility note intentionally has no agent front matter so it does not register a duplicate subagent. `$fixed-point-driver` should invoke the mapper through `$negative-ledger` when negative evidence materially changes routing.
