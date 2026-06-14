# Fixed-Point Execution Loop

Use `$fixed-point-driver` for each non-trivial implementation aperture.

## Route shape

```text
ready $st task
  -> fixed-point-driver frame
  -> route selection
  -> accretive implementation / validation-first / ablation / no-change / blocked
  -> de novo review
  -> one-change challenge
  -> proof receipt
  -> st complete or st blocked
```

## Required handoff context

For each aperture, provide:

- `$st` task id(s)
- plan excerpt / acceptance criterion
- permitted scope
- forbidden actions
- proof required
- relevant files/tests
- language/toolchain signals
- known non-goals

## Stop conditions

Continue until all in-scope `$st` tasks are complete or explicitly blocked/deferred. Do not stop merely because one implementation pass is green.
