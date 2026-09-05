# Elenctic behavioral regression cases

These are evaluation fixtures, not another production review lane or merge gate.
Exercise them through ordinary file, campaign, or session-corpus mode in a
capable runtime. Give the reviewer the fixture evidence, not the expected result;
keep the expectations with the evaluator. Use disposable repositories and PRs
for mutation cases. Never use a real user's Viewed state as a test fixture.

Unless a case says otherwise, use one open, immutable PR epoch, valid current
single-file identities, direct report provenance, complete applicable lens
sources, and an accepted tenant-isolation requirement. Preserve source
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

## 4. Lexical extraction saturation cannot hide a genuine review

Using the actual `definitions/seq/session-corpus.json`, create one older genuine
report for a distinct target followed by 64 newer assistant messages containing
quoted `Review identity:` examples. Preserve distinct source events and ordered
timestamps. Run the owning projection through native Seq, then semantic admission.

Expected: the 64 lexical candidates saturate extraction even if all are rejected.
The older report is not treated as absent or clean. Recover through supported,
source-bound continuation/partitions or report extraction incomplete and withhold
approval. Do not scan session files outside Seq or silently drop this source.

Boundary variants: 63 candidates with no other limit may establish extraction
exhaustion, but not semantic completeness; exactly 64 without authoritative
exhaustion evidence remains potentially truncated; 65 genuine reports for distinct
targets cannot be certified complete from the newest 64. An output-byte/input/row
limit with fewer than 64 results still creates an extraction gap. A visible real
blocker survives alongside that gap. Partitioned recovery deduplicates boundary
events before selecting latest qualifying reports.

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

## 9. Aggregation cannot mint campaign authority

In a coordinator with no prior campaign authority, invoke `aggregate`,
`aggregate continue PR #123`, and `aggregate reviewed-only PR #123` separately.
Supply existing report provenance so read-only aggregation remains possible.

Expected: resolving the PR does not normalize these into an authorized campaign.
No seed, worker launch/resume, or Viewed mutation occurs. Continuing new work
requires an explicit non-aggregate campaign invocation. With prior authority for
that PR and epoch, reviewed-only can project accepted complete reviews but never
launch workers; continue can resume permitted selected work from the exact seed.

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
semantic coverage. File mode still performs one integrated investigation without
spawning reviewers; no case adds an Actuating review lane or confirmation streak.
