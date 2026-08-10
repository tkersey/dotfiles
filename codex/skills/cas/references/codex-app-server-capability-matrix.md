# Codex app-server capability matrix

| Surface | CAS behavior | Required proof |
|---|---|---|
| Complete methods | Stable client, server-request, and notification sets are baseline contract data | structural contract |
| Thread pinning | Preserve `Thread.isPinned`; pin/unpin and list filters | `full` probe |
| Paginated forks | Exact completed boundary with `lastTurnId`; experimental `beforeTurnId` and `excludeTurns` | `session-inquiry` or `full` probe |
| Ephemeral forks | `ephemeral == true`, `path == null`, absent from ordinary list | `session-inquiry` or `full` probe |
| Remote Code Mode host | Exact outbound argument, security policy, redacted identity, no fallback | selected-host probe |
| Transports | Distinct stdio, WebSocket, and Unix-socket identities | selected transport probe |
| Initialization | Typed capability profiles plus bounded raw additions for instance runner | core lifecycle probe |
| Server requests | Named conservative policy for every baseline method; typed auth/attestation provider failures | core coverage probe |
| MCP elicitation | Form, OpenAI form, and URL modes; no inferred consent | policy tests |
| PathUri | Opaque canonical `file:` URI until an explicit filesystem boundary | schema and fixtures |
| Plugin attribution | Preserve `pluginId` and `scriptPath` as attribution only | schema and item fixtures |
| Executor skills/resources | Lossless listing/read with source path or URI identity | `full` probe |
| Plugins/apps | Preserve refetch, workspace-publish capability, enabled/disabled/read-only metadata | schema fixtures |
| Managed config | Preserve all admitted `ConfigRequirements`; session-static defaults are not hot-reloaded | schema fixtures |
| External import | Bounded detect/import and provider-attributed record history in isolated state | `full` probe |
| Account plan | Preserve `ent26` and unknown plan values as data | account tests |
| Additive payloads | Preserve raw metadata; reject unknown control flow explicitly | contract mutation tests |
| Backpressure | Retry only overload `-32001` with bounded jitter/backoff/count | core integration fixture |

The matrix describes raw client compatibility. It grants no semantic workflow,
trust, consent, repair, publication, or closure authority.
