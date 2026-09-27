---
name: negative-ledger
description: "Implicitly invoke when implementation, debugging, review, or validation encounters a witnessed failed/no-effect attempt, benchmark or test regression, revert, repeated same-cluster retry, abandoned strategy, or asks what has already been tried. Project the route gate before repeating a route; transact only inspectable decision-shaping negative evidence through the passive Negative Evidence definition; reopen only after proved applicability changes; selectively admit complete projections to Codex memory."
metadata:
  version: "8.3.0"
---

# Negative Ledger

## Mission

Prune semantic search space without turning stale failures into permanent dogma.

The structural boundary is the passive definition:

```text
${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json
```

Its `events` logical slot in `$ledger`-resolved custody is canonical. The Ledger
skill alone owns physical storage location, worktree-family registration,
initialization, and migration policy. Do not derive a separate history from each
checkout. Worktrees share evidence, not automatic applicability or exclusions.

The derived memory-admission channel remains:

```text
~/.codex/memories/extensions/negative-ledger/notes/*.md
```

`$negative-ledger` owns the meaning and lifecycle of negative-evidence state.
Ledger replays/projects the declared protocol without semantic authority.
`memory-note` transports an immutable projection to Phase 2, which decides
whether to compile a route constraint, routing trigger, or reusable memory skill.

Never use memory notes as the operational route gate. For accepted admission,
load `$memory-source-notes` before invoking `run_memory_note_tool`.

## Trigger Cues

- `$negative-ledger`;
- failed/no-effect attempts, reverts, benchmark/test regressions;
- repeated semantic routes or same-cluster retries;
- strategy pivots abandoning a concrete route future work might repeat;
- "what have we already tried?" or "do not retry this route";
- route reopening after artifact-state changes;
- fixed-point or review-governor negative evidence;
- memory admission of active/stale/reopened/superseded `NEG-*` projections.

## Activation Policy

Activation is broad; capture is narrow.

Invoke implicitly when work may change route selection because a concrete route
failed, had no effect, regressed a signal, was reverted, was rejected by current
proof/review evidence, or is about to be retried under the same cluster. Do not
wait for the user to name the skill.

Before selecting a route resembling a prior failure, project canonical
`route-gate`. A recalled learning may trigger the check, not block directly.
After a material strategy pivot, regression-confirmed revert, or closeout leaving
a failed route likely to recur, evaluate capture. A transient red test, syntax
error, first incomplete implementation, or discarded typo is `no-op` unless it
exposes a durable failed hypothesis that changes future routing.

Retain exactly one internal disposition for each material activation:

```text
mapped       current ledger checked; no write required
captured     witnessed negative evidence appended
transitioned existing NEG record changed lifecycle state
no-op        activation evaluated; evidence was not durable or route-shaping
blocked      context/store unavailable or invalid, or an active applicable exclusion matched
```

A material closeout without failed-route semantics does not activate this source.
Do not resolve storage, query, doctor, or capture to manufacture a no-op receipt.

## Canonical Store and CLI

Load `$ledger` and complete `$ledger ensure` before the first native command.
Require Ledger 1.3.0 or newer within major version 1 and `ledger-artifact-abi/v1`.
Reuse unchanged readiness; recheck for changed executable/environment or selected
definition requirements.

```bash
negative_ledger_definition="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/negative-ledger/definitions/ledger/negative-evidence-protocol.json")"
```

Resolve the verified workspace through `$ledger`. Retain `store_root`, `store_id`,
`repository_id`, and `workspace_root`. Every canonical doctor, transaction, and
projection uses that managed selector, including memory admission. Only an
authorized first capture may initialize; reads cannot silently create a new
history. Legacy binding, rebinding, and cold adoption follow the Ledger skill's
exact maintenance policy, not per-worktree initialization or fallback readers.

Native surface:

```text
ledger definition check --definition DEFINITION
ledger transact --definition DEFINITION --operation capture|promote|transition|bind-existing|rebind-existing --store-root ROOT --store-id ID
ledger project --definition DEFINITION --projection current-records|route-gate|memory-note --store-root ROOT --store-id ID
ledger doctor --definition DEFINITION --store-root ROOT --store-id ID
```

`memory-note` is the authoritative admission payload. Never reconstruct it from
a summary projection. Do not use rebinding to select a divergent history or bless
an unknown replacement; preserve lineages for explicit owner reconciliation.

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

Only `active` may block: witness evidence, valid exclusion scope, current artifact
applicability, and exact-enough route/cluster matching are all required. Fuzzy or
lexical overlap is suggest-only.

## Route-Gate Workflow

For review-driven repair, apply the owner boundary in
[counterexample-construction-integration.md](references/counterexample-construction-integration.md).

1. Identify the resolved `repository_id`, immutable `artifact_state_id`, readable
   `artifact_state_label`, route, cluster, scope, target signal, and changed surface.
   For new captures, use the stable repository identity from Ledger context;
   branch/worktree paths are provenance. A commit alone does not identify relevant
   dirty code, fixtures, or configuration; use a supported immutable surface
   identity when those affect the claim.
2. Run:

   ```bash
   ledger project \
     --definition "$negative_ledger_definition" \
     --projection route-gate \
     --store-root "<context.store_root>" --store-id "<context.store_id>" \
     --param "artifact=<artifact-state-id>" \
     --param "identity=<declared-scope-identity>" \
     --format json
   ```

3. Interpret exit codes: `0` no active exact exclusion, `2` active exact/applicable
   exclusion, `3` canonical context/store unavailable or invalid. Never turn a
   failed managed lookup into an empty checkout-local gate.
4. Pass the identity for the declared exact, route, route-family, cluster,
   authority-model, distinction-pattern, or proof-pattern scope.
5. Treat fuzzy candidates as search hints only.
6. Recheck current applicability before suppression. A record inapplicable to
   this worktree does not, by itself, justify globally marking it stale/reopened
   for another artifact. Global lifecycle changes retain their proof obligations.
7. Resolve symbolic Git refs before the call. Pass immutable identity as
   `artifact`, retaining readable provenance in `artifact_state_label`.

## Capture Workflow

Capture only a failure that changes future routing: witnessed no-effect attempt,
local/global regression, unsound route, complexity disproportionate to value,
revert with concrete rationale, repeated proof-wound pattern, or a strategy pivot
whose abandoned route would otherwise be retried.

Before capture/promotion, apply the [scope challenge](#exclusion-scope-challenge).
A witnessed failure alone does not justify its breadth.

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation capture \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input capture=capture.json \
  --format json
```

`capture.json` contains one `record`, including requested initial `status`.
Inadequate witness evidence means `need-evidence` or `capture_candidate`, not an
active exclusion. Active capture requires supported scope/identity, immutable
artifact identity, structured source references, applicability conditions,
a narrow exclusion, and identified reopening criteria. Select `need-evidence`
when structure is incomplete; never assert `active` after Ledger rejects it.

Every transition to `active`, including promotion/reactivation/reopening,
requires transition proof and a complete replacement record with status `active`.
Use the dedicated operation to replace the reducer's retained record atomically:

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation promote \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input promotion=promotion.json \
  --format json
```

## Exclusion Scope Challenge

Ask whether a materially different realization of the excluded route could meet
the same requirement under declared applicability conditions. Distinguish a
failed implementation from a failed strategy; broader suppression requires a
stronger scope argument. Inspect existing witnesses/proofs first; use a
necessary, authorized discriminating evaluation when evidence is insufficient.
No fixed number of challenges or successful samples establishes a universal ban.

An inspectable success within the exclusion scope is counterevidence to its
breadth; success outside scope is not. Confirm the case exercises the disputed
route, uses an independently justified requirement as oracle, and isolates the
route rather than an invalid fixture or unrelated environment error. An imagined
alternative warrants scrutiny, not a claimed successful execution.

A successful sample alone does not refute a failure-rate, cost, or risk claim.
Evaluate counterevidence against the recorded hypothesis and measurement
conditions; contrary samples can warrant investigation without changing the
gate. Do not treat variable outcomes as deterministic impossibility proofs.

Use existing hypothesis, outcome, evidence, exclusion, applicability, and
reopening fields to retain the supported boundary. A stale cache entry may
justify excluding reuse when its key omits a semantic input, not all caching.
Choose the narrowest useful supported scope, retaining `need-evidence` or
`capture_candidate` when support is inadequate. Do not weaken active structure
just to make a transaction pass.

For counterevidence to an active record, preserve the gate until its legal
source-owned lifecycle changes it. Capture any still-supported narrower
exclusion before superseding an overbroad one, linking evidence/replacement with
structured source references. Reopening still requires proved changes to
identified existing criteria; an unjustified old conclusion is not a fabricated
artifact change. Use proof-bearing supersession when appropriate.

Scope review grants no retry/mutation permission. Do not bypass an active exact
applicable exclusion by calling the retry a test, sandbox, or experiment. Use
supported lifecycle and enclosing authority before retry; project the gate again.
An unchanged/inapplicable challenge requires no write. Stop when scope is
supported, narrowed, or pending evidence. Correcting an exclusion does not
activate Learnings automatically or grant architecture-selection authority.

## Lifecycle Transitions

Use append-only status events. Every transition requires JSON proof with reason
and structured source references:

```json
{
  "neg_id": "NEG-000001",
  "from": "active",
  "to": "accepted_risk",
  "reason": "The prior evidence was accepted as a bounded risk.",
  "criterion_ids": [],
  "criterion_changes": [],
  "source_refs": [{"kind": "review", "ref": "PR 123 acceptance"}]
}
```

```bash
ledger transact \
  --definition "$negative_ledger_definition" \
  --operation transition \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input transition=transition.json \
  --format json
```

Reopening requires a proved before/after change for a criterion already present:

```json
{
  "neg_id": "NEG-000001",
  "from": "stale",
  "to": "reopened",
  "reason": "The implementation and representative fixture changed.",
  "criterion_ids": ["artifact-or-fixture-changed"],
  "criterion_changes": [{
    "criterion_id": "artifact-or-fixture-changed",
    "before": "commit abc123 with fixture v1",
    "after": "commit def456 with fixture v2"
  }],
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
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input transition=reopen-proof.json \
  --format json
```

Ledger rejects illegal edges, promotion without a complete active record,
unknown criteria, and unchanged before/after claims before append. Never rewrite
old events. Concurrent worktrees do not weaken these transition preconditions.

## Memory Admission Gate

A source note is allowed only when:

1. a canonical `NEG-*` record exists;
2. definition-bound doctor passes in resolved canonical custody;
3. `memory-note --param id=NEG-ID` returns a complete current projection;
4. active projections include witness, applicability, exclusion, and reopening;
5. the record is likely to matter in future related work;
6. the note embeds the full bounded projection, stable repository identity,
   event-chain/projection fingerprints, and any prior projection link.

Do not admit prose-only claims, unpromoted Learnings hits, partial
`current-records` output, every `need-evidence` candidate, or stale history with
no future routing value.

## Admission Workflow

After the source owner accepts admission, load `$memory-source-notes` and resolve
its installed root independently of the target repository:

```bash
memory_source_notes_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/memory-source-notes")"
```

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --repo "<workspace-root>" \
  --id NEG-000001 \
  --kind ledger-projection
```

For a status transition:

```bash
uv run "$memory_source_notes_root/scripts/negative_ledger_memory_note.py" \
  admit \
  --repo "<workspace-root>" \
  --id NEG-000001 \
  --kind ledger-status-transition
```

The adapter's `--repo` identifies the evidence workspace. It delegates custody
resolution to `$ledger` and passes the managed selector to native doctor/project;
it must not use that workspace as the native storage address. It rejects
incomplete projections, preserves deterministic payload bytes, and invokes the
immutable writer idempotently. It transports an accepted decision, not a judgment
about recurrence, utility, or route applicability.

If context/projection is unavailable, preserve any successful canonical transaction:

```text
memory-note: not-attempted: ledger projection unavailable
```

Do not reconstruct authority from memory/prose, fall back to local history, or
rewrite old immutable notes/provenance during adoption.

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

Report the layers separately.

## Learnings Relationship

Learnings are historical candidate evidence, not route exclusions. Retired source
stores are addressed only during owner-authorized recovery. Verify current
applicability and promote qualifying evidence through canonical `capture`.

## Guardrails

- Do not record vibes or turn one failed implementation into a broad strategy ban.
- Do not block from fuzzy matches or use stale benchmarks without applicability.
- Do not treat absence of an entry as novelty proof.
- Do not bypass Ledger, hand-edit records, or use a checkout-local fallback.
- Do not let memory notes outrank canonical custody or write compiled memory.
- Do not publish incomplete projections or capture every transient red test.
- Failed context, route-gate, memory-note, or doctor boundaries fail closed.
- Do not invoke sibling sources merely because Negative Ledger activated.

For exclusion-scope changes, use Negative Ledger cases in
[validation-probes.md](../learnings/validation-probes.md). These are package
validation, not a runtime dependency or activation of Learnings.
