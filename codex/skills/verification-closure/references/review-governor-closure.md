# Review Governor Closure

For `$resolve` closure, require:

- clean review streak;
- full validation;
- PR sweep;
- governor gate closed or not triggered;
- negative route gate pass or not-required;
- material improvement score present;
- no active negative exclusion against the selected route.

If invoked, emit:

```yaml
verification_closure_receipt:
  artifact_state:
  proof_current: yes | no
  closure_scope:
  unresolved_risk:
  closure_allowed:
```

For cybernetic/complex interventions, green tests may be probe evidence rather than full closure. Record monitoring or next feedback interval.
