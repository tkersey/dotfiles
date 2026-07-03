# Examples

## Existing PR, review-closeout

```text
/goal $actuating review-closeout this PR
```

Means:

```text
CAS review, classify, build a resolution plan, fix accepted liabilities only, verify, require caller-owned repeated clean CAS review evidence units, then proof-patch.
```

## Existing PR, triage

```text
/goal $actuating triage this PR
```

Means:

```text
CAS review, review-fold, disposition report, stop.
```

## Debugging repeated failure

```text
Use $agent-loop-schemes to choose a loop for this flaky test failure.
```

Likely output:

```yaml
selected_loop: debug_history
memory:
  attempt_history: yes
  memoized_classes:
    - flaky-timeout-signature
stop:
  success: focused test passes repeatedly
  blocked: failure cannot be reproduced
```

## Migration with many same-shaped errors

```text
Use $agent-loop-schemes to structure this strict TypeScript migration.
```

Likely output:

```yaml
selected_loop: migration_memoized
work_producer:
  decomposition: representative error classes
memory:
  memoized_classes:
    - nullability-boundary
    - generated-types-mismatch
proof:
  artifact: typecheck + package tests
```
