# Aggregate presentation and synthesis

The aggregate belongs to Ergasterion. Preserve original reviewer identities and
dispositions; never project architecture findings into an Elenctic worker identity
or count rendering/handling as review credit. Native Actuating strategy retains
its own output. Standalone reviewer delegation retains that owner's output unless
an aggregate workflow was explicitly selected.

## Select evidence before synthesis

`for construction` uses the explicitly supplied established aggregate/campaign
when present; otherwise bind the unique open PR and analyze its complete relevant
feedback under Elenctic's
[construction evidence procedure](../../elenctic/references/construction.md#select-evidence-before-campaign-preflight).
Do not start Architectonic or an Elenctic campaign merely to obtain more findings.
A selector or selection flag alone supplies no fresh-review authority. Existing
architectural evidence may participate with original provenance and current
revalidation; do not invent a second source when none was supplied.

`review for construction` runs the explicitly selected assessment(s) first, under
proposal-only/no-GitHub-mutation authority, then synthesizes once. A strategy/workflow
switch on an established source does not fabricate new review coverage or confirmations.
A new actual assessment receives its own identity; feedback analysis never borrows it.

After [aggregation](aggregation.md), preserve canonical aggregate numbers and the
map to all original owner references. Reuse Elenctic's
[resolution identity and membership rules](../../elenctic/references/resolution.md):
each retained finding belongs to exactly one unit; each member retains its own
completion evidence; real dependencies are acyclic; optional findings stay optional.
These are presentation rules over the aggregate, not permission to relabel it Elenctic.

- **Comments:** deliver the aggregate, scope and eligible drafts; no grouping pass.
- **Resolution:** coordinator-only Glaze then Metanoetic over the full aggregate,
  followed by one lossless work-unit synthesis. Do not group source reports separately.
- **Construction:** coordinator-only Actuating `analyze` over the full evidence,
  using its selected source/counterexample/architecture guides with corpus writes
  forbidden. Reuse Elenctic's concrete proposal fields and cross-unit compatibility
  check; do not run resolution synthesis first. Proposed, preserve-incumbent,
  unresolved and obstructed remain distinct; proposals are not implemented fixes.

Resolution with no retained findings returns empty groups without invoking helpers.
Construction still accounts for substantive rejected/unknown feedback and supported
no-change judgments. Empty groups are not evidence of review approval.

On missing synthesis capability preserve all original evidence and declare synthesis
unavailable. Rejecting a complaint must not erase its source/adjudication; accepting
it does not accept the proposed fix. Return substantive no-change and unresolved
outcomes, not fictitious findings made merely to fill a group.

For non-PR Architectonic subjects, use its subject-bound assessment and, when requested,
textual groups/proposals with the same membership and authority discipline. Do not
invent PR numbers, merge status, Elenctic coverage or a PR-only HTML identity.

## Draft ownership

Follow each source owner's current draft rules after joint reconciliation.
Architectonic can supply verified nonblocking opportunity drafts; Elenctic's drafts
remain supported novel blockers/follow-ups under its discussion contract. A combined
inference can yield one new blocker draft only after its own full source-bound
falsification, discussion-novelty check and verified diff anchor. Keep its aggregate
attribution explicit. No duplicate draft for an already represented discussion.

Keep one eligible copy-ready draft per aggregate finding with its accountable
`draft_owner`. Preserve other original drafts in source evidence when material;
never publish them. Nonblocking architecture advice stays nonblocking. No numeric
priority labels, fabricated line anchors or permission to post/approve/merge.
Honor `no-drafts` and summary-only constraints. Missing novelty evidence withholds
a draft, not otherwise supported findings or evidence.

## One shared offline workspace

For a PR-bound aggregate, reuse the installed/frozen Elenctic
[sanitized report fields and renderer](../../elenctic/references/html-report.md).
The renderer also accepts **`ergasterion-report/v1`**, retaining the shared offline
UI, stable numbering, groups, construction proposals, safe text/links, private
atomic output and handling persistence. There is no separate report engine.

Change the top-level `schema` to `ergasterion-report/v1`. A review aggregate uses
`identity.schema: ergasterion-review-identity/v1`, `mode: campaign`, actual repo/PR,
review merge-base `base`, `base_tip`, `candidate`, `view: pr-head`, actual opaque
aggregate-round `campaign_id`, selected non-native `strategy`, and the ordinary
coverage/verdict fields. This is a derived aggregate identity, not an owner receipt.
Do not include Elenctic context/seed/policy fields at aggregate level, even null:
the real source output retains those. Include source descriptors in `assessments`:

```json
{
  "architectonic": {
    "source_ref": "<actual architectural output reference>",
    "repo": "<owner/name>", "pr": 123,
    "base": "<review merge base>", "base_tip": "<base tip>",
    "candidate": "<head>", "scope": "<examined obligations and scenarios>",
    "coverage": "complete"
  },
  "elenctic": {
    "source_ref": "<actual complete native campaign output reference>",
    "repo": "<owner/name>", "pr": 123,
    "base": "<same review merge base>", "base_tip": "<same base tip>",
    "candidate": "<same head>", "scope": "<actual selection and coverage>",
    "coverage": "complete", "whole_pr_coverage": "complete"
  }
}
```

Those illustrative values are not defaults or evidence. Missing/unrun sources are
absent; incomplete actual sources retain `coverage: partial`. All descriptors must
match the actual round subject. A complete combined scope requires both complete
assessments and Elenctic whole-PR coverage, plus the coordinator's reconciled
interactions. Architecture-only scope can be complete without claiming Elenctic
whole-PR coverage. Preserve separate source verdicts and full policy/seed/coverage
provenance in `report_text`; descriptors do not replace or certify them. Renderer
validation establishes representation consistency, not execution, coverage or credit.

Feedback-only construction uses `identity.schema:
ergasterion-construction-identity/v1`, `mode: analysis`, actual `analysis_id`,
repo/PR/base/base_tip/candidate/view/strategy and nonempty `evidence_refs` for the
inspected sources. It must not contain assessments, campaign provenance, coverage
or a verdict. No review was performed by merely reading feedback.

Every aggregate finding carries its original sources, separately from linked URLs:

```json
{
  "id": "f-stable-token", "number": 1,
  "origins": [
    {"owner": "architectonic", "reference": "<source finding reference>", "disposition": "opportunity"}
  ],
  "draft_owner": "architectonic"
}
```

Extend the ordinary finding object, not a standalone input. `origins` is nonempty;
owner is architectonic, elenctic or pr-feedback, each with a genuine source
reference and original disposition. Keep all origins through deduplication. State
source attribution in the visible detail as well. `draft_owner` is needed only
when a draft exists: an actual source owner, or ergasterion for an aggregate
blocker. Only an Architectonic-origin `concern` can carry a nonblocking draft.
Map opportunities to concern without hiding their original disposition; preserve
preserve/unresolved/rejected decisions and evidence gaps in the full report or
construction adjudications rather than inventing blockers.

Generate with the shared renderer, through its observed installed path:

```bash
uv run --no-project python <installed-elenctic>/scripts/report.py \
  --input <private-aggregate.json>
```

Reuse the actual returned path only for this same aggregate round/analysis.
Different round, head, base tip or strategy gets a separate handling namespace;
regrouping or switching presentation does not clear checks. Stable origin/evidence
changes conservatively reopen handling; notes and retired finding-number history
remain preserved. Keep the source reports and prior round evidence resolvable,
not merged into false current coverage. Browser checks never satisfy a fix or round.

Return the verified artifact path before the final practical conclusion. No-file,
text-only and explicit summary-only limits can suppress the artifact; renderer
failure is a named delivery limitation alongside the full textual aggregate.
Do not publish scratch JSON/HTML, raw private history, secrets or private reasoning.
After closeout give the real PR and head, actual credited count/strategy, remaining
optional work and limitations; a successful report write is not that closeout.
