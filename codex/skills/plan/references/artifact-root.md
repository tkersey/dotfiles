# Planning Artifacts

The self-contained execution specification is Plan's primary semantic representation.
No persistent artifact is required for ordinary human output. The emitted block may
be used directly as accepted implementation source without another skill or EPG.

When the user requests a saved human plan, write the complete specification to an
ordinary user-selected Markdown path, preserving its plan ID, revision, and source
binding. Do not invent a new store, duplicate task registry, or `.ledger` Markdown
file. Writing a requested planning artifact does not authorize implementation changes.

## Existing EPG custody

Only explicit EPG persistence uses:

```text
.ledger/plan/<plan-id>/policy.json
```

Keep the existing `plan/plan-policy-document` definition and its `create`, `revise`,
`show`, and explicit binding operations. Ledger alone owns this document's custody.
Do not write it directly or silently migrate/rebind a prior store.

Before create/revise, admit the new export under epg-export.md. The export embeds
the complete primary specification so it can be recovered without lost conversation
text. Readback must recover the same specification and identity, not regenerate a
richer plan from a digest. Do not introduce a second authoritative specification
store alongside this snapshot.

`revise` requires the exact current storage revision digest and retry-stable request
ID; the EPG's integer `revision` is not the storage comparison token. Verify that the
requested ID, exported plan ID, and returned logical reference agree. Re-read after
a concurrent-write conflict; never overwrite a competing revision blindly.

Historical EPG-v1 policies remain readable through their existing definition and
custody protocol. Missing embedded source is a recovery limitation, not a reason to
invent it. Recover source authority before publishing a new execution-complete
revision. The stricter new-export definition does not retroactively certify or
rewrite old policies.

Runtime state, observations, execution receipts, validation results, and synthesis
history are not Plan artifacts and do not belong under `.ledger/plan/`.
