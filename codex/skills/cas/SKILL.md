---
name: cas
description: "Run the Zig CAS app-server helpers for account and goal control, direct app-server methods, detached review attempts, session inquiry, and bounded fanout. For reviews, CAS owns target capture, attempt lifecycle, transport recovery, principal quality, structured tuple-bound verdicts, and finding provenance through the current cas review run, start, and wait surface."
---

# CAS

## Mission

Own Codex app-server transport and the facts it directly observes. For review,
CAS starts, waits for, recovers, and reports one exact attempt. It does not own
Actuating's review topology, lens selection, Counterexample classification,
Construction selection, review credit, repository mutation, publication, or
closure.

~~~text
review target + opaque request binding + exact instructions
-> CAS attempt
-> structured owner receipt
-> caller evaluation
~~~

## Native surface

~~~text
cas capabilities
cas account status
cas goal <resolve|get|set|clear|status|wait>
cas smoke_check
cas instance_runner
cas review <run|start|wait>
cas session_inquiry <preflight|run|start|status|wait|interrupt|receipt|cleanup>
cas trial <preflight|compile-replay|run|status|cleanup|key-info>
cas conformance
~~~

`cas smoke_check` proves app-server handshake and method reachability. It is
never review output. `cas conformance` probes helper compatibility. Session
inquiry owns `$retrace` replay transport; see
[retrace-session-inquiry.md](references/retrace-session-inquiry.md).

## Codex 0.145 compatibility

Before every `cas review run` or `cas review start`, run
`cas capabilities --json` and require
`cas_capabilities.features.cas_codex_0145_structured_review_v4=true`. Stop
before `review/start` when the feature is absent. CAS 0.2.87 through 0.2.92 do
not satisfy this gate: 0.2.87 through 0.2.89 can complete a Codex 0.145 review
without a valid structured receipt, while 0.2.90 cannot preserve its structured
timeout contract before an inline rollout materializes and 0.2.91 can mistake a
partially materialized `completed` turn for terminal missing output. CAS 0.2.92
can classify a resumed wait using the currently installed runtime instead of
the attempt's recorded runtime.

The compatible CAS route keeps the attempt isolated but runs Codex's native
review inline within a fresh CAS-owned thread on Codex 0.145 and newer. Codex's
detached delivery is now an ordinary prose-oriented `$review-agent` turn and
does not emit `exited_review_mode.review_output`. Earlier Codex runtimes retain
their detached delivery path. Do not pass `--parent-thread-id` on the 0.145+
route: compatible CAS rejects parent reuse before `review/start` so the inline
parent ID remains a unique persisted attempt handle. This transport choice
changes neither tuple identity nor semantic credit. Before the inline rollout
materializes, compatible CAS preserves a structured non-terminal state and
still requires the exact review turn before accepting a terminal result. A
partially materialized `completed` turn that entered review mode but has not
emitted its structured exit also remains non-terminal. Later `wait` calls bind
completion semantics to the attempt's recorded Codex runtime; the currently
installed runtime is used only for tuple-currentness checks. Process completion
and prose remain non-proof.

Codex 0.145 ignores request-scoped `multiAgentMode`. Do not pass
`--multi-agent-mode` to `cas review` or `cas instance_runner`; current CAS
rejects that retired option before any app-server request. Configure
multi-agent V2 through `[features.multi_agent_v2]` and canonical concurrency,
model, and reasoning settings through `[agents]`. Use current Codex reasoning
effort when proactive delegation is required.

Historical CAS records may still contain `requestedMultiAgentMode`,
`effectiveMultiAgentMode`, `multiAgentModeSupport`, and
`multiAgentModeMetricEligible`. Those fields preserve old receipt readability;
they do not prove that a current Codex runtime applied the retired request
field. New CAS-generated requests omit it and new receipts grant it no credit.

CAS uses `excludeTurns:true` for metadata-only `thread/resume` calls on Codex
0.145 and newer, and preserves the older request shape for earlier runtimes.
This optimization changes neither review identity nor semantic credit.

`cas session_inquiry` rejects a paginated source thread before `thread/fork`,
because Codex 0.145 does not support forking paginated history. Use a
legacy-history source thread or the verified `rollout_transcript` lineage.

## Review attempt law

~~~text
A process is not a review.
A parent thread is not a review.
A review attempt starts only after review/start returns reviewThreadId.
A semantic verdict exists only when reviewVerdict binds the exact target.
~~~

CAS owns:

- target capture for exactly one of `--base`, `--commit`, or `--uncommitted`;
- exact custom instruction bytes and opaque workflow binding transport;
- review thread and turn identity;
- exact `principalStrength`, `accountFingerprintReducedProtection`, and
  `backendClass` owner facts;
- bounded wait and same-handle recovery;
- structured verdict, failure, and finding provenance;
- internal exclusion of duplicate active attempts for one exact request target.

The caller owns why the attempt exists and what its receipt means to its own
workflow. For Actuating, that includes the static 1+4 topology, request-local
recovery allowance, Counterexample evaluation, clean streak, material-change
reset, next action, and closure.

## Current review commands

Use `run` for the normal start-and-wait path:

~~~bash
cas review run --cwd <repo> --base <base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> \
  --timeout-ms 2700000 --json
~~~

Use `start` only when the caller needs a detached handle or is launching an
Actuating concurrent wave:

~~~bash
cas review start --cwd <repo> --base <bound-base> \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> --json
~~~

For a post-Ship Actuating wave, pass the exact published-subject selector that
Actuating bound; normally this is `--base <bound-base>`. Never substitute
`--uncommitted` merely because the published checkout is clean. Use
`--uncommitted` only when the bound review subject is the current uncommitted
working tree, such as an explicitly local triage.

Use `wait` to recover or finish that exact attempt:

~~~bash
cas review wait --cwd <repo> \
  --review-thread-id <reviewThreadId> \
  --timeout-ms 2700000 --json
~~~

`wait --path <record.json>` and `wait --latest` are selectors for an already
started attempt. They never start new work. Prefer the explicit
`reviewThreadId` whenever the caller retained it.

Pass `--timeout-ms 2700000` for every real review wait unless the user
explicitly selects another budget. A timeout with a live handle is pending
transport evidence; recover with `wait` rather than starting a duplicate.

Start a new same-target attempt only when the caller has admitted a distinct
attempt and supplies `--fresh-attempt <source-bound-reason>`. CAS validates and
records the reason but does not decide whether a workflow permits that attempt.

## Target and request identity

Exactly one review selector is required:

- `--base BRANCH` captures the current changes against that base;
- `--commit SHA` captures the named commit;
- `--uncommitted` captures staged, unstaged, and untracked changes.

This target capture belongs to CAS because CAS must bind the reviewed bytes to
its receipt. It is not repository mutation or a general Git-subject service.

Actuating binds each request before dispatch and passes this two-field object
directly to `--workflow-binding-json`:

~~~json
{
  "requestId": "opaque-caller-id",
  "requestFingerprint": "sha256:..."
}
~~~

CAS requires both strings to be non-empty, binds the complete object into
attempt identity, and returns it unchanged under the owner receipt's
`workflowBinding` field. The flag input is not wrapped in a `workflowBinding`
object. CAS never infers a lens, role, campaign, clean credit, or repair from
those bytes.

## Structured owner receipt

Waited `start` and terminal `wait` return a current structured receipt whose
`reviewVerdict` carries:

~~~text
status
reviewAttemptPhase
reviewAttemptExists
tupleVerdictExists
principalStrength
accountFingerprintReducedProtection
backendClass
baseSha
headSha
targetFingerprint
reviewThreadId
reviewTurnId
findingCount
findings
failureClass
failureCode
failureHint
workflowBinding
~~~

CAS reports these fields without deciding workflow credit. Actuating maps them
to its static quality predicates: `principalStrength == "strong"`,
`accountFingerprintReducedProtection == false`, and
`backendClass == "cas-start-wait"`, alongside exact request, context, and tuple
matching. Process exit status describes command or transport completion only.
It never substitutes for `reviewVerdict`.

A terminal attempt without a structured semantic verdict has zero semantic
credit. CAS reports the failure and terminal attempt identity. Actuating alone
decides whether its one request-local fresh recovery is legal.

Account or resource exhaustion is neither reviewer output nor transport loss.
Report it as an owner failure fact and do not claim a clean or findings verdict.

## Finding provenance

Each canonical compact finding row is deliberately small:

~~~json
{
  "title": "finding title",
  "body": "finding body",
  "file": "/absolute/or/repository/path",
  "line": 1,
  "priority": 1
}
~~~

The enclosing `reviewVerdict` supplies the attempt, tuple, request binding, and
verdict status. `$review-fold` may digest the exact canonical row bytes and
cite the enclosing receipt; it performs stable law-and-boundary classification.
CAS does not manufacture a second per-finding identity or duplicate receipt
provenance into every row.

## Concurrent reporting

For concurrent attempts, monitor each receipt independently. Report an attempt
immediately and exactly once when its complete receipt and process exit status
exist. Read semantic status and findings only from `reviewVerdict`; use the
exit status only for command or transport completion. Do not wait for siblings
before reporting one terminal attempt, and never cancel a sibling on CAS's
behalf.

## Review report

~~~text
CAS Review:
- Request binding:
- Target base/head/fingerprint:
- Attempt and thread/turn identity:
- Principal / transport:
- Verdict / finding count:
- Failure class / code:
- Transport state:
- Owner receipt:
~~~

## Hard rules

- Review begins only when `reviewThreadId` exists.
- CAS reports owner facts; it does not interpret them as Actuating credit.
- Use only `cas review run`, `cas review start`, and `cas review wait` for review lifecycle.
- Recover a live exact attempt with `wait`; do not duplicate it.
- Start admitted new work only with a fresh attempt identity and reason.
- Completed findings are not transport failure.
- Missing structured output is not clean.
- CAS exposes no alternate review fallback. Verdictless transport remains
  no-credit owner evidence for Actuating's bounded request-local recovery.
- CAS never selects a lens, Counterexample disposition, repair, Construction,
  repository operation, public effect, or closure verdict.
