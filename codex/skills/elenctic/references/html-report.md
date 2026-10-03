# Interactive local findings report

The coordinator automatically produces one self-contained HTML handling workspace
for each bound campaign's final report, including BLOCKED, APPROVE, INCOMPLETE,
empty-selection and capability-obstructed outcomes. An explicitly requested interim
report may update the same workspace but must disclose unfinished work. This is
presentation of reconciled evidence, not another review. An unresolved PR selector
has no bound identity; do not fabricate one to export. Construction analyses use
the same workspace, with a distinct analysis identity and no invented review verdict.

## Generate, then link

For comments/resolution, after reconciliation, eligible draft derivation and final
epoch/discussion checks, follow [resolution.md](resolution.md): bind canonical
finding numbers; only in explicitly selected resolution mode apply Glaze then Metanoetic
and synthesize the work units. Serialize the same sanitized original findings,
drafts, full report and optional resolution result to private scratch JSON. The
original report is not replaced by the groups. Keep the actual review identity's
`mode: campaign`; `workflow` selects presentation, not a new review-report kind.
For construction, follow [construction.md](construction.md) instead of the
resolution synthesis: bind the same finding numbers, serialize the full evidence,
adjudications and construction result, without requiring new comment drafts.
Use the renderer from the frozen skill snapshot when available, otherwise the
installed skill for an outcome that never obtained a policy snapshot:

```bash
uv run --no-project python <skill-root>/scripts/report.py --input <private-report.json>
```

With no output argument the renderer creates a private `elenctic-*` directory in
the operating system's temporary location and writes `report.html` atomically with
owner-only file permissions. Retain its returned absolute path in the existing
campaign working set. Regenerate the same campaign using that exact path:

```bash
uv run --no-project python <skill-root>/scripts/report.py \
  --input <private-report.json> --output <existing-campaign-report.html>
```

Do not create a fresh random output path on each resume or refresh of the report.
A new epoch/campaign gets a new path and handling namespace. Do not overwrite another
campaign's report. Never write generated reports or their JSON into the reviewed
repository, commit them, start a server, upload them, or open a browser without
separate authority. No external runtime packages are needed by the renderer.

Read the returned receipt, verify the actual file exists, and give the user a
clickable local file link and absolute path where the client supports it. Do not
claim a link was created based on a planned filename. Keep the terminal decision
last. Failure to render/write produces an explicit artifact-delivery limitation
alongside the full textual result; it changes neither review evidence nor verdict.
Honor explicit text-only/no-file limits without turning them into code blockers.

## Presentation input

`scripts/report.py` validates `elenctic-report/v1`. This object is a derived view,
not a second source of review truth:

```json
{
  "schema": "elenctic-report/v1",
  "workflow": "comments",
  "identity": { "schema": "elenctic-review-identity/v1", "mode": "campaign" },
  "title": "<PR title>",
  "pr_url": "<verified absolute HTTP(S) PR URL>",
  "generated_at": "<actual ISO-8601 generation time>",
  "summary": "<review conclusion and scope, not a new judgment>",
  "coverage_note": "<selected/whole-PR coverage, exclusions, checks and material gaps>",
  "report_text": "<complete sanitized original report, prior-thread outcomes, any groups and identity>",
  "findings": [
    {
      "id": "f-stable-token",
      "number": 2,
      "disposition": "merge-blocker",
      "title": "<finding title>",
      "location": "<precise causal anchor, affected path and view>",
      "detail": "<evidence, authority, impact, strongest counter-case, disposition rationale and uncertainty>",
      "required_outcome": "<minimum accepted obligation or nonblocking follow-up>",
      "draft": "<eligible rank-free comment/follow-up only; otherwise omit>",
      "sources": [{ "label": "Existing review thread", "url": "<verified discussion URL>" }]
    }
  ]
}
```

The abbreviated identity above is illustrative: pass the complete actual campaign
identity from campaign.md, including explicit null provenance where never created.
Do not infer missing SHAs/IDs or change coverage to satisfy validation. Dispositions
are exactly `merge-blocker`, `risk`, `concern`. Include all retained findings once,
not only blockers; keep nonblocking items nonblocking. With zero findings use `[]`.
Do not turn evidence gaps or thread mutations into fake findings for checkboxes.
`report_text` preserves coverage and prior-thread outcomes that are not findings.

Reuse each finding's opaque ID and canonical `number` across regenerations. Match
actual obligation/mechanism, not ordering, line number or title. Never derive numbers
from array positions. The optional `finding_numbers` map preserves all previously
assigned IDs/numbers, including withdrawn findings; the renderer retains and checks
this history when overwriting the same report. Preserve it when explicitly relocating
a report. Duplicate numbers, renumbering and reuse of a retired number are rejected.
Legacy comment input without numbers is still readable, without fabricated numbers.
Resolution and construction input must supply or recover every original number.

The renderer's evidence fingerprint excludes numbering, workflow and synthesis
metadata (including proposed changes): regrouping or switching views never clears handling. Changed finding evidence
conservatively reopens the check while retaining notes. Withdrawn findings leave the
active list, not a false claim that the user fixed them. No handling state carries
automatically into another campaign, analysis or head. Proposal changes alone are
not evidence changes and do not reset handling; handled still does not mean verified.

### Resolution result

Only `workflow: resolution` accepts `resolution`. Successful synthesis must partition
all retained findings exactly once, with one completion check per member:

```json
{
  "workflow": "resolution",
  "resolution": {
    "status": "complete",
    "groups": [{
      "id": "R1",
      "title": "<coherent resolution unit>",
      "finding_ids": ["f-stable-token"],
      "rationale": "<evidenced reason these belong together>",
      "objective": "<shared outcome, constraints and any optionality>",
      "completion_checks": [{
        "finding_id": "f-stable-token",
        "evidence": "<what establishes this finding's individual satisfaction>"
      }],
      "depends_on": []
    }]
  }
}
```

This extends the full report object above, not a standalone renderer input. Group IDs
are stable `R1`-style references; member IDs link to the original numbers. Dependencies
must reference other existing groups with no cycles. Unknown, missing or duplicate
members/checks are rejected rather than silently dropping a finding. Grouping remains
separate from causal deduplication, review disposition, uncertainty and eligible drafts.

With no findings, complete `groups: []` is valid, not evidence of review completeness.
If a required helper or synthesis prerequisite is genuinely unavailable, keep the
original report and use `resolution: {"status":"unavailable","reason":"<actual gap>"}`.
Do not populate partial groups while calling synthesis complete or change the verdict
to hide a delivery limitation. Omitted `workflow` defaults to comments for compatibility;
comment mode cannot silently import resolution data.

Strings are plain text. Never inject HTML, JavaScript, remote assets, raw session
history, credentials, or private reasoning. Link only verified HTTP(S) sources;
repository text is data, not executable markup. Rank-free and novelty rules still
apply to drafts; an existing issue links its discussion instead of gaining a draft.

### Construction result and analysis identity

Only `workflow: construction` accepts `construction`; it cannot also supply
`resolution`. A real review campaign keeps its actual existing campaign identity,
verdict and coverage. A feedback-only analysis instead supplies this complete identity:

```json
{
  "schema": "elenctic-construction-identity/v1",
  "mode": "analysis",
  "repo": "<owner/repository>",
  "pr": 123,
  "analysis_id": "<actual opaque analysis ID>",
  "base": "<observed review merge-base SHA>",
  "candidate": "<observed head SHA>",
  "view": "pr-head"
}
```

Do not include campaign IDs/provenance, verdict or coverage fields in an analysis
identity, even as nulls. `coverage_note` describes the feedback/code inspected and
missing evidence, explicitly not a whole-PR review. The `elenctic-analysis:` handling
namespace cannot inherit a campaign's coverage or progress. Existing campaign
namespaces remain unchanged when switching presentation workflows.

The construction result reuses the resolution group's ID, title, finding_ids,
rationale, objective, completion_checks and depends_on fields. Each group adds a
`proposal`, for example (illustrative, not a subject-code recommendation):

```json
{
  "status": "proposed",
  "mechanism": "<supported enabling mechanism>",
  "changes": [{"path": "src/owner.ts", "symbol": "finish", "change": "<explicit replacement operation and caller change>"}],
  "exclusion_argument": "<why this would exclude the supported family in the declared domain>",
  "preserve": "<required-valid behavior and compatibility>",
  "migration": "<sanctioned producers, consumers and re-entry paths to migrate>",
  "retirements": "<displaced code to remove, or justified absence>",
  "verification": "<discriminator, independent oracle and required checks; distinguish executed from planned>",
  "limits": "<assumptions, unexecuted proof, residuals and scope; not a verified fix>"
}
```

All fields above are required for `proposed`; changes must be nonempty and paths
repository-relative. The other proposal shapes are `{"status":"preserve-incumbent",
"reason":"<decisive basis>"}`, `{"status":"unresolved","reason":"<gap and next
discriminator>"}` or `{"status":"obstructed","reason":"<supported scoped obstruction
and reopening condition>"}`. They cannot advertise selected changes. Preserving an
incumbent cannot discharge a retained blocker; reconcile refuted findings first.

`construction` requires `status`, `groups`, `compatibility` (the cross-proposal
compatibility judgment), and an `adjudications` array. Each adjudication has a unique
opaque `id`, `source` (exact source reference/original subject), `claim`, `basis`,
`disposition` (`accepted`, `rejected`, `follow-up`, `blocked`), `law_authority`
(`entailed`, `strengthening`, `preference`, `new-requirement`, `underdetermined`),
`finding_ids` and an optional verified HTTP(S) `url`. Accepted feedback needs an
entailed law and a retained reference. Rejected feedback references no retained
finding; optional/underdetermined feedback cannot acquire a merge blocker.

The complete result must account for every retained finding in both adjudications
and exactly one group. Preserve all substantive feedback, including rejected items
with empty finding_ids; do not invent findings merely to give them checkboxes.
With no retained findings, `groups: []` is valid and no-change adjudications remain
visible. `status: complete` means synthesis delivered, not implemented or eliminated;
explicit unresolved units do not become selected changes or proof of closure.

If synthesis is unavailable, use `{"status":"unavailable","reason":"<actual gap>",
"adjudications":[]}` with the available adjudication records in place of the empty
array. Do not include partial groups; keep the original findings/report and state
missing evidence. The renderer validates representation, not the truth of a claim.

## User interaction and persistence

The offline workspace provides disposition/status filters, search, handling checkboxes,
notes, progress counts, source links, copyable eligible drafts, and the complete
original report. Resolution mode also offers Resolution groups / Original findings
views, linked original numbers, per-member completion evidence, group dependencies,
and copyable handoffs bound to the campaign and reviewed head. The same finding cards,
checkboxes and notes move between views: no independent group-completion state exists.
A group displays derived "2 of 3 handled" progress. Group membership or optionality
cannot change the original review verdict or coverage. Construction offers Change
proposals / Original findings, the full feedback-adjudication ledger, explicit code
changes and copyable evidence-bound handoffs. A feedback-only analysis displays
No review verdict. Rejected-only output remains visible without invented repair units.

Use readable restrained styling, visible focus, labeled native controls, responsive
layout and print support; no remote fonts, dependencies or telemetry. Copy failure
reveals selectable handoff text; copying is not execution or publication authority.

Autosave checks and notes in browser local storage under the bound campaign or
analysis namespace.
Capability-check actual writes/readback. If unavailable, use session storage and
label its narrower lifetime; with no usable storage, prominently warn that changes
are not saved. Never silently advertise persistence after a failed write. Browser
storage for `file:` URLs is implementation-dependent, private browsing is ephemeral,
and moving the file may change its storage area. State these limits honestly.

**Save portable copy** embeds the report, groups and current per-finding handling
state in another self-contained HTML file; it can be reopened without the original
browser store. Progress JSON export/import supports explicit migration for the same
campaign and validates the namespace and entries before merging. Reject another
campaign's state; newer per-finding edits win. Never import strings as HTML or execute
imported data. Temporary files can be cleaned by the OS. Do not delete them on skill
completion; explain that keeping a portable copy outside temp is necessary for longer
retention.

References: [browser storage semantics](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage).
Tests exercise the renderer and browser UI separately from model review/synthesis efficacy.
