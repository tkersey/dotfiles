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
settings, tools, runtime, and grader. Do not freeze downstream actions or history
that the intervention is meant to change. Verify candidate delivery on each
compared condition. Preserve exact source snapshots or diffs and all completed
attempts, errors, exclusions, and interruptions; do not overwrite failed variants
or pool changed configurations. Repeat frozen conditions and interleave controls
when variation or drift matters. Use the task's sampling policy, never retry until
pass. Keep denominators and per-criterion outcomes explicit, and distinguish
final-output quality from recovered execution defects and missing observations.

Prefer deterministic checks of required artifacts/state when possible. A model
judge is fallible: calibrate against known cases, blind candidate labels and
randomize presentation when useful, and preserve the rubric. Investigate grader
errors separately. An authorized evaluator correction establishes a new comparison
with baseline and candidates re-evaluated; it cannot rescue a candidate by changing
its criteria alone. Do not let the candidate's self-description determine success.

Keep development examples, known regression controls, and untouched confirmation
cases distinct. Do not feed confirmation answers or hidden grader material into
candidate authoring or the evaluated agent. If an author sees or uses a confirmation
failure to revise the candidate, retire its held-out status for that successor.
Label-only tasks, plausible explanations, and correct initial actions cannot
qualify a claim about native execution and its downstream consequences.

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
Repeated selection on the same cases increases selection bias. Use a declared
sequential rule or fresh confirmation after exploration rather than repeatedly
peeking and stopping at the first favorable result.

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

## Confirmation and continuation

Diagnostic deletion may remove the symptom by removing a required behavior. Such
a result can inform attribution but is not an adoptable repair. Test
positive, negative, recovery, and opposing-obligation cases implicated by the edit.
Investigate successful controls as well as failures; redundant instructions may
matter only in combination or under harder conditions.

During optimization, each accepted change becomes the working incumbent; preserve
the original baseline.
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
