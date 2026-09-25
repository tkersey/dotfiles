# App-server, smoke, and instances

Use `cas app-server schema --json` for a structural schema/cache report and
`cas app-server preflight --json` for the structural and behavioral verdict.
Use `cas app-server session` for a raw stateful app-server stream and
`cas app-server daemon` for released daemon lifecycle commands. Both delegate
to the selected Codex executable, preserve its raw bytes and exit status, and
accept `--codex-path`; they do not impose a version gate.

Use a stateful session when a workflow needs multiple requests on the same
connection. `cas instance_runner` executes one method per isolated instance;
repeated invocations are not a persistent subscription or shared session.
Use `cas smoke_check` for bounded handshake and reachability observations.
Preserve additive response, notification, and item data rather than projecting
it away; derive available methods and fields from the exact generated schemas.

Codex 0.157.0's automatic daemon startup for interactive sessions does not
change CAS route ownership. Review and inquiry retain their required
CAS-managed WebSocket transport. Do not implicitly attach to, restart, or
stop a user's daemon to make a failed owned route pass. Use the delegated
daemon surface only for an authorized lifecycle operation.

When a caller requires immutable prepared-seed fanout, bind the source thread
ID and a completed seed turn ID once. Fork each child through that exact
`lastTurnId` (inclusive), not the coordinator's subsequently evolving head.
Use `excludeTurns:true` when only fork metadata is needed; retrieve required
history with `thread/turns/list` and `thread/items/list`, following cursors.
An in-progress or interrupted turn is not a completed seed. Do not use
`thread/rollback` or mutate the source with `thread/revert` to simulate a fork.

Explicit transport or remote Code Mode host selection is fail-closed. The
outbound Code Mode host is distinct from the inbound app-server endpoint and
uses the released HTTP(S) root-endpoint form. Authenticated WebSocket listener
flags belong to the delegated app-server session surface.
