---
name: cas
description: "Operate native Codex: non-interactive reviews, exact-thread follow-ups, app-server sessions, account/goal facts, and prepared-history forks. The skill calls codex directly; it does not require the CAS executable."
---

# CAS

## Mission

Operate native Codex, not another control-plane product. `$cas` is the skill's
name; no `cas` executable, wrapper, compatibility alias, or automatic fallback is
part of this workflow. Use the caller's selected Codex executable and preserve
its model, configuration, permissions, target, and endpoint.

The runtime owns execution and its original output. The caller owns requirements,
review credit, finding truth, repairs, publication, and closure. Implicit selection
does not authorize effects or start a coding/review campaign on its own.

## Selected guidance

Load only the selected route before its governed operation. Use the installed
`codex --help` and selected subcommand's help; [runtime qualification](runtime-compatibility.md)
explains the remaining evidence boundaries without a separate preflight product.

| Intent / effect | Native route |
|---|---|
| Native standard, auxiliary, or focused review | [reviews.md](reviews.md): `codex exec review`; retain original execution output and the exact native structured review artifact. |
| Stateful RPC, source/seed forks, account or goal operations | [app-server.md](app-server.md): `codex app-server`; use the selected native protocol, not a recreated CAS client. |
| Existing-thread follow-up | [queueing.md](queueing.md): `codex queue`; enqueue and optional resume are separate effects. |
| Session/daemon lifecycle or schema inspection | [app-server.md](app-server.md): native help and schema generation; lifecycle mutations require their own authority. |
| Local automation or historical replay | Retired routes below; no invented command or silent substitute. |

Recover from established effects. An observation timeout is not terminal failure,
a queued message is not completed work, and resumption is not passive observation.
Preserve partial results and limitations; do not manufacture missing evidence.

<a id="runtime-compatibility-gate"></a>
[Native runtime qualification](runtime-compatibility.md).
<a id="route-guidance"></a>
The selected-route table above owns routing.
<a id="app-server-smoke-and-instances"></a>
[Native app-server operations](app-server.md).
<a id="review"></a>
[Native reviews](reviews.md).
<a id="session-inquiry"></a>
Historical replay is not an available execution route; see Retired routes.

## Account and goals

`codex login status` inspects login state, not comprehensive usage or plan data.
For richer account facts or native goals, use the exact schema-advertised
app-server operations in [app-server.md](app-server.md). There is no assumed
`codex account` or `codex goal` CLI family.

`thread/goal/get` observes; `thread/goal/set` and `thread/goal/clear` mutate.
`thread/resume` is a separate lifecycle effect and may resume work. Do not resume
merely to inspect a goal. Native goal state is not semantic Goal Contract authority.

## Retired routes

This migration removes the skill's automation CRUD/scheduler and capsule-based
historical-inquiry routes, along with CAS-only smoke, fanout, and conformance
requirements. A native fork is not historical workspace reconstruction. Use `$seq`
for independently answerable historical observations, not fabricated replay proof.

There is no assumed native automation CRUD or scheduler command. Existing local
schedules, rows, files, run records, memories, and installed scheduler jobs are
unchanged. Before the later executable removal, inventory and explicitly migrate
or retire any active scheduler or external caller that still depends on it.
Do not edit the database, install another scheduler, migrate a task to hosted
reminders, uninstall a binary, or delete historical evidence as part of this route.

Old execution records keep their original attribution and contract. New native
results are not CAS receipts, and old credit is not native credit. Finish/drain
old campaigns before cutover, or resolve possibly live attempts and start a newly
bound native campaign without transferring their review credit. Preserve findings.

## Hard rules

- Prefer native operations; no new launcher, receipt store, schema cache, or
  general-purpose transport framework is required.
- Preserve explicit endpoints and transports. Local execution does not prove a
  remote endpoint; model-side WebSockets are separate from app-server transport.
- Never invent credentials, attestations, consent, trust, or publication authority.
- Never log secret response bodies or publish raw session/private reasoning payloads.
- State which native facts were observed. Missing evidence blocks only its dependent
  claim; it does not authorize broader permissions or an executor substitution.
