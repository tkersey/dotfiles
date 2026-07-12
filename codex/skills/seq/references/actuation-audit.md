# `$actuating` Audit

Use `seq actuation-audit` to measure whether material work followed the live
Zig kernel protocol.

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

Measure separately:

~~~text
actuation-open/v1 source authority and obligation coverage
actuation-event/v1 hash-chain and transition coverage
current repository and artifact bindings
prepared-operation-before-effect coverage
idempotency and capability-consumption coverage
operation-observation and evidence-fold joins
review-fold classification coverage
review-resolution/v1 strategy distribution
local-repair versus replacement-kernel outcomes
abstraction retirement and semantic-balance failures
workflow-bound CAS record coverage
non-cancelling initial review-wave completion
distinct standard clean chain length and final current-tuple clean
auxiliary-remediation carry evidence and non-credit accounting
auxiliary lens coverage and invalid evidence
Zig closure-decision/v1 live projection
proof-patch-after-closure ordering
ship-only public effects
subagent selection and lead fan-in
~~~

Treat scalar clean counts, old attempts relabeled to a new tuple, carry edges
without auxiliary resolution/correctness/actuation/SHIP evidence, opaque proof
references, raw review-to-patch transitions, any case where an auxiliary
finding cancels an in-flight lane, missing prepared operations, and replayed
closure decisions as control failures.

The installed `hylo`, `slices`, and `proof` modes remain historical dual-read
surfaces for older sessions. Do not interpret their legacy receipt coverage as
new-protocol success. Until the native command exposes the kernel fields,
use `report` plus `skill-decision-audit`, `skill-evidence`,
`tool-lifecycle`, and bounded `query` joins for missing dimensions.

Never call persistent goal context or internal context injection a successful
downstream skill outcome.
