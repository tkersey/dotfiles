# Error Playbooks

Use these playbooks exactly in order. Do not skip straight to manual workarounds.

## CONTACT_REQUIRED

1. Establish consent path:
`scripts/relay.py link --project <project> --requester <agent> --target <agent> --auto-accept --ttl-seconds 86400`
2. Verify link exists:
`scripts/relay.py --dry-run link --project <project> --requester <agent> --target <agent>`
3. Retry original send with the same `thread_id`.
4. If still blocked, escalate and retry once with narrowed recipients.

## CONTACT_BLOCKED

1. Confirm target policy:
Inspect policy via backend diagnostics.
2. Stop retries if policy remains `block_all`.
3. Route message to coordinator/overseer or approved alternate recipient.
4. Post an in-thread status update documenting blocked route and alternate handoff.

## RECIPIENT_NOT_FOUND

1. Discover active names:
Inspect active names via backend diagnostics.
2. If recipient should exist, register identity:
bootstrap/start the missing agent identity.
3. Retry `send_message` once.
4. If cross-project, handshake with `to_project` before retrying send.

## FILE_RESERVATION_CONFLICT

1. Inspect active reservations:
inspect active reservation views in your backend.
2. Reduce scope to narrower paths and retry reservation.
3. If overlap is intentional, coordinate via message in shared `thread_id`.
4. Re-run `scripts/relay.py reserve` with adjusted path set.

## ACK_REQUIRED Backlog

1. Poll pending receipts:
`scripts/relay.py poll --project <project> --agent <agent> --limit 50`
2. Acknowledge oldest first:
`scripts/relay.py ack --project <project> --agent <agent> --message-id <id>`
3. Reply in thread only when action/decision is needed; avoid redundant text replies.
