# Interaction-evolving interfaces

Some apparent abstraction is actually a stateful protocol. Reduce incidental wrappers first, but do not flatten essential protocol evolution into a fixed global interface without proof.

## What counts as an evolving interface

An interface is interaction-evolving when the valid operations, required inputs, or output shape changes after events.

Examples:

- Authentication flow: unauthenticated -> MFA pending -> authenticated -> privileged.
- Checkout flow: cart -> shipping -> payment -> confirmation.
- Capability protocol: tool unavailable -> granted -> revoked -> expired.
- Streaming or realtime session: connecting -> subscribed -> backfilled -> live -> closed.
- Wizard/progressive UI: step-specific fields, validation, and actions.
- Distributed workflow: pending -> reserved -> committed -> compensated.

## Detection checklist

Before removing a layer that appears to manage interaction state, ask:

```text
- Does the allowed operation set change after user/system events?
- Does authorization or capability scope change during the interaction?
- Are there invalid transitions that must be rejected?
- Does the output schema depend on state?
- Are there retries, compensation, expiration, or cancellation states?
- Do tests assert state transitions or only final output?
- Is state stored durably, in session, in cache, or in client memory?
```

If two or more answers are yes, treat the abstraction as protocol-bearing until proven otherwise.

## Required transition table

For protocol-bearing layers, produce a transition table before recommending deletion.

| State | Event/input | Allowed operation set | Side effects | Next state | Proof |
|---|---|---|---|---|---|
| unauthenticated | valid password | submit credentials | create MFA challenge | mfa_pending | auth test |
| mfa_pending | valid code | verify code | create session | authenticated | auth test |

Use the repository's domain terms rather than generic names when possible.

## Reduction rules

Good reductions:

- Replace hidden runtime checks with an explicit state machine or transition table.
- Move protocol logic out of framework hooks into pure transition functions.
- Collapse duplicate state representations into one source of truth.
- Replace ad-hoc booleans with named states when the protocol is real.
- Isolate external/session storage behind a small boundary.

Bad reductions:

- Flattening all states into one permissive handler.
- Removing validation because tests only cover the happy path.
- Collapsing capability grants/revocations into static roles.
- Treating state-specific fields as optional global fields.
- Removing idempotency, retry, expiration, or compensation behavior without proof.

## Protocol value scoring

Protocol-bearing abstractions often earn higher `V` when they prove:

- Invalid transitions are rejected.
- Authorization/capabilities change safely.
- Persistence and recovery semantics are tested.
- External clients depend on state-specific responses.
- Operational safety depends on idempotency or compensation.

However, the wrapper around the protocol may still be reducible. Separate these two questions:

```text
1. Is the stateful protocol essential?
2. Is the current implementation layer the simplest safe representation of that protocol?
```

## Preferred primitive

The preferred replacement for a hidden evolving interface is usually not a flat function. It is often:

```text
explicit state enum + transition function + small storage boundary + focused tests
```

Example shape:

```text
State: Draft | Submitted | Approved | Rejected
Event: Edit | Submit | Approve | Reject | Reopen
Transition: (state, event, actor, input) -> { next_state, effects }
```

This can be simpler than framework hooks, decorators, or scattered runtime checks while preserving the real protocol.

## Proof signals

Use these proof signals before cutting protocol layers:

- Transition table covers all observed states and events.
- Tests cover at least one invalid transition per protected state.
- Public outputs remain compatible for each state.
- Authorization/capability checks remain state-specific.
- Recovery/retry/cancellation behavior is preserved where present.
- Rollback restores prior protocol handling without data migration loss.
