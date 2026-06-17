# Example Invocations

## Ready by default

```text
Use $actuating. Turn this plan into tasks, implement, validate, and open a PR.
```

If tasks complete and validation passes, `$actuating` passes:

```yaml
pr_mode: ready
```

## Explicit draft

```text
Use $actuating and open a draft PR for early visibility once the first validated slice is done.
```

Then `$actuating` may pass:

```yaml
pr_mode: draft
draft_allowed_reason: explicit-user
```
