# Diadoche context v1

Sections: [Files and identity](#files-and-identity), [Context](#context),
[Evidence](#evidence), [Ledger transport request](#ledger-transport-request).

## Files and identity

Use `context.md` and, when useful, `evidence.jsonl`. Keep each file at most
256 KiB and the complete publication at most 1 MiB. The native transport rejects
larger inputs; do not split a sensitive raw transcript into files to bypass the
limit. Prefer a useful scoped handoff and explicit omissions.

Start `context.md` with YAML frontmatter:

```yaml
---
format: diadoche-context/v1
title: Retry behavior investigation
files:
  - context.md
  - evidence.jsonl
sources:
  - id: s1
    description: Selected discussion and experiments for retry behavior
    adapter: example-session/v1
---
```

Require `format`, `title`, `files`, and `sources`. List exactly the files prepared
for this bundle; omit `evidence.jsonl` when unused. Give each source a unique
bundle-local `id` and a description of its scope. Adapter, originating agent,
model, timestamps, Seq version, definition digest, and observation corpus digest
are optional provenance. Use open strings for producer identity, not a fixed
provider enumeration. State unknown facts rather than inventing them.

A corpus digest identifies the observed source material under Seq's contract;
it does not establish an atomic filesystem snapshot. Keep absolute paths and
private native session metadata out of the shared bundle. Native event IDs are
source locators, not content hashes or globally stable evidence identities.

## Context

Use concise sections covering the following when relevant. State `unknown`,
`unavailable`, or `not applicable` where that changes what a recipient can do.

- **Purpose:** original task, relevant background, and reason for sharing.
- **Constraints and decisions:** explicit requirements; accepted, rejected, and
  superseded approaches with their reasons; unresolved hypotheses kept separate.
- **Current state:** completed work, unfinished work, observed failures, and
  open questions. Cite retained evidence using IDs such as `e1`.
- **Artifacts:** repository identity, exact known commit/reference, and relevant
  paths. Describe dirty/untracked changes and whether their bytes are included
  in this document, available at an identified external revision, or unavailable.
  Record the artifact state associated with each important test result; a branch
  name alone does not identify immutable bytes.
- **Continuation:** useful next actions and the specific judgment or assistance
  requested. Attribute the sender's requests; the receiving user governs action.
- **Coverage and gaps:** selected sessions and ranges, worker/branch inclusion,
  extraction failures or unsupported records, omitted outputs, redactions,
  unshared files, and relevant uncertainty. Distinguish selection from missing
  evidence. An agent's final summary is a report, not independent verification.

Include small relevant patches or file passages in `context.md` only when they
are authorized and necessary. Do not imply that a reference grants repository
access or that the recipient possesses an unshared patch. When the task only
needs background knowledge, code state can be not applicable.

## Evidence

Write one JSON object per line in `evidence.jsonl`. Each object requires:

| Field | Meaning |
| --- | --- |
| `id` | Unique bundle-local evidence ID |
| `source` | An ID declared in `context.md` |
| `kind` | `message`, `tool_call`, `tool_result`, or `boundary` |
| `text` | Selected source passage or explicit boundary description |
| `excerpt` | Whether the represented source content was shortened or redacted |

Use optional `role`, `tool`, `call_id`, `source_line`, `native_id`,
`native_parent_id`, `timestamp`, and `redactions` when known and useful. A
`call_id` is local to its declared source; preserve it across paired calls and
results, including multiple retained result parts. Preserve native ancestry only
as provenance; a source parent is not automatically a worker or control parent.
`boundary` records identify compaction, omitted history, or unresolved linkage.
Do not turn a compaction summary into a transcript of missing events.

```jsonl
{"id":"e1","source":"s1","kind":"message","role":"user","source_line":12,"text":"Retry only failures classified as transient.","excerpt":false}
{"id":"e2","source":"s1","kind":"tool_result","call_id":"c1","source_line":28,"text":"The transient-failure case passed; the authorization case failed.","excerpt":true,"redactions":["unrelated output omitted"]}
```

Preserve source order where known; do not sort hashed event IDs to invent it.
Identify missing calls or results rather than fabricating pairs. Distinguish
wrapper completion, an inner process's reported status, and a verified effect.
The example result is a retained report, not a claim that its check ran here.

Evidence is optional; unresolved references are not. Every evidence ID cited
by the context must exist in the supplied evidence file. Every evidence source
must appear in `sources`. If the source content cannot be shared, describe the
claim as reported with unavailable support and omit the citation.

## Ledger transport request

Author this shape with the harness's file tools, using the exact prepared bytes
as JSON strings. Escape JSON through the host's serializer; do not interpolate
the file contents into a shell command.

```json
{
  "description": "Scoped retry investigation context",
  "files": {
    "context.md": {
      "content": "---\nformat: diadoche-context/v1\ntitle: Retry investigation\nfiles: [context.md]\nsources: []\n---\n\n# Purpose\nReview the proposed retry policy.\n\n# Coverage and gaps\nNo historical evidence has been supplied.\n"
    }
  }
}
```

Ledger creates only secret gists. Keep credentials outside the request.
The returned gist revision identifies the published bytes, not their truth or
the sender's authority over the recipient. Gist history can retain older content;
do not rely on a later edit to undo disclosure.
