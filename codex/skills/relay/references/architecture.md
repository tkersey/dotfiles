# Architecture

This note summarizes how mail-coordinated agents communicate so workflow decisions stay consistent.

## Public Interface

Use the adapter CLI in `scripts/relay.py` with stable verbs:

- `health`
- `start`
- `prepare`
- `reserve`
- `send`
- `poll`
- `ack`
- `link`

If backend tool names differ, override mapping with `--tool-map` or `RELAY_TOOL_MAP`.

## Core Data Flow

1. `send` resolves recipients and enforces contact policy.
2. Message rows are written into the coordination datastore.
3. Bundle writer emits canonical message, outbox copy, inbox copies, and optional thread digest.
4. Git commit records the mailbox artifacts for audit and human review.

## Delivery Surfaces

- Canonical: `messages/YYYY/MM/*.md`
- Sender outbox: `agents/<Agent>/outbox/YYYY/MM/*.md`
- Recipient inbox: `agents/<Agent>/inbox/YYYY/MM/*.md`
- Thread digest: `messages/threads/<thread_id>.md`

## Read Surfaces

- Mutable workflow reads: `fetch_inbox`
- Resource reads:
`resource://inbox/{agent}`
`resource://thread/{thread_id}`
`resource://message/{message_id}`

## Acknowledgement Semantics

- `ack` sets both `read_ts` and `ack_ts` for the `(agent, message)` recipient edge.
- Calls are idempotent; repeat acknowledgements should not corrupt state.

## Contact and Routing Semantics

- Contact request/approve flows manage explicit link approvals.
- `send` may auto-allow based on thread participation, prior contact window, or reservation overlap.
- `link` is the preferred recovery path when direct send is blocked.
