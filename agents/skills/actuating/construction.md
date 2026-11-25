# Construction and acceptance

Use the applicable sections for implementation, source-bound analysis, verification,
resumption, or local completion. These are the construction and acceptance rules;
review execution belongs to [review-closeout.md](review-closeout.md).

## Source binding

Derive the Goal directly from the current accepted specification or direct user
instruction; read the exact source, not just a prior summary. Preserve required
outcomes, non-goals, hard constraints, compatibility contracts, permitted breaks,
and migration obligations. Bind repository, immutable base, and authorized path
scope; an implementation or plan cannot silently broaden them.

Separate required deliverables and source-fixed architecture from preferences,
examples, and proposed means. Do not promote a suggested mechanism into a law or
demote an explicit requirement. Source binding records obligations; Actuating
chooses source-permitted means. A plan, review, or prior implementation cannot
broaden source authority.

Keep semantic requirements distinct from execution authority. Bind mutation,
validation, publication, and review posture to the accepted source and selected
route; permission to work neither authorizes every effect nor proves completion.
For each required law, retain applicability and its deciding observation. If that
observation cannot be identified or required authority is missing, block only the
dependent action or claim; continue independent authorized work.

Before affected mutation, refresh these bindings when the source, authority,
scope, compatibility, or required observations change. Have `$review-fold`
reclassify all available applicable findings and failures against the refreshed
Goal; preserve unresolved evidence and original provenance rather than erasing it
or inventing continuity. Existing review-epoch and proof-invalidation rules apply.

Reuse an adequate binding in the Working Set and existing downstream owner formats.
No separate skill invocation, mandatory Goal Contract packet, durable record, or new
identity is required. A summary or digest never replaces the source or proves completion.

## Initial construction

This is the construction core for initial work and accepted counterexample repair.
Treat representations, algorithms, operation boundaries, and decomposition as
design variables wherever the source permits. Use mathematical and domain knowledge
to derive the construction, including `$universalist` for task-relevant semantic
work; a named defect, owner, axis, or typed hole is not a prerequisite. Reuse
adequate derivations rather than running a duplicate pass.

Work directly between required observations, concrete code, and deciding evidence.
Choose the next inspection, derivation, or authorized experiment because it resolves
an actual uncertainty or establishes a required relationship. No fixed order of
diagnosis, algebraic derivation, prototyping, or proof attempts is required. This
freedom changes neither effect authority nor the proof required for acceptance.

Missing proof is not a witnessed defect. A counterexample can challenge the
implementation, its model, an oracle, or a claimed justification; establish which
before treating its proposed remedy as necessary. Do not silently assume a missing
premise, transfer it to callers, or reject required-valid behavior to avoid it.

Prefer constructions that make required relationships consequences of permitted
operations over ones that repeatedly ask callers to reconstruct them. When the
relationship composes judgments, derive what each required condition can decide
from admitted evidence and its actual applicability, identity, and lifetime
dependencies. Distinguish prerequisites for using that evidence from other
conditions required for the enclosing result. Make the relationship explicit in
the native code: preserve independently decidable conditions and combine them
with the source-required scope, bindings, and quantifiers. Missing evidence may
obscure a condition only when that judgment depends on it; admission remains a
genuine dependency.

When effects must preserve separately owned resources, derive the permitted
footprint, legal surrounding context, and preservation by primitives and their
composition, including failure and recovery. Establish required information
independence separately: unchanged resources and differently named owners do not
alone prove it. Use the existing dependency variation in [proof acceptance](#proof-acceptance).
If the effect/specification relationship or a proposed refinement is unresolved,
consult [resource-sensitive effects](../universalist/references/resource-sensitive-effects.md).
Distinguish repairing execution from restricting admission or justified claims;
every source-required valid operation remains an obligation.

When the construction relies on a compositional law, cover its actual admitted
environments, callbacks, application, and handlers. Preserve required joint
observations with shared context; agreement of isolated results or marginal
distributions can erase a deciding relationship. Distinguish a captured value,
a fresh effect occurrence, and replay of an acquired response when those behaviors
are observable. Use the existing proof selection and
[laws in admitted contexts](../universalist/references/claim-appropriate-proof.md#laws-in-admitted-contexts)
to settle missing closure or contextual preservation. Neither restricting away
required-valid uses nor adding an unrequired probability or replay framework
discharges the source obligation.

Develop the implementation and its argument together. Establish primitive meaning
and why permitted composition gives the required result, including exceptional
outcomes and subsequent behavior. For admitted plans, commands, or checked
representations, establish that erasure, compilation, and actual handlers realize
the meaning justified by their construction rules. A changed interpretation can
invalidate that correspondence while leaving the syntax unchanged; re-establish
affected dependencies and reuse unaffected evidence. Hard or repetitive proof may
justify changing the representation, algorithm, or decomposition. Preserve authoritative facts,
derived observations, distinct history, and independent evidence in their actual
roles even when production meanings are shared. Complete the affected producers,
consumers, migrations, and retirements; a partial slice remains work in progress.
A local correction remains adequate when the existing construction establishes
the general relationship; neither local-repair-first nor redesign is compulsory.
A larger owner, extra type, or relocated check is not itself a gain, and neither
is a second deciding site: production code, such as a guard, reader, walk, or
eligibility predicate, that independently decides a law another site already
decides. Tests and independent oracles are evidence, not deciding sites. Add none
unless it carries a distinct accepted obligation or a justified derived
defense-in-depth or observation role, classified as [$reduce](../reduce/SKILL.md)
classifies enforcement sites; otherwise fix the sole site, delegate to the law's
owner, or unify the sites. Compare the resulting semantic responsibilities,
implementation complexity, and proof burden; a site count or smaller diff alone
does not establish adequacy.

Use the [construction repertoire](references/counterexample-guided-normalization.md#constructive-derivation)
and [supporting skills](architecture.md) when useful. Their examples are not
required architectures or intermediate deliverables. Keep the applicable
[common proof obligations](#realization-and-common-proof-obligations) and
[completion contract](#completion) fixed, not a prescribed account of how to think.

## Construction rules

Apply these rules to the stored state, transitions, and interfaces the Goal builds
or changes. Each excludes a defect family that review and simulation keep finding
in stateful software. They are construction means, not source requirements: a
violation is a liability only through a required law it breaks, and an explicit
source requirement governs a rule it contradicts.

- Delete state whose subject no longer exists. A record kept for a required
  observation, audit, idempotence, or recovery is history about its subject, not
  live state: no transition reads it as current.
- Give every stored state an exit by an ordinary transition until it reaches
  rest, a state with no pending obligation. Ordinary transitions are triggered by
  a request through the software's own interface, including an operator's, or by
  completion, elapsed time, a specified fault, or restart. Editing data, code, or
  configuration outside that interface is not one.
- Compute each derived quantity in exactly one function, invoked by every
  transition that changes it. An incremental update is an optimization of that
  function and keeps it as its oracle.
- Give every admitted input exactly one recorded terminal disposition, such as
  applied, rejected, superseded, or failed: never none and never two.
- Give each wire value one canonical spelling. Accept another spelling only where
  a compatibility contract requires it, normalize it on admission, and emit only
  the canonical one.
- Pass values, not references, across trust or namespace boundaries: wherever the
  receiver cannot resolve the sender's references against the same state, such as
  another trust domain, process lifetime, or owner.
- Make read surfaces report recorded facts, not predictions of a later decision.
  A surface whose purpose is prediction, such as a dry run, computes it with the
  deciding function.

## Simulation-first correctness

Reviews and example tests sample traces; the laws of stateful or concurrent
software quantify over them. A law is trace-dependent when its truth depends on
one of the properties listed below: state that outlives a run, the interleaving of
actors, retry, restart, recovery, or replay, time, or the outcome of an external
effect. A law that depends only on the order of operations on in-memory state is
a sequence law; property tests that generate operation sequences check it,
wherever the code lives. Classify each program or library the Goal builds or changes; a Goal
that changes no program or library, such as documentation alone, needs no
classification. It is stateful or concurrent when it has any of:

- durable state: data that outlives the process that wrote it and that a later
  run, or another actor of the same software, reads or relies on;
- concurrency: actors such as threads, tasks, processes, or peers whose
  interleaving can change an observation;
- retry, restart, recovery, or replay of an input;
- time: clocks, deadlines, timeouts, or schedules;
- external effects whose outcome later behavior depends on: calls or writes
  outside the process that can fail, stall, repeat, or reorder, when the software
  retries them, resumes after them, re-runs idempotently over them, compensates
  for them, or coordinates with other actors through them.

Daemons, runtimes, stores, schedulers, and protocols qualify. Software with none
of these, such as a parser, codec, or in-memory data structure, is a pure library.
So is a one-shot tool whose effects only fail fast: on failure it reports and
exits, leaving no partial state that a later run reads, and its outputs are its
result rather than state it reads back, such as a formatter or an artifact
generator. A tool that resumes, retries, syncs, caches, or keeps a state file is
stateful. Classify by these properties, not by repository, language, or size.
[Recurring sequence- or trace-dependent findings](recurrence.md#progress-before-another-iteration)
require reassessing the applicable generator or oracle and this classification.
Input order alone does not establish any of these properties: a pure library's
property tests can generate operation sequences. Reclassify it only when the
evidence establishes a listed property that its earlier classification missed.

For stateful or concurrent software, the construction includes:

- **Executable laws.** Each invariant is a function that tests and the simulator
  call. It carries, as data, the accepted-source location it encodes, such as a
  requirement clause or user instruction, or the construction rule it enforces,
  and its failure report names it. A construction-rule assertion that gates code
  also cites the required source law it protects and the conditions under which
  violating the rule breaks that law. A rule alone grants no gating authority.
- **Two-way law coverage.** Every trace-dependent law in the
  [source binding](#source-binding) is cited by an executable law the simulator
  checks, and every sequence law by a property test. Every executable law that
  gates code cites a binding law; a construction-rule assertion also names the
  [construction rule](#construction-rules) it enforces. A binding law without a
  check is missing required verification. A law that cites no binding law cannot
  gate the code: it either reveals a binding law to add from the source or remains
  a diagnostic without source authority. Where the accepted source has stable
  clause identifiers in the repository, make this check executable. Coverage shows
  that each law is checked, not that its check is adequate;
  [re-injection](counterexamples.md#re-inject-confirmed-defects) calibrates that.
- **Lifecycle tables.** Each stored-state machine has an explicit table of its
  states, [ordinary transitions](#construction-rules), and enabling conditions.
  Each state's pending obligation cites the binding law that creates it; that law
  is the source law the rest-reachability check protects. A mechanical check, at
  compile time where the language allows, establishes that every state reaches
  rest through ordinary inputs under the stated source-required environment
  assumptions. The simulator asserts that every transition it observes is in the
  table. This checks observed membership only; it cannot establish that a
  declared exit is implemented or its guard can be satisfied. Under
  [proof acceptance](#proof-acceptance), establish that the real code implements
  the exits and feasible guards on which the reachability check relies. Reuse
  adequate native evidence or a shared authoritative representation of table and
  implementation. Reachability establishes a possible exit; required eventual
  progress needs the separate check below.
- **A deterministic simulator over the real code**, as specified below.
- **Oracles for optimizations.** Every optimization the Goal builds or changes
  keeps its slow, obviously correct counterpart as an oracle, compared on the
  required observations in tests and in the simulator. The oracle shares none of
  the deciding logic it checks:
  [shared production logic cannot certify itself](verification.md#construct-the-necessary-work).

From one seed, the simulator runs the system's real code, such as its application,
drivers, and daemons:

- It owns every source of nondeterminism that code consumes: time, randomness
  (including runtime-seeded hashing), the scheduling of runnable actors, and
  services outside the software. Run embedded storage code, including an
  in-process database engine, for real in a per-run scratch area. Control its
  filesystem or disk seam when source-required faults include lost unsynced
  writes, torn or reordered writes, or power loss. Keep the real storage
  implementation above that seam; a process restart with surviving operating
  system caches does not establish power-loss durability. Choose the seam by the
  required fault model, not process placement alone. A service in another process,
  including a database server, is faked at its client seam; each
  fake produces the failures, delays, duplicates, reorderings, and isolation
  behavior its contract allows, checked against the real service. A fake that
  cannot produce a permitted behavior hides that behavior's defects.
- It chooses every interleaving and disturbance from the seed: restarts, replays,
  and faults, plus the other disturbances the requirements say the system
  survives, such as clock regression, configuration changes, or handoffs between
  owners. Running one seed twice yields the same event trace.
- It checks safety laws after every event. Check required progress under the
  source-required assumptions about future inputs, dependency availability,
  recovery, and scheduling fairness. State and realize those premises in the
  generated continuation. When the source requires admitted work to drain under
  those conditions, stop new admissions, supply the required outstanding inputs,
  settle faults as specified, and advance fake time through the relevant
  deadlines; check that the admitted obligations reach rest. A source-permitted
  wait for approval, a future input, or an unavailable dependency is valid while
  its progress premise is absent. Do not invent a timeout or terminal disposition
  to force it to rest. Also exercise the continuation where that premise holds,
  so a missing required exit still fails. An idle recurring schedule is at rest.
- It pins each failure as its seed and recorded event trace. The trace replays as
  a regression even after a generator change alters what the seed produces.

Pure libraries use property-based tests of their laws, with the same two-way
coverage against the binding, generators that reach the source domain and its
boundaries, and the same optimization oracles. A one-shot
tool also injects a failure at every effect seam and checks that the failure is
reported and leaves nothing a later run reads.

These are required verification under [proof acceptance](#proof-acceptance), and
only the user can reduce them. The laws, lifecycle checks, oracles, property tests,
and the simulator's pinned seeds and traces plus a sweep of fresh seeds belong in
the proof inventory that makes a head reviewable. Record each sweep's seeds,
generator version, and the event kinds it produced; a sweep that never produces an
event kind the changed code handles is incomplete. A sweep samples traces; keep it
distinct from exhaustive checking under the
[behavioral-model evidence rules](references/counterexample-guided-normalization.md#executable-behavioral-models).

When no simulator exists, build the smallest one that runs the real code paths the
Goal builds or changes, owns the nondeterminism those paths consume, and checks the
laws the Goal establishes or could break; grow it through
[re-injection](counterexamples.md#re-inject-confirmed-defects). A changed module
with no trace-dependent law, such as a string helper or an in-memory deque inside
a daemon, keeps its ordinary tests, with property tests for its sequence laws, and
runs in the simulator as real code; an in-memory module with one, such as an index
or cache that must agree with its source across restarts or interleaved writers,
has that law checked there. Seams the simulator
needs are part of the construction; a seam outside the authorized path scope is a
[source-binding](#source-binding) blocker, not license to broaden that scope. The
simulator drives the real code, so it is not the optional
[executable behavioral model](references/counterexample-guided-normalization.md#executable-behavioral-models),
which abstracts the code. In `analyze`, classify and judge against these rules
without building, extending, or running mutating controls.

## Proof acceptance

Required verification gates completion. Every required check must finish
successfully against the delivered state before you declare the work passed,
verified, or complete. Stopped, interrupted, timed-out, missing, or inconclusive
results leave verification outstanding. Resume or rerun the check; if blocked,
report the blocker and incomplete status. Do not silently waive a check,
substitute narrower evidence, or treat absence of a failure as success. Only the
user can authorize reducing the accepted verification requirement.

Keep each required check's command, mode, inputs, candidate, and terminal result
in the existing proof inventory. Collect the terminal result of a still-running
check; an observation timeout does not stop its execution. A skipped required
check or a successful result for a different candidate or required mode does not
discharge the obligation. Apply this rule to delegated checks and review-reported
validation as well as parent-run checks.

Before realizing a selected candidate, derive the required relationship from the
accepted source and identify the candidate's proposed guarantee. [Challenge its
sufficiency](references/counterexample-guided-normalization.md#challenge-the-sufficiency-of-a-local-guarantee)
by keeping that guarantee true while varying a source-relevant relationship or
permitted continuation: could the source-required relationship still fail? If so,
carry the missing distinction into the construction while preserving required-valid
alternatives. Reuse native evidence that already settles the implication. Check
that implication across the required consumers, phases, enclosing operation, and
evidence lifetime, including composition and resource growth when the source
constrains them. Preserve distinct historical and current-authority judgments when
reusing immutable evidence. A narrower improvement remains partial; a desirable
stronger property is not a correctness liability without source authority. Choose
a source-supported discriminator or decisive source argument and the exact-head
verifier before that realization. When partial evidence may introduce an unnecessary
dependency, keep a condition's deciding evidence fixed while varying a source-permitted
observation outside its dependencies. Check both the condition and its contribution
to the required result; the enclosing result need not remain unchanged. Preserve the
nearest required-valid case and a case whose genuine missing premise requires
uncertainty. Derive the variation from the source and native evidence path;
independently named fields do not establish independent meaning.
This selection rule does not demand a finished
causal account before authorized exploration; experiments remain subject to the
common proof and effect rules. Acceptance requires the actual mechanism,
migrations, and retirements, not intent.

When interacting operations leave a material construction or proof uncertainty,
use an [executable behavioral model](references/counterexample-guided-normalization.md#executable-behavioral-models)
if it supplies deciding evidence that adequate native evidence does not already
provide. Keep modeling optional and within existing proof selection.

When transfer from a model, certified syntax, or abstraction to execution remains
unresolved,
use [claim-directed correspondence](../universalist/references/claim-appropriate-proof.md#claim-directed-correspondence).
For construction rules and interpreters, use the
[syntax-specific argument](../universalist/references/syntax-semantics-pivot.md#from-construction-rules-to-interpretation).
Reuse adequate native evidence.

When a construction or its deciding evidence uses a projection, normalization,
summary, reconstructed witness, or round trip, inspect the actual consumer and
establish whether its inputs determine the source-required judgment. For a common
witness, distinguish the adequacy of its relevant producer paths from the
correctness of the shared judgment. When the claim requires more than those inputs
directly observe, use
[determination before cancellation](../universalist/references/claim-appropriate-proof.md#determination-before-cancellation).
Reuse an adequate argument or establish why agreement determines the required
property. Include the next actions and claims justified by the evidence: could
two cases agree in the compared view but require different decisions under the
accepted source? When that implication is uncertain, use the existing
[law-adequacy countermodel technique](../universalist/references/domain-algebra/property-test-derivation.md#test-whether-the-laws-specify-the-intended-behavior)
to seek a source-permitted violation hidden by the comparison. Keep independent
evidence for required distinctions the comparison discards, including permitted
continuations; recover missing deciding evidence before the dependent decision.
Retain adequate existing oracles. A countermodel challenges the
proof implication, not automatically the production code. Intentionally lossy
observations remain adequate when they and their required continuations are the
accepted contract; do not require irrelevant representation equality. Keep this
in the existing proof selection, with no new pass, report, or per-test quota.

At entry and after material change, bind the Goal, immutable base, exact head,
current construction, proof inventory, and any publication state. Read the
relevant source, not a remembered architecture. Unknown evidence receives no credit.

Preserve source-backed obligations and the independent observations and conditions
that distinguish their relevant failures. Unless source-fixed, fixture sizes,
repetition, preparation, check placement, and build arrangements are design
variables. When replacing verification inputs or execution paths, ask whether the
replacement could pass despite a source-relevant failure the prior witness would
expose, even with unchanged assertions. Preserve required deciding evidence through
the replacement or another adequate argument, and describe any reduced coverage.
Reuse decisive native evidence; incidental fixture detail or redundant execution
need not survive merely because it existed. When another witness exercises the
same supported relationship, generalize the deciding evidence through an adequate
property, table, generator, or native argument. Use a reference path as oracle only
where the source requires its behavior. Keep witness inputs as named cases and
preserve or re-establish sensitivity to each distinct violation. Retain separate
checks when they supply independent evidence or observe different required behavior.

Retain distinct executable evidence for continuing source-backed obligations in
the repository's existing verification path for affected successors. Confirm
that it actually runs and preserves defect sensitivity and required-valid cases.
Reuse adequate checks or decisive source arguments; temporary investigative
probes need not become permanent tests.

Before accepting validation for local completion or reviewability, inspect the
base-to-candidate diff and actual check selection for deleted tests, weakened
assertions, skipped checks, or reduced coverage, including changes made directly
by Actuating. Map each affected check to its source-backed obligation; require
preserved or stronger proof, a source-grounded oracle correction with independent
evidence, or explicit user authority retiring the obligation. A passing weakened suite
cannot discharge an unchanged requirement. Keep unexplained proof loss unresolved
and block only dependent completion or reviewability. Reuse the existing proof
inventory; no separate critic, packet, or review stage.


## Comments in code

Do not write explanatory comments in source code, tests, or examples, including
inline/block comments, docstrings, and optional API documentation. Apply this rule
to delegated implementation work.

Express intent through precise names, types, ownership, and operations; enforce
invariants in the construction. The absence of comments is not correctness evidence.
Do not add abstractions or documentation files solely to avoid a comment.

Reserve comment syntax for mandatory legal notices, required machine directives,
and documentation explicitly required by the accepted source or current user.
Preserve unrelated existing comments. Check added comments against this rule
during the existing diff inspection.

## Realization and common proof obligations

There is one operation: realize the selected construction, initially or as a
successor. Selection states an intended mechanism and falsifier; acceptance
requires the actual exact-head code.
Local experiments may occur only with mutation authority and outside an open
review epoch. They are not reviewable, publishable as complete, or proof by intent.

Every initial construction and correction must establish the applicable obligations:

```text
required relationships realized and required-valid behavior and observations preserved
current accepted witnesses addressed when present
supported causal families covered at the declared claim strength when present
required verifiers and required sibling/domain discriminators completed successfully on the exact candidate
all relevant sanctioned producers, consumers, transitions, and bypasses accounted for
admission and permitted operations enforce the required law in the declared domain
proof authority, inputs, domain, and public claim agree
all correctness-bearing Git changes have accepted authority
displaced primary compensators retired or justified by distinct obligations
complete Goal-required proof inventory on the exact candidate
```

For an invariant-style safety law, establish valid admission, preservation under
permitted operations, implication of the law, and closure of sanctioned escapes.
Cut coverage proves passage through an owner, not preservation afterward. Account
for aliases, lifetime, interleavings, and externally visible effects when implicated;
transient invalidity must not escape its owning transition. Required progress and
trace behavior need their own arguments; disabling all operations is not success.

Prove every applicable changed-boundary obligation using the strongest adequate
repository-native evidence. A closed construction/operation surface can establish
coverage directly; an opaque type name or passing build alone cannot. Where route
or migration coverage remains unestablished, use the source-derived topology proof
in [counterexample-guided-normalization.md](references/counterexample-guided-normalization.md).
Never derive the verification domain solely from the candidate's asserted list.
New unaccounted sanctioned paths invalidate coverage under either representation.

For finite domains, complete claims need exhaustive coverage or a justified
construction proof. For open domains, they need a justified generator and
preservation argument. Samples, sibling tests, and clean reviews are falsification evidence, not universal proof.
Otherwise report the explicit bounded domain and residuals; never silently turn
containment into elimination or weaken required behavior to obtain a green result.

`isolated-restoration` and `construction-normalization` may describe the actual
delta afterward. They are not pre-mutation certificates or different proof bars.
A changed owner, cut, carrier, interpretation, topology authority, proof universe,
or claim strength cannot be hidden in a batch labeled restoration. A public claim
correction retains its own authority and closure consequence. Unknown evidence
means investigate or block the affected claim, not invent a digest or a rewrite.

## Construction Working Set

Keep the current Goal/head, required relationships and source-derived domains,
construction and deciding evidence, admitted witnesses and causal account when
present, source horizon, actual proof, migrations, retirements, residuals, and
unresolved work in the active thread or accepted implementation
specification. Reuse owner evidence rather than re-expressing it in another packet.
These are working facts, not a report template or durable Actuating store. Surface
only material decisions and limitations; preserve historical witness provenance.

Carry the [recent attempt history](recurrence.md#progress-before-another-iteration)
with these facts through successor heads, delegation, and resumption, including
compaction. Review-credit resets do not erase unsuccessful approaches or the
evidence needed to reconsider them. Recover missing history from its owners;
unknown history is not a fresh start.

Make the construction assignment the source-required relationship, not the reported
edit. For an admitted counterexample, identify the implicated success: the fact,
authority, or effect being granted, not merely a successful return. Identify the
condition the accepted source requires whenever it is granted, the required-valid
behavior, and the deciding evidence or unresolved question. Construct the successor
so every relevant way of granting that success satisfies the condition within its
source-required domain and evidence lifetime, including newly introduced shortcuts
and permitted continuations that can invalidate its basis. Follow the implicated
operations, not unrelated commands. Preserve the requirement, not an obsolete
mechanism; reuse adequate native constructions and direct corrections. Retire
displaced weaker success decisions without erasing distinct authorities.
Closing a finding or passing its witness does not retire that requirement; revise
or retire obligations only as their accepted source and applicability permit.

Carry this assignment, its source, and deciding evidence through selection,
delegation, and resumption, including compaction; recover it from the bound source
when missing. Finding identities, locations, and suggested edits are evidence and
revisable means, not the assignment's scope or completion condition. Narrower
subtasks do not discharge the enclosing obligation. Keep this in the existing work,
without a separate packet, stage, or required presentation.

When completed reasoning should change future construction, verification, or
adjudication, preserve its useful consequence through
[Learnings' destination selection](../learnings/SKILL.md#decision-before-retention).
Reuse an adequate existing owner artifact; retain deciding premises and evidence,
or recoverable owner references, when the conclusion alone cannot guide reuse.
A retained argument supplies conditional evidence, not authority or current
applicability. Failed authorized retention remains failed; preserve material
recovery references through an existing authorized handoff before their sole
context is discarded. This neither creates an alternate corpus nor blocks work
justified independently of missing history.

## Completion

`implement` stops at local completion, not publication or review convergence.
Local completion requires the accepted Goal realized on the exact head, its
complete required validation, no unresolved accepted liability or unauthorized
strengthening, and honest claim strength and owned residuals. Do not claim an
experiment or an incomplete proof as complete. Read [closure.md](references/closure.md)
when deciding a publication-bearing or review-closeout terminal state. State the
law attempted, the conclusion established by the actual construction and evidence,
and its limits. A narrower supported claim does not complete a broader accepted Goal.
An explicit limitation or owned residual cannot discharge required verification;
apply [proof acceptance](#proof-acceptance) before any completion claim.

Bare Actuating continues through authorized Ship and review-closeout; do not
stop for approval merely because the first implementation exists. Missing
information, evidence, or authority blocks only its dependent action or claim;
continue independent authorized work. Complete the object-level task before
optional learning or memory capture.
