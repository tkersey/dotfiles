# Session inquiry

## Session inquiry

Use the `session-inquiry` preflight profile before execution. A paginated source
is admissible when the exact runtime probe passes. Fork boundary and anchor
digest verification remain mandatory. A successful paginated fork is not proof
of historical workspace reconstruction.

Pass `--transport managed-ws` to `session_inquiry run|start`; do not let the
execution fall back to its `auto` default after proving a selected transport.

Validate Retrace inputs with their owner definitions and validate the returned
FIR with CAS's passive definition before interpreting it. See
[retrace-session-inquiry.md](references/retrace-session-inquiry.md).
