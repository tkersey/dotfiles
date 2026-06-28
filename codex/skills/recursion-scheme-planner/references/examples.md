# Examples

## Accepted spec with straightforward implementation

Input:

```text
Accepted spec says add CLI flag, preserve existing behavior, run focused tests.
```

Output:

```yaml
selected:
  primary_scheme: hylo
work_shape:
  structure: line
handoff:
  next_owner: $goal-actuating
```

## Review campaign on existing PR

Input:

```text
/goal $actuating review and fix this PR
```

Output:

```yaml
selected:
  primary_scheme: chrono
  composition:
    - cata: CAS findings -> review-fold
    - dyna: repeated review classes
    - futu: branch-race if local fix vs refactor-kernel competes
    - hylo: accepted liabilities -> fix/prove loop
    - zygo: proof-patch
review_policy:
  source: cas-review
  mode: review-fix
  clean_cas_runs_required: 3
```

## Migration with many same-shaped errors

Input:

```text
Accepted spec migrates package set to strict typing.
```

Output:

```yaml
selected:
  primary_scheme: dyna
  composition:
    - ana: unfold package/error matrix
    - dyna: memoize error classes
    - hylo: representative fix/proof loop
    - cata: fold package evidence into repo verdict
work_shape:
  structure: migration-matrix
```

## Hard debugging

Input:

```text
A flaky test keeps moving after each patch.
```

Output:

```yaml
selected:
  primary_scheme: chrono
  composition:
    - histo: attempt history
    - futu: competing hypotheses
    - hylo: test/fix loop
memory:
  attempt_history: yes
  invalid_strategies: []
```

## Parallelism

Input:

```text
CAS produced 18 findings across independent modules.
```

Output:

```yaml
selected:
  primary_scheme: parallel-traverse
  composition:
    - cata: review-fold
    - dyna: cluster finding classes
    - parallel-traverse: scout/reducer fanout
    - cata: closure fan-in
parallelism:
  mode: review-class-fanout
  forbidden_frontier:
    - patch-fanout-before-closure-agenda
```
