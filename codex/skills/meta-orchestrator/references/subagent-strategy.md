# Specialist subagent strategy

Use the specialist swarm to strengthen the orchestrator without turning it into a parallel write free-for-all.

## Principle

The orchestrator stays responsible for:
- scope
- routing
- remediation decisions
- fixed-point judgment
- final readiness

Subagents contribute:
- evidence maps
- invariant ledgers
- foot-gun ledgers
- complexity grading
- verification audits

## Swarm rules

- Spawn specialists only for read-heavy work.
- Default to the smallest informative set, usually one or two roles, unless the surface is clearly broad enough to justify the full swarm.
- Wait for all relevant results before synthesis.
- Require packet-native briefings that follow `specialist-briefing-contract.md`.
- Treat specialist turns as internal packets, not user-facing responses: no `Echo:`, no instruction acknowledgements, no progress-only chatter, and no prose outside the packet.
- If the first specialist in a turn returns handshake junk or a malformed packet, mark transport degraded for the current artifact state and stop broad fanout on that state.
- If specialists return handshake junk or malformed packets, fail closed and reduce or skip the swarm instead of rerunning the same noisy fanout.
- Do not rerun the same specialist role on an unchanged artifact state after an invalid packet.
- Treat specialists as lenses, not authorities.
- In exhaustive subagent mode, after each material validation or remediation, rerun the full-scope swarm over the current artifact set.

## When to run the full swarm

Run the full swarm when:
- the user explicitly asks for subagents or parallel specialist review
- the artifact set spans multiple modules or subsystems
- a prior loop surfaced invariant, hazard, complexity, or verification concerns
- the work is broad enough that a single-thread review is likely to miss second-order effects
 - earlier specialist packets in the turn were valid enough that transport is still clean

## When not to run the full swarm

Avoid the full swarm when:
- the task is trivial
- the review surface is tiny and obvious
- the next work is write-heavy remediation rather than read-heavy analysis
- environment constraints make parallel agent work unreliable
- recent specialist turns returned instruction acknowledgements or other non-briefing output
- the current artifact state is already marked transport-degraded for specialist work
