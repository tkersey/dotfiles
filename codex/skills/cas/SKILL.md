---
name: cas
description: "Operate the CAS Codex control-plane CLI: app-server, automations, account/goal facts, reviews, session inquiry, smoke/conformance checks, and instance fanout. Callers retain semantic authority."
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

Require installed CAS `0.6.0` or newer. There is no standalone automation
product, compatibility skill, or legacy command route.

## Native surface

```text
cas capabilities
cas app-server <preflight|schema|session|daemon>
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

## Selected guidance

Load the selected route before issuing its commands. Before an app-server-backed
route, read [runtime-compatibility.md](runtime-compatibility.md) and establish its
required profile for the exact executable/schema cache, or reuse an unchanged
compatible result. Version strings alone are not compatibility proof.

| Route | Selected guidance |
|---|---|
| App-server, smoke, instance fanout, conformance | [app-server.md](app-server.md) plus the applicable compatibility profile |
| Tuple-bound review | [reviews.md](reviews.md) plus `review`/`managed-ws` compatibility |
| Session inquiry | [session-inquiry.md](session-inquiry.md) plus `session-inquiry`/`managed-ws` compatibility |
| Automation | Automation below; use its store/scheduler doctor, not an unrelated app-server preflight. |
| Account and native goals | Account and goals below |

Read a deeper reference only where the selected route requires it. Do not preload
review, inquiry, and automation manuals together.

<a id="runtime-compatibility-gate"></a>
Runtime compatibility: [runtime-compatibility.md](runtime-compatibility.md).
<a id="route-guidance"></a>
The selected-route table above replaces the combined route manual.
<a id="app-server-smoke-and-instances"></a>
App-server, smoke, and instances: [app-server.md](app-server.md).
<a id="review"></a>
Review: [reviews.md](reviews.md).
<a id="session-inquiry"></a>
Session inquiry: [session-inquiry.md](session-inquiry.md).

## Automation

Use `cas automation` for every automation operation. When store or scheduler
compatibility is uncertain, and before troubleshooting or mutation that relies
on it, run:

```bash
cas automation doctor --json
```

Do not perform row or file mutations when `safeToMutate` is false. The only
narrow remediation exception is the doctor-directed same-label scheduler
adoption documented below. Use `--db` only when deliberately selecting a
non-default database; automation files still belong to the existing Codex
automation root. See [automation.md](references/automation.md) and
[automation-db.md](references/automation-db.md).

## Account and goals

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
