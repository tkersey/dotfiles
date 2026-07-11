---
name: negative-ledger
description: "Durably capture, query, map, transition, compact, export, and hand off witnessed negative evidence in repo-local `.ledger/negative-ledger/events.jsonl`; selectively admit full ledger projections to Codex memory through memory-source-notes. Use for failed semantic routes, benchmark regressions, no-effect attempts, reverts, route exclusions, reopening, or search-space pruning."
metadata:
  version: "6.0.0"
---

# Negative Ledger

## Mission

Prune semantic search space without turning stale failures into permanent dogma.

The operational truth is:

```text
<repo>/.ledger/negative-ledger/events.jsonl
```

The memory-admission channel is:

```text
~/.codex/memories/extensions/negative-ledger/notes/*.md
```

The native `ledger` kernel decides current negative-evidence state; `$ledger`
owns runtime mediation. `memory-note` transports an immutable exported
projection to Phase 2. Phase 2 decides whether to compile a route constraint,
routing trigger, or reusable memory skill.

Never use memory notes as the operational route gate. For accepted admission, load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Trigger Cues

- `$negative-ledger`;
- failed attempts, no-effect attempts, reverts, benchmark regressions;
- repeated semantic routes or same-cluster retries;
- "what have we already tried?";
- "do not retry this route";
- route reopening after artifact-state changes;
- fixed-point or review-governor negative evidence;
- memory admission of an active/stale/reopened/superseded `NEG-*` projection.

## Canonical Store and CLI

```text
.ledger/negative-ledger/events.jsonl
$ledger run -- <negative-ledger command>
```

Expected commands:

```text
$ledger run -- init
$ledger run -- capture --json FILE|-
$ledger run -- query
$ledger run -- map --route ID --cluster ID --artifact ID
$ledger run -- show --id NEG-ID
$ledger run -- handoff
$ledger run -- compact
$ledger run -- doctor
$ledger run -- export --id NEG-ID [--format full|memory-note]
$ledger run -- status --id NEG-ID --to STATUS --reason TEXT [--source-ref ...]
```

Until `export` ships, do not create authoritative memory admission from a lossy
`$ledger run -- show` projection.

## Valid Statuses

```text
capture_candidate
need-evidence
unknown
active
accepted_risk
stale
reopened
superseded
```

Only `active` can block, and only when witness evidence exists, exclusion scope is valid, applicability still matches the current artifact state, and the route/cluster match is exact enough for the declared scope.

Fuzzy or lexical overlap is suggest-only.

## Query/Map Workflow

1. Identify `artifact_state_id`, route, cluster, scope, target signal, and changed surface.
2. Run:

   ```text
   $ledger run -- map \
     --route "<selected-route>" \
     --cluster "<cluster-id>" \
     --artifact "<artifact-state-id>"
   ```

3. Interpret exit codes: `0` no active exact exclusion, `2` active exact/applicable exclusion, `3` ledger unavailable or invalid.
4. Treat fuzzy candidates as search hints only.
5. Re-check current applicability before route suppression.

## Capture Workflow

Capture only when a failure changes future routing: witnessed no-effect attempt, local/global regression, unsound route, complexity disproportionate to value, revert with concrete rationale, repeated proof-wound pattern, or a strategy pivot whose abandoned route would otherwise be retried.

Append only through:

```text
$ledger run -- capture --json capture.json
```

Captures without adequate witness evidence must become `need-evidence` or `capture_candidate`, never active exclusions.

## Lifecycle Transitions

Use append-only status events:

```text
$ledger run -- status \
  --id NEG-000001 \
  --to stale \
  --reason "The prior bookkeeping path was replaced." \
  --source-ref "commit:abc123"
```

Never rewrite old JSONL events.

## Memory Admission Gate

A negative-ledger source note is allowed only when:

1. a canonical `NEG-*` record exists;
2. `$ledger run -- doctor` passes;
3. `$ledger run -- export --id` returns a complete current projection;
4. projection includes witness, applicability, narrow exclusion, and reopening criteria when status is active;
5. the record is likely to matter in future related work;
6. the note embeds the full bounded projection and projection fingerprint.

Do not admit prose-only negative-evidence claims, unpromoted `learnings` hits,
partial `$ledger run -- show` output, every `need-evidence` candidate, or stale
history with no future routing value.

## Admission Workflow

After capture or lifecycle transition:

```text
$ledger run -- doctor
$ledger run -- export --id NEG-000001 --format memory-note
run_memory_note_tool append --extension negative-ledger \
  --kind ledger-projection --json <export-output>
```

For a status transition:

```text
$ledger run -- export --id NEG-000001 --format memory-note
run_memory_note_tool append --extension negative-ledger \
  --kind ledger-status-transition --json <export-output>
```

If `$ledger run -- export` is unavailable, preserve the canonical Ledger write and report:

```text
memory-note: not-attempted: ledger export unavailable
```

Do not reconstruct an authoritative projection from memory or prose.

## Proof Lines

Canonical write:

```text
ledger-capture: neg_id=NEG-... status=active
ledger-status: neg_id=NEG-... status=stale
ledger-capture: not-attempted: evidence not durable enough
```

Memory admission:

```text
memory-note: id=MSN-... extension=negative-ledger kind=ledger-projection status=created
memory-note: not-attempted: ledger export unavailable
memory-note: not-attempted: source admission gate not met
memory-note: not-attempted: cli unavailable
```

Report both layers separately.

## Learnings Relationship

`.ledger/learnings/events.jsonl` is historical candidate evidence, not the route-exclusion store. Legacy `.ledger/learnings/learnings.jsonl` and `.learnings.jsonl` are read only during migration. Verify current applicability and promote qualifying evidence through `$ledger run -- capture`.

## Guardrails

- Do not record vibes as negative evidence.
- Do not convert one failed implementation into a broad strategy ban.
- Do not block from fuzzy matches.
- Do not use stale benchmarks without current applicability reasoning.
- Do not treat absence of a ledger entry as novelty proof.
- Do not hand-edit `.ledger/negative-ledger/events.jsonl`.
- Do not let memory notes outrank the repo-local ledger.
- Do not write compiled memory directly.
- Do not publish incomplete projections to Phase 2.
