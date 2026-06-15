# System Pattern Route

Some review comments are not merely local defects. They are signals that the system is producing a repeated pattern.

Add this flag:

```yaml
system_pattern_signal:
  present: yes | no
  reason: "..."
  recommended_companion: cybernetic | none
```

Signal present when a review item implies:

- same-cluster recurrence;
- repeated invalid state;
- bad feedback boundary;
- public bypass incentive;
- metric/proxy gaming;
- local patch causing global harm;
- delayed failure after local green proof;
- repeated route failure.

If present, `$resolve` should consider `$cybernetic` before mutating.
