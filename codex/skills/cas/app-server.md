# App-server, smoke, and instances

## App-server, smoke, and instances

Use `cas app-server schema --json` for a non-mutating schema/cache report and
`cas app-server preflight --json` for the structural and behavioral verdict.
Use `cas app-server session` for a raw stateful app-server stream and
`cas app-server daemon` for released daemon lifecycle commands. Both delegate
to the selected Codex executable, preserve its raw bytes and exit status, and
accept `--codex-path`; they do not impose a version gate.
Use `cas smoke_check` for bounded handshake and reachability observations.
Use `cas instance_runner` for bounded raw requests or fanout. Preserve additive
response, notification, and item data rather than projecting it away.

Explicit transport or remote Code Mode host selection is fail-closed. The
outbound Code Mode host is distinct from the inbound app-server endpoint and
uses the released HTTP(S) root-endpoint form. Authenticated WebSocket listener
flags belong to the delegated app-server session surface.
