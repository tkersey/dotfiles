# `$actuating` Audit

Use the native Artifact Kernel join for one exact session and goal:

~~~bash
seq actuation-audit \
  --root ~/.codex/sessions \
  --session-id <session-id> \
  --evidence-store <repo>/.ledger/actuation/<goal-id>/evidence.jsonl \
  --goal-id <goal-id> \
  --mode kernel \
  --format json
~~~

`SEQ-ACTKERNEL-v1` directly verifies canonical Evidence envelopes, sequence,
hash-chain custody, Goal identity, and the session timestamp window. It reports
formal Construction, Counterexample Set, effect, operation, subject-transition,
and recurrence counts; owner-local implementation proof coverage; recurrent
example-only violations; and aggregate-only violations. The capability flag is
`actuation_artifact_kernel_audit_v1`.

These are structural measurements only. Seq does not classify findings, judge
proof adequacy, compute review credit, interpret publication, select the next
action, grade the run, or establish closure. Keep those owner decisions separate
with `report`, `skill-decision-audit`, `skill-evidence`, `tool-lifecycle`, and
bounded `query` joins when evaluating:

~~~text
Goal source authority and semantic law coverage
Construction selection before effects and one current Construction per subject
operation scope and exact subject-observation procedure before every effect
Counterexample source classification quotienting exclusion rejection or blocker
successor claim preservation and dominated-construct retirement
proof strength and independent verifier attachment adequacy
CAS receipt identity initial 1+4 recovery and five-clean convergence
review-credit reset after material subject change
Actuating-owned closure after proof retirement review and Ship premises
proof-patch ordering public-effect ownership and worker fan-in
~~~

Treat these as control failures: authority selected by a plan, finding,
validator, executor, CAS, Ship, or Proof Patch; accepted findings patched without
a current Construction; architecture, proof, scope, or retirement selected
outside that Construction; Ledger or Seq choosing a next action or closure;
review credit surviving material change; sibling cancellation; verdictless
credit or repeated recovery; clean counts replacing distinct ordered attempts;
dominated residue at closure; public effects outside Ship; or memory status
gating delivery.

Historical artifact names remain observed text, not conformance. Never call
persistent goal context or internal context injection a successful downstream
skill outcome.
