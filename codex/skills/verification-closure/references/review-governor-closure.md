# Review Governor Closure

For `$resolve` closure, require:

- clean review streak;
- full validation;
- PR sweep;
- governor gate closed or not triggered;
- positive production net embargo passed or not required;
- owner coarseness gate passed or not required;
- boundary inventory satisfied or not required;
- negative route gate pass or not-required;
- proof matrix gate pass or not-required;
- material improvement score present;
- no active negative exclusion against selected route.

If invoked, emit:

```yaml
verification_closure_receipt:
  artifact_state:
  proof_current: yes | no
  closure_scope:
  unresolved_risk:
  closure_allowed:
```
