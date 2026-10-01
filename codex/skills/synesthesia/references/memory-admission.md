# Synesthesia memory admission

Synesthesia owns durable sensory semantics and canonical capture. `$ledger` owns
custody and the definition runtime. `$memory-source-notes` owns validated note
transport, installed adapter paths, synchronization, digest generation, and
reconciliation. Ordinary sensory output is not persisted.

## Admission gate

Explicit durable endorsement, correction, rejection, retraction, reopening, or a
reusable mapping/boundary instruction is sufficient without repetition. A
current-task compliment is not necessarily durable authority. Without explicit
durability, require accepted operational use in at least two independent contexts
and evidence that it changed diagnosis or explanation. Assistant novelty never
qualifies on its own.

Retain the narrowest reusable scope, source references, concrete engineering
meaning, activation/non-activation boundaries, and a verification rule. Endorsing
a correspondence does not verify its applicability to every future architecture.
Do not globalize repository vocabulary without broader authority.

Do not capture transient incidents, one-off poetry, ambient colors, ordinary
technical facts owned by `$learnings`, or failed-route exclusions owned by
`$negative-ledger`. Do not evaluate persistence merely at handoff or closeout.

When already active, an actionable non-durable mapping may be proposed with its
evidence, translation, boundaries, and missing endorsement. It is not a ledger
row, source note, or future authority; no candidate protocol is mandatory.

## Events and identities

| Event | Logical kind | Stored kind | Operation | Prior identity |
|---|---|---|---|---|
| Endorsement | `mapping-endorsement` | same | `assert` | None |
| Confirmation | `mapping-confirmation` | `mapping-endorsement` | `confirm` | Required in `related_ids` |
| Correction | `mapping-correction` | same | `supersede` | Required |
| Rejection | `mapping-rejection` | same | `reject` | Required |
| Boundary assertion/confirmation/correction/reopening | `activation-boundary` | same | `assert` / `confirm` / `supersede` / `reopen` | Required except for `assert` |
| Withdrawal | `boundary-retraction` | same | `retract` | Required |
| Mapping reopening | `mapping-endorsement` | same | `reopen` | Required |

Use the passive definition's operation/authority matrix: endorsements and
confirmations use explicit endorsement or repeated accepted use; mapping
corrections use explicit correction; mapping rejections use explicit rejection;
boundary withdrawal uses explicit correction or rejection. Preserve the prior
relationship rather than asserting a replacement as an unrelated new mapping.

`SYN-*` identifies a canonical event. `MSN-*` identifies an immutable admission.
They are not interchangeable. Canonical relationships may retain either supported
identity; the transport adapter resolves canonical relationships to exact admitted
note identities, preserves canonical provenance, and leaves canonical rows alone.
A missing or ambiguous prior admission blocks the dependent admission—not the
already successful canonical capture. Never guess a note ID or bulk-admit history.

## Canonical submission

Resolve `<synesthesia-definition>` to this skill's
`definitions/ledger/synesthesia-protocol.json`. Its passive schema is authoritative;
do not duplicate validation in prose or hand-write a canonical row.

```json
{
  "logical_kind": "mapping-endorsement",
  "physical_kind": "mapping-endorsement",
  "record": {
    "operation": "assert",
    "authority": "explicit-user-endorsement",
    "summary": "Endorse long corridor as serialized-wait vocabulary.",
    "scope": {"kind": "task-family", "repo": null, "paths": []},
    "source_refs": [{
      "kind": "user-endorsement",
      "ref": "<actual source reference>",
      "summary": "User explicitly accepted the correspondence as reusable."
    }],
    "related_ids": [],
    "supersedes_id": null,
    "payload": {
      "sensory_phrase": "long corridor",
      "engineering_translation": "A chain of serialized waits.",
      "activation_boundary": "Explicit sensory explanation of evidenced serial waits.",
      "non_activation_boundary": "Do not infer measured latency from dependency depth alone.",
      "verification": "Name the waits and distinguish observed duration from topology."
    }
  }
}
```

Corrections and confirmations retain the mapping payload. Rejection uses
`sensory_phrase`, boundaries, `rejection_reason`, and `verification`; engineering
translation is optional. A pure boundary has both boundaries and `verification`.
Withdrawal has `retracted_boundary`, `reason`, and `verification`. Use real source
references, not the example placeholder. Transport-only provenance kinds
`synesthesia-canonical-event` and `synesthesia-canonical-relationship` belong to
the adapter, not canonical submission authors.

## Custody and capture

Load `$ledger` and complete `$ledger ensure` before the first native command.
This revision retains Synesthesia's existing explicitly selected **unmanaged
custody**, rather than silently opting its history into managed storage. In the
commands below, `<canonical-custody-root>` is that exact selected root—not
whichever worktree happens to be the current directory.

Use the same selection for capture, recall, admission, doctor, and reconciliation.
Changing worktrees does not authorize a new parallel history, fallback, implicit
binding, or automatic migration. When the established custody cannot be selected,
report the continuity problem; do not initialize an empty replacement. A future
repository-family adoption must use Ledger-owned maintenance and update every
reader and writer together. This reference defines semantic scope, not physical
storage paths or a competing context resolver.

```bash
ledger doctor --definition "<synesthesia-definition>" \
  --repo "<canonical-custody-root>" --format json
ledger transact --definition "<synesthesia-definition>" \
  --operation capture --repo "<canonical-custody-root>" \
  --input submission="<file|->" --format json
```

Retain the canonical transaction result and exact returned `SYN-*` ID. Capture
once; reuse a successful identity instead of capturing again during handoff.
Existing stores require explicit, separately authorized `bind-existing` only
where appropriate under `$ledger`; normal operations never bind implicitly.
Existing immutable notes remain valid source evidence and are not imported into
or rewritten as canonical events.

## Same-turn derived admission

When global memory admission is warranted, load `$memory-source-notes` and use
its source-bound `synesthesia_memory_note.py admit` command with the exact
canonical custody and returned `SYN-*` ID. It derives the logical kind from the
canonical event, validates the source and note envelopes, resolves relationships,
and invokes the sole immutable writer. Do not pipe unresolved `SYN-*`
relationships directly to the low-level `append` command.

The adapter reuses an existing exact validated snapshot, including compatible
older snapshots, without rewriting it. It does not infer correspondence from a
phrase, substring, timestamp alone, or aesthetic similarity. Historical admission
requires the source owner's independent eligibility decision. A read-only
`inspect-admission` command exposes the prepared transport and any identity gap.

## Results and promotion

Report canonical and derived outcomes separately when persistence matters:

```text
canonical capture: created | duplicate | failed
memory admission: not warranted | created | duplicate | failed
digest: unchanged | refreshed | degraded
```

These are distinctions, not mandatory headings. Preserve the real canonical
receipt and the writer's real proof line. A note or digest failure never rolls
back canonical success; digest failure never invalidates an admitted note. Do
not report ordinary diagnostic no-ops as persistence failures.

The generated current-state digest is disposable and non-canonical. It folds
assert/confirm/supersede/reject/retract/reopen histories, preserving inactive,
invalid, and unresolved entries. Every promotable entry must retain resolvable
`source_note_ids`; the digest's fingerprint must match the current immutable
notes. Phase 2 owns promotion and compiled memory. Use `$memory-source-notes` for
refresh, copy-based instruction synchronization, doctor, and reconciliation;
never hand-author notes or edit compiled memory as a fallback.
