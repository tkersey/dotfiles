---
name: memory-source-notes
description: "Safely append, inspect, and validate typed source-evidence notes for controlled Codex memory extensions. Use only after a handoff from harness-memory, learnings, negative-ledger, or synesthesia, or an explicit custom source capture request. Never edits compiled memory."
metadata:
  version: "1.0.0"
---

# Memory Source Notes

## Mission

Provide one generalized, append-only write path for controlled custom memory sources while preserving domain authority and Phase 2's compiler boundary.

This skill writes source evidence only:

```text
~/.codex/memories/extensions/<extension>/notes/*.md
```

It never writes:

```text
~/.codex/memories/memory_summary.md
~/.codex/memories/MEMORY.md
~/.codex/memories/skills/*
```

## Authority Model

```text
source skill / canonical domain store
  -> memory-note admission snapshot
  -> extension instructions.md interpretation
  -> Phase 2 consolidation
  -> compiled memory
```

- `learnings` owns `.learnings.jsonl`.
- `ledger` owns `.ledger/negative-ledger.jsonl`.
- `harness-memory` owns the evidence gate for durable operating corrections.
- `synesthesia` owns the evidence gate for mappings and activation boundaries.
- `memory-note` owns only safe immutable transport into the memory workspace.
- Phase 2 owns promotion, deduplication, supersession, and optional memory-root skill creation.

## Allowed Extensions

Only these custom sources are valid:

```text
harness
learnings
negative-ledger
synesthesia
```

Refuse `ad_hoc` and `chronicle`. Explicit user remember/forget/update requests belong to Codex's native ad-hoc path; Chronicle is upstream-owned and not controlled by this workflow.

## Trigger Cues

- explicit `$memory-source-notes`;
- a documented handoff from `$harness-memory`, `$learnings`, `$negative-ledger`, or `$synesthesia`;
- "record this in the harness memory source";
- "admit this learning to memory consolidation";
- "publish this negative-ledger projection to memory";
- "remember this endorsed synesthetic mapping";
- custom memory-source layout or writer diagnostics.

Do not trigger merely because a task produced ordinary history. The owning skill must first establish that the event meets its source-specific admission gate.

## CLI Discovery

Use this lightweight resolver:

```bash
run_memory_note_tool() {
  if command -v memory-note >/dev/null 2>&1; then
    memory-note "$@"
    return
  fi

  local repo="${SKILLS_ZIG_REPO:-$HOME/workspace/tk/skills-zig}"
  if [ -x "$repo/zig-out/bin/memory-note" ]; then
    "$repo/zig-out/bin/memory-note" "$@"
    return
  fi

  echo "memory-note: not-attempted: cli unavailable" >&2
  return 127
}
```

Do not silently install unreleased tooling. Never hand-author a note as a fallback for a missing CLI.

## Append Workflow

1. Receive an accepted payload from the owning skill.
2. Confirm the live memory root and extension directory are real directories, not symlinks.
3. Remove secrets, unnecessary local paths, raw transcript chronology, and unsupported inference.
4. Ensure `authority`, `scope`, `source_refs`, and `payload` are complete.
5. Run:

   ```bash
   run_memory_note_tool append \
     --extension <extension> \
     --kind <kind> \
     --json -
   ```

6. Capture the structured result.
7. Emit exactly one proof line.

## Proof Lines

Successful append:

```text
memory-note: id=MSN-... extension=<name> kind=<kind> status=created
```

Duplicate accepted as no-op:

```text
memory-note: duplicate-skip: extension=<name> fingerprint=<fingerprint>
```

No qualifying event:

```text
memory-note: not-attempted: source admission gate not met
```

Unavailable CLI:

```text
memory-note: not-attempted: cli unavailable
```

Unsafe topology or failed validation:

```text
memory-note: failed: <concise reason>
```

A memory-note failure must not undo a successful canonical `.learnings.jsonl` or `.ledger/negative-ledger.jsonl` write. Report both outcomes separately.

## Source-Specific Kinds

Harness:

```text
harness-rule
harness-confirmation
harness-supersession
harness-retraction
```

Learnings:

```text
learning-admission
learning-confirmation
learning-supersession
learning-withdrawal
```

Negative ledger:

```text
ledger-projection
ledger-status-transition
ledger-supersession
ledger-retraction
```

Synesthesia:

```text
mapping-endorsement
mapping-correction
mapping-rejection
activation-boundary
boundary-retraction
```

See [note-contract.md](references/note-contract.md) and [extension-payloads.md](references/extension-payloads.md).

## Read and Doctor Workflow

Use read-only operations for diagnostics:

```bash
run_memory_note_tool doctor
run_memory_note_tool doctor --extension negative-ledger
run_memory_note_tool list --extension harness
run_memory_note_tool show --extension negative-ledger --id MSN-...
```

## Privacy and Retrieval

Source notes can be exposed by broad read-only memory search even though normal runtime memory should route through compiled outputs. Never store credentials, tokens, private keys, raw chat logs, or long tool outputs.

## Non-Goals

Do not use this skill to:

- bypass the native ad-hoc remember/forget/update workflow;
- write compiled memory directly;
- replace `.learnings.jsonl` or `.ledger/negative-ledger.jsonl`;
- decide whether negative evidence blocks a route;
- infer user preferences from assistant-authored prose alone;
- capture ordinary chronology;
- write into Chronicle;
- delete or mutate previous source notes.
