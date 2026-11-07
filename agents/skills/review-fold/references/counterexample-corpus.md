# Counterexample Corpus

Normative when Review Fold accepts a current witness as a counterexample to an
accepted law.

## Purpose

Persist admitted counterexamples with their original authority and provenance:

```text
exact owner-issued observation
+ accepted Goal authority
+ original witness subject
-> admitted counterexample
```

The corpus is not a bug tracker, current Review Fold, family registry,
architecture store, or workflow control plane.

## Authority split

```text
Codex / host runtime / test / verifier / incident / provider
  owns what was observed and the exact source evidence

Review Fold
  owns the decision that the witness was current, entailed, and accepted
  when captured

review-fold/counterexample-corpus
  preserves that immutable semantic admission and provenance

The requesting task
  consumes the current fold and owner facts to decide any family, owner, cut,
  carrier, route, and closure within its authority; stored rows do not supply
  those decisions
```

A stored row never proves that the witness remains applicable or belongs to the
current family. Persist counterexamples; recompile their meaning.

## Effect authority

New semantic capture requires `corpus_write_authorized: true` from the enclosing
task. Omitted or false authority permits projection and adjudication, not
`ledger transact --operation capture`, provisioning, or source-memory writes.
The caller supplies false when its route does not authorize semantic capture.
This flag does not gate corpus reads or Ledger's required custody preparation,
including native maintenance transactions. Follow Ledger's read-first owner access
without requesting separate approval for needed preparation or exact restoration.
Corpus ownership cannot grant new semantic captures or unrelated effects.

With no capture authority, retain accepted witnesses in context and return empty
`captured_ids`; report non-persistence only when material to the handoff. This is
not a failed adjudication or a new workflow mode. Current claims use the available
source evidence; historical absence still needs a complete relevant horizon.

## Store and definition

```text
definition
  ${CODEX_HOME:-$HOME/.codex}/skills/review-fold/definitions/ledger/counterexample-corpus.json

logical slot in Ledger personal custody
  review-fold/counterexamples/events.jsonl
```

Before the first Ledger command in the enclosing workflow, load `$ledger` and
complete `$ledger ensure` with `--min-version 1.7.0` once.

Resolve the personal context through Ledger's canonical-custody guidance and use
its `native_args` for every corpus operation. Preserve existing repository IDs
and witness provenance when projecting or retrying an earlier submission; moving
custody does not rename a semantic scope. New independent scopes may use the
context's stable `repository_id`.

Use the `ledger_home` selected by Ledger. Start a corpus read with its owner-read
route, including analysis with false or omitted `corpus_write_authorized`:

```bash
counterexample_owner="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/review-fold")"
counterexample_definition="$counterexample_owner/definitions/ledger/counterexample-corpus.json"
counterexample_manifest="$counterexample_owner/migration.json"

ledger context --catalog-root "$ledger_home" --workspace "<workspace-root>" \
  --read-only --definition "$counterexample_definition" \
  --owner-manifest "$counterexample_manifest"
```

Use the known `--store-id` instead when no workspace is selected. The
returned `native_args` select present, healthy custody without legacy-source
discovery. Ledger's [owner access](../../ledger/references/canonical-custody.md#owner-access)
owns the exact `OwnerPreparationRequired` and `StoreBindingWithoutSlot` routes.
When allowed, perform only that required preparation or restoration and retain
its result. Explicit no-maintenance constraints prevent those effects; analysis
or a false capture flag alone does not. Other failures remain blockers, never
permission to use a local store, invent empty history, or guess another selector.

## Project before folding

Project the repository basis before current classification:

```bash
ledger project \
  --definition "$counterexample_definition" \
  --projection basis \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --param "repository=<existing-semantic-repository-id>" \
  --format json
```

Retain the native result and selected context; pass its rows as
`relevant_prior_owner_evidence`. A supplied projection may be reused when its
selector, semantic repository scope, definition, and source state remain
applicable. Empty rows from the wrong scope do not establish an empty corpus.
If projection cannot run, retain the actual failed operation or explicit access
constraint in the existing missing-source fields. Merely declaring history
incomplete does not substitute for this outcome. Re-check every row against the
current Goal, exact head, validity horizon, and source evidence.
Absence from an incomplete horizon never proves `first-observed`, disjointness,
or family elimination.

An absent slot in an otherwise valid selected store is not proof that no historical
counterexamples exist. An invalid store or unresolved binding blocks claims
that depend on complete historical evidence. Use `bind-existing` or
`rebind-existing` only when the definition-bound doctor prescribes that exact
operation after validating the complete store.

Use `law-history` for a focused exact-law projection and `record` for one known
`CEX-*` identity.

## Capture after folding

Apply [Counterexample admission](../SKILL.md#counterexample-admission) before
capture. A structured finding or prior admission is not validation of its content.
Use existing authority/evidence references and bounded observed facts for the
supported claim; retain the original allegation through its source reference.
Do not persist rejected or unresolved claims as counterexamples, or add current
adjudication state to the immutable schema.

For a new current witness, enclosing write authority permits one record for each
independent witness satisfying all of the following. Completing a missed original
submission follows [delayed capture](#delayed-capture) instead of changing its
current applicability to satisfy this list.

```text
corpus_write_authorized = true
current applicability = still-present | transformed-applicable
law authority = entailed
disposition = accepted
Counterexample admission established validity and current Goal relevance
owner-issued evidence and original subject are exact
```

Before the first semantic capture, run Ledger's strict `--ensure-owner` with the
same selection, definition, and manifest. A successful read does not satisfy write
preparation or prove legacy writers have stopped. Use the returned managed
selector; retain semantic-capture failure separately from successful preparation.

```bash
ledger transact \
  --definition "$counterexample_definition" \
  --operation capture \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --input submission=<counterexample.json> \
  --format json
```

The semantic identity derives from repository, Goal digest, accepted law,
original witness subject, and observed fact. Reviewer, thread, file, suggested
repair, detection site, and current family are not identity. Duplicate reports
of the same semantic witness therefore do not become independent
counterexamples.

Store exact references and bounded summaries, not full transcripts, logs,
credentials, secrets, or speculative architecture.

## Delayed capture

With enclosing capture authority, complete a previously missed or interrupted submission
only after re-establishing that its original evidence and accepted Goal supported
admission against its original witness subject. Retain the original semantic
repository scope, law, observed fact, and provenance; inspect a known record or
prior result before retrying an uncertain append. The original semantic identity
makes the retry idempotent. Native `captured_at` records the actual append time.

A defect fixed since that admission may now be `already-excluded`; do not relabel
it as currently applicable or discard its admitted historical witness for that
reason. Current repair pressure still requires current applicability. This route
completes an evidenced original admission, not bulk import or acceptance of an
old report on its own authority. Missing or refuted original premises block capture.

## Durable fields

A record preserves only:

```text
repository identity
Goal digest under which the law was accepted
law and law provenance
authority basis references
source owner references
original witness subject
observed fact and detection boundary
evidence references
independence basis
capture identity and timestamp
```

Do not persist as authority:

```text
current applicability
observational class
causal generator
family membership
recurrence status
canonical owner
earliest enforceable cut
admitted carrier
mutation route
review credit
closure status
suggested repair
```

Those are current projections.

## Handoff

Return the current fold plus:

```yaml
counterexample_corpus:
  projected_ids: []
  captured_ids: []
  evidence_horizon_complete_for_claims: true | false
  missing_or_blocked_sources: []
```

A capture failure never rewrites the owner evidence or makes the current fold
false. It is visible semantic-memory loss. The requesting task may continue from
the current in-context evidence only when it does not claim complete historical
recurrence or elimination from the missing corpus.

## Anti-ceremony falsifier

Narrow or delete the corpus if watched use shows that it merely copies CAS
prose, agents still reason only from the latest wave, persisted interpretation
becomes stale authority, capture bookkeeping dominates the review, or runs with
and without the corpus select materially equivalent constructions.

It earns permanence when later sessions recover prior independent witnesses,
recognize same-family recurrence, compile broader constructions sooner, and
safely retire wound-specific code while preserving why it once existed.
