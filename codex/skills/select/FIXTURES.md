# Select fixtures (regressions)

These are small, human-checkable fixtures to prevent regressions like "No ready slices" when work exists.

## F1: `subtasks` does not mean non-leaf
SLICES fragment:
```yaml
- id: sl-a
  title: "A"
  status: closed
- id: sl-b
  title: "B"
  status: open
  subtasks: ["do x", "do y"]
  dependencies:
    - type: blocks
      depends_on_id: sl-a
```
Expected: `sl-b` is a ready leaf and is selectable.

## F2: in_progress triage -> recommend close when done exists
SLICES fragment:
```yaml
- id: sl-run
  title: "Runner harness"
  status: in_progress
  verification: |
    - Run: zig build test
```
Expected: if `zig build test` passes (or artifacts clearly exist), emit `triage: recommend close sl-run`.

## F3: in_progress triage -> continue when active proof exists
SLICES fragment:
```yaml
- id: sl-x
  title: "Implement X"
  status: in_progress
```
Expected: if there is an open PR/branch/commit mentioning `sl-x`, emit `triage: continue sl-x` and select only `sl-x`.

## F4: unknown dep id -> warn and keep selecting
SLICES fragment:
```yaml
- id: sl-a
  title: "A"
  status: open
  dependencies:
    - type: blocks
      depends_on_id: sl-missing
- id: sl-b
  title: "B"
  status: open
```
Expected: warn `unknown_deps: [sl-missing]`; treat `sl-a` blocked; still select `sl-b`.

## F5: no ready tasks -> pick closest unblocker
SLICES fragment:
```yaml
- id: sl-a
  title: "A"
  status: open
  dependencies:
    - type: blocks
      depends_on_id: sl-b
- id: sl-b
  title: "B"
  status: open
  dependencies:
    - type: blocks
      depends_on_id: sl-c
- id: sl-c
  title: "C"
  status: open
```
Expected: pick `sl-c` (fewest unmet blocks) as the unblocker.

## F6: auto-remediate unknown dep id via alias
Invocation list fragment:
```text
Use $select:
1. First task.
   - id: t-1
2. Second task.
   - id: t-2
   - depends_on: [1]
```
Expected: map `depends_on: [1]` to `t-1`; no unknown-deps warning; `auto_fix` includes `dep_alias`.

## F7: auto-infer scope from explicit path tokens
Invocation list fragment:
```text
Use $select:
1. Update docs.
   - id: docs
   - title: "Edit README.md and docs/guide.md"
```
Expected: infer `scope` from `README.md` and `docs/guide.md`; no missing-scope warning; `auto_fix` includes `scope_infer`.

## F8: overly-broad scope -> warn and serialize
Invocation list fragment:
```text
Use $select:
1. Huge refactor.
   - id: big
   - scope: ["**"]
2. Small change.
   - id: small
   - scope: ["docs/**"]
```
Expected: warn `broad_scope`; treat `big` as overlapping everything (no parallel wave with `small`).

## F9: overlap without depends -> warn implicit order
Invocation list fragment:
```text
Use $select:
1. Touch src.
   - id: a
   - scope: ["src/**"]
2. Touch src/foo.
   - id: b
   - scope: ["src/foo/**"]
```
Expected: schedule serial due to overlap; warn `implicit_order` (ordering chosen by stable order / tie-breaks).

## F10: parallel wave missing validation -> warn
Invocation list fragment:
```text
Use $select:
1. Change A.
   - id: a
   - scope: ["src/a/**"]
2. Change B.
   - id: b
   - scope: ["src/b/**"]
   - validation: ["npm test"]
```
Expected: `a` and `b` can share a wave; warn `missing_validation` for `a` (parallel work without proof signal).

## F11: scope normalization -> auto_fix
Invocation list fragment:
```text
Use $select:
1. Normalize scope.
   - id: n
   - scope: ["./src/**"]
```
Expected: normalize scope entry to `src/**`; `auto_fix` includes `scope_normalize`.

## F12: selecting ready work -> claim in_progress
SLICES fragment:
```yaml
- id: sl-a
  title: "A"
  status: closed
- id: sl-b
  title: "B"
  status: open
  dependencies:
    - type: blocks
      depends_on_id: sl-a
```
Expected: select `sl-b` and include `claim: mark in_progress sl-b` in the Decision Trace.
