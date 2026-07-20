---
name: cas
description: "Run the Zig CAS app-server helpers for account and goal control, direct app-server methods, detached review attempts, session inquiry, HCTP lane execution, and bounded fanout. For reviews, CAS owns target capture, attempt lifecycle, transport recovery, principal quality, structured tuple-bound verdicts, and finding provenance through the current cas review run, start, and wait surface."
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
cas review start --cwd <repo> --uncommitted \
  --custom-instructions @<instructions> \
  --workflow-binding-json @<binding.json> --json
~~~

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

Actuating binds each request before dispatch and passes only this opaque shape:

~~~json
{
  "workflowBinding": {
    "requestId": "opaque-caller-id",
    "requestFingerprint": "sha256:..."
  }
}
~~~

CAS requires both strings to be non-empty, binds the complete object into
attempt identity, and returns it unchanged. It never infers a lens, role,
campaign, clean credit, or repair from those bytes.

## Structured owner receipt

`run`, waited `start`, and terminal `wait` return a current structured receipt
whose `reviewVerdict` carries:

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

Each finding row carries enough owner provenance to cite the exact observation:

~~~json
{
  "findingId": "cas-finding:<attempt>:<ordinal>",
  "findingFingerprint": "best-effort-cross-attempt-hash",
  "reviewAttemptId": "cas-review-attempt-id",
  "reviewThreadId": "thread-id",
  "reviewTurnId": "turn-id",
  "baseSha": "base",
  "headSha": "head",
  "targetFingerprint": "diff-fingerprint",
  "titleHash": "sha256:title",
  "bodyHash": "sha256:body",
  "normalizedLocation": {
    "path": "src/file.ext",
    "line": 1,
    "side": "RIGHT|LEFT|unknown"
  },
  "severity": "info|low|medium|high|unknown",
  "verdictStatus": "findings"
}
~~~

`findingId` identifies one emitted row. `findingFingerprint` is only a
best-effort cross-attempt comparison key. Neither is a Counterexample class,
repair, or mutation authority; `$review-fold` performs stable law-and-boundary
classification.

## Concurrent reporting

For concurrent attempts, monitor each receipt independently. Report an attempt
immediately and exactly once when its complete receipt and process exit status
exist. Read semantic status and findings only from `reviewVerdict`; use the
exit status only for command or transport completion. Do not wait for siblings
before reporting one terminal attempt, and never cancel a sibling on CAS's
behalf.

## Separate HCTP boundary

HCTP trial execution is an independent CAS product surface. It does not
participate in Actuating implementation, review, Construction, or closure.
Before its first Ledger command, load `$ledger` and complete `$ledger ensure`
once. Probe `cas capabilities --json` and require only the exact v2 features
needed by the selected direct or historical route.

For every `hylo-trial/v2` lane:

- run `cas trial preflight --trial trial.json --lane-id <lane-id> --json`;
- require the exact route projection before choosing direct or historical
  execution;
- receive the Ledger-issued private materialization claim only through
  `--materialization-fd`;
- use distinct anonymous directional descriptors numbered `>=3` for claims,
  source profiles, leases, visible inputs, and signing seeds;
- keep semantic role, treatment material, private source profiles, and full FIR
  outside argv, environment, regular files, stdout, event stores, and public
  receipts;
- execute one admitted lane once, then use status or recovery only to finish
  that same work;
- require the safe materialization receipt and run receipt fingerprints to
  exact-join before reveal.

Historical execution prepares its DCP, RIP, and FIR inside `cas trial run`.
`compile-replay` is a diagnostic and grants no execution authority. Sealed
assurance requires an explicitly admitted external broker; fail closed when it
is absent. Do not claim hostile same-user isolation.

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
