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

Emit this table after `## Resolution Warrants`:

```md
## Surface Budget Ledger

| warrant id | mode | target net loc | max positive loc | max new public symbols | max new files | max new helpers | max new flags/knobs | max new state variants | max new branches | duplicate path budget | subtractive probes required | expansion warrant required | expansion status | proof required | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

## Allowed values

### `mode`

- `subtractive-first`
- `neutral-first`
- `additive-capped`
- `exploratory`

`mutate-code` warrants should default to `subtractive-first`. `exploratory` is
not implementation permission.

### `target net loc`

- `negative`
- `zero`
- `small-positive`
- `unknown`
- `uncapped-blocked`

`negative` and `zero` are preferred. `small-positive` requires a cap and a reason
why the added code reduces total semantic surface. `uncapped-blocked` means do
not implement yet.

### Numeric budgets

These fields must be non-negative integers:

- `max positive loc`
- `max new public symbols`
- `max new files`
- `max new helpers`
- `max new flags/knobs`
- `max new state variants`
- `max new branches`
- `duplicate path budget`

Public API, state, flags/knobs, duplicate paths, and new files default to `0`
unless the warrant explains why they are unavoidable.

## Fixed-point-driver handoff

Every `mutate-code` warrant should hand off to `$fixed-point-driver` with a
Surface Budget Preflight:

```md
## Surface Budget Preflight

- warrant_id:
- claim:
- feature to preserve:
- current source of truth:
- deletion probe:
- reuse probe:
- refactor probe:
- expected target_net_loc:
- forbidden new surface:
- first proof command:
- implementation may proceed: yes/no
```

After each patch group, `$fixed-point-driver` should emit a Surface Delta Receipt:

```md
## Surface Delta Receipt

- warrant_id:
- patch number:
- production insertions:
- production deletions:
- net production LOC:
- public symbols added:
- helpers added:
- flags/knobs added:
- state variants added:
- duplicate paths added:
- deleted/collapsed paths:
- budget status: within-budget / expansion-needed / violation
```

## Expansion warrant

When an implementation needs to exceed the surface budget, stop and issue an
Expansion Warrant Request:

```md
## Expansion Warrant Request

- warrant_id:
- additive change requested:
- budget exceeded:
- deletion probe result:
- reuse probe result:
- refactor probe result:
- why added surface reduces total complexity:
- new proof obligation:
- approved: yes/no
```

No approval means redesign or block.

## Checker use

The mechanical checker can validate surface budgets in output-only mode and can
also consume a diffstat or surface counters:

```bash
python codex/skills/review-adjudication/tools/review_adjudication_gate.py adjudication.md \
  --diffstat "3 files changed, 8 insertions(+), 12 deletions(-)" \
  --new-public-symbols 0 \
  --new-files 0 \
  --new-helpers 1 \
  --new-flags-or-knobs 0
```
