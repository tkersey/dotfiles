# Explicit EPG Export

Activate only for `--format json`, `--format both`, an unambiguous complete EPG
request, or explicit EPG persistence/revision. Human-only planning needs no hidden
graph, Ledger bootstrap, utility scores, or machine-validation claim.

EPG-v1 is a derived encoding of the same execution specification. Keep its wire
version, existing fields, source modes, and custody operations. Read
execution-policy-graph.md for the legacy wire shape. New exports additionally embed
the complete primary block as `source.execution_specification`; bind its exact UTF-8
bytes with `source.source_digest`. The string is source, never executable code.

`plan/execution-policy-export` imports the unchanged legacy definition and tightens
new-export requirements without breaking historical store reads. It requires the
embedded source, action owners, effect-based repository boundaries/lock roots, proof
and rollback for mutation-bearing actions, and retirement coverage. This is a
new-export admission boundary, not a second artifact or execution runtime.

The small artifact-only `scripts/check-epg.py` additionally rejects cyclic action
prerequisites, foreign-seam factor use, and mismatched embedded-source digests. It
does not duplicate Ledger shape validation or interpret the policy at runtime.
Neither check proves source fidelity, conditional reachability, software correctness,
mutation authority, or completion. The final semantic reread must still walk each
live branch and verify that its required evidence is produced on that route.

## Emit and validate

Synthesize the complete primary specification first, even for `json`; embed it rather
than emitting extra prose in that view. Derive the graph without adding or removing
requirements. Preserve the architecture authorities, selected means, conditions,
proof routes, failure terminals, and source invalidators. Do not represent all
alternative implementations as simultaneously required. When every rule selects a
single action, a single neutral utility dimension satisfies the legacy encoding;
do not invent a quantitative estimate or claim it chose the architecture.

Load `$ledger` and complete `$ledger ensure` once before native validation. Stage
JSON using two-space indentation, no minified nested values, and one trailing newline.
Stage the exact primary block separately and use the actual staged paths below:

```bash
plan_root="$(realpath "${CODEX_HOME:-$HOME/.codex}/skills/plan")"
epg=/tmp/epg.json
specification=/tmp/primary-block.md
ledger definition check \
  --definition "$plan_root/definitions/ledger/execution-policy-export.json" --format json
ledger validate \
  --definition "$plan_root/definitions/ledger/execution-policy-export.json" \
  --input "policy=$epg" --format json
uv run "$plan_root/scripts/check-epg.py" "$epg" --specification "$specification"
```

Accept only the expected valid native definition/validation results with
`ledger-artifact-abi/v1`, `plan/execution-policy-export`, and the exact input and
definition digests, plus a successful graph check over those same staged bytes.
Missing tools or an invalid export blocks that requested export; never substitute a
homegrown Ledger implementation or claim native validation that did not occur.

`json` emits only those exact JSON bytes, without status prose or Markdown.
`both` emits the complete primary block and appends exactly that JSON in one fence;
the delimiters are not validation input. Export metadata and the structural claim
belong outside the primary block. State
`EPG structurally valid under <definition-id>@<definition-digest>.`
only after actual native validation. Never validate one serialization and emit another.

A structural repair changes encoding only. A graph/specification disagreement
returns to the affected semantic decision and regenerates the export. Do not let
validation choose architecture, expand authority, or supply missing user judgment.

Before persistence, use artifact-root.md and validate the exact new export first.
The existing document definition still owns its create/revise transaction and
readback; the stronger export check grants no custody or execution authority.

On export failure, report the exact blocker rather than emitting a fabricated EPG.
