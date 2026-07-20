# CAS Review Transport Boundary

CAS starts, waits for, recovers, and reports exact review attempts through:

~~~text
cas review run
cas review start
cas review wait
~~~

Its owner receipt binds the review target, opaque request identity, exact
instructions, attempt and thread/turn identity, principal quality, backend,
transport state, structured semantic verdict, failures, and finding provenance.

CAS decides no review policy. The caller owns dispatch topology, whether a
fresh attempt is admitted, semantic credit, finding classification, repair,
mutation, and closure.

## Opaque request binding

~~~json
{
  "workflowBinding": {
    "requestId": "opaque-caller-id",
    "requestFingerprint": "sha256:..."
  }
}
~~~

CAS requires two non-empty strings, includes the complete object in attempt
identity, and returns it unchanged. It does not decode a lens, role, campaign,
or credit rule from the binding.

## Attempt evidence

`reviewAttemptExists` is true only after `reviewThreadId` exists. A semantic
tuple verdict exists only when `reviewVerdict.tupleVerdictExists=true` and its
base, head, and target fingerprint match the requested target.

The owner receipt may expose:

~~~text
reviewAttemptPhase
reviewAttemptExists
reviewThreadId
reviewTurnId
baseSha
headSha
targetFingerprint
principalStrength
accountFingerprintReducedProtection
backendClass
reviewVerdict.status
findingCount
failureClass
failureCode
failureHint
findingId
findingFingerprint
reviewAttemptId
titleHash
bodyHash
normalizedLocation
~~~

Process exit status is transport evidence only. It never creates `clean`,
`findings`, or workflow credit. A live timed-out attempt is recovered through
`wait`. A new attempt requires a caller-admitted fresh identity and
`--fresh-attempt` reason.

CAS reports those owner facts without deciding their semantic adequacy.
Actuating requires `principalStrength == "strong"`,
`accountFingerprintReducedProtection == false`, and
`backendClass == "cas-start-wait"` for review credit under its current static
Review Contract.

For Actuating, CAS receipts are external evidence. Actuating binds the 1+4
requests, controls dispatch order, evaluates current identity, applies the
one-recovery rule, classifies findings through `$review-fold`, counts clean
attempts, resets credit on material subject change, and decides the next action
and closure.
