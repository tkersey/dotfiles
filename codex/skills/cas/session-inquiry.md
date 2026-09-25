# Session inquiry

Use the `session-inquiry` preflight profile before execution. A paginated source
is admissible when the exact runtime probe passes. Bind the exact completed
fork boundary with `lastTurnId`, use `excludeTurns:true`, then verify the
required paginated history and retained-anchor digest. Do not fork an evolving
head or accept an interrupted suffix as completed history. A successful
paginated fork is not proof of historical workspace reconstruction.

Codex 0.157.0 has no `thread/rollback` endpoint. A failed paginated fork remains
a compatibility/transport failure; do not retry through rollback, mutate the
source with revert, or silently switch to transcript lineage. Transcript replay
requires its separately evidenced source and lineage admission.

Pass `--transport managed-ws` to `session_inquiry run|start`; do not let the
execution fall back to its `auto` default after proving a selected transport.

Validate Retrace inputs with their owner definitions and validate the returned
FIR with CAS's passive definition before interpreting it. See
[retrace-session-inquiry.md](references/retrace-session-inquiry.md).
