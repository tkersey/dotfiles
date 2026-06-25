# Plan Namespacing

## IDs

Within a plan:

```text
st-001
proof-001
intent-001
```

Across the workspace:

```text
plan://<plan-id>/st-001
plan://<plan-id>/proof-001
plan://<plan-id>/intent-001
```

## CLI resolution

```text
--plan supplied:
  unqualified IDs resolve inside that plan

one active plan:
  CLI may infer the plan

two or more active plans:
  unqualified command without --plan fails
```

Global commands always emit qualified references.

## Projection

Session-visible IDs are qualified:

```text
[auth/st-001]
[cache/st-004]
```

This prevents two agents from reporting ambiguous `[st-001]` rows.

## Import

Importing a plan must:

- choose or create one plan namespace;
- reject task IDs already present in that plan unless update semantics are
  explicit;
- permit the same local ID in a different plan;
- rewrite cross-plan links only through the workspace command surface.
