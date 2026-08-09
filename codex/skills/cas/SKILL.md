---
name: cas
description: "Use the native CAS Codex control-plane CLI for app-server inspection and transport, account and goal facts, automations, smoke and conformance checks, instance fanout, tuple-bound reviews, and session inquiry. CAS owns execution and directly observed facts; callers retain semantic authority."
---

# CAS

## Mission

Use CAS as the single local Codex control-plane product. Its primary runtime
boundary is the Codex app-server protocol. Automation is a direct adapter over
the existing local Codex database and files because app-server has no
automation CRUD or scheduler API.

CAS owns route execution and facts it directly observes. It does not decide
Goal semantics, review credit, finding truth, repairs, mutation, publication,
closure, what an automation ought to do, or whether its result is correct.

Require installed CAS `0.4.1` or newer. There is no standalone automation
product, compatibility skill, or legacy command route.

## Native surface

```text
cas capabilities
cas app-server <preflight|schema>
cas account status
cas automation <doctor|list|show|create|update|enable|disable|run-now|delete|run-due|scheduler>
cas goal <resolve|get|set|clear|status|wait>
cas smoke_check
cas instance_runner
cas review <run|start|wait>
cas session_inquiry <preflight|run|start|status|wait|interrupt|receipt|cleanup>
cas conformance
```

Underscore/hyphen spelling conveniences already shown by `cas --help` may be
used. They do not create another product identity.

## Runtime compatibility gate

Before an app-server-backed route whose compatibility has not already been
established for the exact resolved Codex executable and current schema cache,
run:

```bash
cas app-server preflight \
  --cwd <repo> \
  --profile <core|review|session-inquiry|full> \
  --json
```

Use these profiles:

| Route | Profile |
|---|---|
| schema inspection, smoke check, generic instance execution | `core` |
| `cas review run|start` | `review` |
| `cas session_inquiry preflight|run|start` | `session-inquiry` |
| release conformance and the complete feature surface | `full` |

Require `status == "compatible"`, the intended resolved Codex path, contract
ID `codex-app-server-0.146.0`, no missing required methods or handlers, and all
required selected-profile probes passed. `degraded` is not compatible proof for
a required route behavior.

Compile-time capabilities report what CAS implements. They do not prove that
the resolved runtime implements it. For review, require both the compatible
`review` preflight and
`cas_capabilities.features.cas_codex_0146_structured_review_v1 == true`.

See [codex_app_server_contract.md](references/codex_app_server_contract.md) and
[codex-0146-feature-matrix.md](references/codex-0146-feature-matrix.md).

## Route guidance

### App-server, smoke, and instances

Use `cas app-server schema --json` for a non-mutating schema/cache report and
`cas app-server preflight --json` for the structural and behavioral verdict.
Use `cas smoke_check` for bounded handshake and reachability observations.
Use `cas instance_runner` for bounded raw requests or fanout. Preserve additive
response, notification, and item data rather than projecting it away.

Explicit transport or remote Code Mode host selection is fail-closed. The
outbound Code Mode host is distinct from the inbound app-server endpoint.

### Automation

Use `cas automation` for every automation operation. When store or scheduler
compatibility is uncertain, and before troubleshooting or mutation that relies
on it, run:

```bash
cas automation doctor --json
```

Do not mutate when `safeToMutate` is false. Use `--db` only when deliberately
selecting a non-default database; automation files still belong to the existing
Codex automation root. See [automation.md](references/automation.md) and
[automation-db.md](references/automation-db.md).

### Review

Use `run` for a standalone one-off review. Use one owner-lived
`start --wait` process for workflow-bound or Actuating review. Use `wait` only
to recover or inspect an already-started admissible attempt.

```bash
cas app-server preflight --cwd <repo> --profile review --json

cas review run --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json

cas review start --wait --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json
```

A process is not a review. An attempt exists only after `reviewThreadId`; a
semantic verdict exists only when the structured verdict binds the exact
target tuple. CAS reports the backend. The caller decides credit and finding
disposition. See [review-proof-boundary.md](references/review-proof-boundary.md).

### Session inquiry

Use the `session-inquiry` preflight profile before execution. A paginated source
is admissible when the exact runtime probe passes. Fork boundary and anchor
digest verification remain mandatory. A successful paginated fork is not proof
of historical workspace reconstruction.

Validate Retrace inputs with their owner definitions and validate the returned
FIR with CAS's passive definition before interpreting it. See
[retrace-session-inquiry.md](references/retrace-session-inquiry.md).

### Account and goals

`cas account status` reports account facts and preserves plan values as data.
`cas goal` resolves, observes, mutates, or waits for native CAS goal state only
when the caller authorizes that route. Neither command creates semantic Goal
Contract authority.

## Hard rules

- Treat the installed Codex executable and its generated stable and
  experimental schemas as the runtime source.
- Version strings and schema digests alone are not compatibility proof.
- Unknown server requests get an immediate unsupported response and never
  deadlock a request loop.
- Never synthesize credentials, attestations, elicitation consent, plugin
  trust, or publication authority.
- Never log or persist secret server-request response bodies.
- Preserve additive non-control data; reject unknown control flow explicitly.
- Explicit transports and Code Mode hosts never silently fall back.
- Automation keeps the existing Codex rows, files, RRULEs, run records,
  memories, scheduler label, and log paths.
- CAS reports owner facts; callers retain semantic decisions and authority.
