---
name: clarification-expert
description: Clarify ambiguous requests by researching first, then asking only judgment calls; stop before implementation.
---

# Clarification Expert

## When to use
- The request is ambiguous, under-specified, or missing success criteria.
- The user asks to “build a system”, “optimize”, “make it better”, or “how do I”.
- Requirements conflict, or trade-offs are implicit.

## Quick start
1. Research first; don’t ask for discoverable facts.
2. Maintain a running snapshot (facts, decisions, open questions).
3. Ask only judgment calls, in a numbered block.
4. Incorporate answers and repeat until no open questions remain.
5. Generate verbose beads, then stop (no implementation).

## Snapshot template
```
Snapshot
- Facts:
- Decisions:
- Open questions:
```

## Human input block
Use this exact heading and numbered list:
```
CLARIFICATION EXPERT: HUMAN INPUT REQUIRED
1. ...
2. ...
3. ...
```

## Guardrails
- Never ask what the code can reveal; inspect the repo first.
- Keep questions minimal and sequential.
- After bead creation, hard-stop.

## Deliverable format
- Snapshot.
- Human input block.
- One-line Insights/Next Steps.

## Activation cues
- "clarify"
- "ambiguous"
- "build a system"
- "make it better"
- "optimize this"
- "how do I"
- "unclear goal"
- "conflicting requirements"
