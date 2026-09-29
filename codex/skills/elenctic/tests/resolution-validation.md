# Resolution mode: validation and behavioral cases

Recorded 2026-09-29 against the change based on dotfiles
`84a3797154b7a7be012da7b2fd1181739580f064`. Production changes are confined to
Elenctic. The Glaze and Metanoetic canonical skill texts, concurrency policy,
worker review and review identity schemas are unchanged.

## Executed implementation checks

| Check | Result | Scope |
|---|---|---|
| `test_resolution.py` | 18 passed | Legacy comment compatibility; lossless explicit resolution; supplied original numbers; ordering/fingerprint independence; complete group/check partitions; dependency validity; unavailable/empty synthesis; same-report number history including withdrawn findings; cross-campaign rejection; inert source text. |
| `ResolutionDomTests` | 13 passed | Real Chromium DOM with controlled browser storage: original numbers, one set of finding controls across views, derived progress, filters, dependency/member navigation, bound handoffs and clipboard fallback, portable HTML bytes, regrouping versus changed evidence, session fallback and import isolation, default/unavailable/empty modes, hostile group text, print and mobile layout. |
| `NativeResolutionTests.test_native_refresh` | Attempted; obstructed before page load | Chromium rejected the `file:` URL with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Native refresh, regeneration and actual download/reopening are not qualified by this run. No browser administration policy was disabled. |
| Python compilation and changed-code whitespace | Passed | Syntax/whitespace only, not model behavior. |
| Desktop and mobile rendering | Inspected | Fixture rendered through `set_content`, not native file-origin navigation. |
| Live Codex/Glaze/Metanoetic campaign evaluation | Unrun | No `codex`, `cas` or `gh` executable is present in this environment. Connector publication is not a campaign run. |

Observed implementation-test runtime: Python 3.13.5, Playwright 1.57.0, Chromium
144.0.7559.96. The production renderer remains standard-library Python and the
export remains a single offline HTML file with no network-dependent assets.

The DOM suite reconstructs pages using controlled storage maps and captures the
portable Blob's actual HTML bytes, then loads those bytes in a fresh page. This
is not a substitute for actual browser refresh/download/storage-origin behavior.
The normal test run reports 31 passes and one explicitly unselected native test;
the separately selected native test reports the actual navigation obstruction.

From the repository root, with Playwright and its browser already available:

```bash
uv run --no-project python -m unittest discover \
  -s codex/skills/elenctic/tests -p test_resolution.py -v
uv run --no-project --with playwright python -m unittest discover \
  -s codex/skills/elenctic/tests -p test_resolution_browser.py -v
```

Set `ELENCTIC_CHROMIUM` to an installed Chromium executable when not using
Playwright's managed browser. Qualify native file behavior in a capable environment:

```bash
ELENCTIC_NATIVE_BROWSER=1 \
PYTHONPATH=codex/skills/elenctic/tests \
uv run --no-project --with playwright python -m unittest \
  test_resolution_browser.NativeResolutionTests.test_native_refresh -v
```

No production server, new model dependency, native fork route, storage ledger or
review lane was introduced. Existing report/fork/thread qualifications retain
their original limitations; this record does not retroactively upgrade them.

## Skill-level behavioral cases (unrun)

Use a capable runtime with pinned PR evidence. Keep expected results with the
evaluator, not in the worker seed. Inspect actual helper reads/application, findings,
drafts, group associations, final artifact and tool effects; phrase presence alone
is not efficacy evidence. These cases add no production review gates.

| Case | Required behavior |
|---|---|
| Default invocation on another developer's PR and on the viewer's own PR | Same comment-oriented review. Authorship does not select resolution; this feature invokes neither helper and emits no groups. |
| Explicit `for resolution`, natural equivalent, and concurrency 10 | Same target/selection/review and concurrency policy. After reconciliation/falsification/discussion comparison and draft derivation, the coordinator applies actual installed Glaze then Metanoetic, unchanged, to the full evidence. Workers invoke neither and acquire no new authority. |
| Cross-file findings share a lifecycle guarantee; same-file findings have unrelated obligations | Synthesize justified shared units in the first case; separate or singleton units in the second. No file/topic-only grouping, forced rewrite, or one-comment-one-patch assumption. |
| Canonical #2/#5/#8 coexist with colliding worker-local #1 labels | Use the established coordinator IDs/numbers. R1 explicitly references #2/#5/#8 in terminal, original cards, group view and handoff; never renumber by array position. |
| A blocker has only an existing disputed discussion, plus a nonblocking concern | Include both findings without fabricating a new draft or promoting the concern. Every retained finding appears in one unit with its own satisfaction condition. |
| Synthesis exposes a verified defense or unreviewed path | Return the new evidence to ordinary adjudication/continuation; do not silently clear a blocker or manufacture completeness in grouping. Regroup only after the evidence-backed report changes. |
| Same-epoch resume, reordering, regrouping, withdrawn finding and a new finding | Retain workflow, canonical number history and individual checks/notes. New numbers do not replace withdrawn references. Group progress is derived; changed evidence reopens only its finding. |
| Missing helper, no retained findings, or incomplete selected scope | Missing helper is disclosed as unavailable synthesis with original findings intact. An empty finding set has empty groups without pointless helper invocation. Group completeness never implies review completeness or approval. |
| Explicit report-only/text-only, requested mode switch, or late PR movement | Honor effect limits, preserve review evidence and avoid new reviewer passes for an output-mode change. Recheck epoch/discussion before delivery. Never present stale findings as current-head evidence. |
| User copies `Address R1` handoff | Include its original member numbers, reviewed head/campaign, evidence, completion conditions and optionality. No editing, publication, thread mutation, approval or merging occurs from grouping/copying alone. |

The renderer's structural checks cannot establish that the chosen grouping is
semantically optimal or that a model obeyed the invocation order. Those claims
require observed live evaluation; none is asserted here.
