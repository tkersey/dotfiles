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

An authorized campaign selects unchecked files but the runtime cannot fork an
explicit seed ID or expose parent provenance.

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
