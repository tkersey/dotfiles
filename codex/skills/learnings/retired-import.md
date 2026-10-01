# Retired Learnings import

This owner constructor recovers identifiable original records into canonical
Learnings without recapturing them. It requires Ledger 1.3.x or a compatible
later 1.x runtime. `$ledger` owns custody selection and migration orchestration;
this owner owns historical record semantics. No bulk memory admission occurs.

## Contract

`scripts/import_retired_learnings.py` accepts consecutive JSON objects, including
multiline and non-ASCII records. Version-0 `learning.import` events preserve the
original record object and carry source SHA-256, original byte span, record index,
and framing-control digest. The version-1 event and normal capture submission
remain strict. Historical descriptive identifiers, long path lists, and absent
context are not rewritten, truncated, or populated with invented values.

Before any append, the constructor parses every source, rejects duplicate keys
and source IDs, validates every packet through the owner definition, and compares
all source IDs with a native full-record projection. Equal copies import once;
conflicting original or current records block the entire preflight. Native
`import-record` uses an ID-derived retry key and the witnessed store revision.
Afterward every original and previously current record receives exact full-record
parity checking, followed by native doctor and source digest verification.

An absent store has no revision for compare-and-append. Its first append uses the
separate `import-initialize` operation only with explicit empty-initialization
and writer-quiescence authority. This is NOT a native assertion that the store
remains absent: the operator must actually stop competing writers. Every
subsequent append uses `import-record` with a witnessed revision. Do not use the
initialization operation to bypass a stale-revision failure.

## Invocation

Complete `$ledger ensure` bootstrap and obtain its managed selector first.
Inspection performs no custody writes:

```bash
uv run "$learnings_skill_root/scripts/import_retired_learnings.py" \
  --source "<original-retired-source>" \
  --store-root "<context.store_root>" --store-id "<context.store_id>"
```

For an authorized import, add `--apply`. For a genuinely absent store, also add
`--initialize-empty --confirm-no-writers`, only after establishing quiescence.
Multiple `--source` options preflight together. Never feed reconstructed capture
submissions in place of original records. Retain the complete JSON result as the
migration receipt. On failure after an append, stop and rerun this constructor
after resolving the reported blocker; native projection and retry identities
reconcile completed work. A saved count is not a restart offset.

## Exceptional framing

Malformed sources stop; no heuristic repair, concatenation, skipped row, or
fabricated record is allowed. An explicitly approved `--framing-controls` JSON
file may map an exact source SHA-256 to:

```json
{"source_sha256":"<64 lowercase hex digits>","spans":[
  {"start":123,"end":129,"kind":"missing-tags-quote"},
  {"start":900,"end":965,"kind":"anonymous-fragment"}
]}
```

Offsets above are illustrative, not repair instructions for a particular file.
The first control can insert only the missing opening quote in the exact bytes
`tags":`. The second retains an explicitly identified anonymous fragment between
records. It cannot remove a field from a parsed record or discard an identified
record. Original bytes never change; retained fragments remain base64-encoded
in the receipt as well as in the original and migration archive. Unknown damage
requires owner investigation, not broader repair permissions.

## Qualification and existing local recovery work

Run `uv run python -m unittest discover -s codex/skills/learnings/tests -p
 'test_retired_import.py' -v` (on one shell line). Set `LEDGER_BIN` to a released
native binary to run conformance as well as constructor tests. The focused CI
workflow verifies the Ledger 1.3.0 release checksum before executing native tests.
Mock tests alone do not qualify this protocol for production custody.

The October 1 Boundary report describes additional locally installed, uncommitted
recovery artifacts. Their exact source is not part of that report. This change
is independently implemented against published code, not a reproduction of that
unpublished patch. Reconcile overlapping local protocol/importer changes before
installation; never replace an existing recovered store or its definition
archives to make a newer protocol pass. Test its actual version-0 events and
archived closures before declaring compatibility with that local recovery.
