# Review Distillation Scar Tissue

In Review Distillation Mode, the lab can accumulate exploratory fixes. The delivery branch must not inherit them by default.

Use negative evidence to mark lab surfaces:

```yaml
scar_tissue_negative_ledger:
  - neg_id:
    lab_surface:
    hypothesis:
    observed_outcome:
    fate: discard | distill | transplant-with-rent | blocked
    exclusion_rule:
    reopening_criteria: []
```

If lab surface is `transplant-with-rent`, require abstraction rent and proof matrix coverage.

If lab surface is `discard`, it must not appear in delivery patch unless reopened by current proof.
