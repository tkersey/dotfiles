# Shipping Gate

`$ship` is allowed only when:

- graph has no unhandled in-scope tasks, or caveated draft is explicitly warranted;
- current head includes intended work;
- validation passes or limitations are explicitly accounted for;
- no fixed-point/ablation/soundness/verification blocker remains;
- PR side effect is in scope;
- proof summary is ready;
- `pr_mode` is explicit.

Ready PR is default after full validation.
