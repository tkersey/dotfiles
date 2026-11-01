# Counterexample Corpus

Normative when Review Fold accepts a current witness as a counterexample to an
accepted law.

## Purpose

Persist the monotone semantic evidence that Actuating exists to compile:

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

Actuating
  reprojects current applicability, recurrence, family, owner, cut, carrier,
  route, and closure from the corpus plus current owner facts
```

A stored row never proves that the witness remains applicable or belongs to the
current family. Persist counterexamples; recompile their meaning.

## Effect authority

New semantic capture requires `corpus_write_authorized: true` from the enclosing
task. Omitted or false authority permits projection and adjudication, not
`ledger transact --operation capture`, provisioning, or source-memory writes.
Actuating `analyze` always supplies false. This flag does not gate Ledger's
automatic custody preparation, including its native maintenance transactions.
Prepare custody before projection or capture without requesting separate approval.
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
complete `$ledger ensure` once.

Resolve the personal context through Ledger's canonical-custody guidance and use
its `native_args` for every corpus operation. Preserve existing repository IDs
and witness provenance when projecting or retrying an earlier submission; moving
custody does not rename a semantic scope. New independent scopes may use the
context's stable `repository_id`.

Use the `ledger_home` selected by the Ledger skill body. Ensure the owner automatically before the first corpus projection or capture,
including analysis with false or omitted `corpus_write_authorized`:

```bash
counterexample_definition="$(realpath \
  "${CODEX_HOME:-$HOME/.codex}/skills/review-fold/definitions/ledger/counterexample-corpus.json")"

ledger context --catalog-root "$ledger_home" --workspace "<workspace-root>" \
  --ensure-owner --definition "$counterexample_definition" \
  --owner-manifest "$(dirname "$(dirname "$(dirname "$counterexample_definition")")")/migration.json"
```

This initializes new managed custody, migrates compatible current-format local
history, or restores missing bound bytes as needed, then returns the managed
`native_args`. It waits for active writers and rechecks the protected source
before publication. Retain the source bytes and original IDs; never continue
normal corpus operations against a local store because migration or repair failed.

Ledger's [owner upgrade guidance](../../ledger/references/automatic-migration.md#automatic-owner-upgrade)
owns selection, migration, repair, locking, and refusal rules. Routine preparation
is part of using the corpus and requires no separate migration authorization,
confirmation, or user-maintained checklist. Unknown or conflicting
history still cannot be invented or discarded to force success.

Only when the user explicitly prohibits file/custody maintenance or the environment
enforces non-writable access, use `--read-only --definition` instead of
`--ensure-owner`. It selects intact managed history without creating, migrating,
or repairing anything. Report unavailable history under that constraint; an
analysis route or false capture flag alone does not select this mode.

## Project before folding

Project the repository basis before current classification:

```bash
counterexample_definition="$(realpath \
  "${CODEX_HOME:-$HOME/.codex}/skills/review-fold/definitions/ledger/counterexample-corpus.json")"

ledger project \
  --definition "$counterexample_definition" \
  --projection basis \
  --store-root "<context.store_root>" --store-id "<context.store_id>" \
  --param "repository=<repository-id>" \
  --payload-only \
  --format json
```

Pass the projected rows as `relevant_prior_owner_evidence`. Re-check every row
against the current Goal, exact head, validity horizon, and source evidence.
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

With enclosing write authority, capture one record for each independent witness satisfying all of:

```text
corpus_write_authorized = true
current applicability = still-present | transformed-applicable
law authority = entailed
disposition = accepted
Counterexample admission established validity and current Goal relevance
owner-issued evidence and original subject are exact
```

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
false. It is visible semantic-memory loss. Actuating may continue from the
current in-context evidence only when it does not claim complete historical
recurrence or elimination from the missing corpus.

## Anti-ceremony falsifier

Narrow or delete the corpus if watched use shows that it merely copies CAS
prose, agents still reason only from the latest wave, persisted interpretation
becomes stale authority, capture bookkeeping dominates the review, or runs with
and without the corpus select materially equivalent constructions.

It earns permanence when later sessions recover prior independent witnesses,
recognize same-family recurrence, compile broader constructions sooner, and
safely retire wound-specific code while preserving why it once existed.
