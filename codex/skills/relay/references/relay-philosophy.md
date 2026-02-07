# Relay Philosophy

Agent mail is a coordination protocol, not a chat feature.
`relay` should expose that protocol as a small, stable control surface.

## One-Line Problem Statement

Enable multiple autonomous agents to collaborate on one codebase without clobbering edits, losing context, or requiring human relay of every handoff.

## Core Model

- `project_key`: coordination namespace (absolute repo path)
- `agent`: scoped identity inside a project
- `thread_id`: durable task conversation key
- `message`: async work/decision artifact
- `file reservation`: advisory intent claim on edit surfaces
- `contact link`: explicit consent/routing edge
- `ack`: explicit receipt state transition

## Invariants

I1. Project identity invariant
- All cooperating agents MUST use the same absolute `project_key`.
- Same path means same coordination bus.

I2. Agent identity invariant
- An agent MUST be registered before sending messages or claiming files.
- Identity SHOULD remain stable for the life of a task session.

I3. Thread continuity invariant
- One task SHOULD map to one stable `thread_id` (`bd-123`, ticket ID, etc.).
- Task updates MUST stay in-thread (`thread_id` or `reply_message`).

I4. Topic coherence invariant
- A thread subject SHOULD represent one topic.
- New topics SHOULD start a new thread.

I5. Consent/routing invariant
- Delivery MUST respect recipient contact policy.
- `CONTACT_REQUIRED` means handshake path required; `CONTACT_BLOCKED` means escalate or reroute.

I6. Recipient resolvability invariant
- Recipients MUST be resolvable in-project or through approved cross-project links.
- Unknown recipients are recoverable routing failures, not silent drops.

I7. Reservation semantics invariant
- File reservations are advisory intent, not mutex locks.
- Conflicts SHOULD surface as coordination signals (`granted + conflicts`), not immediate hard failure.

I8. Reservation hygiene invariant
- Claims SHOULD be narrow, TTL-bounded, and released at task completion.
- Broad or stale claims are coordination debt.

I9. Ack semantics invariant
- `ack_required` upgrades delivery to an explicit receipt contract.
- `ack` MUST be idempotent and set both read and ack timestamps.

I10. Durability/audit invariant
- Messages and reservation events MUST be durable and inspectable (DB + git-backed artifacts).
- Coordination history is a first-class output, not debug residue.

I11. Macro-first invariant
- Default path SHOULD use macros (`start`, `prepare`, `reserve`, `link`) for reliability.
- Atomic tools are fallback for debugging or uncommon flows.

I12. Deterministic recovery invariant
- Known error classes MUST map to ordered recovery playbooks before ad hoc retries.

## Design Consequences For Relay

- Keep relay verbs stable; hide backend tool naming churn.
- Prefer protocol guarantees over convenience shortcuts.
- Treat playbooks as executable contracts.
- Optimize for predictable recovery, not optimistic one-shot success.

