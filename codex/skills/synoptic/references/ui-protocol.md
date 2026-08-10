# Browser domain protocol

The browser speaks only versioned Synoptic domain messages. It never receives
raw Codex app-server envelopes and never receives shell or generic `gh`
capability.

## Transport

- Bootstrap: `GET /api/bootstrap?token=<launch-token>`.
- WebSocket: `GET /ws?token=<launch-token>`.
- Envelope: `{"schema":"synoptic-ui/v1","type":"...","seq":N,"payload":{}}`.
- The browser ignores duplicate/out-of-order events whose `seq` is not greater
  than the last applied sequence, except a full bootstrap/snapshot replacement.
- On reconnect, send `snapshot.get` and rebuild from the returned snapshot.

Client commands are `file.open`, `session.message`, `session.interrupt`,
`session.close`, `approval.resolve`, `action.confirm`, `action.reject`,
`snapshot.get`, `pr.refresh`, `round.finish`, and `app.stop`.

`action.confirm` and `action.reject` carry exactly `{cardId}`. Completion is not
a browser command: it must originate as an explicit human conversational
instruction and model tool call. Approval resolution carries the exact offered
decision and approval ID, plus session ID when the approval is session-owned.

The UI renders current PR identity, the primary readiness gate, unviewed queue,
session-identity tabs, canonical diff state, visible conversation items,
approval requests, action cards, warnings, failures, and round status. It does
not render the hidden primary transcript, a Reviewed list, direct line
selection, a shell, or direct GitHub controls.

All repository, GitHub, and model content is inserted with DOM text APIs, never
as HTML. Assets are same-origin and CSP-compatible.
