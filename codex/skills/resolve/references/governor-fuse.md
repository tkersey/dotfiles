# Governor Fuse

Quantitative fuses are secondary backstops, not semantic authority.

Suggested warning thresholds:

```text
same raw cluster >= 3
same-class recurrence >= 1
owner mutations >= 3
same-owner commits >= 3
apply_patch >= 10
production net > +250
```

Any same-class recurrence is already a hard realization invalidation under the current protocol.

Threshold trips may trigger read-only distillation or blocking, but cannot override AC/CEX/PHI gates.
