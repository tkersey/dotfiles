<proposed_plan>
## Summary
Deliver one internal Cache representation that preserves the public API and
invalidation correctness while meeting the stated latency and memory bounds.
First compare the two allowed mechanisms on one workload; implement only the
selected route. Done requires final-tree acceptance proof and no dual strategy.

## Governed Specification
This is an illustrative Zig repository, not a claim about an inspected checkout.
The public Cache.get and Cache.invalidate signatures in src/cache.zig are fixed.
The source permits either generation-tagged entries (A) or eager invalidation (B)
internally, and forbids a runtime strategy switch or new public API. A get after
invalidate must never return the old value. Required-valid observations include
hits, misses, repeated invalidation, and subsequent refill. P95 must be at most
10 ms and peak cache memory at most 8 MiB on bench/workload.json.
The assumed build already supplies bench-cache, test-cache-a, test-cache-b, and
check targets. Verify these assumptions before effects; missing targets or an
unrepresentative workload returns to planning, not fabricated evidence.

## Architecture Decisions
SEAM-CACHE is source_bounded: keep the public API and required behavior, while
selecting A or B using OBS-ROUTE. Cache is the only production owner. A uses a
Cache-owned generation, tags entries, and admits a hit only for the current
generation; safely clear entries before counter reuse. B evicts affected entries
on invalidation so stale entries cannot satisfy a hit. Synchronization must preserve
this ordering on all supported access paths. Retire the losing representation and
any strategy-switch owner. These means are revisable only within the stated source
envelope; expanding the candidate space requires source revision.
The family is stale reads enabled by an invalidation bypass. Preserve every valid
hit/miss/refill outcome. Falsifier: a sanctioned path returns a stale value, both
representations remain active, or public API/latency/memory requirements fail.

## Implementation Sequence
ACTION-PROBE (performance owner): Verify the source/API/workload binding, then run
`zig build bench-cache -- --workload bench/workload.json --json` without production
mutation. Compare p95_ms, peak_bytes, and invalidation_pass for A and B using the
same workload digest. Failed, missing, contradictory, or inconclusive evidence is
contract_invalid. OBS-ROUTE selects the route by the exact rules below.

ACTION-A (engineering owner; after ACTION-PROBE and only route_a): Implement the
generation-tagged mechanism in src/cache.zig::Cache.get and Cache.invalidate;
update test/cache_test.zig for stale-read, generation rollover, and valid-refill
cases. Retire the losing owner/runtime switch. Run
`zig build test-cache-a --summary all` on that tree. Failure requires restoring
only session-owned edits and rechecking the baseline before a revised attempt.

ACTION-B (engineering owner; after ACTION-PROBE and only route_b): Implement eager
invalidation in the same owner and symbols; update test/cache_test.zig for stale-
read and valid-refill cases. Retire the losing owner/runtime switch. Run
`zig build test-cache-b --summary all`. Failure has the same bounded restoration
route. ACTION-A and ACTION-B are alternatives, never dependencies of one another.

ACTION-FINAL (engineering owner; after the selected implementation passes): Run
`zig build check --summary all` on the exact final tree. This common verifier must
check the fixed public API, required-valid matrix, stale-read exclusion, workload
latency/memory limits, and absence of the rejected production representation.
Inspect actual imports, construction, reads, invalidation, concurrency, and cache
ownership paths independently of the candidate's asserted inventory. Missing
coverage or an inadequate check target returns to planning; never claim the target
proves more than it checks. Only this common final proof closes both obligations.

## Decision Points and Branches
OBS-ROUTE: a candidate qualifies only if invalidation_pass is true, p95_ms <= 10,
and peak_bytes <= 8388608. Select the sole qualifier. If both qualify, select lower
peak_bytes, then lower p95_ms, then A on an exact tie. Neither qualifying blocks.
Invalid/inconclusive evidence or a false source assumption returns to planning.
Focused or final proof failure stops delivery and triggers restoration/revision.
Observe planned successor trees; expected implementation edits alone do not make
the plan stale. Unexpected source, workload, or relevant API changes invalidate
only affected assumptions and proof.

## Proof, Rollback, and Done-State
Select the stale-read and valid-refill discriminator before implementation. Derive
coverage from the repository's real sanctioned paths, including concurrency and
counter reuse for A. Samples are bounded evidence, not a universal guarantee;
claim full family exclusion only with a justified construction/preservation argument.
No source-required outcome may be weakened to make a test green. The common
PROOF-FINAL, produced after either selected implementation, closes OBL-IMPL and
OBL-FINAL; the other branch's focused proof is not required or credited.
On abort, restore the session-owned code/test delta without overwriting unrelated
changes and rerun the baseline checks. No deployment or publication is authorized.
Done requires one production representation, unchanged required API/valid behavior,
all acceptance checks on the final tree, and no unowned coverage or proof residual.

## Plan Identity and Source
plan_id: PLAN-cache-strategy
revision: 1
Target: illustrative /repo/cache on feature/cache; base/head labels are illustrative,
not observed commits. Source authority: the user requirements and delegated choices
fully stated in this block. Persistence: transient; optional EPG export embeds this
exact block. Runtime currentness and mutation authority remain with the consumer.
</proposed_plan>
