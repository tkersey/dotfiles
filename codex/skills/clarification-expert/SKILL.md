---
name: clarification-expert
description: Clarification protocol for ambiguous requests, "build/optimize/make it better" prompts, or unclear goals; use to research first, ask only judgment questions, and hard-stop before implementation.
---

# Clarification Expert

## When to use
- The request is ambiguous or under-specified.
- User says "build a system", "optimize this", "make it better", "how do I".
- Requirements are unclear, conflicting, or success criteria are missing.
- The goal is vague, broad, or not tied to a concrete outcome.

## Quick start
1. Research first; do not ask for discoverable facts.
2. Keep a running snapshot: facts, decisions, open questions.
3. Ask only judgment-call questions in a numbered block.
4. Incorporate answers and repeat until no questions remain.
5. Generate verbose beads, then hard-stop (no implementation yet).

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
- Do not implement after questions; stop after bead creation.

## Deliverable format
- Snapshot block.
- Human input block (numbered).
- Short Insights/Next Steps line.

## Activation cues
- "clarify"
- "ambiguous"
- "build a system"
- "make it better"
- "optimize this"
- "how do I"
- "not sure what you want"
- "unclear goal"
- "conflicting requirements"
