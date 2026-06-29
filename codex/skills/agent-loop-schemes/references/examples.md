# Examples

## Existing PR, review and fix

```text
/goal $actuating review and fix this PR
```

Means:

```text
CAS review, classify, build a closure agenda, fix accepted liabilities only, verify, require caller-owned repeated clean CAS review runs, then proof-patch.
```

## Existing PR, no implementation

```text
/goal $actuating review this PR; do not implement
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
