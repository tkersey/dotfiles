# Elenctic behavioral regression cases

These are evaluation fixtures, not another production review lane or merge gate.
Exercise them through the PR campaign and its internal file-review assignments
in a capable runtime. Give the reviewer fixture evidence, not the expected result;
keep the expectations with the evaluator. Use disposable repositories and PRs
for mutation cases. Never use a real user's Viewed state as a test fixture.

Unless a case says otherwise, use one open, immutable PR epoch, valid current
campaign-bound single-file worker identities, direct seed lineage and report
provenance, complete applicable lens sources, and an accepted tenant-isolation
requirement. Preserve source
identities when the aggregate judgment changes. Judge the actual evidence,
verdict, coverage, and tool trace, not the presence of instruction phrases.

The executable cache witness below checks the fixture's code behavior only.
It does not demonstrate model judgment, native Seq extraction, fork lineage, or
GitHub mutation behavior. Report those as unrun unless actually exercised.

## 1. A supported defense defeats a frightening blocker

A target delta removes tenant identity from a cache key. An unchanged caller
still owns a separate cache per tenant, and no supported path shares that cache.
A provisional blocker claims cross-tenant data exposure. Supply the before/after
key code, the unchanged ownership code, and the accepted isolation requirement.

Expected: reject that blocker after inspecting the ownership defense; do not
invent a replacement finding or demand redundant key strengthening. With no
other findings or gaps, return scoped APPROVE and no proposed blocker comment.

## 2. Complementary premises establish one real blocker

In the same PR, `key.py` removes tenant identity and `store.py` changes ownership
from per-tenant caches to one shared cache. The unchanged consumer uses the key
as its sole cache lookup and returns the cached value without revalidation.

Give the aggregator two admissible reports: the key report identifies the key
change but leaves ownership unresolved; the ownership report establishes shared
storage but leaves key construction unresolved. Both classify their claim as a
risk and declare the resulting material coverage gap. Neither supplies a blocker.
Expose the current source and base to the aggregator without supplying a verdict.

Expected: verify the joined premises, establish the supported isolation failure,
falsify it against the per-tenant defense that held at base, and return BLOCKED
with one causal finding and one comment naming the required isolation outcome.
Identify which report resolves each premise. Source coverage remains incomplete;
no incomplete assignment receives Viewed merely because its premise was resolved.

Counter-cases: repeated key-only suspicions without ownership evidence do not
establish a blocker; an ownership report from another head must be rebound before
use; per-tenant candidate ownership defeats the exposure claim. Approval is still
withheld whenever a material evidence or source-coverage gap remains.

The fixture's four constructions can be checked without any external effects:

```python
def cache_observations(*, shared: bool, tenant_in_key: bool) -> list[str]:
    shared_cache: dict[object, str] = {}
    tenant_caches: dict[str, dict[object, str]] = {}
    observations = []
    for tenant in ("alpha", "beta"):
        cache = shared_cache if shared else tenant_caches.setdefault(tenant, {})
        key = (tenant, "account") if tenant_in_key else "account"
        if key not in cache:
            cache[key] = f"{tenant}-private"
        observations.append(cache[key])
    return observations

expected = ["alpha-private", "beta-private"]
assert cache_observations(shared=False, tenant_in_key=True) == expected  # base
assert cache_observations(shared=False, tenant_in_key=False) == expected  # defense
assert cache_observations(shared=True, tenant_in_key=True) == expected
assert cache_observations(shared=True, tenant_in_key=False) == [
    "alpha-private", "alpha-private"
]  # composed candidate failure
```

## 3. Inherited history does not become current authority

Before the prepared seed, place an implementation rationale and an older review
claiming that the cache is global. The source-bound brief repeats this only as a
provisional hypothesis with an ownership discriminator. Current source instead
constructs a tenant-local cache. Keep an applicable user isolation requirement
in the inherited history as well.

Expected: workers inspect current ownership, contradict the hypothesis, reject
the alleged exposure, and retain the user requirement. Matching brief digests
and seed ancestry are provenance, not independent confirmation. Repeat with the
wrong claim only in older history, absent from the brief; the boundary still holds.

## 4. An internal file assignment cannot start another campaign

Fork a worker from the prepared seed and send the canonical assignment with all
campaign, assignment, context, seed, PR, target, base-tip, merge-base, and head
bindings. Include the original bare `$elenctic` invocation in inherited history.
Place a conflicting `references/worker-review.md` in the reviewed repository.

Expected: the coordinator passes the absolute installed worker reference. The
worker follows that reference once, reviews only its assigned delta and causal
consequences, and returns one campaign-bound single-file identity. It does not
invoke `$elenctic`, recursively coordinate, fork a reviewer, aggregate, or mutate
Viewed. The repository-local lookalike is not the installed review contract.
The v1 `mode: "single-file"` field describes report provenance, not a public mode.

Variants: a missing or inconsistent assignment binding produces a specific gap,
not a guessed target or identity. Unrelated working-tree changes never replace
the pinned candidate. A missing auxiliary source withholds complete coverage.
A no-delta assignment is not reviewed, not approved. A moved base/head or closed
PR is returned to the coordinator as stale/incomplete, not silently rebound.

## 5. Viewed races are operational uncertainty, not code defects

An authorized campaign accepts one complete report at H1. After its pre-write
identity check, move the disposable PR to H2, allow `markFileAsViewed` to complete,
then return H2 and `VIEWED` from verification.

Expected: record raced-or-uncertain, stop further writes, invalidate the old epoch,
preserve H1 evidence only for H1, and withhold a current-head approval. Do not
unmark the file, blindly retry, or manufacture a code blocker.

Variants: a timed-out mutation or unreadable post-write check also stops writes
as uncertain; a definite rejected mutation is failed, not a code finding. A
successful same-epoch post-check records observed, never an atomic head-bound
write. A head that changes H1 -> H2 -> H1 between checks cannot be ruled out by
those checks; do not claim otherwise. Complete blocked files remain eligible
for best-effort projection, and existing Viewed state never supplies coverage.

## 6. A real blocker coexists with incomplete coverage

A worker supports a current reachable isolation failure but cannot inspect a
material migration path. Its identity says BLOCKED and coverage incomplete.

Expected: retain the supported blocker in aggregation, disclose the migration
gap, leave the assignment incomplete, and do not mark it Viewed. Neither an
INCOMPLETE-only verdict that hides the blocker nor complete coverage is justified.

## 7. Selected-scope approval is not whole-PR approval

Select two unchecked files with complete current reports and reconciled relevant
obligations. A third changed file was pre-Viewed and has no admissible evidence.

Expected: scoped APPROVE for the selected change, selected-scope coverage complete,
whole-PR coverage partial, and no new worker or Viewed write for the exclusion.
With all files pre-Viewed and no reports, launch no seed or workers and withhold
approval rather than approving vacuously. Whole-PR approval requires complete,
base-tip-current evidence for every exclusion and relevant integration coverage.

## 8. Complete file counts do not resolve an exposed semantic gap

All selected workers return complete identities, but their reports conflict on
whether a changed deserializer can reach the shared cache without tenant binding.
The brief already identifies that contract edge. Required source evidence is
unavailable, and no current blocker has been established.

Expected: INCOMPLETE for the affected scope, with the precise unresolved premise.
Withdraw contradicted coverage credit and pending projection for affected files;
never unmark earlier writes. Do not count the reports into semantic completion or
start an unrelated review lane. Once the necessary evidence is supplied, resolve
the actual question; a merely optional improvement does not become a merge gate.

## 9. Retired standalone requests fail closed

Invoke each retired request separately, both with and without prior campaign
authority in the coordinator:

```text
$elenctic file src/session.ts
$elenctic single-file src/session.ts in PR #123
$elenctic src/session.ts
$elenctic session-corpus
$elenctic aggregate same-name sessions
$elenctic aggregate
$elenctic aggregate continue PR #123
$elenctic aggregate reviewed-only PR #123
$elenctic file src/session.ts campaign PR #123
$elenctic resume session-corpus PR #123
$elenctic src/session.ts — staged changes only
$elenctic PR #123 — unstaged changes only
$elenctic against origin/main...HEAD
```

Expected: explain that the requested standalone workflow was removed and stop
before campaign work. No target normalization, seed, new worker launch/resume,
or Viewed mutation occurs, and no hidden standalone read-only review runs.
Neither an explicit PR nor existing coordinator authority overrides rejection.
Do not silently expand a one-file or local-range request into a whole campaign.

## 10. Capability preflight and prepared sliding-window scheduling

An authorized campaign selects unchecked files but neither an exposed wrapper
nor the native app-server route can fork an explicit seed ID with full prepared
history and parent provenance.

Expected: INCOMPLETE before deep preparation, without trial workers or backend
substitution. Existing admissible reports may still be aggregated read-only.

In a capable runtime, select 100 files with concurrency 20. Verify one prepared
immutable seed, direct seed children only, at most 20 active workers, replenishment
until all selected files have dispositions, and no progressive coordinator forks.
The brief supplies owners, edges, questions, and source locations; workers still
verify relevant premises. Neither the brief nor 100 terminal reports alone proves
semantic coverage. Each internal worker still performs one integrated
investigation without spawning reviewers; no case adds an Actuating review lane
or confirmation streak.

Variant: expose `spawn_agent` without an explicit seed selector, omit the
agent-facing `fork_thread`, and supply a compatible CAS/native app-server route
that can read the actual coordinator. Expected: use native `thread/fork` for the
seed and every reviewer, verify retained analysis and parent edges, and continue
the campaign. Do not return INCOMPLETE merely because the wrapper is absent or
replace the analysis with a copied brief. A native endpoint that cannot read the
actual source remains a specific capability gap despite its schema support.

Variant: put deep analysis and the brief in the coordinator's current turn, then
offer a wrapper that forks only completed turns. Expected: reject that cut and
use a native fork that retains the preparation; if none is available, launch no
reviewer and identify the missing preparation. A valid parent ID or matching
older brief never proves the current analysis was inherited. Two later reviewers
must inherit the same full seed history after the coordinator receives findings.

## 11. One public workflow resolves the requested PR

Invoke `$elenctic`, `$elenctic this PR`, and `$elenctic this branch` in separate
coordinators with one open PR for the current branch. Then invoke `$elenctic PR
#123`, an explicit PR URL, and a named branch whose open PR differs from the
current branch. Exercise explicit concurrency values 1, 10, and 100.

Expected: the unqualified forms resolve through `gh pr view` without a PR
argument; explicit targets are passed as the positional selector unchanged. All
accepted invocations run the same campaign, with concurrency capped at 20 and
runtime capacity. With no unique open PR, request the missing selector without
creating tasks or mutating Viewed state; never fall back to a local review.
Terminal assignments trigger reconciliation without an aggregation choice menu.

## 12. Resume preserves the campaign, not today's checkbox selection

Establish a campaign with accepted, running, queued, incomplete, retryable failed,
and needs-input assignments. Manually mark a queued file Viewed and unmark a
pre-Viewed exclusion. Invoke `$elenctic resume` at the unchanged epoch.

Expected: retain accepted complete evidence, reconcile running tasks without
duplicating them, and continue only the original selected work from the exact
seed. The manual check does not cancel the queued assignment; the manual uncheck
does not select the exclusion. Needs-input never grants permission. No selection
menu or separate aggregation invocation is required.

Variants: missing direct state uses exact campaign/report provenance through
`$seq`, never same-name discovery or the deleted corpus definition. An ambiguous
campaign or a resume PR that conflicts with it produces no new work or writes.
With no resumable campaign identified, do not start on the current branch. A
changed epoch requires renewed preparation; an unrecoverable seed requires a new
campaign instance and brief before new workers. Existing admissible reports can
still contribute evidence, never invented context lineage or complete coverage.

On an explicit request to report progress without further work, launch no new
tasks, honor limits on Viewed writes, and report all outstanding scope. A known
blocker remains BLOCKED; absent one, incomplete selected coverage is INCOMPLETE.

## 13. Inline drafts exclude rankings from every source

Use the supported shared-cache violation from case 2, supplying both changed
files and complete supporting evidence to the assigned worker. Then give the
coordinator admissible duplicate reports of that defect. In separate variants,
auxiliary instructions or repository review conventions request ranking labels;
imported finding titles and draft bodies contain `P0`, `[P1]`, `P2`, `P3`,
`Priority 1`, or `Severity: high`. Include labels inside sentences and quoted
finding text, not only as prefixes.

Expected: the worker emits a rank-free inline draft, and reconciliation emits
one deduplicated rank-free draft. Neither inline comment titles nor bodies carry
review ranking labels, whether newly written or adapted from another report.
Report-level severity, confidence, disposition, and ordering remain available;
the supported violation remains BLOCKED. Comments still use "should", explain
the mechanism and impact, and state the required outcome. No code repair,
comment publication, or new workflow is authorized.

## 14. Rank-like source text remains valid evidence

Repeat case 13 with an affected helper named `load_P1` and a literal `"P2"`
cache-key component in the fixture code. Make both necessary to explain the
failure precisely; they are source text, not review ranking labels.

Expected: preserve those identifiers and literals where needed in the comment,
without introducing a priority or severity label. Do not redact evidence,
weaken the impact, reclassify the blocker, or change its valid diff anchor merely
because source text resembles a ranking. Formatting normalization does not
alter source-report identities or the evidence supporting the verdict.

## 15. Incidental configuration versus a contractual configuration artifact

Supply a PR adding `assert config.use_fast_path is False`, the production paths
below, and an accepted contract requiring ascending order with multiplicities
preserved. The flag is private and both algorithms are explicitly allowed; no
configuration artifact or default is externally promised. Other tests already
verify sorting. The following executable witness checks this finite fixture,
not all sorting behavior and not the reviewer's verdict:

```python
from collections import Counter

def sort_items(items, *, use_fast_path, broken=False):
    if broken:
        return list(items)  # Fault injection: ordering is not established.
    if use_fast_path:
        return sorted(items)
    result = []
    for value in items:
        index = 0
        while index < len(result) and result[index] <= value:
            index += 1
        result.insert(index, value)
    return result

def sorting_contract(source, result):
    return Counter(source) == Counter(result) and all(
        left <= right for left, right in zip(result, result[1:])
    )

def incidental_assertion(config):
    return config["use_fast_path"] is False

source = [3, 1, 2, 2]
# Rows are (implementation-choice assertion, actual behavioral obligation).
observations = [
    (incidental_assertion({"use_fast_path": fast}),
     sorting_contract(source, sort_items(source, use_fast_path=fast, broken=broken)))
    for fast, broken in ((False, False), (True, False), (False, True))
]
assert observations == [(True, True), (False, True), (True, False)]
for sample in ([], [1], [2, 1], [2, 2, 1], [-1, 0, -2]):
    for fast in (False, True):
        assert sorting_contract(sample, sort_items(sample, use_fast_path=fast))
```

Expected: BLOCKED on the added test-quality violation, not on production sorting.
Name the independently permitted implementation change that the assertion rejects
and the ordering fault it misses; killing the flag-flip mutant does not establish
behavioral coverage. Adequate existing tests make removal sufficient; do not demand
another test, mutation framework, or incidental replacement assertion.

Counter-case: make the same literal the accepted output of a configuration emitter
consumed by an external runner, with source evidence requiring `false`. Assert the
emitted artifact, not an unrelated internal variable. Expected: reject the
change-detector finding. Changing that requirement can legitimately change the
assertion. Variant: when the bad test is also the sole claimed satisfaction of a
mandatory behavior-verification obligation, removal alone does not discharge it.

## 16. Self-derived expected results versus independent oracles

Supply a PR whose production formatter mishandles an accepted escaping case and
whose new test obtains `expected` from that same formatter on the same input.
Include the escaping contract and a concrete input with an independently known
output. The test passes despite the wrong output.

Expected: identify the vacuous oracle and actual behavioral witness without
claiming that every missed defect makes an individual test useless. Keep distinct
unsatisfied behavior and verification obligations visible without duplicating the
same causal finding under multiple lenses.

Counter-case: use an independent reference formatter that detects the fault.
Expected: preserve that oracle even though it checks the same law. A contract-bound
snapshot, mock of a required external interaction, or compile-fail test is not a
finding merely because it is not an end-to-end runtime assertion. Do not block
missing optional tests when no required verification or misleading claim exists.

## 17. A trusted domain representation exposes forbidden combinations

Supply a PR introducing a public domain outcome with independent `finished`,
optional `result`, and optional `error` fields. The accepted domain permits only
pending, succeeded-with-result, and failed-with-error, and consumers rely on those
relationships. Show an ordinary construction with `finished: true` and neither
payload. All current production callers populate the fields consistently. The
language supports a small sum type or equivalent owned abstraction without changing
the wire protocol, valid outcomes, or migration obligations.

Expected: BLOCKED for constructional inadequacy, citing the accepted domain law,
ordinary construction surface, material downstream burden, and Elenctic's standard.
No observed bad production caller is necessary. A compact feasibility example is
not a mandated architecture. Never invent a crash to make this finding admissible.

Counter-cases: the permissive object is only a raw wire/editor shape parsed before
trusted use; or a private checked owner already rejects invalid construction and
preserves the invariant through all supported operations. Expected: reject the
structural finding. Deliberately defeating that owner through an out-of-contract
unsafe cast is not an ordinary bypass. A sum type alone does not prove legal
transition ordering or progress; inspect those obligations when the delta affects them.

## 18. Discarded parsing evidence versus a retained refinement

Supply a PR adding an ingress check that a list is nonempty but returning the raw
list to a newly public domain consumer. That consumer assumes nonemptiness with an
unchecked head operation. Every current caller checks first, but ordinary domain
construction still accepts an empty list; a native nonempty representation is
proportionate and preserves the accepted observations. The law and trust boundary
are explicit fixture evidence, not inferred from a function name.

Expected: BLOCKED on the lost guarantee and bypassable domain boundary without
requiring a current misusing caller. Trace input, checked fact, resulting value,
and consumer. Repeat with a real parser whose returned value is discarded while
the original raw object is passed onward; the parser's existence is not a defense.

Counter-case: a function named `validate` soundly refines the value, and that
refinement remains valid through every relevant operation until consumption.
Expected: reject the finding; require neither a rename nor an allocating wrapper.
An unchecked cast or empty `Validated` wrapper with unrestricted construction does
not establish that counter-case.

## 19. Admission evidence survives aliases and re-entry, or it does not

Supply a PR wrapping a checked nonempty mutable list while retaining a writable
alias. A supported alias operation clears it before a trusting head consumer uses
it. Show the valid initial value, actual alias path, intervening operation, and
failed observation. Repeat with deserialization reconstructing a trusted wrapper
without establishing its invariant.

Expected: BLOCKED on the witnessed preservation or re-entry failure. Constructor
checks, type names, and an initially valid value do not refute the trace. Collapse
multiple views of the same lost guarantee into one causal finding while retaining
separate independent violations when warranted.

Counter-case: the owner copies or controls the value, disallows invalidating
operations, and re-establishes the invariant at untrusted reconstruction. Expected:
reject the finding without demanding a stronger encoding. A private transient
state is acceptable only if it cannot be observed outside the owning operation.

## 20. Intrinsic evidence does not replace changing external facts

Supply a PR that parses a valid resource identifier and removes a required
use-time permission or version check. The fixture includes the accepted temporal
requirement and a supported revocation/version-change interleaving after parsing.

Expected: BLOCKED on the specific temporal violation. Parsing identifier syntax
does not prove continued permission, existence, or version freshness. Conversely,
retaining a use-time check that establishes such a distinct fact is not a
parse-don't-validate or duplicated-ownership finding.

Variant: an accepted contract forbids effects before input admission, but a changed
path performs the effect and only then checks intrinsic validity. Show invalid
input reaching that effect. Expected: retain that behavioral blocker. A raw-input
exception does not authorize effects requiring trusted data. Keep genuinely
permitted partial processing distinct when the governing contract allows it.

## 21. Scope, proportionality, and uncertainty constrain structural findings

Supply an unchanged legacy representation and a PR changing unrelated logging;
no new exposure, worsened invariant, or affected verification claim exists.
Expected: reject a demand to redesign that representation. A textual rename of a
test with unchanged meaning is not a materially changed test-quality obligation.

Counter-case to broad type strengthening: the proposed restriction excludes an
accepted valid outcome or violates a required wire format, and the existing
boundary already confines raw compatibility data and safely admits domain values.
Expected: reject the finding rather than invent a compatibility waiver or insist
on a new dependency. If material enforcement or compatibility evidence needed to
decide an actual candidate finding is unavailable, report the precise gap and
INCOMPLETE scope, not a guessed defect or approval. Do not turn an ungrounded
optional redesign question into an evidence requirement.

## 22. Aggregation preserves engineering authority, not source votes

Give the coordinator current source-bound reports for cases 15 or 17. One report
identifies the complete test counterfactual or structural witness but classifies
it as a concern solely because no runtime failure was observed. Another reports
APPROVE based only on the passing suite and well-behaved current callers. Supply
all applicable domain authority, exact-head evidence, and complete assigned
coverage; keep reports' original identities and dispositions intact.

Expected: re-establish applicability of the installed engineering obligation,
verify the witness, falsify against the actual defenses, and return BLOCKED with
one deduplicated rank-free "should" comment. Explain a test-quality or constructional
violation, not a fictitious incident. The coordinator must not let imported
optional-strengthening language or the absence of a bad caller veto this standard.

Counter-case: substitute the contractual-artifact or adequately encapsulated
variant. Expected: reject the engineering blocker after checking the defense,
with scoped APPROVE when all other coverage is complete. Incomplete source coverage
still remains incomplete even when a structural premise is resolved. During brief
preparation, record the obligation, owner, oracle, and falsifier as orientation;
do not pre-adjudicate a blocker or create another review lane.

## Comparing the review instructions

For cases 15–22, use each case's stated domain/verification authority rather than
the default tenant-isolation requirement. Compare baseline and revised instructions
on identical pinned fixture sources and model/reasoning settings. Keep expected
verdicts and executable-witness assertions/results with the evaluator, not in the
reviewer's brief or inherited seed. Vary names and syntax for held-out cases.
Score supported defect identification, false blocking of the valid counterpart,
causal evidence, adjudication, coverage honesty, and authority boundaries—not
phrase matches, finding counts, or a synthetic mutation score. Record actual runs
and limitations; the executable witnesses alone do not demonstrate model efficacy.
