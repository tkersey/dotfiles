# Validation record and remaining qualification

## 2026-10-23 subagent execution mode

The optional `execution=subagents` route retains one coordinator preparation and
the ordinary review semantics. `execution=fork` remains the new-campaign default.
Subagent identities carry their actual execution choice, null seed and a
coordinator-owned per-delivery token; the token does not authenticate native
provenance. Existing legacy identities and report namespaces retain their meaning.

| Check | Observed result | Evidence scope |
|---|---|---|
| Elenctic core suites (`test_campaign_state`, `test_report`, `test_policy`, `test_resolution`, `test_construction`, `test_review_cases`) | 113 passed | Mode-specific admission, missing/mismatched/stale attempts, nullable native turn IDs, selected coverage, legacy compatibility, report isolation, policy capture and existing workflow compatibility. |
| Ergasterion shared-renderer suite | 32 passed | Shared renderer compatibility, aggregate source boundaries and report regeneration. |
| Skill metadata, 57 relative reference targets, actual frozen-policy capture/verification and whitespace | Passed | Installed-package shape, source binding and availability of the new execution reference. |
| Actual subagent report generation and JavaScript compilation | Passed | Preserved actual execution identity/null seed and syntactically valid generated report script. |
| Independent instruction walkthrough on five supplied runtime states | Expected route and recovery actions | Explicit subagents without CAS, default fork obstruction, mode change preserving selection, stale token while a newer attempt is active, and feedback-only construction without worker launch. |
| Independent contract review | No actionable contradiction found | Default fork history requirements, explicit alternative, context delivery, permission boundaries and legacy recovery. |

The walkthrough was a plan from supplied runtime facts, not a live PR review.
Native history inheritance is preferred where supported; later subagent waves may
inherit extra coordinator context and do not claim identical seed histories.
No end-to-end session/subagent campaign or account-permission comparison was run:
this environment lacks `gh`, `codex` and `cas`. Browser execution was not run
(Playwright unavailable); report generation and JavaScript parsing do not qualify
browser rendering, storage, or prompt reduction across accounts.

## Earlier qualification records

The 2026-09-28 record below is historical. It does not qualify later revisions;
revision-specific work and the executable comparison assets follow it.

Recorded 2026-09-28 for the interactive-report and policy-binding change. These
checks validate implementation mechanisms, not the model's review judgment or
adherence to the campaign instructions. No native campaign efficacy claim is made.

## Executed checks

| Check | Observed result | Evidence scope |
|---|---|---|
| `test_policy.py` | 8 passed | Semantic lens projection, bound source/snapshot identities, installation changes, tampered/wrong/missing policy, no overwrite/path escape, changing capture inputs, installed directory symlinks. |
| `test_report.py` | 7 passed | Report serialization, seedless outcomes, verdict/coverage consistency, hostile text and URLs, stable identity/fingerprints, private atomic files and cross-campaign overwrite rejection. |
| `test_report_dom.py` | 5 passed | Actual Chromium DOM with controlled storage fixtures: check/note roundtrip, filters, mobile width, storage-write failure/session fallback, valid and wrong-campaign imports, hostile text, changed-evidence reopening and portable HTML bytes. |
| Native file-origin refresh/reopen | Attempted; navigation blocked | Chromium returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` before loading the report. This is not a passed refresh/reopen test. |
| Loopback diagnostic | Attempted; navigation blocked | The same navigation policy rejected loopback HTTP. It is not file-origin qualification even in an environment where it succeeds. |
| Desktop/mobile rendering | Inspected | Rendered fixture at desktop and mobile widths through `set_content`; no assertion of native file storage semantics. |
| Live Codex campaign, prepared forks, GitHub review mutations, model A/B evaluation | Unrun | This implementation environment has no `codex`, `cas`, or `gh` executable. Do not count fixture tests as those runs. |

The passing browser fixtures use `set_content`, explicitly supplied storage maps,
and captured portable-export bytes. They do not replace native browser storage,
reload, download or reopening tests. The native browser suite is supplied for that
qualification in a capable environment; no browser administration policy was disabled.

Runtime observed for the executed checks: Python 3.13, Playwright 1.57, and the
installed Chromium executable. Production scripts use only Python's standard library;
Playwright is a test dependency, not part of generated reports or skill execution.

## Reproduce implementation checks

From the repository root:

```bash
uv run --no-project python -m unittest discover \
  -s codex/skills/elenctic/tests -p test_policy.py -v
uv run --no-project python -m unittest discover \
  -s codex/skills/elenctic/tests -p test_report.py -v
uv run --no-project --with playwright python -m playwright install chromium
uv run --no-project --with playwright python -m unittest discover \
  -s codex/skills/elenctic/tests -p test_report_dom.py -v
uv run --no-project --with playwright python -m unittest discover \
  -s codex/skills/elenctic/tests -p test_report_browser.py -v
```

`ELENCTIC_CHROMIUM` may identify an already installed Chromium executable; otherwise
Playwright uses its installed browser. Browser suites report unrun/skipped when the
Python package is unavailable, and fail explicitly on browser/permission errors.
Do not turn missing runtime coverage into a pass. `ELENCTIC_TEST_HTTP=1` selects the
native suite's temporary loopback diagnostic only; the generated report itself
never starts a server. Python 3.10+ is required by the scripts' type syntax.

The native suite includes actual same-file refresh/reopen, session fallback,
portable download/reopening in a fresh context, import protection, multiple tabs,
keyboard operation, empty incomplete scope, text safety and responsive layout.
Browser `file:` storage behavior is implementation-dependent. Verify the target
browser rather than inferring it from DOM fixtures or from another URL scheme.

## Campaign regression scenarios to execute in a capable runtime

Retain the 36 [campaign cases](behavioral-cases.md) and 28
[thread cases](prior-review-threads.md). Add the following concrete variants to
those evaluations; give the reviewer source evidence, not expected conclusions.
These are currently unrun scenarios, not extra production review lanes or gates.

| Scenario | Required observation |
|---|---|
| Empty selection; native capability absent; failed seed after a published brief | Serialize and render each final report. Never-created context/seed fields are JSON null; an existing inaccessible seed retains its actual ID. A prior-thread blocker remains BLOCKED with incomplete coverage where appropriate. |
| Installed worker/lens changes after seed capture | Later/replacement workers use the same verified frozen bytes. The new installation does not silently change the campaign; changed snapshot bytes fail verification without granting coverage. |
| Elenctic and Actuating consume the same lens source | Elenctic receives the semantic prefix without native output commands. Actuating retains its native structured output and credit authority. Neither consumer loses substantive review questions. |
| Regenerate a report after continuation and after changed evidence | Same campaign/path/unchanged finding IDs retain user progress. Changed evidence reopens handling without losing notes. New epochs receive separate handling namespaces. Checkboxes never change verdict/coverage or call GitHub. |
| No findings, partial coverage, denied artifact write and explicit text-only | No vacuous approval or fabricated finding. Deliver the textual result and accurate artifact limitation; never claim a nonexistent HTML path or evade no-file authority. |

## Native-fork qualification

Keep the full prepared-history seed requirement. On the actual installed runtime,
freeze policy, prepare source analysis and the brief in the current turn, fork the
seed, verify observable retained history, then create two direct seed children.
Deliver full assignments while preserving resolved model/reasoning and permissions.
Collect exact-turn terminal reports and exercise interruption/recovery without
creating overlapping attempts. Verify policy provenance separately from source/seed
provenance. Runtime version strings or generic schema availability do not establish
this sequence's behavior. The existing native-forks reference labels its historical
observations by version; this change does not silently promote them to current proof.

## Historical semantic evaluation plan

Use the existing comparison instructions, identical pinned fixture sources and
model/reasoning settings, and withheld expected outcomes. Compare the original
instructions with one focused change at a time: slim routing metadata, consolidated
campaign wording, semantic lens projection, then the combined version. Preserve
full-history seeds and engineering obligations across those comparisons.

Measure supported defect detection, false blocking of valid counterparts, causal
discovery, acceptance of verified rebuttals, coverage honesty, evidence preservation,
mutation authority and actual preparation/review/reconciliation effort. Do not use
instruction phrase matches, finding counts, or shorter text as efficacy evidence.

Hold out causal structures, not just names: an ownership transition in an unchanged
adapter, a misleading prepared recovery hypothesis, equivalent invariant obligations
expressed through builders or aliases, and adequate encapsulation that must not be
blocked. The investigator must discover the discriminator; do not put the missing
premise or expected answer into the inherited seed. Record observed outcomes and
obstructions before making any claim of improved model performance.

## 2026-10-17 PR #343 revision: blind review subjects and report capture

`review_cases.py` supplies seven defective/adequate pairs with base and candidate
file trees: retained guarantees, temporal facts, liveness, composition through an
unchanged adapter, test authority, partial/complete author rebuttals, and valid
wire compatibility. These are small synthetic discriminators, not representative
efficacy evidence. Their requirements state the supported domain; reviewer exports
contain no allegation, expected verdict, family label, pairing, or executable probe.

The export/evaluator separation follows the existing
[Actuating auxiliary-discovery fixtures](../../actuating/tests/auxiliary-discovery.md).
Keep this utility, evaluator key, probe output, this document, and paired subjects
out of each reviewer's context and readable input directory. Give a reviewer only
one opaque subject directory plus its assigned instructions. A digest identifies
source bytes; it does not establish that a reviewer read them or prove its judgment.

```bash
uv run --no-project python -B codex/skills/elenctic/tests/review_cases.py export \
  --subjects /tmp/elenctic-subjects --key /tmp/elenctic-evaluator/key.json
uv run --no-project python -B codex/skills/elenctic/tests/review_cases.py check \
  --subjects /tmp/elenctic-subjects --key /tmp/elenctic-evaluator/key.json
uv run --no-project python -B -m unittest discover \
  -s codex/skills/elenctic/tests -p test_review_cases.py -v
```

Use new destinations for exports; `--seed INTEGER` makes an export reproducible.
Opaque IDs and order change across seeds. The reviewer-safe manifest binds each ID
to its source digest. The key stays outside the export tree. `check` executes only
the supplied fixture probes against matching source bytes and verifies both the
defective observations and adequate controls. A passing probe is not a model result.

Preserve each original report before evaluator adjudication, including incomplete,
incorrect, timed-out, and otherwise unsuccessful attempts. `record` copies bytes
without parsing verdict phrases or rewriting the report; it rejects a missing or
changed exported subject. `--context` can retain the actual supplied prompt/context
and declared model, reasoning, permissions, resource limits, and instruction hashes.
It is an observation record, not independent verification of those declarations.

```bash
uv run --no-project python -B codex/skills/elenctic/tests/review_cases.py record \
  --subjects /tmp/elenctic-subjects --subject OPAQUE_ID --arm current-full \
  --execution isolated-semantic --report /tmp/original-report.txt \
  --context /tmp/delivered-context.txt --records /tmp/elenctic-evaluator/reports
```

The execution label distinguishes an isolated semantic check, a seeded comparison,
and an actual native campaign. Recording a label cannot establish that execution.
Fresh generic subagents may perform isolated semantic checks; they do not satisfy
native seed/history/provenance requirements or establish a completed comparison.
The full native campaign and seeded three-arm comparison remain unrun until their
actual observable execution is recorded separately. This revision adds no production
review lane, score, automatic finding judge, model framework, or review credit.

### Executed on PR #343

Recorded 2026-10-17 using Python 3.12.14 and Node 24.19.0:

| Check | Observed result | Evidence scope |
|---|---|---|
| Complete Elenctic unittest discovery | 81 passed, 40 skipped; 121 discovered | Policy binding, report serialization and recovery, construction/resolution compatibility, fair queue and attempt checks, fixture isolation and raw report capture. |
| Ergasterion shared-renderer suite | 31 passed | Shared renderer compatibility, composition identities, source scope, numbering, drafts and private regeneration. |
| Exported fixture probes | All 14 matched their key | Seven witnessed failures and seven adequate counterparts; no model grading. |
| Skill metadata validation and relative reference targets | Passed | Package shape and source-link availability, not instruction adherence. |
| Three fresh isolated semantic reviews | One supported blocker; two adequate subjects approved | The deferred-preview pair was distinguished through the unchanged gateway and strongest author response. The adequate envelope preserved vendor compatibility without a spurious representation blocker. |

The 40 skips comprise 39 checks needing unavailable Python Playwright and one
opt-in native file-origin check. The executed storage tests run the production
JavaScript functions and startup call with controlled providers; they do not
qualify real browser storage. `codex`, `cas`, and a native browser runtime were
unavailable. The native drill and seeded three-arm comparison remain unrun.

Each isolated reviewer received one source package, its requirements/discussion,
and the self-contained worker contract, with no answer key, paired subject,
authoring diagnosis, or previous review. The full frozen auxiliary-policy bundle
and prepared-history seed were not supplied. Preserve these first reports and
source identities as isolated semantic observations; they are neither a complete
production campaign nor matched evidence for any comparison arm. Their source
traces were adjudicated against the fixture, rather than scored by verdict text.

Reproduce the combined implementation checks with:

```bash
uv run --no-project python -B -m unittest discover \
  -s codex/skills/elenctic/tests -p 'test_*.py' -v
uv run --no-project python -B -m unittest discover \
  -s codex/skills/ergasterion/tests -p test_report.py -v
```

### Three-arm comparison

Use the transferable source-binding, knowledge-access, contamination, repetition,
and all-attempt controls from
[construction-comparison.md](../../actuating/tests/construction-comparison.md),
with these Elenctic-specific interventions. Its construction prompts and acceptance
endpoints do not apply to this review experiment.

| Recorded arm | Worker semantic instructions | Prepared context |
|---|---|---|
| `current-full` | Exact frozen current worker contract and applicable semantic lens text. | Full prepared source-analysis history through the factual brief, from one immutable checkpoint. |
| `compact-full` | The compact experimental text below, with the same engineering authority and obligations. | The same full prepared source-analysis history as `current-full`. |
| `current-facts` | The same frozen current worker contract as `current-full`. | Source-bound facts, accepted requirements, complete relevant discussion, and factual topology; no inherited implementation rationale or provisional review hypotheses. |

Keep source, knowledge access, model/reasoning, permissions, and resource limits
matched. Both full-context arms must inherit the same preparation, not each other's
findings. Do not preload either arm's worker prompt into common preparation and
thereby restore text supposedly removed by the compact arm. Inspect the actual
visible instructions; if common inherited history already exposes that material,
report the instruction ablation as confounded. The facts arm must retain the same
necessary facts and author responses; removing a necessary fact is a different
experiment. It is deliberately experimental and changes no production seed rule.
For comparisons using the merge-policy revision, hold the actual selected policy
constant across arms and supply the same frozen Review Fold admission, merge-policy,
and engineering-standard sources to each. Earlier records retain their original
contracts and unrecorded mode. Use [merge-policy-cases.md](merge-policy-cases.md) for
the separate experiment that changes policy while holding evidence constant.

The compact arm replaces semantic choreography, not native assignment binding,
authority, identity, recovery, or report transport. Supply those unchanged carrier
requirements separately when exercising native transport. Use this experimental
worker text only in the comparison:

> Review the exact assigned delta and its causal consequences under the accepted
> requirements. Reconstruct the required observations and trace producers, owners,
> consumers, unchanged dependents, lifecycle, recovery, and relevant integration.
> Challenge positive claims, reasonable caller expectations, invariant preservation,
> duplicated correctness responsibilities, and omitted behavior or progress. Use
> decisive source evidence or the smallest authorized discriminator.
>
> Investigate Elenctic's engineering standards: changed tests should distinguish relevant
> incorrect behavior without freezing noncontractual choices; changed trusted
> boundaries should preserve stable laws through proportionate native ownership or
> representation. Establish applicability, material burden, and feasibility.
> Preserve independent oracles, raw/wire/draft shapes, adequate refinements and
> encapsulation, distinct temporal checks, required-valid behavior, compatibility,
> and actual resource constraints. No bad production caller is required for a
> demonstrated structural or test-quality violation; do not invent one.
> Apply the supplied Review Fold admission and bound merge policy separately:
> factual validity does not automatically establish a pre-merge obligation.
> Behavioral test adequacy remains a merge requirement in both modes. Pedantic
> adopts the additional construction commitment; pragmatic requires practical
> merge necessity or independent mandatory authority for structural construction
> findings. Preserve proven nonblocking risks and optional unknowns.
>
> Before retaining a blocker, try to defeat it with the strongest actual defense,
> including complete relevant author responses. Distinguish accepted obligations
> from preferences and missing evidence from violations. Reject refuted claims;
> classify retained findings as blocker, risk, or concern. Keep finding merit,
> coverage, discussion novelty, and action authority separate. Account for earlier
> evidence without silently dropping it. Complete the assigned causal scope or
> name the exact unresolved gap. Do not select repairs, publish, or mutate source.
>
> Return supported findings with authority, mechanism, evidence, impact, countercase,
> and scope. Use BLOCKED for a retained mandatory violation, APPROVE only with
> complete scope and no material decision gap, otherwise INCOMPLETE. Draft only
> eligible blockers, using rank-free "should" wording; link covered discussions
> rather than duplicating them. A different reviewer, head, or phrasing does not
> establish discussion novelty. Do not use finding counts or repeated votes as proof.

Select sample size, repetitions, ordering, and decision criteria before outcomes.
Score supported material discoveries, false blockers on adequate counterparts,
discovered decisive paths, valid rebuttals, required-valid preservation, honest
coverage, and actual work. Adjudicate unexpected valid findings from source rather
than treating the key as infallible. Preserve raw reports and source identities;
do not grade by phrases, preferred abstractions, or verdict extraction. These
published subjects are calibration material for anyone who has seen their keys.
Confirm any promising result on unseen causal structures and real pinned changes
before claiming a general benefit or changing production preparation policy.

## 2026-10-17 pragmatic/pedantic adjudication revision

This is the initial record at commit `6780b808620286fb1b99862c9dfda7a583cbbf44`.
It remains evidence of that policy's behavior. The test-quality correction below
supersedes its treatment of brittle tests; do not count the initial pragmatic
Concern as satisfying the clarified quality requirement.

This revision composes Review Fold's shared admission semantics into the existing
Elenctic investigation and adjudication. It defaults new work to pragmatic merge
obligations and permits an explicit pedantic engineering commitment. It does not
add a review lane or claim that weaker coverage produces better decisions.

### Executed implementation checks

Recorded with Python 3.12.14 and Node 24.19.0:

| Check | Observed result | Evidence scope |
|---|---|---|
| Complete Elenctic unittest discovery | 92 passed, 42 skipped; 134 discovered | Existing behavior plus explicit/legacy policy binding, rejected missing or mismatched assignment modes, policy-aware report identities, analysis/composition compatibility, and frozen shared admission. |
| Ergasterion shared-renderer suite | 31 passed | Existing composition and regeneration behavior remains compatible. |
| Review Fold admission suite | Passed | 18 concrete fixture probes, 20 declared evaluation cases, seven discriminating pairs, preservation and handoff checks. Its model evaluation remained unrun; these are executable/source contract checks. |
| Merge-policy fixture probes | All eight matched their factual observations | Source-bound extra test coupling, trusted carrier, subtotal, authorization revocation, mandatory verification, validated value, bounded preview, and optional durability cases. These probes do not grade model output. |
| Skill metadata, policy capture/verification, source reference targets, whitespace | Passed | Both affected packages validate; the shared admission bytes participate in policy identity. |
| Independent fresh source review | No material findings | Read-only review of policy authority, exact-mode continuity, historical compatibility, downstream optionality, and current implementation changes. |

The 42 skips comprise 41 checks needing unavailable Python Playwright and one
opt-in native file-origin check. Controlled JavaScript checks do not establish
browser rendering, real storage, or native file-origin behavior. The live native
campaign, complete worker/lens integration, and seeded three-arm comparison remain
unrun. Do not count unavailable checks as passes or synthetic subject checks as
evidence of native workflow execution.

### First isolated adjudication observations

Nine fresh reviewers examined seven distinct exported subjects. Two subjects
received paired reviews with identical evidence and semantic instructions and
different mode bindings. Other subjects received the one mode listed below.
Each reviewer received one opaque subject, the frozen shared admission and merge
policy, and the same Engineering obligations section. No reviewer received the
authoring history, evaluator key, sibling subject, or another reviewer's result.
There were no answer-seeking retries of an unchanged subject.

| Subject | Mode | First observed judgment | Source-based adjudication |
|---|---|---|---|
| Extra test coupling | Pragmatic | APPROVE with Concern | Preserved the real brittle assertion and adequate independent behavioral checks; did not invent a production failure. |
| Same extra test coupling | Pedantic | BLOCKED | An allowed inline implementation passes behavioral checks but fails the added helper-call assertion; the extra test standard supplies the merge obligation. |
| Internal completion carrier | Pragmatic | APPROVE with Concern | All actual producers preserve the domain law. The redundant structural burden remains optional without an invented external caller. |
| Same internal carrier | Pedantic | BLOCKED | The new trusted constructor admits forbidden combinations and independently maintains one relationship across producers; the review established a proportionate invariant-preserving construction. |
| Revocation during export | Pragmatic | BLOCKED | A permitted event hook revokes access before the second read. The candidate releases the document anyway; rarity does not waive authorization. |
| Bounded preview observation | Pragmatic | APPROVE with Concern | Demonstrated a split Unicode sequence while exact opening/export remained intact. The report retained factual certainty and optionality. |
| Optional durability question | Pragmatic | APPROVE with Concern | Current atomic visibility was supported. Unknown power-loss behavior for an unaccepted future offline mode did not force INCOMPLETE. |
| Supported value boundary | Pedantic | APPROVE with no findings | The checked, frozen owner preserves the invariant; unsafe state editing outside the explicit trust model did not establish a bypass. |
| Mandatory codec verification | Pragmatic | Merge blocked | Preserved the known skipped mandatory check as an unmet merge condition without calling it a demonstrated codec defect or inventing a pass. |

The bounded-preview evaluator hypothesis expected Risk rather than Concern.
The first reviewer instead treated grapheme-preserving truncation as optional
strengthening because the subject expressly permits approximate previews. That
source-backed boundary disagreement is preserved: the observed display limitation
was certain, its full-body containment remained explicit, and the merge consequence
was correct. These observations do not establish an exact disposition-match score.

The raw first reports and source identities were retained. Reviewers were fresh
isolated agents with inherited runtime settings and no model/reasoning override;
this was not a provider-version-controlled or repeated model comparison. Supplied
semantic sources came from policy snapshot
`sha256:345f5aa395e6b85e460702c5af802cc6db476a606ec73238ebde8eb1ec574893`.
Later navigation and prose-formatting edits changed snapshot bytes without changing
those adjudication rules. Only the named semantic components were supplied, not
the complete worker/lens bundle or a prepared-history seed. This is source-only
admission/policy evidence, not campaign provenance or a full-worker evaluation arm.

The eight fixture probes include the ordinary subtotal case, which received no
model review in this run. No general reduction in false blockers, unchanged recall,
or real-world merge throughput has been measured. Use
[merge-policy-cases.md](merge-policy-cases.md) to reproduce the isolated experiment;
use unseen causal structures and actual pinned changes before claiming broad
efficacy. Published cases become calibration material after their key is seen.

## 2026-10-17 test-quality correction

The user clarified that the existing test-quality rule intentionally builds
quality into reviews and removes brittle tests. The initial pragmatic exemption
weakened that requirement. Behavioral test adequacy now remains binding in both
modes; the subject still supplies independent authority for expected behavior and
permitted implementation changes. Adequate other tests can make deletion the
minimum sufficient correction. Keep the earlier reports and their policy identity
as historical observations, not evidence that the exemption met the user's intent.

The helper-call subject and its factual probe are unchanged. Its evaluator
expectation now requires resolution in both modes. One added contractual-delivery
subject distinguishes a legitimate interaction assertion from private-helper
coupling: internal delegation preserves the test, while duplicate external
delivery fails it. No production review script, report JavaScript, identity
format, or runtime protocol changes in this correction.

| Check | Observed result | Evidence scope |
|---|---|---|
| Policy-binding suite | 11 passed | Frozen policy and shared admission mechanisms. |
| Exported fixture checks | All nine factual observations matched | Source digests and compilable fixtures; the new delivery probe passes its permitted refactor and rejects duplicate delivery. |
| Skill metadata, actual policy capture/verification, relative references, whitespace | Passed | Package and source integration. |
| Fresh pragmatic review of the unchanged helper-call subject | BLOCKED on test quality | Established the ordinary inline counterfactual and accepted authority; retained correct production behavior and adequate independent coverage; removing the new test was sufficient. |
| Fresh pragmatic review of the contractual-delivery subject | APPROVE with no findings | Preserved the required external call count, arguments, and receipt identity; rejected the brittle-test allegation from independent protocol authority. |

Both reviewers used decisive source traces and claimed no test execution. The
fixture probes were executed separately. Each fresh reviewer received one opaque
subject and the shared admission, merge-policy, and Engineering obligations text,
without authoring history, evaluator key, sibling subject, or another result.
Preserve their first raw reports, exact delivered assignments, and source hashes.
They used inherited runtime settings without model or reasoning overrides.

The evaluated semantic sources are bound by policy identity
`sha256:18c3bc692bfaffb4a8bae93b453ddea76b7e1b39c3f11e3f08dce9c803435700`.
The broader implementation suite results above belong to the prior revision;
only the focused checks listed here were rerun. These two observations establish
the intended distinction on the supplied evidence, without qualifying a full
worker/lens bundle, native campaign, browser behavior, or general review efficacy.

## 2026-10-17 pre-merge report attribution correction

A focused final review found that composed-report branding replaced every
`Elenctic` occurrence in the trusted HTML template. The newly added source-policy
label therefore became `Ergasterion merge policy`, although only the Elenctic
assessment supplied that policy. The rendered metadata and copied handoff share
this label; the serialized source identity and verdict were unaffected.

Restrict branding to explicit title and wordmark placeholders. The existing
single-pass substitution continues to escape report data and leaves semantic
source names intact. Extend the existing trusted-template regression with a
source-policy label: it failed before the production fix and passed afterward.

| Check | Observed result | Evidence scope |
|---|---|---|
| Elenctic report suite | 15 passed | Rendering, escaping, identity, policy, and controlled storage-script checks. |
| Ergasterion report suite | 31 passed | Shared renderer, source boundaries, file mechanics, and the corrected branding regression. |
| Policy-binding suite | 11 passed | Snapshot capture and verification mechanisms. |
| Independent review and actual combined-report render | Correct source attribution; no further actionable finding in the corrective delta | Both assessments were present; only Elenctic supplied `merge_policy`. The title/wordmark remained Ergasterion and the policy label remained Elenctic. |
| Targeted browser policy-label check | Skipped: Playwright unavailable | Browser metadata and clipboard behavior remain unrun. |

The final policy/handoff source pass found no further actionable contradiction in
the pragmatic default, additional pedantic construction obligations, or shared
test-quality requirement. These were focused source reviews, not native Elenctic
campaigns. The actual-document observation checks generated source; it does not
replace browser execution or broaden the earlier efficacy claims.
