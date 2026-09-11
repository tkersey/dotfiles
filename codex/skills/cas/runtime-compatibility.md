# Runtime compatibility gate

## Runtime compatibility gate

Before an app-server-backed route whose compatibility has not already been
established for the exact resolved Codex executable and current schema cache,
run:

```bash
cas app-server preflight \
  --cwd <repo> \
  --profile <core|review|session-inquiry|full> \
  --app-server-transport <selected-transport> \
  --json
```

Use these profiles:

| Route | Profile |
|---|---|
| schema inspection, smoke check, generic instance execution | `core` |
| `cas review run|start` | `review` with `managed-ws` preflight |
| `cas session_inquiry preflight|run|start` | `session-inquiry` with `managed-ws` preflight and execution |
| release conformance and the complete feature surface | `full` |

Require `status == "compatible"`, the intended resolved Codex path, contract
ID `codex-app-server-capabilities-v2`, no missing required methods or handlers,
and all required selected-profile probes passed. Codex version and release
channel are diagnostic only. `degraded` is not compatible proof for a required
route behavior.

CAS 0.6.0 is qualified against released Codex 0.151.0. That version is an
evidence baseline, not a runtime pin or upper bound: admit later released
runtimes when the selected capability profile and probes pass. Do not use an
unreleased or prerelease build as qualification evidence unless the caller
explicitly requests prerelease testing.

For review and session inquiry, also require the preflight receipt's
`transport.selected == "managed-ws"`; a compatible stdio receipt is not
equivalent proof. CAS 0.6.0 review runs this gate internally before starting
and reports the realized connection as `selectedTransport == "websocket"`.
Session inquiry additionally receives `--transport managed-ws` on execution.

Compile-time capabilities report what CAS implements. They do not prove that
the resolved runtime implements it. For review, require both the compatible
`review` preflight and
`cas_capabilities.features.cas_structured_review_v1 == true`.

See [codex_app_server_contract.md](references/codex_app_server_contract.md) and
[codex-app-server-capability-matrix.md](references/codex-app-server-capability-matrix.md).
