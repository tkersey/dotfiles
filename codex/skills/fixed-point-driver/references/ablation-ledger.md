# Ablation Ledger

Use the Ablation Ledger to make deletion/collapse/canonicalization pressure a
checkable fixed-point artifact.

```md
| id | surface | kind | current obligation | obligation status | canonical owner | replacement path | action | deletion/collapse proof | keep warrant | status |
|---|---|---|---|---|---|---|---|---|---|---|
```

Kinds:

- `dominated`
- `subsumed`
- `vestigial`
- `uninhabited`
- `unreachable`
- `pass-through`
- `duplicate-truth-surface`
- `non-canonical`
- `additive-scaffold`
- `temporary-proof-scaffold`

Actions:

- `delete`
- `collapse`
- `canonicalize`
- `privatize`
- `decommission`
- `validate-first`
- `keep-with-warrant`

Open or unresolved rows block fixed-point closure unless explicitly accepted as
risk by the user or converted to `keep-with-warrant` with evidence.
