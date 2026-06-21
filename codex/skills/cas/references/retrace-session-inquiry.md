# `$retrace` Session Inquiry

`$cas` owns controlled Codex app-server fork lifecycle for `$retrace`.

Preferred future command:

```bash
cas session_inquiry run \
  --capsule capsule.json \
  --plan inquiry-plan.json \
  --receipt-dir .retrace/<inquiry-id> \
  --json
```

Required behavior:

```text
thread/fork
exact thread/rollback or equivalent prefix anchor
read-only permission profile
ephemeral by default
network off by default
one bounded inquiry turn
wait/interrupt
FIR-v1 receipt
cleanup
```

Do not let a fork access the current checkout when the capsule requests transcript-only or historical workspace reconstruction is incomplete.

Do not use `thread/shellCommand`; it is unsandboxed.

Implementation requirements are in:

```text
CAS_SESSION_INQUIRY_CLI_SPEC.md
```
