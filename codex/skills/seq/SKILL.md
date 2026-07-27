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

Seq does not scan memory roots, Ledger stores, artifact directories, or another
durable source implicitly. Compose durable facts explicitly:

```bash
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
tool-search.json
turn-metrics.json
turn-report.json
```

Example:

```bash
seq observe \
  --definition "${CODEX_HOME:-$HOME/.codex}/skills/seq/definitions/seq/message-search.json" \
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
- Do not interpret a definition condition-by-condition in the hot loop.
- Do not validate SKDC, SDR, DCP, EPG, or another durable artifact with Seq;
  use its canonical Ledger definition.
- Do not read a Ledger store or memory root implicitly.
- Do not replace a missing operator with shell, `jq`, Python, a plugin, or a subprocess.
- Report unresolved units, identities, contamination, and evidence gaps.
