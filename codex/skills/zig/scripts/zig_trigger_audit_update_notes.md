# Zig trigger and semantic-routing audit notes

The trigger surface now has two layers.

## Direct Zig cues

Keep existing file/tool/version/comptime/hazard cues.

## Contextual semantic-family cues

Only count these when the session is already in a Zig context.

```text
claim-binding:
  fingerprint receipt certificate cursor checkpoint replay evidence ref verify

lifetime-escape:
  arena parsed JSON decoded bytes returned slice snapshot report deinit

atomic-transition:
  rollback append commit stage transfer ledger journal outbox event pair

verifier-completeness:
  parser decoder verifier WASM opcode section LEB metadata stack result

repo-closure:
  golden expected output compile-fail path registry generated artifact manifest

proof-context:
  stale proof wrong head dirty tree after push/commit fork cache permission
```

Do not make generic words such as `commit`, `proof`, `manifest`, or `report` global `$zig` triggers.

## Quality metrics

Track separately:

```text
Zig intent sessions
$zig activation sessions
semantic-family opportunity sessions
ZSR-v1 route sessions
family selected before first edit
decision-effect episodes
review reopen by family
proof epoch stale events
repository closure misses
```

Activation recall is necessary but no longer sufficient.
