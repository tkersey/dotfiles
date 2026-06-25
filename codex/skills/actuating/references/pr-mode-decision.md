# PR Mode Decision

```yaml
pr_mode_decision:
  mode:
    ready |
    draft |
    update-existing |
    promote-draft |
    blocked
  reason:
  draft_allowed_reason:
    none |
    explicit-user |
    incomplete-validation |
    blocked-tasks |
    early-visibility |
    repo-policy
```

Default:

```text
all in-scope work complete + current final proof -> ready
```

Draft requires an explicit warrant.

`$actuating` must pass the mode to `$ship`.
