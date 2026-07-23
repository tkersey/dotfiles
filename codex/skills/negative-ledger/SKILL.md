---
name: negative-ledger
description: "Implicitly invoke when implementation, debugging, review, or validation encounters a witnessed failed/no-effect attempt, benchmark or test regression, revert, repeated same-cluster retry, abandoned strategy, or asks what has already been tried. Query/map before repeating a route; capture only inspectable decision-shaping negative evidence through the repo-local `ledger` source API; reopen only after proved applicability changes; selectively admit complete projections to Codex memory."
metadata:
  version: "7.0.0"
---

# Negative Ledger

## Mission

Prune semantic search space without turning stale failures into permanent dogma.

The operational authority is:

```text
ledger --source negative-ledger
```

Source-less Negative Ledger commands remain compatible, but the source
namespace is canonical for shared coordination.

`.ledger/negative-ledger/events.jsonl` is the current persistent-adapter
location, retained for path compatibility and legacy migration.

The memory-admission channel is:

```text
~/.codex/memories/extensions/negative-ledger/notes/*.md
```

`ledger` decides current negative-evidence state. `memory-note` transports an immutable exported projection to Phase 2. Phase 2 decides whether to compile a route constraint, routing trigger, or reusable memory skill.

Never use memory notes as the operational route gate. For accepted admission, load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Trigger Cues

- `$negative-ledger`;
- failed attempts, no-effect attempts, reverts, benchmark or test regressions;
- repeated semantic routes or same-cluster retries;
- strategy pivots that abandon a concrete route future work might repeat;
- "what have we already tried?";
- "do not retry this route";
- route reopening after artifact-state changes;
- fixed-point or review-governor negative evidence;
- memory admission of an active/stale/reopened/superseded `NEG-*` projection.

## Activation Policy

Activation is broad; capture is narrow.

Invoke this skill implicitly when current work may change route selection because a concrete route failed, had no effect, regressed a signal, was reverted, was rejected by current proof/review evidence, or is about to be retried under the same cluster. Do not wait for the user to literally name `$negative-ledger`.

Before selecting a route that resembles a prior failure, query or map the canonical ledger. A recalled `$learnings` row may trigger this check, but it cannot block directly.

After a material strategy pivot, regression-confirmed revert, or closeout that leaves a failed route likely to recur, evaluate capture. A transient red test, syntax error, first incomplete implementation, or discarded local typo is `no-op` unless it exposes a durable failed hypothesis that changes future routing.

Retain exactly one internal disposition for each material activation:

```text
mapped       current ledger checked; no write required
captured     witnessed negative evidence appended
transitioned existing NEG record changed lifecycle state
no-op        activation evaluated; evidence was not durable or route-shaping
blocked      ledger unavailable/invalid or active exact/applicable exclusion matched
```

## Ledger checkpoint participant

When invoked with `checkpoint_context=source-memory-checkpoint/v1`, consume the
coordinator's existing Ledger readiness and shared evidence packet. Do not
rerun `$ledger ensure`, invoke `$ledger` as lifecycle coordinator, or call
Learnings or Synesthesia.

This lifecycle evaluation is distinct from the pre-route map. Normal successful
work with no failed, no-effect, regressed, reverted, or abandoned route returns
`no-op` without querying or doctoring the store. When the packet contains
qualified negative evidence, apply the existing narrow capture or transition
gate and return exactly one of `mapped|captured|transitioned|no-op|blocked`.
Continue to require current artifact identity, exact source references,
applicability, a narrow exclusion, and reopening criteria.

Return one separate admission disposition after a capture or transition. Use
`created` or `duplicate-skip` only after the complete current native projection
passes the recurrence/utility gate; use `not-eligible` for a complete but
non-reusable projection, `not-applicable` when no canonical write or transition
occurred, and `blocked` when required export, validation, topology, or transport
fails. Never admit `need-evidence`, `capture_candidate`, or an incomplete active
projection. Admission failure does not change canonical capture or transition
success.

## Canonical Store and CLI

Before the first native Ledger command in this workflow, load `$ledger` and complete `$ledger ensure`. After readiness, invoke `ledger` directly.

This hardened standalone contract requires Ledger 0.7.0 or newer. The uniform
source namespace and lifecycle participant require Ledger 0.10.0 or newer;
the coordinator probes that version before checkpoint fan-out.

Immediately observe the native compatibility boundary:

```bash
ledger --version
```

If the reported version is older than 0.7.0, unparseable, or unavailable, retain `blocked` and do not invoke `map`, `capture`, `status`, `reopen`, `export`, or `handoff`. The `$ledger ensure` receipt proves command availability only; it does not prove version compatibility.

```text
ledger
```

Use native Ledger commands for ordinary reads, writes, and diagnostics. Do not
open the persistent adapter directly.

Expected commands:

```text
ledger init --source negative-ledger
ledger --version
ledger capture --source negative-ledger --json FILE|-
ledger query --source negative-ledger
ledger map --source negative-ledger --route ID --cluster ID --artifact ID [scope selectors]
ledger show --source negative-ledger --id NEG-ID
ledger handoff --source negative-ledger
ledger compact --source negative-ledger
ledger doctor --source negative-ledger
ledger export --source negative-ledger --id NEG-ID [--format full|memory-note]
ledger status --source negative-ledger --id NEG-ID --to STATUS --json transition.json
ledger reopen --source negative-ledger --id NEG-ID --json reopen-proof.json
```

`ledger export` is the only authoritative projection surface for memory admission. Never reconstruct a projection from the concise `ledger show` output.

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

For review-driven repair, apply the owner boundary in
[counterexample-construction-integration.md](references/counterexample-construction-integration.md).

1. Identify `repository_id`, immutable `artifact_state_id`, human-readable `artifact_state_label`, route, cluster, declared scope, target signal, and changed surface.
2. Run:

   ```bash
   ledger map --source negative-ledger \
     --route "<selected-route>" \
     --cluster "<cluster-id>" \
     --artifact "<artifact-state-id>"
   ```

3. Interpret exit codes: `0` no active exact exclusion, `2` active exact/applicable exclusion, `3` ledger unavailable or invalid.
4. Use the selector for the declared scope: `--route`, `--route-family`, `--cluster`, `--authority-model`, `--distinction-pattern`, or `--proof-pattern`. Ledger supports the exact, route, route-family, cluster, authority-model, distinction-pattern, and proof-pattern scopes.
5. Treat fuzzy candidates as search hints only.
6. Re-check current applicability before route suppression.
7. Ledger resolves symbolic Git refs such as `HEAD` to a full commit and retains the input only as `artifact_state_label`; reject empty or unresolved identities.

## Capture Workflow

Capture only when a failure changes future routing: witnessed no-effect attempt, local/global regression, unsound route, complexity disproportionate to value, revert with concrete rationale, repeated proof-wound pattern, or a strategy pivot whose abandoned route would otherwise be retried.

Append only through:

```bash
ledger capture --source negative-ledger --json capture.json
```

Captures without adequate witness evidence must become `need-evidence` or `capture_candidate`, never active exclusions.

An active capture requires an explicit supported scope and its identity, an immutable artifact identity, structured source references, applicability conditions, a narrow exclusion rule, and identified reopening criteria. Let Ledger downgrade an incomplete active request to `need-evidence`; do not repair or reinterpret the projection in prose.

## Lifecycle Transitions

Use append-only status events. Every transition requires a JSON proof packet with a reason and structured source references:

```json
{
  "reason": "The prior evidence was accepted as a bounded risk.",
  "source_refs": [
    {"kind": "review", "ref": "PR 123 acceptance"}
  ]
}
```

```bash
ledger status --source negative-ledger \
  --id NEG-000001 \
  --to accepted_risk \
  --json transition.json
```

Reopening requires a proved before/after change for an identified criterion already present on the record:

```json
{
  "reason": "The implementation and representative fixture changed.",
  "criterion_changes": [
    {
      "criterion_id": "artifact-or-fixture-changed",
      "before": "commit abc123 with fixture v1",
      "after": "commit def456 with fixture v2"
    }
  ],
  "source_refs": [
    {"kind": "git", "ref": "commit:def456"},
    {"kind": "test", "ref": "zig build test-ledger --summary all"}
  ]
}
```

```bash
ledger reopen --source negative-ledger --id NEG-000001 --json reopen-proof.json
```

Ledger rejects illegal edges, proofless promotion, unknown criteria, and unchanged before/after claims before append.

Never rewrite old events.

## Memory Admission Gate

A negative-ledger source note is allowed only when:

1. a canonical `NEG-*` record exists;
2. `ledger doctor` passes;
3. `ledger export --id` returns a complete current projection;
4. projection includes witness, applicability, narrow exclusion, and reopening criteria when status is active;
5. the record is likely to matter in future related work;
6. the note embeds the full bounded projection, stable repository identity, event-chain fingerprint, projection fingerprint, and any prior projection link.

Do not admit prose-only negative-evidence claims, unpromoted `learnings` hits, partial `ledger show` output, every `need-evidence` candidate, or stale history with no future routing value.

## Admission Workflow

After the source owner accepts admission for a capture or lifecycle transition,
load `$memory-source-notes` and use the validated Negative Ledger adapter:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/negative_ledger_memory_note.py \
  admit \
  --id NEG-000001 \
  --kind ledger-projection
```

For a status transition:

```bash
uv run python \
  codex/skills/memory-source-notes/scripts/negative_ledger_memory_note.py \
  admit \
  --id NEG-000001 \
  --kind ledger-status-transition
```

The adapter runs the source doctor, obtains the authoritative native export,
rejects incomplete projections, preserves the deterministic export bytes, and
invokes `memory-note` idempotently. It transports an accepted source decision;
it does not decide recurrence, utility, or route applicability.

If `ledger export` is unavailable, preserve the canonical ledger write and report:

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

The learning source is historical candidate evidence, not the route-exclusion
store. Legacy `.ledger/learnings/learnings.jsonl` and `.learnings.jsonl` are
read only during migration. Verify current applicability and promote
qualifying evidence through `ledger capture`.

## Guardrails

- Do not record vibes as negative evidence.
- Do not convert one failed implementation into a broad strategy ban.
- Do not block from fuzzy matches.
- Do not use stale benchmarks without current applicability reasoning.
- Do not treat absence of a ledger entry as novelty proof.
- Do not bypass Ledger or hand-edit persistent-adapter records.
- Do not let memory notes outrank the repo-local ledger.
- Do not write compiled memory directly.
- Do not publish incomplete projections to Phase 2.
- Do not capture every transient test failure merely because implicit activation occurred.
- Do not bypass failed validation in `map`, `export`, or `handoff`; those boundaries must fail closed.
- In checkpoint context, do not invoke the coordinator or a sibling participant.
