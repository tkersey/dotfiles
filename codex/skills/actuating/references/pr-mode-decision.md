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
    missing-context |
    repo-policy
```

Default:

```text
complete graph + terminal AFRs + current full proof -> ready
```

Draft requires a warrant.

No `$ship` call without explicit mode.
