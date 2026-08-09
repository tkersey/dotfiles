# CAS review proof boundary

Before `cas review run` or `cas review start`, require:

```bash
cas app-server preflight --cwd <repo> --profile review --json
cas capabilities --json
```

The preflight must be compatible for the exact resolved runtime. The capability
receipt must report `cas_codex_0146_structured_review_v1: true` and, for a
workflow-bound start, `cas_workflow_bound_owner_lived_review_v1: true`.

## Evidence law

```text
A process is not a review.
A parent thread is not a review.
An attempt begins only when reviewThreadId exists.
A semantic verdict exists only when the structured verdict binds the target.
```

CAS owns the exact selector, instruction bytes, opaque workflow binding,
review thread and turn, runtime/contract/transport identity, bounded recovery,
principal facts, structured verdict, failure class, and finding provenance.

The caller owns topology, lens meaning, review credit, finding truth and scope,
Counterexample classification, repairs, mutation, publication, and closure.
Process exit and prose are transport observations only.

## Commands

Use `run` for a standalone one-off review. Use one owner-lived `start --wait`
process for a workflow-bound or Actuating request. Recover an already-started
admissible diagnostic attempt with `wait`; do not duplicate a live handle.

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

For post-publication review, use the exact bound base/head selector. A clean
checkout is not a reason to substitute `--uncommitted`.

The workflow binding is the direct two-field input:

```json
{
  "requestId": "opaque-caller-id",
  "requestFingerprint": "sha256:..."
}
```

CAS returns it opaquely and does not infer a lens or policy.

## Receipt use

A semantic consumer requires a structured receipt whose target base, head, and
fingerprint agree at receipt and verdict level. Validate it through CAS's
passive `definitions/ledger/review-receipt.json` before interpretation.

Actuating review credit additionally requires the static Review Contract's
exact request/context match, `principalStrength == "strong"`,
`accountFingerprintReducedProtection == false`, and
`backendClass == "cas-start-wait"`. Missing structured output, auth-provider
failure, attestation-provider failure, account exhaustion, or transport loss
earns no clean verdict.
