# Framework Boundaries

## Purpose

This file helps `universalist` land stronger internal models without forcing
premature changes to APIs, serializers, or persistence.

The default move is:

1. keep the external shape stable
2. parse or adapt at the boundary
3. use the stronger model internally
4. unwrap only at explicit output boundaries

## Boundary types to inspect first

- HTTP request and response DTOs
- JSON, YAML, protobuf, or message envelopes
- ORM entities and database rows
- background job payloads
- template or view models
- CLI flags and environment config

## General adapter rules

- Keep legacy wire or row shapes at the edge during the first seam.
- Name the adapter explicitly: `decode`, `fromRow`, `toDomain`, `toWire`, `fromDto`.
- Avoid sprinkling partial conversions through business code.
- One place should fail fast on invalid external combinations.
- One place should intentionally unwrap refined or witness types when leaving the domain layer.

## TypeScript / JavaScript notes

- Keep raw API objects or ORM rows distinct from internal tagged unions.
- If the repo already uses a decoder or schema library, prefer it at the edge.
- Introduce the discriminant internally first; keep old response shape stable with an encoder if needed.
- For refined types, parse once in route handlers, RPC adapters, or repository edges.

## Python notes

- Prefer a small constructor or `parse` method next to a frozen wrapper or value object.
- Let serializers and request handlers convert from raw strings into refined values once.
- Do not let `str` leak back into service signatures if the refined type exists.
- When full static enforcement is impossible, say so and rely on boundary tests.

## Java / Kotlin notes

- Keep DTOs and entities separate from domain types during the first migration step.
- Use factories, static constructors, or companion methods to centralize refinement.
- Keep sealed hierarchies internal if persistence or Jackson models are still legacy-shaped.
- Use explicit mappers or converters instead of annotation magic when clarity matters more than cleverness.

## Go notes

- Keep row or JSON structs in an adapter package when the domain type gains invariants.
- Prefer unexported fields plus constructor functions for refined values and witnesses.
- Make invalid states impossible by construction inside the package, not by caller convention.
- Preserve both projections on witness types so callers do not reconstruct raw pairs.

## Rust / Swift notes

- Newtypes are cheap boundary wins for refined values.
- Keep `serde` or `Codable` adapters at the edge if the wire shape must remain legacy-compatible.
- Enum-based coproducts often pay off quickly because exhaustiveness becomes available immediately.

## Persistence cautions

Check these before widening a seam:

- Does the stronger model require a schema change, or can it be adapter-only first?
- Are values serialized into queues, caches, or audits that still expect the legacy shape?
- Are migrations reversible?
- Is there a parity corpus that can prove legacy and new decoding agree on valid data?

## Good stop point

Stop after the internal shape is stronger, one boundary adapter is in place, and
the proof signal passes. Do not widen into a storage rewrite unless the user
asks for that next seam.
