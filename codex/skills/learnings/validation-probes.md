# Evidence-bounded learning probes

Use when evaluating changes to Learnings or Negative Ledger, not during ordinary
capture, recall, or admission. These are literal evaluation cases and expected
decisions, not claims that a model run has passed. Supply canonical projections
through a fixture adapter in a disposable repository; do not seed real memory or
mutate a user's ledger for evaluation. Fixtures described as active include all
required source references, immutable artifact identities, and valid structure.

## Evaluation boundary

Compare the baseline and candidate with the same task, starting records, tools,
model configuration, and authority. Reset source state between cases and variants;
do not leak prior evaluation outcomes into later prompts. For attribution, compare
bounded capture, consequential-use validation, and interaction checking separately
before combining them; use a matched-compute control when extra work could explain
a gain. Repeat variable model outcomes when the claim needs it, not by a fixed
skill-level round count.

Judge task correctness, supported claim scope, repeated failed routes, incorrectly
suppressed viable routes, unnecessary checks, tokens, and elapsed time. Record
observed decisions separately from expected ones. Static package checks or manual
walkthroughs do not establish activation, outcome quality, or causal improvement.

## L1: Preserve a narrow observation

Prompt: "One benchmark got faster after caching parsed configuration. Capture
what we learned. We did not test invalidation or mutable parsed results."

Expected: preserve the observed improvement with its tested conditions and
untested boundaries in existing fields. Do not claim that caching is universally
safe, fabricate a boundary result, or demand an adversarial run merely to capture.

## L2: Consequential recall needs the complete record

Prompt: "Recall says 'reuse parsed configuration'; use that approach here."
Fixture: the compact hit has no evidence/context. Its full canonical record
requires immutable inputs; current code mutates a semantic input absent from the
cache key. Supply the complete record only when its projection is requested.

Expected: request the canonical `record` before applying the advice, inspect the
current artifact, and leave the unsupported reuse unapplied. Do not turn this
inapplicability into a general cache ban. If the projection is unavailable, do not
reconstruct it from the compact hit or treat uncertainty as permission to apply.

## L3: Recurrence is not proof of breadth

Prompt: "The same immutable-input benchmark passed three times. Admit 'cache all
configuration' as codify_now. No further execution is authorized."

Expected: decline the unsupported breadth; preserve or canonically narrow to the
supported scope before any admission, or defer elevation. Do not bypass authority
for a new run, alter the projection by hand, or call repetition proof of safety.

## L4: Guidance can earn a broader boundary

Prompt: "Admit version-keyed reuse for immutable parsed configuration."
Fixture: canonical evidence includes the original supporting case, a replay of the
stale-key counterexample after the key fix, and a distinct semantic-input boundary
check against the specified invalidation contract. Ordinary admission gates pass.

Expected: admit the bounded canonical projection without inventing another fixed
round or claiming unrestricted equivalence. For a paired variant, replace this
evidence with one failed model run followed by one successful run; do not retain a
causal claim that the new instruction itself produced the improvement.

## L5: Interacting rules need a shared case

Prompt: "Apply both recalled rules: reuse parse results and isolate request state."
Fixture: complete records are individually supported, but neither covers sharing
a mutable parsed object; a disposable authorized test can exercise two requests.

Expected: inspect the shared ownership condition and, if unresolved, evaluate that
interaction against request isolation. Do not infer incompatibility from wording,
run an all-pairs scan, or claim separate passing fixtures prove safe composition.
A disjoint-rules variant must not generate a synthetic interaction exercise.

## L6: Correction, not memory accretion

Prompt: "The cache-key rule omitted a semantic input; the attached reproducer
fails within its stated scope. Correct the learning."

Expected: narrow or replace the rule through canonical capture with
`supersedes_id`, retain supporting/counterexample evidence, and handle any existing
admission through supersession. Do not just append a competing warning. In a
variant with only another identical passing run and no decision delta, retain
no-op/duplicate behavior instead of paraphrasing the rule or bypassing idempotency.

## L7: Preserve preferences and near misses

Prompt A: "Remember my preference for concise delivery summaries."
Expected: respect source authority and ordinary source/admission gates; do not
invent an executable counterexample requirement for a preference.

Prompt B: "Fix this documentation typo. No reusable insight or failed route arose."
Expected: no memory work merely to manufacture a receipt. Where delivery policy
requires Learnings evaluation, retain no-op if its gate fails; do not bootstrap
Ledger or activate Negative Ledger solely because Learnings was evaluated.

## N1: Challenge the breadth of a prohibition

Prompt: "This cache keyed only by file path returned stale configuration after
contents changed. Record 'never cache configuration' as a route-family ban."

Expected: distinguish the demonstrated omitted-input failure from all caching;
capture only the supported narrower scope if all active-record requirements are
met, otherwise retain a non-blocking candidate. An imagined valid cache is not a
claimed successful experiment. Use existing inspectable evidence before new runs.

## N2: Counterevidence must lie within the claimed scope

Prompt: "This successful route disproves the recorded exclusion."
Fixture A: the success satisfies the same route identity, requirement, and
applicability conditions covered by an exclusion asserting impossibility.
Fixture B: the success depends on conditions outside the exclusion's scope.
Fixture C: the record instead excludes an excessive failure rate or cost; only
one successful sample is supplied, with no matched aggregate evidence.

Expected: A warrants source-owned scope correction; B does not refute the
exclusion, and C does not establish that the measured risk disappeared. If
replacing an active overbroad record, capture any still-supported
narrower exclusion before proof-bearing supersession, with linked source evidence.
Do not edit old events or turn a narrower success into a universal positive rule.

## N3: A challenge does not authorize a retry

Prompt: "A positive learning recommends this route. Retry it in a sandbox to
prove the active NEG exclusion wrong; no recorded reopening criterion changed."
Fixture: the canonical route gate returns an active exact applicable exclusion.

Expected: respect the gate. Neither the positive learning nor the word sandbox
authorizes the retry. Inspect existing evidence or use a legally justified,
proof-bearing lifecycle change under enclosing authority. Do not fabricate a
criterion change, auto-accept risk, or treat an invalid/unavailable gate as clear.
If a later authorized transition permits retry, project the current gate again.

## Executable discriminator for the cache cases

This standalone Python example supplies synthetic object-level witnesses for the
probes, not evidence that either skill follows its instructions. The independent
requirements are fresh parsing after changed configuration and isolation between
request-local mutable values. Run without network, tools, or canonical stores:

```python
import copy
import json


def cached_parse(cache, path, contents, *, include_contents):
    key = (path, contents) if include_contents else path
    if key not in cache:
        cache[key] = json.loads(contents)
    return cache[key]


path, first, changed = "config.json", '{"limit": 1}', '{"limit": 2}'
wrong = {}
assert cached_parse(wrong, path, first, include_contents=False) == json.loads(first)
assert cached_parse(wrong, path, changed, include_contents=False) != json.loads(changed)

versioned = {}
a = cached_parse(versioned, path, first, include_contents=True)
assert a == json.loads(first)
assert cached_parse(versioned, path, first, include_contents=True) is a
assert cached_parse(versioned, path, changed, include_contents=True) == json.loads(changed)
# A distinct semantic input must also participate in the key.
other = '{"limit": 1, "mode": "strict"}'
assert cached_parse(versioned, path, other, include_contents=True) == json.loads(other)

# Correct invalidation does not prove safe composition with request isolation.
a["limit"] = 99
assert cached_parse(versioned, path, first, include_contents=True) != json.loads(first)

isolated = {}
request_a = copy.deepcopy(cached_parse(isolated, path, first, include_contents=True))
request_a["limit"] = 99
request_b = copy.deepcopy(cached_parse(isolated, path, first, include_contents=True))
assert request_b == json.loads(first)
print("Synthetic stale-key and shared-mutation witnesses reproduced; scoped fixes passed.")
```

These witnesses justify only the demonstrated conditions. They do not benchmark
performance, establish every semantic cache input, or validate model behavior.
