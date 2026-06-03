# Surface Budget Warrants

Surface Budget Warrants prevent `address` decisions from turning into additive
implementation by default. They bind every mutation-capable Resolution Warrant to
a least-surface implementation search and a measurable expansion budget.

## Doctrine

A review finding may authorize code change only under a surface budget. Additive
code is an exception that must defeat deletion, reuse, duplicate-path collapse,
canonicalization, privatization, and refactor probes, then prove that the added
surface reduces total semantic surface.

Prefer solution shapes in this order:

1. delete while preserving the live feature/contract
2. reuse an existing source of truth
3. collapse duplicate or parallel paths
4. canonicalize ownership / representation / proof surface
5. privatize an exposed internal surface
6. decommission a vestigial compatibility/scaffold path with proof
7. refactor into an existing seam
8. replace with a smaller equivalent
9. make a narrow local edit
10. add a guard/helper only after previous routes are defeated
11. add an abstraction only with explicit expansion warrant

## Surface Budget Ledger

```md
| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | ablative probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

`mutate-code` warrants should default to `ablative-first`. `exploratory` is not
implementation permission. Public API, state, flags/knobs, duplicate paths, and
new files default to `0` unless unavoidable.

## Ablative probe requirements

For every mutation-capable warrant, answer:

- What surface can be deleted?
- What existing owner/path can be reused?
- What duplicate path can be collapsed?
- What owner or representation should be canonicalized?
- What internal surface can be privatized?
- What compatibility or scaffold path is vestigial and should be decommissioned?
- Why is any remaining additive surface not dominated by the options above?

## Fixed-point-driver handoff

Every `mutate-code` warrant should hand off to `$fixed-point-driver` with a
Surface Budget Preflight and receive Surface Delta Receipts plus Ablation Ledger
rows after patch groups.


## Isomorphic safety addendum

Lower-surface routes are not automatically safe. Deletion, collapse, reuse, and canonicalization require an Ablative Isomorphism Card or a `validate-first` warrant. Apparent duplication must be clone-classified before merge: exact, parametric, gapped, semantic, or accidental-rhyme. Semantic clones and accidental rhymes do not collapse without equivalence proof.
