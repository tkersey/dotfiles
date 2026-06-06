---
name: forensic-elicitation
description: "Implicitly use for forensic elicitation from prior Codex/coding-agent sessions: mine $seq/$cas/session JSONL/memories/tool traces/commits/PRs/review receipts to produce provenance-preserving canonical maps. Trigger on requests to learn from past sessions, reconstruct what happened, extract improvements or lessons, audit closure, compare memories vs traces, or resolve contradictions."
---

# forensic-elicitation

## Purpose

Recover the best available knowledge from prior coding-agent work without flattening the evidence into anecdotes. Treat sessions, tool traces, commits, review records, plans, memories, and outcomes as evidence-bearing traces. Produce one canonical map of what is known, how it is known, what remains uncertain, and what query would most improve the model next.

## Activation cues

### Implicit invocation contract

This skill is intended for implicit selection. Do not wait for the user to name `$forensic-elicitation` when the request asks for historical/session evidence, prior-run truth reconstruction, improvement extraction, postmortem synthesis, or provenance-preserving lessons from coding-agent work.

Use this skill as the session-forensics wrapper around `$seq`, with `$cas` only for claims that depend on CAS review/session receipts. Prefer it over raw `seq` when the requested output is a synthesized evidence map, contradiction ledger, governing model, confidence ledger, or next-best-query recommendation.

Do not activate it for ordinary current-repo code search, bounded implementation, or a simple present-state question unless the user asks to compare current state against prior sessions, memories, review receipts, or tool traces.

Use this skill when the user asks to:

- inspect, mine, summarize, or learn from prior Codex/coding-agent sessions;
- use `$seq` for historical/session/artifact forensics;
- explain what actually happened in a session, PR closeout, review loop, subagent swarm, `$resolve`, `$review-adjudication`, `$fixed-point-driver`, or `$cas` run;
- extract lessons, reusable doctrine, failure patterns, improvement opportunities, evidence maps, or postmortems;
- compare memories/summaries against raw traces;
- diagnose contradictions between final answers, receipts, commits, reviews, and tool outputs.

Do not use this skill for ordinary current-repo code search unless the user explicitly asks for historical/session evidence.

## Core doctrine

Operate as:

- **FORENSIC**: every session event, command, review, commit, artifact, summary, and memory may be evidence.
- **PROVENANCE-PRESERVING**: every material claim carries a source path, line/event timestamp, artifact path, record id, commit tuple, or memory provenance.
- **STRATIFIED**: rank raw current artifacts and tool outputs above assistant summaries; rank session artifacts above memories; rank memories above intuition.
- **TRIANGULATING**: confirm important claims across independent surfaces when possible.
- **ABDUCTIVE**: infer the governing pattern that best explains the traces, then seek disconfirming evidence.
- **SATURATING**: continue querying until new searches no longer change the artifact set, chronology, contradictions, governing model, or next-best query.
- **CANONICALIZING**: produce a coherent event/claim map, not a pile of hits.

## Evidence strata

Use this authority ladder. Record the stratum for every claim.

| Stratum | Source class | Authority rule |
|---|---|---|
| S0 | Live current artifacts explicitly queried in the present run: `git`, `gh`, build/test output, current files, current CAS records | Highest authority for current-state claims; still bind to tuple/time. |
| S1 | Raw tool outputs inside JSONL sessions: command output, function_call_output, review JSON, GraphQL output, build logs, CAS records/event logs | Highest authority for prior-session event claims. |
| S2 | Session event metadata: session_meta, timestamps, cwd, source, git commit, parent/child thread ids, update_plan, goal updates, agent lifecycle | Authoritative for chronology and orchestration shape. |
| S3 | Final assistant answers and progress messages | Useful claims, but must be checked against S1/S2 for material facts. |
| S4 | Session-produced artifacts and persisted summaries referenced by traces | Strong if path/timestamp and content are available; otherwise cite as artifact reference only. |
| S5 | Memories, MEMORY.md entries, rollout summaries, remembered claims | Context and search beacons; never closure proof alone. |
| S6 | Inference/intuition | Allowed only when labeled as inference with the evidence that motivated it. |

## Claim taxonomy

Separate claims into these buckets before synthesizing:

- **Observed facts**: directly visible in raw traces, tool outputs, artifacts, or metadata.
- **Decisions**: agent/user choices such as route selection, fix choice, commit/push, close goal, spawn/stop lane.
- **Inferred patterns**: governing explanation that connects facts across traces.
- **Remembered summaries**: memory or final-summary claims not yet backed by raw trace.
- **Contradicted claims**: claims with material counterevidence.
- **Unsupported claims**: plausible statements lacking adequate provenance.
- **Open questions**: unresolved facts whose answer would change the model.

## Working objects

Maintain these internal ledgers while querying:

### Evidence row

```json
{
  "id": "E##",
  "claim_fragment": "short factual fragment",
  "source_ref": "path:line or artifact path",
  "timestamp": "ISO-8601 if available",
  "stratum": "S0-S6",
  "surface": "tool_output|message|metadata|memory|artifact|commit|cas_record",
  "tuple": {"repo": null, "branch": null, "base": null, "head": null, "pr": null},
  "verbatim_snippet": "short non-secret excerpt",
  "notes": "why this matters"
}
```

### Claim row

```json
{
  "claim_id": "C##",
  "claim": "material claim",
  "claim_type": "observed|decision|inferred|remembered|contradicted|unsupported|open_question",
  "supporting_evidence": ["E##"],
  "contrary_evidence": ["E##"],
  "confidence": "high|medium|low|blocked",
  "confidence_reason": "brief reason",
  "next_query": "query that would most improve or falsify this claim"
}
```

### Canonical event row

```json
{
  "event_id": "T##",
  "when": "ISO timestamp or ordered range",
  "actor": "root|subagent|tool|reviewer|user|memory",
  "session_id": "...",
  "source": "path:line",
  "tuple": {"base": "...", "head": "...", "pr": "..."},
  "event": "what happened",
  "evidence": ["E##"],
  "effect_on_model": "why the event changes the reconstruction"
}
```

## $seq-first query ladder

Prefer `$seq` for session/memory/artifact forensics. Use native `seq` surfaces before raw shell/JSON parsing.

1. **Scope and inventory**

   ```bash
   seq artifact-search --root ~/.codex/sessions \
     --contains-any "<topic terms, symbols, commits, PR numbers, skill names>" \
     --since <iso> --until <iso> \
     --surface auto --stats --limit 50 --format jsonl
   ```

   Also run a low-specificity recall query with only one or two durable terms. Exact keywords often miss the governing pattern.

2. **Find candidate sessions**

   ```bash
   seq find-session --root ~/.codex/sessions --contains "<distinct prompt/output term>" --format table
   seq workdir-report --root ~/.codex/sessions --workdir <repo-path> --mode sessions --format table
   ```

3. **Read the transcript without skill-block noise**

   ```bash
   seq session-prompts --session-id <id> --roles user,assistant \
     --strip-skill-blocks --limit 80 --format jsonl
   ```

4. **Interrogate tool traces**

   ```bash
   seq session-tooling --path <jsonl> --summary --group-by command --format table
   seq tool-search --root ~/.codex/sessions --session-id <id> \
     --contains-any "git,gh,zig,cas,jq,reviewVerdict,structuredFindingCount,Build Summary" \
     --mode rows --format jsonl
   seq tool-audit --root ~/.codex/sessions --workdir <repo-path> --group-by executable --format table
   ```

5. **Search contradiction beacons**

   Search for terms that indicate state changes, disagreements, or unreliable closure:

   ```bash
   seq artifact-search --root ~/.codex/sessions \
     --contains-any "clean,findings,patch is incorrect,No findings,blocked,failed,stale,inProgress,MissingReceiptStatus,tuple,baseSha,headSha,unresolved,current head,Goal marked complete" \
     --workdir <repo-path> --surface auto --stats --format jsonl
   ```

6. **Inspect orchestration and concurrency**

   ```bash
   seq orchestration-concurrency --root ~/.codex/sessions --path <jsonl> --format table
   seq workflow-audit --root ~/.codex/sessions --workflow fixed-point-driver --mode report --format markdown
   seq adjudication-audit --root ~/.codex/sessions --session-id <id> --format jsonl
   ```

7. **Mine memory, but demote it**

   ```bash
   seq memory-map --memory-root ~/.codex/memories --contains "<topic>" --format table
   seq memory-history --memory-root ~/.codex/memories --contains "<topic>" --format jsonl
   seq memory-provenance --memory-root ~/.codex/memories --contains "<memory phrase>" --format jsonl
   ```

   Use memory hits as search beacons or remembered summaries until corroborated by raw session/tool evidence.

8. **Use `next_action` from `artifact-search`**

   When `seq artifact-search` returns `next_action_kind` / `next_action`, prefer that command as the next drill-down unless it conflicts with the active hypothesis test.

## $cas receipt interrogation

When a claim depends on CAS review, never accept “CAS clean” without tuple binding.

Required checks:

- `baseSha` equals the PR/base tuple under discussion.
- `headSha` equals the exact commit under discussion.
- `targetFingerprint` binds the same base/head.
- `reviewResultAvailable` is true and `turnStatus` is terminal.
- `structuredFindingCount` and `rawFindingCount` agree, or the disagreement is explained.
- `reviewVerdict.clean` / `findingCount` agrees with the raw review text.
- persisted record path and event log path are captured.

Useful commands:

```bash
cas review_session receipt --path <record.json> --format json --summary
jq '{clean,structuredFindingCount,rawFindingCount,reviewVerdict,reviewResultAvailable,baseSha,headSha,turnStatus,failureCode,failureHint,recordPath,eventLogPath}' <record.json>
cas review_session lane status --lane-id <lane_id> --json
cas review_session lane stop --lane-id <lane_id> --json
```

If the receipt summarizer fails but the record/event log has terminal fields, classify this as a tooling gap, not automatically as review failure. Preserve both surfaces and explain which one has authority for which claim.

If a CAS output file is empty while a lane is still running, classify it as pending. Do not start duplicate reviews against the same tuple unless the previous lane is terminal, stale, or unrecoverable.

## Forensic elicitation workflow

### 1. Bind scope

Record the exact question, repo/workdir, time window, session ids, PR number, base/head commits, branch, and expected surfaces. If the user gives only a vague topic, infer a broad first query, then tighten from evidence.

### 2. Inventory sessions and surfaces

Build a session graph:

- root sessions;
- child/subagent review sessions;
- VS Code stubs or UI lifecycle-only files;
- parent_thread_id / child agent relationships;
- repeated `session_id` across multiple files;
- cwd/repo/branch/head for each file;
- final-answer presence vs in-progress traces.

Do not equate filename with session identity. Do not equate final answer with final truth.

### 3. Extract candidate claims

From each relevant surface, extract:

- problem/finding;
- owner boundary/invariant;
- decision/action taken;
- proof/checks run;
- review/CAS verdict;
- PR/GitHub state;
- commit/head transitions;
- goal state;
- stalled/in-progress lanes;
- explicit uncertainties.

### 4. Stratify and de-duplicate

Promote raw tool outputs and records over assistant summaries. Remove duplicates created by mirrored `event_msg agent_message` and `response_item message` rows. Keep both if one has metadata absent from the other.

### 5. Triangulate material claims

For each closure, repair, or “no issue” claim, seek at least two independent surfaces, e.g.:

- final answer + raw build output;
- CAS record + review subagent final;
- PR GraphQL output + Git status output;
- memory claim + raw rollout path;
- child-agent finding + root remediation commit/test.

If only one surface exists, label confidence accordingly.

### 6. Use contradictions as search beacons

When evidence conflicts, widen search around the conflict rather than smoothing it away. Search the same tuple, timestamp neighborhood, session id, commit hash, reviewThreadId, recordPath, finding title, and tool failure string.

Common beacons:

- clean review later contradicted by same-tuple findings;
- final “complete” followed by additional review/fix sessions;
- PR threads resolved but CAS/subagents still find issues;
- local proof blocked in a clean review;
- CAS summarizer failure but direct record has fields;
- in-progress lane mistaken for failed lane;
- head/base drift making a receipt stale.

### 7. Form abductive hypotheses

Name the governing model that best explains the traces. Good hypotheses are structural, not just descriptive:

- “The work was not a linear fix; it was a fixed-point review loop where each clean receipt was provisional until saturation across current tuple, local proof, CAS, GitHub threads, and challenger lanes.”
- “The recurring defect class is ownership-boundary drift between direct API paths and Runspace-mediated paths.”
- “The extraction failure came from searching visible messages only; the relevant evidence lived in tool outputs and saved review records.”

### 8. Falsify each hypothesis

For each hypothesis, ask:

- What evidence would make this false?
- Which stratum would be authoritative?
- Which `$seq` or `$cas` query would find it?
- Did we search for the strongest counterexample?

### 9. Saturation check

Stop only when additional searches stop changing:

- the relevant session set;
- the canonical chronology;
- the tuple/head map;
- the contradiction/tension set;
- the governing model;
- confidence levels;
- the next-best query.

If time or context runs short, emit a partial map and name the unsaturated surfaces explicitly.

## Output format

Return this canonical map unless the user requests a different format.

### 1. Evidence Map

Group by governing event or claim, not by search result. For each row include provenance.

| Claim/Event | Type | Evidence | Stratum | Status |
|---|---|---|---|---|
| ... | observed/decision/inferred/... | `path:line`, timestamp, artifact path | S# | confirmed/contradicted/open |

### 2. Source Stratification

List sources used, authority rank, freshness/closeness, and what each source can and cannot prove.

### 3. Contradictions / Tensions

Name each tension, cite both sides, explain why it matters, and state the next query or resolution.

### 4. Governing Model

One coherent explanation of the system behavior, workflow, or failure/improvement pattern.

### 5. Confidence Ledger

| Claim | Confidence | Why | What would lower/raise confidence |
|---|---|---|---|

### 6. Missing Evidence

List absent surfaces, stale/incomplete receipts, missing artifacts, unqueried memories, or unreachable logs.

### 7. Next Best Query

Give exactly one highest-yield query or command, with why it dominates alternatives.

### 8. Knowledge Bottom Line

Compact statement of what the user should believe or do next.

## Reporting rules

- Preserve source paths and line/event timestamps for every material claim.
- Label inference explicitly.
- Distinguish “review found no issue” from “issue impossible.”
- Distinguish “goal marked complete” from “all later evidence agrees.”
- Distinguish “tool failed to summarize” from “underlying evidence absent.”
- Treat in-progress lanes and empty output files as pending unless terminal evidence says otherwise.
- Never publish secrets from tool outputs; redact tokens, keys, local credentials, or auth details even if present in logs.
- Prefer canonical maps, timelines, and ledgers over raw hit dumps.
- When producing lessons or improvements, preserve the evidence chain that justifies each lesson.

## Micro-template for a finding-level extraction

```markdown
### Finding: <canonical name>

Observed facts:
- <fact> — `<path>:<line>`, <timestamp>, S#.

Decision/action:
- <action> — `<path>:<line>`, <timestamp>, S#.

Inference:
- <pattern>, inferred from E## + E##. Confidence: <level>.

Contradictions/tensions:
- <counterevidence> — `<path>:<line>`, <timestamp>, S#.

Reusable lesson:
- <lesson>.

Next query:
- `<command>` because <reason>.
```
