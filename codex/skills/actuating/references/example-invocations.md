# Example Invocations

## Standard plan-to-ready-PR

```text
Use $actuating. Compile this plan into $st, implement it, validate it, and open a PR.
```

Expected:

```text
material graph -> GCR -> AFR slices -> proof -> ready PR
```

## Explicit early draft

```text
Use $actuating and open a draft after the first validated wave for early visibility.
```

Expected:

```yaml
pr_mode: draft
draft_allowed_reason: explicit-user
```

## Implementation only

```text
Use $actuating to implement and validate this plan, but do not publish a PR.
```

Stop before `$ship`.

## Graph failure

```text
st compile aperture failed
```

Expected:

```text
graph-repair mode
no delivery mutation
no update_plan prose fallback
```
