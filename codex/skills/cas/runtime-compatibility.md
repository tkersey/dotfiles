# Runtime compatibility gate

CAS `0.6.5` targets released Codex `0.157.0` in its reproducible qualification
lanes. This is a qualification target, not a runtime pin or a claim that a
particular installed binary has passed. Require the selected structural and
behavioral proof; admit later released runtimes when that proof passes.
Prerelease builds do not replace released qualification evidence unless the
caller explicitly requests prerelease testing.

`cas review run|start` runs the exact-binary `review` gate over `managed-ws`
internally before starting a review. Let that gate establish compatibility;
do not run an identical standalone preflight first unless diagnosing or
qualifying the runtime. A failed gate blocks the route before a
`reviewThreadId` exists; no attempt or clean review exists, and failure does
not permit switching transport.

`cas app-server schema` is diagnostic inspection. Run it directly with the
structural profile being inspected, without a preceding live preflight; its
result cannot establish live behavioral compatibility.

For other app-server-backed execution routes whose required compatibility has
not already been established, or for explicit diagnosis/qualification, run:

```bash
cas app-server preflight \
  --cwd <repo> \
  --codex-path <exact-codex-executable> \
  --profile <core|review|session-inquiry|full> \
  --app-server-transport <selected-transport> \
  --json
```

Use these profiles:

| Route | Profile |
|---|---|
| smoke check, generic instance execution | `core` |
| `cas review run|start` | Built-in `review` gate over `managed-ws` |
| `cas session_inquiry preflight|run|start` | `session-inquiry` with `managed-ws` preflight and execution |
| release conformance and the complete feature surface | `full` |

For a standalone receipt, require `status == "compatible"`, the intended
resolved Codex path, contract ID `codex-app-server-capabilities-v2`, no missing
required methods or handlers, and all required selected-profile probes passed.
Codex version and release channel are diagnostic only. `degraded` is not
compatible proof for a required route behavior. Schema-only success is not
live behavioral proof.

Reuse proof only while the CAS build, resolved Codex executable/schema cache,
required profile, cwd/configuration, selected transport/endpoint, and Code Mode
host remain unchanged. A stdio or fresh-local-process receipt cannot qualify
a different endpoint. After an upgrade, rerun the gate; use `cas app-server
schema --refresh` when deliberately regenerating schemas for diagnosis.

For review and session inquiry, a standalone preflight receipt must select
`transport.selected == "managed-ws"`; a compatible stdio receipt is not
equivalent proof. Review reports its realized connection as
`selectedTransport == "websocket"`. Session inquiry additionally receives
`--transport managed-ws` on execution.

Compile-time capabilities report what CAS implements. They do not prove that
the resolved runtime implements it. Review requires both its compatible
`review` gate and `cas_capabilities.features.cas_structured_review_v1 == true`.

Codex 0.157.0 no longer exposes `thread/rollback`. CAS 0.6.5 removes that retired
method from the full capability requirements without relaxing exact fork,
revert, pagination, review, or server-request safety checks. Do not add a
rollback fallback or substitute destructive `thread/revert` for a fork.

See [codex_app_server_contract.md](references/codex_app_server_contract.md) and
[codex-app-server-capability-matrix.md](references/codex-app-server-capability-matrix.md).
