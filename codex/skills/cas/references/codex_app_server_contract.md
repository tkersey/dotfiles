# Codex app-server capability contract

Treat the installed `codex` executable as the runtime schema source. CAS 0.6.0
compares its compact `codex-app-server-capabilities-v2` contract with both
generated bundles and the selected live behavioral probes. The contract names
required capabilities, not a Codex release.

Released Codex 0.151.0 is the qualification baseline for this contract, not a
runtime pin or maximum. Later released runtimes remain admissible when their
generated schemas and selected live probes pass. Prerelease builds do not
replace released qualification evidence unless the caller requests that test.

## Schema and preflight

```bash
codex app-server generate-json-schema --out <stable-dir>
codex app-server generate-json-schema --experimental --out <experimental-dir>

cas app-server schema --cwd <repo> --json
cas app-server preflight --cwd <repo> --profile core --json
```

CAS caches schema bundles by resolved executable identity, reported version,
contract ID, and stable/experimental bundle digests. `--refresh-schema`
regenerates the cache. Exact bundle digests are diagnostics, not the
compatibility predicate.

A compatible profile requires:

- every baseline client method, server request, and notification;
- compatible required fields, scalar kinds, nullability, discriminators, and
  control-flow enums;
- one named terminating policy for every baseline server request;
- all required selected-profile behavioral probes.

Additive client methods, notifications, and non-control object fields are
admissible and reported. An additive server request makes `full` incompatible
until CAS assigns a policy. Unknown item variants remain raw or produce a typed
unsupported-item result.

## Profiles

- `core`: initialization, selected transport, request policy coverage, and
  bounded overload behavior.
- `review`: core plus structured review.
- `session-inquiry`: core plus paginated and ephemeral fork/anchor behavior.
- `full`: all declared features, including thread sections, executor skills and
  resources, external import history, review, and inquiry.

An explicit external endpoint must earn its own runtime and behavioral proof;
CAS may not borrow a fresh local process as the endpoint witness.

## Transports and remote Code Mode host

CAS distinguishes:

```text
stdio
websocket
unix_socket
```

Public selection is `auto|stdio|managed-ws|ws|unix`. Explicit selection fails
instead of changing transports. `auto` alone may use CAS's documented bounded
preference and fallback order.

`--code-mode-host http://LOOPBACK/|https://HOST/` is an outbound gRPC host
passed to the Codex app-server process. It is orthogonal to the inbound
transport endpoint. Plain HTTP is loopback-only; remote hosts require HTTPS.
Userinfo, query, fragment, and non-root paths are rejected. CAS preserves only
the origin plus a digest when needed and never silently falls back to the
in-process host.

`cas app-server session` delegates the raw stateful app-server surface,
including stdio, Unix/loopback WebSocket listeners, authenticated non-loopback
WebSocket listener flags, notifications, and server requests. `cas app-server
daemon` delegates daemon lifecycle commands. These surfaces preserve the
selected Codex executable's bytes and exit status so additive released methods
are not projected away by CAS.

All processes, readiness waits, frames, messages, retry loops, and captured
output are bounded. App-server overload `-32001` alone uses bounded exponential
backoff with jitter.

## Initialization

Every connection performs exactly once:

```text
initialize -> initialized -> ordinary requests
```

Known typed profiles may advertise:

- `experimentalApi`
- `optOutNotificationMethods`
- `mcpServerOpenaiFormElicitation`

Advertise OpenAI form elicitation only when an exact response policy exists.
`instance_runner` may add bounded raw initialization capability fields.
Unknown initialize response fields remain raw.

## Server-request policies

CAS recognizes these baseline requests:

- `item/commandExecution/requestApproval`
- `item/fileChange/requestApproval`
- `item/permissions/requestApproval`
- `item/tool/requestUserInput`
- `mcpServer/elicitation/request`
- `item/tool/call`
- `account/chatgptAuthTokens/refresh`
- `attestation/generate`

Deprecated `applyPatchApproval` and `execCommandApproval` are explicit
rejections. A future unknown request receives method-not-supported immediately
and is recorded by method name.

CAS never invents credentials or attestations. Exact response carriers may
come from owner-readable files or stdin through an authorized instance route;
secret bodies are never emitted, sampled, logged, or persisted. Missing auth
or attestation providers produce typed non-transport failures.

MCP elicitation defaults are conservative:

- `form`: decline without an exact configured response;
- `openai/form`: advertise only with an exact capable response path;
- `url`: decline or cancel and never open automatically.

CAS preserves `_meta` only as opaque caller data and never infers consent.

## Data rules

- `PathUri` is an opaque canonical `file:` URI, not a native path. Preserve
  percent encoding and authorities; convert only at an explicit filesystem
  boundary and retain both identities in diagnostics.
- Preserve `commandExecution.pluginId` and `scriptPath` as attribution, not
  trust or authority.
- Preserve skill icon URLs as metadata and never fetch them implicitly.
- Executor skill roots/resources retain their source environment path or URI;
  CAS does not copy them without a separate authorized file effect.
- Preserve plugin workspace-publish capability and app tool enablement,
  disabled reason, and read-only metadata without converting them into
  publication authority.
- Preserve managed `ConfigRequirements`, including PathUri-valued fields.
  Reloading user config does not hot-reload session-static model, reasoning,
  service-tier, or personality defaults.
- External agent detect/import bounds are caller supplied. Record-history tests
  use an isolated `CODEX_HOME`; provider and source identities stay distinct.
- Treat account plan type, including `ent26`, as open data. Unknown values are
  classified conservatively rather than breaking account status.

## Authority boundary

Schema compatibility means only that CAS can safely speak the selected raw
protocol profile. It does not prove review credit, historical truth, plugin
trust, automation correctness, user consent, repair authority, publication, or
semantic closure.
