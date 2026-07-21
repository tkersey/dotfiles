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

## Codex 0.145 compatibility

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

## HCTP trial execution

This independent CAS product surface does not participate in Actuating
implementation, review, Construction, or closure.

Before the first native Ledger command in this workflow, load `$ledger` and
complete `$ledger ensure` once. Reuse that readiness for every later Ledger
command.

`cas trial` is an admitted macOS product surface. Probe
`cas capabilities --json` and require only the exact features needed by the
route. Private-v2 direct execution requires:

```text
hylo_trial_runner_v2
hylo_fd_lane_lease_v1
hylo_signed_run_receipt_v2
hylo_private_lane_materialization_fd_v1
hylo_private_receipt_redaction_v1
hylo_target_common_projection_opening_v1
hylo_trial_route_projection_v1
```

Historical execution additionally requires:

```text
hylo_internal_historical_replay_v1
dcp_v2
rip_v1
fir_v1
```

These keys are absent on non-macOS builds. Do not infer historical replay or a
sealed broker from `hylo_trial_runner_v2`. Legacy `hylo_trial_runner_v1` and
`hylo_signed_run_receipt_v1` remain compatibility features only.

Run preflight for each frozen lane:

```bash
cas trial preflight --trial trial.json --lane-id <lane-id> --json
```

Its route projection uses these exact fields:

```text
source_profile_kind
compile_replay_required
replay_preparation_mode
source_profile_body_delivery
execution_route
required_lineage
```

For a direct lane, require `source_profile_kind:"direct"`,
`compile_replay_required:false`, `source_profile_body_delivery:"none"`,
`replay_preparation_mode:"none"`, `execution_route:"direct"`, and
`required_lineage:null`. Skip
`compile-replay`; materialize the visible input, receive the exact lease-bound
Ledger claim through `--materialization-fd`, and invoke `cas trial run` exactly
once.

For a historical lane, require `source_profile_kind:"historical_decision"`,
`compile_replay_required:false`, `replay_preparation_mode:"integrated_run"`,
`execution_route:"historical_replay"`, and the frozen `required_lineage`.
For every v2 historical lane, require
`source_profile_body_delivery:"source_profile_fd"`; the public
`units[*].source_profile` is only the exact validator-defined safe projection,
and extra keys or semantic profile material are invalid. Supply the complete
historical profile directly to `cas trial run --source-profile-fd` from the
admitted materializer. Before claiming the lane, `cas trial run` privately
compiles exactly one DCP and RIP and binds their fingerprints into the claim
and terminal receipt. It then executes one bounded replay; a successful
terminal receipt must join the resulting FIR lineage, while a failed terminal
receipt records FIR unavailability. Embedded delivery is legacy v1 or
standalone diagnostic compatibility, not the v2 execution route.

Every `hylo-trial/v2` lane requires `--materialization-fd`, independently of
source route. The FD carries `hylo-lane-materialization-claim/v2` from
`ledger --source hylo lane-materialization`; it binds the public trial,
registration/start lineage, retained lease, selected treatment commitment, and
private treatment body without disclosing semantic role. It is distinct from
the visible-input, lease, source-profile, and signing-seed descriptors.

That private claim also carries the exact
`hylo-target-common-projection-opening/v1`. CAS accepts no raw
`target_common_projection` alias: it verifies the whole opening against the
public trial's target-common-projection commitment, then verifies the nested
`hylo-target-common-projection/v1` against its public projection fingerprint
before executor preparation. Neither opening nor projection body appears in
the public run receipt.

CAS emits `hylo-run-receipt/v2` for v2 trials. Its public materialization
projection is commitment-only: it may expose the treatment commitment,
visible-input lineage, permitted historical fingerprints, source-profile
delivery mode, and non-disclosure booleans. It must not expose semantic role,
raw target snapshot/materialization identities, target/factor archive paths,
package-tree fingerprints, or private evidence references. Its FIR carrier is
exactly `hylo-fir-public-projection/v1`; the full FIR stays private. Legacy
`hylo-trial/v1` continues to emit `hylo-run-receipt/v1` with its compatible
full-FIR carrier.

The v2 public materialization projection also carries
`materialization_claim_fingerprint`. Before reveal, it must exact-join the
same lane's `hylo-lane-materialization-receipt/v2.claim_fingerprint`. Ledger
requires one matching v2 receipt per lane and rejects changed, missing,
duplicate, or version-mixed per-lane safe-receipt sets before appending reveal.
This join does not apply to the legacy v1 receipt carrier.

Protected lane leases, visible inputs, treatment claims, source profiles, and
signing seeds use distinct anonymous directional descriptors numbered `>=3`.
Do not carry their secret bytes in argv, environment variables, regular files,
normal stdout, the event store, or proof bundles. A started one-claim lane is
never retried as new work; `status` and recovery may only finish or re-emit
already-admitted state.

### Diagnostic `compile-replay`

The standalone `cas trial compile-replay` command is historical-only diagnostic
infrastructure. It rejects direct lanes, case-blind or FD-delivered source
profiles, and `role_separated` or `sealed` assurance. It grants no execution
authority, reports `execution_authority:false`, and must not enter the normal
historical path. `cas trial run` neither consumes its receipt nor its DCP/RIP
files; run performs authoritative integrated preparation before the one-shot
claim.

For an allowed open, embedded historical diagnostic, `--output-dir` must name
a caller-owned canonical private root with no symlink path components and mode
`0700`. CAS creates the lane DCP and RIP as new `0600` files, rejects conflicts,
and revalidates modes, ownership, inode shape, and content fingerprints. Normal
stdout contains only `cas-trial-replay-plan-receipt/v1` metadata and
fingerprints; it never returns the semantic source profile, DCP, or RIP bodies.

### Sealed broker boundary

Sealed assurance requires an explicitly admitted external broker satisfying the
published role, protected-FD, checkpoint, recovery, and non-disclosure
contracts. The repository-owned `hctp-sealed-role-driver` is conformance/test
infrastructure, not an installed product command or capability. Fail closed
before secret generation or trial mutation when no admitted broker exists.
Retain `os_confinement:false`; the macOS route does not claim hostile same-user
process isolation.

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
