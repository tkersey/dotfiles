# Validation record and remaining qualification

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

Retain the existing 34 [campaign cases](behavioral-cases.md) and 28
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

## Semantic evaluation and ablation

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
