# Session-Corpus Mode

Use this reference only when `$elenctic` is explicitly invoked to aggregate
same-name sessions. The mode does not run new file reviews. It reconstructs a
bounded corpus of completed Elenctic reports, rebinds their blocker claims to one
current candidate, deduplicates them causally, and applies the ordinary blocker
falsification and final-decision standards.

## Governing model

```text
same-name session discovery
  + repository and candidate binding
  + provenance-preserving report extraction
  + causal deduplication
  + current-candidate blocker falsification
  = aggregate real blockers
```

The shared session name is a corpus-discovery key, never a trust key. Repetition
is not proof, omission is not refutation, and a historical report does not grant
review, publication, merge, or closure authority.

## Bind the aggregate subject

Before reading historical reports, establish:

- the current repository identity;
- the explicit PR, range, staged view, or established branch comparison;
- immutable base and candidate identities;
- the intended aggregate scope;
- the current Codex session ID.

For a PR, resolve the current base/head and relevant prospective-merge view using
the same rules as single-file mode. Recheck mutable refs before reporting.
Historical reports can nominate claims, but every retained blocker must be
established against this current bound candidate.

Require `CODEX_THREAD_ID` or another exact current-session identity supplied by
the environment. If the current session cannot be identified, return
**INCOMPLETE — Aggregate approval withheld** rather than risking
self-contamination.

## Load Seq as the passive adapter

Load `$seq` and follow its bootstrap and evidence discipline. Require Seq major
version 1 and `seq-observation-abi/v1`:

```bash
seq version
seq capabilities --format json
```

Seq owns physical session identity, paths, events, ordering, and provenance.
Elenctic owns the meaning of a completed review, candidate compatibility,
causal deduplication, blocker adjudication, and the final verdict. Never treat a
Seq match as a finding or approval.

Use native commands only for physical structure. Use the Elenctic-owned passive
definition for candidate report messages:

```bash
elenctic_seq_root="$(
  realpath "${CODEX_HOME:-$HOME/.codex}/skills/elenctic/definitions/seq"
)"
```

Do not replace a missing Seq field or operator with shell text search, `grep`,
`jq`, Python, a plugin, or direct session-file scanning. Report the obstruction.

## Discover the current same-name corpus

1. Use `seq session-detail` for the current session ID to recover the
   user-facing thread name, repository/cwd, root lineage, and session path.
   Confirm exact supported selectors with the installed Seq command when needed.
2. Require a nonempty persisted thread `name` or `thread_name`. Do not substitute
   the initial prompt, preview, generated title guess, branch, directory name,
   PR title, or current task text.
3. Use `seq sessions` over the current Codex session root and repository to
   enumerate the live session inventory at one recorded discovery cut.
4. Select non-archived root sessions whose persisted user-facing name exactly
   equals the current name. Match case-sensitively; do not use substring,
   token, fuzzy, or semantic similarity. Linked workers are evidence only when
   they belong to a selected root and contain a qualifying report.
5. Exclude the current session from the Seq scan. A completed single-file
   Elenctic report earlier in the current visible conversation may be included
   directly, bounded before the aggregation request.
6. Freeze the selected session IDs, paths, lineage, repository identity,
   discovery timestamp, and source content identities before extraction.

Here, **current sessions** means non-archived sessions present in the live
inventory at the discovery cut, not only sessions whose execution status is
currently `active`. A completed review may be idle and still belong to the
corpus. If Seq cannot expose persisted name, archive state, or root lineage,
state the missing field and withhold aggregate approval when it can affect the
corpus.

Record excluded near-matches separately. Do not silently broaden the corpus when
exact-name discovery returns zero or one session.

## Extract candidate review reports

For each frozen selected session or qualifying linked worker, run:

```bash
seq observe \
  --definition "$elenctic_seq_root/session-corpus.json" \
  --path "<exact-rollout-path>" \
  --param "exclude_session_id=$CODEX_THREAD_ID" \
  --projection reports \
  --format json
```

The definition returns bounded assistant messages that may contain a completed
Elenctic identity or verdict. It does not decide whether a message is genuine,
current, complete, or authoritative.

For each returned message:

1. Require exactly one unquoted `Review identity:` line containing valid
   one-line JSON with schema `elenctic-review-identity/v1`.
2. Require `mode: "single-file"`. Exclude prior session-corpus reports,
   summaries, quoted transcripts, injected skill text, prompts, examples, and
   messages that contain multiple competing identities.
3. Require a final `BLOCKED`, `APPROVE`, or `INCOMPLETE` decision whose value
   equals the identity's `verdict`.
4. Require matching repository identity and an identified target file.
5. Preserve the source session ID, root/worker lineage, source event ID, path,
   timestamp, turn, exact identity, and bounded report text.
6. Select the latest qualifying completed report per
   `(session, target, base, candidate, view)`; retain superseded reports only as
   provenance.
7. Classify reports bound to another candidate as stale. A stale approval
   contributes no current coverage. A stale blocker may nominate a hypothesis,
   but it must be re-established from current candidate evidence before it can
   survive.

A legacy report without the identity schema may be listed as excluded evidence,
but it cannot provide aggregate blocker or approval authority. Absence of a
qualifying report is a coverage fact, not evidence that the session was clean.

## Build the aggregate evidence set

Ingest source outcomes asymmetrically:

- source **real blockers** nominate candidate blocker claims;
- source **approvals** establish only their identified target coverage at their
  exact candidate;
- source **incomplete** decisions contribute named evidence gaps;
- source risks and concerns may supply counterevidence or context but are not
  promoted into blockers by aggregation.

Do not vote or count repetition as semantic weight:

```text
three repeated blockers != proof
three approvals omitting a blocker != refutation
one blocker plus four approvals != majority approval
```

Group candidate blockers by the earliest failed mandatory obligation and causal
mechanism, not by title, wording, source file, line number, or proposed comment.
One defect may have several witnesses and affected paths. Preserve all source
provenance and contradictory reports inside the grouped candidate.

Do not merge distinct obligations merely because one repair might address them.
Do not split one causal defect merely because several sessions observed
different downstream manifestations.

## Rebind and falsify aggregate blockers

For every deduplicated candidate blocker:

1. Inspect the current exact candidate and current diff at the relevant causal
   anchors and affected paths.
2. Determine whether the claim still exists and is introduced, newly exposed,
   or materially worsened by the current delta.
3. Recheck mandatory authority, supported reachability, existing defenses,
   companion changes, integration state, and the minimum pre-merge obligation.
4. Reconcile supporting and contradicting source reports without treating their
   count as a vote.
5. Apply the ordinary **Falsify provisional blockers** cut once.

A blocker is retained only when current evidence—not historical repetition—
establishes delta causality, mandatory authority, concrete basis, defense
survival, and merge necessity. Reclassify, reject, or mark incomplete exactly as
single-file mode requires.

Do not use corpus mode to discover unrelated new defects or to launch missing
single-file reviews. A newly noticed issue must be causally necessary to
adjudicate an imported blocker; otherwise omit it from this aggregation.

## Coverage and aggregate verdict

Before the final decision, report a compact corpus summary:

```text
Session corpus:
- exact thread name: <name>
- repository: <repo>
- discovery cut: <timestamp>
- matching root sessions: <count>
- qualifying current-candidate reports: <count>
- qualifying blocked / approved / incomplete reports: <counts>
- stale, contaminated, legacy, or otherwise excluded reports: <counts>
- distinct target files covered: <count>
- changed-file coverage: <covered>/<total-or-unknown>
- unresolved corpus limitations: <none-or-list>
```

Use the ordinary verdict priority with aggregate semantics:

- **BLOCKED — Real blockers:** at least one aggregate candidate survives
  current-candidate falsification. A known blocker takes precedence over other
  corpus gaps, which remain disclosed.
- **APPROVE — No real blockers across the aggregated reviewed scope.** Every
  selected eligible session has a completed or explicitly excluded disposition,
  every included approval is current-candidate bound, no material corpus gap
  prevents the decision, and no aggregate blocker survives.
- **INCOMPLETE — Aggregate approval withheld.** No aggregate blocker is
  established, but name discovery, corpus selection, candidate binding,
  qualifying report extraction, intended target coverage, or current integration
  evidence is incomplete.

Approval covers the aggregated reviewed scope. Claim whole-PR coverage only when
the qualifying target set is proven to cover the complete current change set and
all relevant integration evidence is complete.

## Aggregate blocker output

Use the ordinary numbered real-blocker format and proposed-comment style. Add
source provenance without duplicating the report:

```markdown
1. **<Blocker title>** — `<current path>:<line or range>`
   (<current diff side/view>; <aggregate finding>)

   **Supporting session evidence:** <session count and target paths; sanitized
   source identifiers>

   **Why this is a real blocker:** <current delta attachment, mandatory
   authority, and why the strongest current counter-case does not defeat it>

   **Proposed inline review comment:**
   > <Subject> should <minimum required outcome>, because <failure or unmet
   > obligation and its impact>.
```

Verify the inline location against the current diff. If no valid current inline
anchor exists, preserve the blocker, mark **inline location unavailable**, and
cite the current evidence location. Draft one comment per deduplicated blocker,
not one per source session.

## Corpus identity

Immediately before the final decision, emit:

```text
Review identity: {"schema":"elenctic-review-identity/v1","mode":"session-corpus","repo":"<owner/name-or-absolute-root>","thread_name":"<exact-name>","base":"<sha-or-content-id>","candidate":"<sha-or-content-id>","view":"<pr-head|prospective-merge|staged|unstaged|range>","verdict":"<BLOCKED|APPROVE|INCOMPLETE>"}
```

The identity binds the aggregate result only. It must not be admitted as a
single-file source report by a later corpus run.

## Privacy and limits

- Use sanitized session references and bounded excerpts.
- Never expose private reasoning or raw private message/tool payloads.
- Record exact denominators, exclusions, worker policy, and uncertainty.
- Same-name co-occurrence does not establish common intent or causal agreement.
- Session evidence may be stale, partial, contaminated, or mutually
  contradictory.
- Corpus mode remains read-only and never posts review comments, submits an
  approval, marks files viewed, edits code, or merges.
