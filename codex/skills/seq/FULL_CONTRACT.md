---
name: seq
description: "Reconstruct provenance-preserving observations from Codex and OpenCode execution/session evidence with Seq 1.x. Use for explicit `$seq`, session/tool/message forensics, skill activation and outcome audits, decision provenance, `$tune` evidence, `$retrace` source observations, watched-session deltas, worker attribution, or reproducible historical reports. Use native commands only for physical session structure; use the owning passive observation definition for every higher-level question."
metadata:
  version: "2.0.0"
---

# Seq

## Mission

Reconstruct:

```text
facts + provenance + corpus scope + contamination + limitations + uncertainty
```

Seq does not validate durable artifacts or grant action, repair, review,
publication, or closure authority.

## Source boundary

Seq reads only:

- Codex rollout JSONL and session/state metadata needed to locate or interpret it;
- supported OpenCode execution/session sources;
- explicit immutable input relations supplied by the caller.

Select OpenCode prompt history explicitly with
`--path ~/.local/state/opencode/prompt-history.jsonl`; its prompts, parts, and
tool lifecycle use the canonical physical relations, never a source-specific
command.

Seq does not scan memory roots, Ledger stores, artifact directories, or another
durable source implicitly. Compose durable facts explicitly:

```bash
# Load $ledger and complete $ledger ensure once before this composition.
ledger project \
  --definition <artifact-definition.json> \
  --projection <facts> \
  --repo <repo> \
  --payload-only \
  --format json >facts.json

seq observe \
  --definition <observation-definition.json> \
  --input facts=facts.json \
  --projection <projection> \
  --format json
```

## Bootstrap and capability boundary

Require Seq major version 1 and `seq-observation-abi/v1`:

```bash
seq version
seq capabilities --format json
```

Capabilities report only physical adapters, native operators, renderers, cache
format, and generic limits. A missing skill-specific flag is never a fallback
signal; load the owning definition and check its ABI/operators.

## Native surface

Use native commands only for physical session structure:

```text
seq definition check
seq definition describe
seq observe
seq explain
seq sessions
seq turns
seq session-detail
seq tool-lifecycle
seq session-graph
seq tail
seq find-session
seq datasets
seq dataset-schema
seq query
seq index
seq capabilities
seq version
```

If a higher-level question cannot be expressed, add a passive observation
definition to the semantic owner. Request a new native operator only when it is
domain-independent, explicitly bounded, and necessary for three unrelated
definitions or for preserving one live behavior without material performance
loss.

## Standard Seq definitions

Seq owns reusable physical analyses under:

```text
${CODEX_HOME:-$HOME/.codex}/skills/seq/definitions/seq/
```

Current definitions:

```text
message-search.json
session-summary.json
token-usage.json
tool-search.json
turn-metrics.json
turn-report.json
```

`tool-search.json` returns metadata through `rows`. Request `rows-raw` only
when raw arguments, inputs, commands, and outputs are necessary and safe.

`turn-metrics.json` reports raw sums over the selected physical `turns` rows.
Its `selected_turn_*_sum` fields are not lineage-owned token usage and must not
answer session-tree, worker-inclusive, billing-style, or corpus token totals.
Each token sum is partial unless its matching `selected_turn_*_count` equals
`turn_count`; a zero sum with a zero count means unobserved data, not zero use.
Those questions require an owning passive definition over lineage-owned token
deltas; if the installed Seq ABI does not expose that relation or operator,
report obstruction rather than summing `turns` or `sessions` token fields.

`token-usage.json` is the owning corpus-usage definition. It reconstructs
cumulative token transitions in source order from both `total_token_usage` and
`last_token_usage`. For modern rows, the transition is `(total - last) -> total`
and the counted delta is `last`; null-info events are observations without usage
and do not become zero-token transitions. The definition keeps the first
emission of a cumulative total within each session, excludes only exact
transitions replayed from a strict ancestor, retains sibling and independent-root
usage, and applies session and `since`/`until` selection after ownership.
Total-only legacy rows use an estimated snapshot fallback. Inconsistent
modern tuples make the result `invalid` and its token totals null. Its cached
percentage denominator is input tokens:
`cached_input_tokens / input_tokens * 100`.

```bash
seq_definition_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/seq/definitions/seq")"
seq observe \
  --definition "$seq_definition_root/token-usage.json" \
  --root "${CODEX_HOME:-$HOME/.codex}/sessions/2026/07" \
  --since 2026-07-01T00:00:00-07:00 \
  --until 2026-08-01T00:00:00-07:00 \
  --projection summary \
  --format json
```

Example:

```bash
seq_definition_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/seq/definitions/seq")"
seq observe \
  --definition "$seq_definition_root/message-search.json" \
  --path <rollout.jsonl> \
  --param "needle=<term>" \
  --projection rows \
  --format json
```

Domain observations live with their owners. For example, `$tune` owns skill
decision audits and `$retrace` owns decision discovery/source governance. Seq
compiles their passive data; it does not own their vocabulary or conclusions.

## Evidence discipline

For every report preserve:

```text
definition id and closure digest
Seq ABI and binary version
source adapter/schema version
session IDs and path/corpus digest
explicit since/until and timezone when applicable
worker inclusion
current-session exclusion
files opened and bytes read
physical passes and rows scanned/materialized
contamination
limitations and uncertainty
```

A fixed time window is not an immutable corpus snapshot.

Distinguish:

```text
presence
decision influence
downstream outcome
workflow governance
```

Likewise, keep mutation churn, final Git delta, and semantic surface separate.
Presence does not prove influence; outcome association does not prove causality;
an observation does not grant authority.

## Worker attribution

Include linked workers only when requested or when the relevant evidence occurs
there. Preserve root session, worker session, parent edge, lane/receipt ID,
declared skills, observation, and outcome. Never merge unlinked workers into the
root denominator.

## Privacy and contamination

Default to sanitized references and bounded excerpts. Detect injected skill
blocks, current audit prompts, generated reports, quoted transcripts, memory
summaries supplied as explicit inputs, and examples. Do not expose private
reasoning as report evidence.

## Hard rules

- Use the narrowest native physical command or owning passive definition.
- State denominators, exclusions, time bounds, and timezone.
- Preserve evidence provenance and definition identity.
- Use one fused scan when several requested projections share a source.
- Never treat raw `turns` or `sessions` token sums as lineage-owned corpus usage.
- Do not interpret a definition condition-by-condition in the hot loop.
- Do not validate SKDC, SDR, DCP, EPG, or another durable artifact with Seq;
  use its canonical Ledger definition.
- Do not read a Ledger store or memory root implicitly.
- Do not replace a missing operator with shell, `jq`, Python, a plugin, or a subprocess.
- Report unresolved units, identities, contamination, and evidence gaps.
