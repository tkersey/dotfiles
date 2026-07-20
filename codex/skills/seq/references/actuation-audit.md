# `$actuating` Audit

Use `seq actuation-audit` to locate candidate sessions for an Artifact Kernel
audit. The current native command does not parse the new artifacts or establish
kernel conformance by itself.

~~~bash
seq actuation-audit \
  --root ~/.codex/sessions \
  --workdir <workdir> \
  --since <time> \
  --until <time> \
  --exclude-current \
  --mode report \
  --format markdown
~~~

Evaluate these questions separately with `report`, `skill-decision-audit`,
`skill-evidence`, `tool-lifecycle`, and bounded `query` joins over the located
sessions:

~~~text
goal-contract/v3 authority and law coverage
construction-contract/v1 selection before material effects
one current Construction per material subject
governing-law and proof-obligation coverage
Actuating-selected operation scope before each repository effect
actuating-evidence-event/v1 sequence and custody
current subject identity at every proof or review observation
counterexample-set/v1 source binding classification and quotient coverage
accepted Counterexample exclusion rejection or blocker coverage
falsified and preserved predecessor claims across Construction successors
representation total-transition model property and differential proof strength
dominated-construct retirement and independent absence observations
CAS owner-receipt identity and non-cancelling initial 1+4 completion
one request-local recovery maximum after verdictless terminal transport failure
five consecutive distinct current-subject standard clean attempts
all review credit reset after every material subject change
Actuating-owned closure judgment after all current premises
proof-patch-after-closure ordering
Ship-only public effects and current publication readback
subagent selection and lead fan-in
~~~

Treat any of these as control failures:

- a plan, finding, Ledger validation, executor, CAS receipt, Ship receipt, or
  Proof Patch selects architecture or grants mutation;
- an accepted Counterexample selects a patch directly or lacks a current
  Construction disposition;
- architecture, proof strategy, scope, or retirement is selected outside the
  current Construction Contract;
- Ledger launches or interprets CAS, interprets Ship, selects a next action, or
  independently decides closure;
- a material subject change preserves any review credit;
- a finding or transport failure cancels a launched sibling;
- a verdictless request receives semantic credit or more than one recovery;
- a clean count substitutes for five distinct ordered current-subject attempts;
- a dominated predecessor, bypass, validator, representation, or proof path
  remains live at closure;
- public effects occur outside Ship;
- source-memory status gates or rolls back delivery closure.

Historical artifact names may be reported as observed text, but they never
count as Artifact Kernel conformance. Until a native Seq surface explicitly
parses the current four artifact families and owner receipts, do not report any
listed dimension as a direct `seq actuation-audit` measurement.
Never call persistent goal context or internal context injection a successful
downstream skill outcome.
