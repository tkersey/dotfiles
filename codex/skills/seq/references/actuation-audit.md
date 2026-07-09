# `$actuating` Audit

Use `seq actuation-audit` to measure whether material work followed the live
three-object protocol.

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
actuation-run/v1 source and authority coverage
current repo/base/branch/head/target bindings
selected-step-before-mutation coverage
completed-step and evidence-fold joins
review-fold classification coverage
review-resolution/v1 strategy distribution
local-repair versus replacement-kernel outcomes
abstraction retirement and semantic-balance failures
workflow-bound CAS record coverage
distinct current standard clean suffix length
auxiliary lens coverage and invalid evidence
closure-decision/v1 live recomputation
proof-patch-after-closure ordering
ship-only public effects
subagent selection and lead fan-in
~~~

Treat scalar clean counts, opaque proof references, raw review-to-patch
transitions, missing selected steps, and replayed closure decisions as control
failures.

The installed `hylo`, `slices`, and `proof` modes remain historical dual-read
surfaces for older sessions. Do not interpret their legacy receipt coverage as
new-protocol success. Until the native command exposes the three-object fields,
use `report` plus `skill-decision-audit`, `skill-evidence`,
`tool-lifecycle`, and bounded `query` joins for missing dimensions.

Never call persistent goal context or internal context injection a successful
downstream skill outcome.
