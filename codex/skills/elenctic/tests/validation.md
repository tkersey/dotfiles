# Validation record and remaining qualification

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

## 2026-10-17 revision: blind review subjects and report capture

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

### Executed on this revision

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
> Apply Elenctic's engineering authority: changed tests must distinguish relevant
> incorrect behavior without freezing noncontractual choices; changed trusted
> boundaries must preserve stable laws through proportionate native ownership or
> representation. Establish applicability, material burden, and feasibility.
> Preserve independent oracles, raw/wire/draft shapes, adequate refinements and
> encapsulation, distinct temporal checks, required-valid behavior, compatibility,
> and actual resource constraints. No bad production caller is required for a
> demonstrated structural or test-quality violation; do not invent one.
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
