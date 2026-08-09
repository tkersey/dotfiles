---
name: learnings
description: "Capture, browse, query, supersede, and selectively admit evidence-backed execution learnings through the passive Learnings protocol. Trigger for $learnings, lessons learned, takeaways, wrap-up or handoff after material implementation, validation transitions, strategy pivots, hidden footguns, repeated acceleration patterns, and explicit durable-memory admission."
metadata:
  version: "8.1.0"
---
# Learnings

## Mission

Maintain a repo-local evidence-backed learning store and admit only high-value
bounded snapshots to Codex memory.

The canonical learning and memory admission are separate outcomes.

## Activation and capture gate

Activation is broad; append is conditional. Evaluate capture only when a
decision-shaping event occurred:

```text
validation transition
strategy pivot
hidden footgun or brittle assumption
repeated acceleration pattern
useful or failed recalled learning
delivery boundary after material implementation
```

Require decision delta, transferability, and meaningful counterfactual cost.
Prefer one essential learning and append at most three in a turn.

Retain exactly one disposition:

```text
appended
duplicate-skip
no-op
blocked
```

Do not query or write merely to manufacture a receipt.

## Common path

1. Bind the verified repository root and passive Learnings definition.
2. For recall, query the canonical projection and then inspect current artifacts;
   recalled history never replaces current evidence.
3. For capture, gather exact evidence and distill the transferable rule rather
   than a changelog bullet.
4. Append only through the selected Ledger definition.
5. Verify the returned canonical learning identity and readability.
6. Evaluate memory admission separately.
7. Admit only when the complete projection is likely to reduce future steering,
   search, or retries.
8. Report canonical append and memory-source admission independently when
   user-visible.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for a simple recall or
capture-gate decision.

Load it only for:

- exact Ledger ensure, doctor, bind, capture, record, recall, or projection
  commands;
- retired-store recovery and migration rules;
- complete row and submission schemas;
- memory-admission thresholds, adapters, supersession, withdrawal, and digest
  mechanics;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Ground every row in inspectable evidence.
- Write reusable rules, not chronology.
- Never hand-edit the store or compiled memory.
- Do not admit every learning to memory.
- Do not use Learnings as the operational failed-route gate; that belongs to
  `$negative-ledger`.
