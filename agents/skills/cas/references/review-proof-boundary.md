# CAS Review Proof Boundary

[reviews.md](../reviews.md) is the operating contract for capability admission,
the built-in live gate, rubric-preserving invocation, receipt interpretation,
and same-handle recovery. This reference explains their evidence boundary;
it adds no second preflight or review procedure.

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

Use the [invocation and runtime guidance](../reviews.md#invocation-and-runtime).
The caller selects native/default or exact custom instructions; an omitted
rubric is intentional, not a missing argument to fill.

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

Apply [receipt interpretation](../reviews.md#receipt-interpretation) to the
actual owner-issued output, not a reconstructed summary.

The [normalized-clean example](../assets/start-wait-normalized-clean.example.json)
is a **partial illustrative projection**, not a complete admissible receipt.
It uses synthetic identities and omits required current-runtime compatibility
facts. Its `clean: true` does not establish review credit. Do not copy its
values into real evidence or treat schema/JSON validity as admission.

## Resumption

CAS owns durable attempt records, but Actuating maintains no review index.

Reuse only an exact known handle or exact receipt that can be fully
revalidated. If an interrupted Actuating run cannot resolve every receipt
required for its current wave and clean suffix, it starts a fresh full wave.
A summary or claimed count never substitutes for owner evidence.
