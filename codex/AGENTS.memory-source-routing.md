# AGENTS.md Memory-Source Routing Insertion

Merge these blocks manually into the matching sections of `codex/AGENTS.md`.

## Add Under Core Invariants

```md
- Treat custom memory-extension notes as append-only source evidence, not compiled memory and not runtime instructions.
- Preserve domain authority: `.learnings.jsonl` owns execution learnings; `.ledger/negative-ledger.jsonl` owns negative-evidence route state; `memory-note` only admits immutable snapshots to Phase 2.
- Never edit `memory_summary.md`, `MEMORY.md`, or memory-root `skills/*` directly during ordinary work. Explicit user-directed remember/forget/update requests use Codex's native ad-hoc memory path; custom source capture uses the owning skill plus `$memory-source-notes`.
```

## Add To Implicit Skills

```md
- `$memory-source-notes` - append-only custom memory-source capture only after a documented handoff from `$harness-memory`, `$learnings`, `$negative-ledger`, or `$synesthesia`, or when the user explicitly asks to record an event in one of those custom sources. It never writes compiled memory.
- `$harness-memory` - direct user correction or repeated steering about how Codex should operate, but only when the correction expresses a durable trigger/behavior/verification rule rather than tone, frustration, or one-off task detail.
```

## Add After The Learnings Lifecycle Section

````md
## Memory-source admission lifecycle

Use `memory-note` as the single safe writer for controlled custom memory sources:

```text
harness
learnings
negative-ledger
synesthesia
```

- `memory-note` creates immutable typed notes under `~/.codex/memories/extensions/<source>/notes/`.
- Do not use `memory-note` for `ad_hoc` or `chronicle`.
- Source skills own admission decisions and payload semantics.
- The `memory-source-notes` skill owns CLI syntax, path safety, proof lines, and failure behavior.
- Phase 2 owns promotion into `memory_summary.md`, `MEMORY.md`, and memory-root `skills/*`.
- A missing `memory-note` CLI must not block canonical domain capture. Complete `.learnings.jsonl` or `.ledger` writes first, then report `memory-note: not-attempted: cli unavailable`.
- Do not hand-write custom source notes as a fallback.

Admission thresholds:

- harness: explicit durable operating correction or repeated evidence-backed steering;
- learnings: `codify_now`, repeated theme, explicit durable user preference, or unusually high-value failure shield;
- negative-ledger: complete exported ledger projection or witnessed lifecycle transition; never prose-only exclusion claims;
- synesthesia: explicit endorsement/correction/rejection or repeated operationalized mapping/boundary.
````
