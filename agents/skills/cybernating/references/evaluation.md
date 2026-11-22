# Evaluation discipline

Use for authorized behavioral comparisons, timing claims, or confirmation under
[the selected route](../SKILL.md#select-intent-before-the-workflow). Apply only the
sections relevant to the question: analysis does not require a latency objective
or candidate adoption. Reuse the task's runner, records, and Tune's measurement
methods; this is not another evaluation platform.

## What is being compared

Before a comparison, freeze the question, source intervention, baseline,
protected outcomes, important case strata, evaluator/version, competing predictions,
sampling/decision policy, and result-dependent next action in the existing record.
Bind the claim to the intended case distribution or explicitly to the tested corpus.
Keep diagnostic case weighting and repeated attempts distinct from deployment
weighting and independent task coverage when they affect that claim.
For adoption or timing claims, also bind the relevant objective and accepted
error/latency bounds. Do not manufacture tolerances from observed noise. Compare
paired outcomes and actual magnitudes, not only a headline average. If an adoption
tradeoff lacks an accepted preference, retain the qualified incumbent while
reporting the alternatives and continuing useful independent work.

A comparator includes source revisions, exact effective request or its available
identity, model and reasoning settings, tools/data/runtime state, task cases,
randomization/repetition units, resource exposure, and runner commands. A matching
Git head is insufficient when loaded references, conversation state, or generated
text changed. Use [source investigation](source-investigation.md) to trace
delivery. Unknown delivery limits source attribution; it also blocks a promotion
claim that depends on that delivery.

Hold relevant external conditions fixed: case, starting history/state, model
settings, tools, runtime, and grader, except the declared intervention. Do not
freeze downstream actions or history
that the intervention is meant to change. Verify candidate delivery on each
compared condition. Preserve exact source snapshots or diffs and all completed
attempts, errors, exclusions, and interruptions; do not overwrite failed variants
or pool changed configurations. Repeat frozen conditions and interleave controls
when variation or drift matters. Use the task's sampling policy, never retry until
pass. Keep denominators and per-criterion outcomes explicit, and distinguish
final-output quality from recovered execution defects and missing observations.

Prefer deterministic checks of required artifacts/state when possible. A model
judge is fallible: calibrate against known cases, blind candidate labels and
randomize presentation when useful. Freeze each condition's evaluator and rubric;
declare any evaluator or rubric difference as the intervention.
Distinguish measurement errors from target errors. Do not let the candidate's
self-description determine success.

Keep development examples, known regression controls, and untouched confirmation
cases distinct. Do not feed confirmation answers or hidden grader material into
candidate authoring or the evaluated agent. If an author sees or uses a confirmation
failure to revise the candidate, retire its held-out status for that successor.
Label-only tasks, plausible explanations, and correct initial actions cannot
qualify a claim about native execution and its downstream consequences.

## Improve the evaluation method

Use the same investigation loop to improve the evaluation method when this can
change the investigation or selection decision. Seek counterexamples to accepted
and rejected judgments, including judgments that currently appear sound; a
reported grader error is not a prerequisite. Reuse adequate evidence and stop
when the question is resolved or another challenge would not change the next
decision. A passing check alone does not require an audit.

Trace related failures to their measurement mechanism: omitted evidence, a proxy,
rubric interpretation, aggregation, case selection, or an observation boundary.
Preserve valid accepted and rejected counterparts, including unfamiliar valid
solutions. Compare supported corrections by fidelity to the accepted task and
the relevant resource objective, not by whether a preferred system candidate wins.
Distinguish correcting the task's measurement from changing its requirements,
thresholds, or verification policy; use existing authority for corrections and
do not silently change the accepted contract.

Give the evaluator revision its own identity. Compare its judgments against
unchanged task evidence with independently supported outcomes where available;
check the implicated false acceptances, false rejections, and protected controls.
A higher score, calibration agreement, or another judge's agreement alone does
not establish improvement. Apply development and confirmation exposure rules to
evaluator authoring too; a case used to repair the method is development evidence
for its successor. Unsupported distinctions remain unresolved.

Re-evaluate the original baseline and compared candidates under the same corrected
method. Revisit affected prior promotions, rejections, and conclusions whose
support depended on the faulty measurement. Preserve original observations and
judgments under their old identities. Reuse sufficient raw artifacts; rerun when
the corrected question needs missing observations or when changed feedback affects
execution. Reassessment does not require repeating unaffected work.

Separate improved measurement, changed selection, and improved system behavior.
Regrading unchanged artifacts can reverse a decision without changing the system.
A claim of better system behavior still needs a valid comparison under the
supported common method. Better measurement alone does not complete an unfinished
system-behavior objective; retain its remaining work within the accepted scope
and budget.

## Evidence transformations

When the target summarizes, aggregates, delegates, compacts, or resumes evidence,
use a relevant transformation to discriminate a live preservation question in the
existing comparison. Hold the subject, authority, and underlying observations
fixed except for the declared contrast. A transformed view can expose support
already present; omission or repetition cannot create support, independent events,
or permission. Lost deciding evidence calls for authorized source retrieval or an
explicit limitation, not stronger completion claims.

Choose only contrasts relevant to the suspected failure; these are authored probe
expectations, not executed results or a mandatory suite:

| Contrast | Expected distinction |
|---|---|
| Compress a report with an unresolved required check | Retain the unresolved obligation; "no defect established" must not become completed validation |
| Repeat one result under several wrappers or summaries | Preserve its original identity; references may be shared but do not create independent observations or extra review credit |
| Keep the prose but change its bound subject or invocation; contrast a continuation segment with the whole assignment | Re-evaluate applicability and independence from source identity and scope; a completed segment need not complete the assignment |
| Add unrelated compatible context, then separately add decisive new evidence or authorized scope changes | Preserve the supported disposition in the first contrast; revise only as warranted in the second, rather than demanding unconditional answer invariance |
| Supply adequate current evidence and actual authorization | Complete the permitted task; blanket refusal or endless rechecking is a regression, not preservation |

Score actual actions and claims against the source contract, including later
decisions affected by distinctions hidden by the immediate summary. Exercise that
later decision when it is the live preservation question. Matching answers alone
do not establish preservation; the untransformed answer may itself be wrong.
Check unsupported promotion and unjustified refusal, and permit newly derived
conclusions when the original evidence supports them.
Retain protected behavior and the existing end-to-end latency endpoint. Label-only
probes can diagnose a distinction but do not qualify native execution or prove
compaction safe. These are empirical preservation tests, not a formal theorem
about prompts, and require no new store, review lane, or evaluator platform.

## Joint accuracy and latency

Track each required criterion, success/failure/timeout counts, task denominator,
and material case families. Count failures rather than timing only easy successes.
When useful, report successful-completion latency separately alongside all-task
latency and failure rate. Zero successes do not yield zero cost per success or a
valid successful-completion latency. Do not assign a finite success time to a task
that never completed. Preserve cancellations and measurement failures distinctly.

Measure the endpoint the user cares about. Include retries, model round trips,
tools, retrieval, orchestration, and subagents on the actual critical path; do not
sum overlapping spans as serial work. First token, final answer, and completed task
are different endpoints. Tokens, calls, and prompt bytes can explain timing but
cannot replace measured latency. Keep experiment runtime/cost separate from the
runtime/cost of the candidate being improved.

Choose summaries supported by the sample: retain raw paired outcomes, sample size,
spread and uncertainty, and relevant medians/tails. Do not assert stable p95/p99 or
statistical non-inferiority from a few runs. A no-significant-difference result is
not evidence of equivalence. Resolve material uncertainty with the next justified
sample or return inconclusive; do not manufacture precision or retry until pass.
Repeated selection can bias the retained result even when each candidate receives
fresh cases. Scope the preselected decision policy to candidate selection,
result-dependent looks, and promotion attempts across the campaign; fresh confirmation
prevents tuning exposure but does not reset that history. Use evidence appropriate
to the stated claim, such as one reserved final confirmation after exploration or
a suitable sequential and multiple-comparison policy. An accepted empirical gate
remains usable within its declared scope; do not promote its result into a stronger
statistical claim.

Interleave or randomize comparison order where practical. Separate cold and warm
cache conditions when relevant and inspect actual cache observations. Prefix
reuse is not answer reuse; alternating variants can cross-warm shared caches.
Keep provider drift, changed tool data, machine contention, queueing, and concurrent
trial interference visible. Missing timing spans stay unknown, not zero.

A speed-only candidate needs evidence supporting preserved quality under the
accepted rule; a quality-only candidate must respect latency/resource constraints.
Without a stated exchange rate, do not invent a combined score or buy speed with
accuracy loss. A candidate that improves accuracy but costs latency is an explicit
tradeoff, not automatic adoption. Preserve promising non-dominated results without
turning the campaign into a mandatory population-search framework.

For example, an accepted gate may require no observed regressions on eighty
specified native cases and a latency reduction under the agreed timing rule.
If both variants preserve the same case outcomes, protected checks pass, and the
timing rule passes, the candidate can qualify under that gate; exact equality of
population quality is not established. Under a different contract requiring a
population non-inferiority bound, those same outcomes must satisfy that bound
instead. Keep permitted degradation, evidence uncertainty, and claim domain
distinct. Do not invent a loss margin or require a stronger guarantee than the
accepted task.

## Confirmation and continuation

Diagnostic deletion may remove the symptom by removing a required behavior. Such
a result can inform attribution but is not an adoptable repair. Test
positive, negative, recovery, and opposing-obligation cases implicated by the edit.
Investigate successful controls as well as failures; redundant instructions may
matter only in combination or under harder conditions.

During optimization, each accepted change becomes the working incumbent; preserve
the original baseline.
Check an edit's premises against the version it actually follows: an earlier
change can alter the inputs, scope, or authority that made the edit applicable.
Confirm the assembled candidate against that original as well as its predecessor:
several local wins can interact. Restore the native entry and task rather than
shipping a laboratory prompt that was never installed. Freeze the final source,
repeat with fresh confirmation appropriate to the scope, and run all required
package/native checks. Confirmation establishes only the measured claim and domain.

Use fresh confirmation appropriate to the claim. New attempts on tuning cases
assess repeatability there, not generalization; use untouched cases when claiming
transfer beyond them. Once confirmation feedback guides another edit, it becomes
development evidence for the successor.

After rejection or an inconclusive result, retain why it failed and the next useful
contrast. Reopening a settled contrast needs changed evidence or a new discriminator.
A budget limit or unavailable runner yields partial/blocked work, not fabricated
convergence. No number of investigator opinions proves that further improvement is
impossible. State the investigated frontier and remaining uncertainties explicitly.
