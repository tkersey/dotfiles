# Direct native app-server operations

Use the caller's selected `codex` executable, installed help, and generated schemas.
No CAS launcher, schema cache, live-profile gate, instance runner, or receipt adapter
is required. For a local stateful connection:

```bash
codex app-server --listen stdio://
```

Keep the host's process and bidirectional stream alive for all related requests,
notifications, and worker turns. Send `initialize` once with client identity and
required capabilities, then `initialized`, before ordinary requests. Request IDs
correlate replies; thread and turn IDs correlate observations. A sequence of new
processes is not one connection or a persistent subscription. Use a host facility
that actually supports persistent stdin/stdout; do not build another control-plane
product when that facility is unavailable.

## Operations and effects

| Need | Native operation / boundary |
|---|---|
| Schema inspection | `codex app-server generate-json-schema --experimental --out <private-dir>`; no live success claim. |
| Native review with raw configuration | Fresh `thread/start`, then `review/start` with the Git target and inline delivery; use [reviews.md](reviews.md) for original native result admission. |
| Observe thread or goal | `thread/read`, paginated turn/item reads, `thread/goal/get`; no `thread/resume` merely to observe. |
| Account facts | Schema-advertised `account/read` / rate-limit reads; do not request credential refresh or token-bearing data. |
| Create/update/clear goal | `thread/goal/set` / `thread/goal/clear`, only for the authorized exact thread. |
| Prepared-history fanout | Native `thread/fork`, followed by caller-owned history verification and `turn/start`. |
| Daemon lifecycle | `codex app-server daemon --help`; choose only an authorized lifecycle operation, not takeover of an unrelated daemon. |

For native reviews, omit `developerInstructions` for changeset standard. For
auxiliaries/focused work, supply the caller's exact instruction bytes there while
keeping `review/start.target` separate. Preserve selected model/provider, approvals,
permissions, workspace roots, environment, and config. Inspect returned selections
before dispatch. Native review forces its approval policy and prefers `review_model`;
supplied options are not an effective-permissions or effective-repository attestation.

For a fresh review thread, resolve model and effort from the invoking turn under
[review inheritance](reviews.md#inherit-the-invoking-turns-settings). Pass the resolved
model and native configuration overrides for `review_model` and
`model_reasoning_effort` through the installed `thread/start` schema. Verify the
returned effective model/effort before `review/start`; do not rely on a new server
process inheriting the caller's live settings. Existing-thread recovery preserves
the original request's configuration rather than adopting a later caller's settings.

## Existing-thread follow-up

Use [queueing](queueing.md) when it expresses the authorized operation. For direct
RPC, read the exact thread/turn state first and resolve any possibly accepted queue
or turn input. Load with `thread/resume` only when necessary and authorized; it is
not passive observation and may start pending work. Verify what resumed before
issuing another assignment. Preserve the original request's model, effort,
provider, endpoint, permissions and context settings unless a specific change is
authorized; a changed invoking turn is not that authorization.

Use schema-supported configuration on the applicable resume/start operation and
inspect returned selections. Submit `turn/start` only when the thread can accept
the intended new turn and the assignment has not already been accepted. Observe
its actual identity and terminal result on the same connection. An ordinary turn
is supplemental inquiry, not a resumed native review delegate or a new native
standard. Follow [incomplete-inquiry recovery](reviews.md#recover-incomplete-review-inquiry)
for the evidence handoff; matching thread IDs alone do not retain the delegate's
investigative context. An unresolved acknowledgement blocks duplicate submission,
including across CLI and RPC routes.

## Explicit WebSockets and endpoints

For an explicitly required control listener, native Codex also exposes:

```bash
codex app-server --listen ws://127.0.0.1:4500
```

A listener is not a client. Use an available supported persistent WebSocket client
and the installed authentication options. Preserve explicit endpoint/authentication
selection; never replace it with a fresh local process. Use secure remote transport
and do not expose unauthenticated non-loopback listeners. Native exec/review cannot
be redirected with `--remote` in the qualified release. Control transport, remote
Code Mode host, and model-provider WebSockets are separate boundaries; see
[runtime qualification](runtime-compatibility.md).

## Client responsibilities

Raw native delegation does not install response policies or create a managed
receipt. The calling host must correlate and terminate server requests. Deny
unrequested command/file/permission approvals; leave user input unanswered rather
than inventing an answer; decline/cancel elicitation without exact consent. Return
a protocol error immediately for unsupported requests. Do not deadlock a stream,
invent credentials/attestations, grant plugin trust, or log secret response bodies.
Use schema-correct responses, and retain failures as failures rather than silently
changing transport, model, or permissions.

## Forks and readback

An immutable prepared seed receives no assignment, findings, or follow-ups. Fork
it from the actual prepared source, verify `forkedFromId` and retained history,
then fork every child from that unchanged seed ID and verify each edge. A
`lastTurnId` cut is inclusive and must already contain all required preparation;
omit a cut that would discard preparation in the current turn. `excludeTurns:true`
omits response history, not context; follow all required turn/item cursors for
readback. Do not substitute destructive revert for a fork.

`codex exec fork <exact-id>` is a convenient native fork, including no-prompt seed
creation, only where its actual history and configuration meet the caller's
contract. Success or a new ID alone does not establish full prepared-context
retention. Native fork identity is not historical workspace reconstruction.

On a lost connection or acknowledgement, inspect the exact known thread and turn
before retrying or assigning new work. Preserve independently attributable effects;
never retry a possibly accepted assignment blindly. Keep raw replies private and
report only relevant sanitized identities, statuses, and admitted findings.
