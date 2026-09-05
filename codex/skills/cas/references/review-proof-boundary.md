# CAS Review Proof Boundary

Before `cas review run` or `cas review start`, require:

```bash
cas app-server preflight --cwd <repo> --profile review \
  --app-server-transport managed-ws --json
cas capabilities --json
```

The exact resolved runtime must be compatible. Require
`cas_structured_review_v1: true`; workflow-bound starts additionally require
`cas_workflow_bound_owner_lived_review_v1: true` and owner-lived
`start --wait`.

## Evidence law

```text
a process is not a review
a parent thread is not a review
an attempt begins only when reviewThreadId exists
a semantic verdict exists only when the structured verdict binds the target
```

CAS owns:

- exact target selector and target fingerprint;
- instruction bytes;
- opaque workflow binding;
- review thread and turn;
- runtime, contract, transport, and principal facts;
- terminal semantic verdict or failure;
- finding provenance;
- durable attempt record.

The caller owns topology, lens meaning, review credit, finding truth,
classification, architecture, mutation, publication, and closure.

## Commands

Use `run` for a standalone one-off review. Use one owner-lived
`start --wait` process for an Actuating request. Use `wait` only for a known
already-started attempt.

```bash
cas review run --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json

cas review start --wait --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json
```

A live or pending exact handle is recovered with `wait`, not replaced. A
distinct same-target attempt after terminal evidence requires
`--fresh-attempt <source-bound-reason>`.

For post-publication review, use the exact bound base/head selector. A clean
checkout is not a reason to use `--uncommitted`.

The workflow binding remains opaque:

```json
{
  "requestId": "opaque-caller-id",
  "requestFingerprint": "sha256:..."
}
```

CAS echoes it and does not infer Actuating policy. The echo binds identity;
it does not deliver the hashed context or prove that a reviewer saw it.

Repository sources and references accessible through the existing review backend
are evidence; parent-only conversation premises are not implicitly inherited.
For a premise-dependent judgment, distinguish an accessible accepted source from
an opaque digest or an unresolved reference. The same diff under different
compatibility contracts cannot be distinguished by digest alone. Preserve any
material access limitation in the caller's existing evidence horizon, without
rewriting the owner verdict or asserting review of an undisclosed premise.
This clarification adds no context packet, prompt argument, review gate, attempt,
or retry. Native standard and exact auxiliary instruction bytes remain unchanged.

## Receipt interpretation

Actuating consumes the exact owner-issued CAS receipt directly. Require:

- receipt and verdict target tuples agree;
- expected base, head, and target fingerprint;
- exact workflow-binding echo;
- structured semantic status;
- strong principal and no reduced protection;
- backend class `cas-start-wait`;
- exact current runtime compatibility facts.

Do not pass the receipt through Ledger or copy it into an Actuating event log.
Structural parsing is not review credit; Actuating evaluates the exact fields
under its static Review Contract.

Missing structured output, provider failure, account exhaustion, fallback,
transport loss, stale tuple, or mismatched binding earns no semantic credit.

## Resumption

CAS owns durable attempt records, but Actuating maintains no review index.

Reuse only an exact known handle or exact receipt that can be fully
revalidated. If an interrupted Actuating run cannot resolve every receipt
required for its current wave and clean suffix, it starts a fresh full wave.
A summary or claimed count never substitutes for owner evidence.
