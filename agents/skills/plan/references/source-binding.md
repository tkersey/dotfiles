# Source Binding

Every complete plan binds its objective, source authority, and inspected artifact
state. This is provenance, not a claim of runtime currentness or mutation authority.

Human plans name a stable `plan_id`, revision, target repository/branch, inspected
base/head and relevant working-tree state when available, fixed decisions, scope,
compatibility/proof authority, and material invalidators. State unavailable facts
honestly; never manufacture a head, timestamp, hash, or accepted decision.

`spec-to-plan` preserves all execution-relevant candidate and authoritative semantics
inside the emitted specification. `direct` records explicit bypass authority and the
accepted intent. `revise` recovers the exact prior specification, source binding,
and plan identity; never choose a prior plan solely because it is recent.

A hash or reference cannot recover lost conversation text. Reproduce requirements
and fixed decisions in the plan even when source refs also identify their origin.
An old artifact missing essential source requires recovery or explicit reconstruction
from current authority; it cannot be certified complete from its digest alone.

## Optional export

New EPG-v1 exports embed the exact complete `<proposed_plan>` block in
`source.execution_specification`. Set `source.source_digest` to SHA-256 of that
string's exact UTF-8 bytes, without normalization. Other refs retain original source
provenance. Do not include an EPG digest in the embedded block: export metadata lives
outside it, avoiding a self-referential digest. See epg-export.md.

Retain EPG-v1 source modes: `spec_handoff` is the legacy wire spelling for governed
spec-to-plan, not an actual handoff or SGR authority. Use `direct_brief` or
`existing_policy_revision` as appropriate. State the real user/specification authority.

## Invalidation and revision

A superseded user decision, material source change, missing API/protocol, changed
proof topology, lost evidence freshness, or relevant unexpected repository change
invalidates affected assumptions. Expected mutations described by the plan are not
by themselves evidence that the plan has become stale. Consumers determine actual
currentness and revalidate assumptions after expected transitions.

Respond through an affected plan revision, judgment acquisition, refreshed evidence,
or block. Preserve the plan ID for the same objective and increment its revision;
new objectives get new IDs. Return-to-spec means revisiting Plan's internal source
phase, not a separate skill. Never silently alter a sealed source binding.
