# Codex app-server capability matrix

| Surface | CAS behavior | Required proof |
|---|---|---|
| Complete methods | Stable client, server-request, and notification requirements are declared baseline data; additive client methods remain admissible | selected structural contract |
| Thread sections | Create/update/delete sections; move, list, and clear thread membership | `full` probe |
| Thread history | Preserve `historyMode`, turn/item cursors, revert, turns, and items; no required `thread/rollback` on 0.157.0 | structural contract and `full` probe |
| Paginated forks | Stable exact completed `lastTurnId` and `excludeTurns`; experimental `beforeTurnId` and `deferGoalContinuation` only when schema-proven | `session-inquiry` or `full` probe |
| Ephemeral forks | `ephemeral == true`, `path == null`, absent from ordinary list | `session-inquiry` or `full` probe |
| Code Mode host | Exact outbound HTTP(S) root endpoint, loopback/TLS policy, identity digest, no fallback | selected-host probe |
| Raw session | Delegate the stateful app-server byte stream without projecting additive methods or payloads | dispatcher tests and released help surface |
| Daemon | Delegate authorized daemon lifecycle commands and exit status; interactive defaults do not change CAS-owned transport | dispatcher tests and released help surface |
| Authenticated listener | Preserve released WebSocket listener authentication flags on delegated sessions | released help surface |
| Transports | Distinct stdio, WebSocket, and Unix-socket identities | selected transport probe |
| Initialization | Typed capability profiles plus bounded raw additions for instance runner | core lifecycle probe |
| Server requests | Named conservative policy for every baseline method; typed auth/attestation provider failures | core coverage probe |
| MCP elicitation | Form, OpenAI form, and URL modes; no inferred consent | policy tests |
| PathUri | Opaque canonical `file:` URI until an explicit filesystem boundary | schema and fixtures |
| Lifecycle attribution | Preserve thread creator and item lifecycle metadata without inferring review completion or authority | raw payload preservation; exact turn/receipt proof for review |
| Plugin attribution | Preserve `pluginId` and `scriptPath` as attribution only | schema and item fixtures |
| Executor skills/resources | Lossless listing/read with source path or URI identity | `full` probe |
| Plugins/apps | Preserve refetch, workspace-publish capability, enabled/disabled/read-only metadata | schema fixtures |
| Managed config | Preserve all admitted `ConfigRequirements`; session-static defaults are not hot-reloaded | schema fixtures |
| External import | Bounded detect/import and provider-attributed record history in isolated state | `full` probe |
| Account plan | Preserve `ent26` and unknown plan values as data; no implicit gateway OAuth mutation | account tests |
| Additive payloads | Preserve raw metadata; reject unknown control flow explicitly | contract mutation tests |
| Backpressure | Retry only overload `-32001` with bounded jitter/backoff/count | core integration fixture |

The matrix describes raw client compatibility. It grants no semantic workflow,
trust, consent, repair, publication, or closure authority.
