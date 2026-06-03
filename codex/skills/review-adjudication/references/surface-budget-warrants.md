# Surface Budget Warrants

Surface Budget Warrants prevent `address` decisions from turning into additive
implementation by default. They bind every mutation-capable Resolution Warrant to
a least-surface implementation search and a measurable expansion budget.

## Doctrine

A review finding may authorize code change only under a surface budget. Additive
code is an exception that must defeat deletion, reuse, duplicate-path collapse,
and refactor probes, then prove that the added surface reduces total semantic
surface.

Prefer solution shapes in this order:

1. delete while preserving the feature
2. reuse an existing source of truth
3. collapse duplicate or parallel paths
4. refactor into an existing seam
5. replace with a smaller equivalent
6. make a narrow local edit
7. add a guard/helper only after previous routes are defeated
8. add an abstraction only with explicit expansion warrant

## Surface Budget Ledger

```md
| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

`mutate-code` warrants should default to `subtractive-first`. `exploratory` is not
implementation permission. Public API, state, flags/knobs, duplicate paths, and
new files default to `0` unless unavoidable.

## Fixed-point-driver handoff

Every `mutate-code` warrant should hand off to `$fixed-point-driver` with a
Surface Budget Preflight and receive Surface Delta Receipts after patch groups.
