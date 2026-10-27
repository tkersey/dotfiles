# Abstraction Move Packet

Use this packet whenever `universalist`, `reduce`, or an abstraction subagent hands work to another agent. The goal is to prevent one agent from climbing while another flattens the invariant it just found.

```md
# Abstraction Move Packet

## Scope
- Repo area:
- User goal:
- Observed pain:

## Current altitude map
- Altitude 0 / platform primitives:
- Altitude 1 / explicit local code:
- Altitude 2 / domain invariants:
- Altitude 3 / protocols or interpreters:
- Altitude 4 / framework/tooling layers:
- Altitude 5 / distributed/platform layers:

## Candidate upward moves
- Signal:
- Construction:
- First seam:
- Invariant gained:
- Lower-level alternative rejected:
- Proof signal:
- Risk:

## Candidate downward moves
- Layer:
- Tax:
- Proven value:
- Lower-level primitive:
- First seam:
- Proof signal:
- Rollback:
- Essential abstraction check:

## Adjudication
- Recommended move: climb | descend | hold | split
- Why:
- Why nearby move is worse:
- Compatibility boundary:
- Stop condition:

## Implementation permission
- Analysis only | first seam only | staged migration
```

## Handoff rules

- `universalist` must include `lower-level alternative rejected` before asking for a climb.
- `reduce` must include `essential abstraction check` before asking for a descent.
- The adjudicator decides the move type before any implementation agent edits files.
- The implementation agent does exactly one seam unless the packet explicitly allows a staged migration.

## Minimal packet for small tasks

```md
move: climb | descend | hold | split
scope:
current_altitude:
proposed_altitude:
essential_truth:
abstraction-tax:
first_seam:
compatibility_boundary:
proof_signal:
rollback:
stop_condition:
```
