# Session inquiry

CAS owns bounded replay transport and observed lineage. The caller owns source
selection, inquiry meaning, historical claims, and proof credit. This collection
does not bundle an input-capsule or inquiry-plan owner. Before `run` or `start`,
require concrete caller-owned definitions compatible with the native input
contract and their successful validation results. Missing definitions leave this
execution route unavailable; do not reconstruct a retired workflow or invent
validation. Independently answerable session observations can still use Seq.

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

## Lineage and execution

`thread_fork` binds a stored source thread to an exact completed boundary and
verifies retained-prefix count, digest, and fork identity. Interrupted or
incomplete suffixes are not completed history. An ephemeral fork is pathless and
absent from ordinary thread listing. Successful transport proves neither
historical workspace equivalence nor the semantic truth of the replay.

Use `rollout_transcript` only when thread-fork lineage is unavailable for a
separately evidenced reason. It requires a verified rollout and retained-anchor
digest. Its workspace policy remains `transcript_only`: no current-checkout
tools, read-only, network off, and approvals denied.

After resolving the input owner, use `cas session_inquiry run --help` for the
installed command surface. Supply the actual capsule/plan definitions and their
validation results, along with the selected `managed-ws` transport. A version
string or a previously named schema is not input validation.

Validate the returned FIR through CAS's
`definitions/ledger/fork-inquiry-receipt.json` before the caller interprets it.
FIR-v1 preserves exact lineage mode, source and fork identities, anchor digests,
workspace mode, runtime/provider, policy proof, terminal state, and cleanup.
Do not add undeclared durable fields or infer proof credit from transport success.
