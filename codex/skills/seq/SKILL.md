---
name: seq
description: "Reconstruct provenance-preserving observations from Codex and OpenCode session evidence with Seq 1.x. Use for session, tool, and message forensics; skill activation and outcome audits; decision provenance; $tune evidence; $retrace source observations; watched-session deltas; worker attribution; and reproducible historical reports. Use native commands only for physical session structure and the owning passive definition for every higher-level question."
metadata:
  version: "2.0.0"
---
# Seq

## Mission

Return bounded observations with provenance, corpus scope, contamination,
limitations, and uncertainty.

Seq reads history. It does not validate durable artifacts or grant action,
repair, review, publication, or closure authority.

## Routing law

Use native Seq commands only for physical structure:

```text
sessions, turns, messages, tool lifecycle, session graph, raw bounded fields
```

Use the owning passive observation definition for every semantic question:

```text
skill activation or decision influence
workflow governance
review or publication causality
historical candidates
tuning evidence
retrace evidence
domain-specific projection
```

Do not replace a missing definition with an ad hoc grep pipeline.

## Common path

1. Bind repository, source roots, time window, session identity, and current
   contamination boundary.
2. Choose the smallest dataset or passive definition that can answer the exact
   question.
3. Narrow before reading detail; do not dump whole sessions.
4. Preserve stable source-event, turn, call, and session identities.
5. Separate observed facts from inference and absence from top-k omission.
6. Record scope, pagination/completeness, contamination, unsupported fields, and
   uncertainty.
7. Return the smallest reproducible observation plus the command or definition
   that produced it.
8. Stop without converting evidence into another skill's decision.

## Conditional disclosure

The complete pre-split contract is preserved byte-for-byte in
[FULL_CONTRACT.md](FULL_CONTRACT.md). Do not load it for one focused native or
definition-backed query.

Load it only for:

- the complete native command catalog and dataset schemas;
- definition authoring or compatibility mechanics;
- provider normalization across Codex and OpenCode;
- pagination, top-k, worker graph, or contamination edge cases;
- report formats and reproducibility bundles;
- an unported edge route.

Its frontmatter is archived source, not a second skill definition.

## Guardrails

- Do not inspect raw JSONL with shell tools when Seq exposes the fact.
- Do not infer absence from an incomplete result.
- Do not interpolate trace-derived values into shell source.
- Do not treat semantic similarity as identity.
- Do not let historical evidence authorize current mutation.
