# Ablation Ledger

The Ablation Ledger makes deletion, collapse, privatization, decommissioning, and
canonicalization explicit. It prevents fixed-point closure from meaning "all
comments have local patches" while dominated or vestigial surfaces remain.

## Doctrine

Operate in **ABLATIVE**, **CANONICALIZING**, **DOMINATED**, **SUBSUMED**,
**VESTIGIAL**, **UNINHABITED**, **DEFORESTING**, **WITNESS-BACKED**, and
**CONSERVATIVE** mode.

- **ABLATIVE**: remove accumulated surface while preserving the live contract.
- **CANONICALIZING**: select one owner/representation/path/proof surface.
- **DOMINATED**: another route covers the obligation with lower complexity or stronger proof.
- **SUBSUMED**: a local abstraction no longer owns a distinct obligation.
- **VESTIGIAL**: the old obligation is retired or moved.
- **UNINHABITED**: a branch/state has no legal runtime inhabitant under current invariants.
- **DEFORESTING**: remove pass-through wrappers, adapters, mappers, and intermediate structures.
- **WITNESS-BACKED**: every deletion/collapse needs current evidence.
- **CONSERVATIVE**: preserve public behavior and compatibility unless retirement is explicit.

## Ledger shape

```md
| id | surface | kind | current obligation | obligation status | canonical owner | replacement path | action | deletion/collapse proof | keep warrant | status |
|---|---|---|---|---|---|---|---|---|---|---|
```

Allowed `kind` values:

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

Allowed `action` values:

- `delete`
- `collapse`
- `canonicalize`
- `privatize`
- `decommission`
- `validate-first`
- `keep-with-warrant`

## Keep warrants

A `keep-with-warrant` row must name:

- the live obligation;
- why deletion/collapse would weaken the contract;
- compatibility or public API risk, if any;
- the proof surface that keeps the obligation checked;
- reopening criteria.

## Closure rule

A fixed point cannot be claimed while any material ablation row is `open`,
`unresolved`, `vetoed`, or `keep-without-warrant`.
