---
name: relay
description: "Coordinate multiple coding subagents through a shared mail coordination service with a macro-first workflow: session bootstrap, thread preparation, contact handshakes, file reservations, inbox polling, and acknowledgements. Use when prompts ask to coordinate a swarm, manage subagent handoffs, keep agents in one thread per task, or help agents 'be excellent to each other' while avoiding duplicate edits and routing failures."
---

# Relay

Drive multi-agent execution with predictable communication contracts.

Use stable relay verbs first, then only drop to backend-native tools when debugging.

## Prerequisites

- Run your mail coordination server and mount it in your client config.
- Use `scripts/relay.py health` to confirm transport and auth.
- Use absolute repo path as `project_key`/`human_key`.
- Set environment once:
`RELAY_SERVER_URL=<endpoint>`
`RELAY_BEARER_TOKEN=<token>`

## Adapter Contract

Use relay verbs as the public interface:

- `start`: bootstrap a working identity and inbox context.
- `prepare`: align an agent on one active thread.
- `reserve`: claim file scopes before edits.
- `send`: publish a thread update.
- `poll`: fetch inbox deltas.
- `ack`: mark receipt of required messages.
- `link`: open a contact path when routing is blocked.

Backend tool names are implementation details inside `scripts/relay.py`.

## Script Entry Point

- Command: `scripts/relay.py`
- Safe inspection mode: add `--dry-run` to print the exact outbound request payload.
- Backend remap mode: use `--tool-map <json-file>` or `RELAY_TOOL_MAP='{\"start\":\"...\"}'` to remap verbs.

## Operating Workflow

1. Bootstrap identity and inbox.
`scripts/relay.py start --project <abs-repo> --program <agent-cli> --model <model> --task "<task>"`
2. Align on active thread.
`scripts/relay.py prepare --project <abs-repo> --thread <task-id> --program <agent-cli> --model <model>`
3. Reserve files before edits.
`scripts/relay.py reserve --project <abs-repo> --agent <agent> --path <glob> --reason <task-id>`
4. Message with durable thread IDs.
`scripts/relay.py send --project <abs-repo> --sender <agent> --to <agent-list> --subject "<subject>" --body "<markdown>" --thread <task-id> --ack-required`
5. Poll inbox and acknowledge required receipts.
`scripts/relay.py poll --project <abs-repo> --agent <agent>` then `scripts/relay.py ack --project <abs-repo> --agent <agent> --message-id <id>`
6. Release reservations when work is done.
`scripts/relay.py reserve --project <abs-repo> --agent <agent> --path <glob> --auto-release`

## Thread Contract

- Reuse one stable `thread_id` per task (`bd-123`, ticket ID, etc.).
- Keep subject line scoped to one topic.
- Reply in-thread using `reply_message` when continuity matters.
- Set `importance` and `ack_required` deliberately; do not overuse `urgent`.

## Contact Contract

- Default policy is consent-aware (`auto`); cold outreach may require handshake.
- For unknown recipients or blocked delivery, run `scripts/relay.py link --project <abs-repo> --requester <agent> --target <agent> --auto-accept` where policy allows.
- For cross-project communication, include `to_project` and use explicit handshakes.

## File Reservation Contract

- Reserve narrow path patterns only.
- Treat conflict surfaces as coordination signals, not hard failures.
- Use reason strings aligned with task IDs for auditability.

## Failure Routing

- `CONTACT_REQUIRED`: request or handshake contact, then retry send.
- `CONTACT_BLOCKED`: escalate to human coordinator or alternate recipient.
- `RECIPIENT_NOT_FOUND`: register/mint missing identity, then retry.
- `FILE_RESERVATION_CONFLICT`: narrow target paths or coordinate and re-reserve.
- Execute the exact remediation sequence in `references/error-playbooks.md` before trying ad hoc fixes.

## References

- Detailed architecture and communication flow: `references/architecture.md`.
- Error playbooks and retry recipes: `references/error-playbooks.md`.
- Prompt and workflow examples: `references/examples.md`.
- Delegation phrasing adapters for real prompts: `references/prompt-adapters.md`.
