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
