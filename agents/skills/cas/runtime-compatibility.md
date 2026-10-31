# Native runtime qualification

Use the selected installed `codex` executable directly. The migration was developed
against released Codex 0.166.0; that is a reproducible qualification subject, not a
maximum, an automatic upgrade instruction, or proof about another installation.

For ordinary execution, native CLI argument/configuration admission and the actual
result govern. Do not run an external CAS compatibility gate or an unrelated live
probe before each review. Reuse unchanged interface knowledge. Inspect help and,
when implementing or diagnosing raw RPC, generate schemas from that exact binary:

```bash
codex --version
codex exec review --help
codex app-server generate-json-schema --experimental --out <private-schema-dir>
```

Generation is structural inspection, not live execution proof. Use the installed
schema rather than a copied complete method/field inventory. On relevant runtime
changes, qualify the consumed operation and result shape; missing required behavior
remains unavailable. Do not silently broaden permissions, change the selected
executor/endpoint, or fabricate a compatibility receipt.

## Two transport boundaries

`codex exec review` uses Codex's in-process app-server path. It does not need a
separate local WebSocket listener. Codex independently owns the reviewer-to-provider
Responses transport, including native HTTP fallback. A local WebSocket connection
neither forces nor proves model-side WebSocket use; removing it does not disable
model-side WebSockets. Preserve the caller's provider configuration.

`codex app-server --listen ...` chooses a control listener. An explicit remote
endpoint needs its own supported client and authorization. In the qualified
release, `exec` and `review` reject `--remote`; do not pass it and silently run
locally. Native Code Mode host selection is a third, distinct outbound boundary;
use the installed help for its accepted form rather than inferring it from
`--listen` or `--remote`.

An explicit model-side-WebSocket requirement needs observed provider-connection
evidence; a feature setting, version, or control connection is insufficient.
Ordinary native transport fallback is not an executor switch. Record it when it
limits a requested claim; never present it as a proven WebSocket-only run.

## Qualification scope

The test-only native probe under `tests/` uses an isolated Codex home, disposable
Git subjects, and a loopback provider. It checks native command/configuration
propagation, output discrimination, recovery observations, forks, and WebSocket
boundaries without user credentials or CAS. It does not measure real-model review
quality, production account behavior, or the user's installed runtime.
