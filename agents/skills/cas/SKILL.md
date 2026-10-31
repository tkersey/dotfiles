---
name: cas
description: "Operate local Codex through CAS: reviews, app-server sessions, account facts, goals, automations, smoke/conformance checks, and instance fanout. Use native Codex for queued follow-ups. Historical inquiry requires caller-owned validated inputs."
---

# CAS

## Mission

Use CAS as the single local Codex control-plane product, not as a general coding
workflow or a hosted-reminder interface. Its primary runtime boundary is the Codex
app-server protocol. Automation is a direct adapter over
the existing local Codex database and files because app-server has no
automation CRUD or scheduler API.

For existing-thread follow-ups, use `codex queue` directly as the native
exception to CAS command routing; no CAS wrapper is required.

CAS owns route execution and facts it directly observes. It does not decide
Goal semantics, review credit, finding truth, repairs, mutation, publication,
closure, what an automation ought to do, or whether its result is correct.

Implicit selection does not authorize effects. Select the operation by the
caller's intended effect, not by the apparent meaning of its command name.

Require installed CAS `0.6.5` or newer. There is no standalone automation
product, compatibility skill, or legacy command route.

## Native surface

Use `cas --help` and the selected subcommand's help for the installed command
surface. Underscore/hyphen conveniences shown by help are spelling alternatives,
not another product or a fallback route.

## Selected guidance

Load only the selected route before its governed operation. For managed
app-server execution, establish the applicable [runtime compatibility](runtime-compatibility.md)
or reuse unchanged proof. Review runs its live gate internally; do not add a
redundant standalone preflight. Raw delegation has caller-owned client duties.

| Intent / effect | Route and selected guidance |
|---|---|
| Start or recover an exact-target review | [reviews.md](reviews.md); caller retains rubric, credit, and finding decisions. |
| App-server schemas/preflight, smoke checks, instance fanout, conformance, or raw session/daemon | [app-server.md](app-server.md); distinguish managed execution from raw delegation. |
| Historical session inquiry | [session-inquiry.md](session-inquiry.md), only with caller-owned input definitions and successful validation; ordinary prepared-seed fanout uses the app-server route. |
| Local Codex automation | Automation below, then [automation.md](references/automation.md); use the store/scheduler doctor, not an unrelated app-server preflight. |
| Inspect account or native goal facts; change or resume a goal | Account and goals below; distinguish observation, mutation, and resumption. |
| Queue an authorized existing-thread follow-up | [queueing.md](queueing.md); invoke `codex queue` directly, without a CAS preflight. |

Do not preload unrelated manuals. Recover from established effects: a pending
review is not a new attempt, an accepted queued message is not failed enqueueing,
and a committed automation database change is not rolled back by file-sync failure.
Report partial results without claiming execution, correctness, or completion
that the route did not establish.

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

## Native queueing

Use [queueing.md](queueing.md) for enqueueing, optional resumption, and partial-result recovery.

## Automation

Use `cas automation` for local Codex automation operations. When store or scheduler
compatibility is uncertain, and before troubleshooting or mutation that relies
on it, run:

```bash
cas automation doctor --json
```

Do not perform row or file mutations when `safeToMutate` is false. The only
narrow remediation exception is the doctor-directed same-label scheduler
adoption in [automation.md](references/automation.md#safety-gate). Use `--db` only
when deliberately selecting a non-default database; automation files still belong to the existing Codex
automation root. See [automation.md](references/automation.md) and
[automation-db.md](references/automation-db.md).

## Account and goals

| Operation | Effect |
|---|---|
| `cas account status` | Read account facts; preserve plan values as data. |
| `cas goal resolve` / `cas goal get` | Resolve a target / read its native goal. Use `get` to inspect goal status. |
| `cas goal set` | Write a goal; may create a thread when no existing target is selected. |
| `cas goal status --status ...` / `cas goal clear` | Change status / clear the goal; neither is observation. |
| `cas goal wait` | Resume the selected thread, then poll; requires resumption authority. |

For observation without resumption, use `goal get`, not `goal wait` or
`goal status`. Resolve the intended target; do not substitute another thread
because it is latest. Inspect the installed command's help for options and use
`--dry-run` when a goal operation needs a target/effect preview. A preview does
not authorize execution. Neither account facts nor native goal state creates
semantic Goal Contract authority or proves task completion.

## Hard rules

- Treat the installed Codex executable and its generated stable and
  experimental schemas as the runtime source.
- Version strings and schema digests alone are not compatibility proof.
- Managed CAS clients reject unknown server requests immediately. A raw
  session's client must provide terminating request handling; delegation alone
  does not install managed-client policies or receipts.
- Never synthesize credentials, attestations, elicitation consent, plugin
  trust, or publication authority.
- Never log or persist secret server-request response bodies.
- Preserve additive non-control data; reject unknown control flow explicitly.
- Explicit transports and Code Mode hosts never silently fall back.
- Automation keeps the existing Codex rows, files, RRULEs, run records,
  memories, scheduler label, and log paths.
- CAS reports owner facts; callers retain semantic decisions and authority.
