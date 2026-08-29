---
name: negative-ledger
description: "Implicitly invoke when implementation, debugging, review, or validation encounters a witnessed failed/no-effect attempt, benchmark or test regression, revert, repeated same-cluster retry, abandoned strategy, or asks what has already been tried. Project the route gate before repeating a route; transact only inspectable decision-shaping negative evidence through the passive Negative Evidence definition; reopen only after proved applicability changes; selectively admit complete projections to Codex memory."
metadata:
  version: "8.1.1"
---

# Negative Ledger

## Mission

Prune semantic search space without turning stale failures into permanent dogma.

The structural boundary is the passive definition:

```text
${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json
```

The selected definition exclusively addresses the canonical store at
`.ledger/negative-ledger/events.jsonl`, and every operation or projection is
explicit.

The memory-admission channel is:

```text
~/.codex/memories/extensions/negative-ledger/notes/*.md
```

`$negative-ledger` owns the meaning and lifecycle of current negative-evidence
state. Ledger structurally replays the declared protocol and projects that
state without acquiring its semantic authority. `memory-note` transports an
immutable projection to Phase 2. Phase 2 decides whether to compile a route
constraint, routing trigger, or reusable memory skill.

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

Before selecting a route that resembles a prior failure, project the canonical
`route-gate`. A recalled `$learnings` row may trigger this check, but it cannot
block directly.

After a material strategy pivot, regression-confirmed revert, or closeout that leaves a failed route likely to recur, evaluate capture. A transient red test, syntax error, first incomplete implementation, or discarded local typo is `no-op` unless it exposes a durable failed hypothesis that changes future routing.

Retain exactly one internal disposition for each material activation:

```text
mapped       current ledger checked; no write required
captured     witnessed negative evidence appended
transitioned existing NEG record changed lifecycle state
no-op        activation evaluated; evidence was not durable or route-shaping
blocked      ledger unavailable/invalid or active exact/applicable exclusion matched
```

A material closeout with no failed-route semantics does not activate this
source. Do not query, doctor, or capture merely to manufacture a no-op receipt.

## Canonical Store and CLI

Before the first Ledger command in this workflow, load `$ledger` and complete
`$ledger ensure` once. Require Ledger major version 1 and
`ledger-artifact-abi/v1`:

```bash
ledger version
ledger capabilities --format json
```

Set the canonical definition once:

```bash
negative_ledger_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json")"
```

Use only:

```text
ledger definition check --definition DEFINITION
ledger transact --definition DEFINITION --operation capture|promote|transition|bind-existing|rebind-existing --repo REPO
ledger project --definition DEFINITION --projection current-records|route-gate|memory-note --repo REPO
ledger doctor --definition DEFINITION --repo REPO
```

`ledger project --projection memory-note` is the authoritative source payload
for memory admission. Never reconstruct it from a summary projection.

Bind a pre-cutover current-format store exactly once before ordinary reads or
writes. This validates every existing row and records the selected definition
digest without rewriting the event log:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation bind-existing \
  --repo "<repo-root>" \
  --format json
```

When an authoritative external transport replaces an already-bound store and
`ledger doctor` reports a stale binding, use the separate one-shot custody
operation. It validates the complete current event log and replaces only the
binding metadata:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation rebind-existing \
  --repo "<repo-root>" \
  --format json
```

Do not use rebind to choose between divergent ledgers or to bless an unknown
store. Establish the authoritative transport and preserve the losing lineage as
an explicit reconciliation input before rebinding.

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

## Route-Gate Workflow

For review-driven repair, apply the owner boundary in
[counterexample-construction-integration.md](references/counterexample-construction-integration.md).

1. Identify `repository_id`, immutable `artifact_state_id`, human-readable `artifact_state_label`, route, cluster, declared scope, target signal, and changed surface.
2. Run:

   ```bash
   ledger project \
     --definition "$negative_ledger_definition" \
     --projection route-gate \
     --repo "<repo-root>" \
     --param "artifact=<artifact-state-id>" \
     --param "identity=<declared-scope-identity>" \
     --format json
   ```

3. Interpret exit codes: `0` no active exact exclusion, `2` active exact/applicable exclusion, `3` ledger unavailable or invalid.
4. Pass the identity selected by the record's declared exact, route, route-family, cluster, authority-model, distinction-pattern, or proof-pattern scope.
5. Treat fuzzy candidates as search hints only.
6. Re-check current applicability before route suppression.
7. Resolve symbolic Git refs before the call, pass the immutable identity as `artifact`, and retain the human-readable source as `artifact_state_label` in capture data.

## Capture Workflow

Capture only when a failure changes future routing: witnessed no-effect attempt, local/global regression, unsound route, complexity disproportionate to value, revert with concrete rationale, repeated proof-wound pattern, or a strategy pivot whose abandoned route would otherwise be retried.

Append only through:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation capture \
  --repo "<repo-root>" \
  --input capture=capture.json \
  --format json
```

Captures without adequate witness evidence must become `need-evidence` or `capture_candidate`, never active exclusions.

`capture.json` contains one `record` object, including its requested initial
`status`. An active capture requires an explicit supported scope and its
identity, an immutable artifact identity, structured source references,
applicability conditions, a narrow exclusion rule, and identified reopening
criteria. Select `need-evidence` before transaction when those structural
requirements are incomplete; never assert `active` in prose after Ledger
rejects it.

Every transition to `active`, including promotion, reactivation, and
reopening, requires the transition proof plus the complete replacement record,
whose `status` is `active`. Use the dedicated operation so the event atomically
replaces the reducer's retained record:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation promote \
  --repo "<repo-root>" \
  --input promotion=promotion.json \
  --format json
```

## Lifecycle Transitions

Use append-only status events. Every transition requires a JSON proof packet with a reason and structured source references:

```json
{
  "neg_id": "NEG-000001",
  "from": "active",
  "to": "accepted_risk",
  "reason": "The prior evidence was accepted as a bounded risk.",
  "criterion_ids": [],
  "criterion_changes": [],
  "source_refs": [
    {"kind": "review", "ref": "PR 123 acceptance"}
  ]
}
```

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation transition \
  --repo "<repo-root>" \
  --input transition=transition.json \
  --format json
```

Reopening requires a proved before/after change for an identified criterion already present on the record:

```json
{
  "neg_id": "NEG-000001",
  "from": "stale",
  "to": "reopened",
  "reason": "The implementation and representative fixture changed.",
  "criterion_ids": ["artifact-or-fixture-changed"],
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
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation transition \
  --repo "<repo-root>" \
  --input transition=reopen-proof.json \
  --format json
```

Ledger rejects illegal edges, promotion without a complete active record,
unknown criteria, and unchanged before/after claims before append.

Never rewrite old events.

## Memory Admission Gate

A negative-ledger source note is allowed only when:

1. a canonical `NEG-*` record exists;
2. definition-bound `ledger doctor` passes;
3. `ledger project --projection memory-note --param id=NEG-ID` returns a complete current projection;
4. projection includes witness, applicability, narrow exclusion, and reopening criteria when status is active;
5. the record is likely to matter in future related work;
6. the note embeds the full bounded projection, stable repository identity, event-chain fingerprint, projection fingerprint, and any prior projection link.

Do not admit prose-only negative-evidence claims, unpromoted `learnings` hits,
partial `current-records` output, every `need-evidence` candidate, or stale
history with no future routing value.

## Admission Workflow

After the source owner accepts admission for a capture or lifecycle transition,
load `$memory-source-notes` and use the validated Negative Ledger adapter:

```bash
uv run codex/skills/memory-source-notes/scripts/negative_ledger_memory_note.py \
  admit \
  --id NEG-000001 \
  --kind ledger-projection
```

For a status transition:

```bash
uv run codex/skills/memory-source-notes/scripts/negative_ledger_memory_note.py \
  admit \
  --id NEG-000001 \
  --kind ledger-status-transition
```

The adapter runs the definition-bound doctor, obtains the source-owned
projection, rejects incomplete projections, preserves the deterministic
projection payload bytes, and invokes `memory-note` idempotently. It transports
an accepted source decision; it does not decide recurrence, utility, or route
applicability.

If the definition projection is unavailable, preserve the canonical Ledger transaction and report:

```text
memory-note: not-attempted: ledger projection unavailable
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
memory-note: not-attempted: ledger projection unavailable
memory-note: not-attempted: source admission gate not met
memory-note: not-attempted: cli unavailable
```

Report both layers separately.

## Learnings Relationship

The learning source is historical candidate evidence, not the route-exclusion
store. Legacy `.ledger/learnings/learnings.jsonl` and `.learnings.jsonl` are
read only during migration. Verify current applicability and promote
qualifying evidence through the definition's `capture` transaction.

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
- Do not bypass failed `route-gate`, `memory-note`, or doctor projections; those boundaries must fail closed.
- Do not invoke a sibling source merely because Negative Ledger activated.
