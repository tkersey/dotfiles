# Falsification Rules in Resolve

If a same-cluster finding appears after a prior RCP or implementation where `universalist_check.decision: not-needed`, mark:

```yaml
prior_universalist_not_needed_falsified: yes
```

The next packet must route to `use-universalist` or `blocked` unless a universal boundary packet proves not-needed remains valid.
