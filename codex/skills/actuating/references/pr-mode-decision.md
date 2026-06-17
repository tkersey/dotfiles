# PR Mode Decision

`$actuating` must pass explicit `pr_mode` to `$ship`.

```yaml
pr_mode_decision:
  mode: ready | draft | update-existing | promote-draft | blocked
  reason:
  draft_allowed_reason:
```

Default:

```text
complete graph + passing validation -> ready
```

Draft requires a warrant:

- explicit user request;
- incomplete/failing/blocked/caveated validation;
- blocked/deferred/open task with requested early publication;
- early visibility;
- repo policy.

No `$ship` call without `pr_mode`.
