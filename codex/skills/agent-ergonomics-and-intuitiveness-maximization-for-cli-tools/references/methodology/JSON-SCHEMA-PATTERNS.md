# JSON-SCHEMA-PATTERNS — Designing capabilities + verb output schemas

JSON output is the canonical agent-facing surface. This file gives the schema design patterns that maximize parseability, evolvability, and contract stability.

---

## The Universal Envelope

Every `--json` output, regardless of verb, conforms to:

```jsonc
{
  "ok":           true,                    // boolean: did the operation succeed
  "tool_version": "0.4.1",                 // string: semver of the producing binary
  "data":         { /* verb-specific */ }, // object | array | scalar: the verb's payload
  "meta":         { /* see below */ },     // object: provenance + parseability metadata
  "warnings":     [],                      // array: non-fatal issues
  "commands":     [],                      // array: paste-ready follow-up commands (if applicable)
  "errors":       []                       // array: fatal issues (only if ok==false)
}
```

This envelope is the single most important schema decision. Use it consistently across every verb.

---

## The `meta` field

Provenance + parseability metadata. Fields:

```jsonc
"meta": {
  "request_id":           "req_abc123",         // unique per call (stable across retries)
  "ts_iso":               "2026-05-06T12:00:00Z", // honors SOURCE_DATE_EPOCH
  "data_hash":            "sha256:abc123",      // fingerprint of `data` (for change detection)
  "contract_version":     "1",                  // monotonic; breaks indicate breaking changes
  "elapsed_ms":           42,                   // wall-clock latency
  "search_mode":          "hybrid",             // for tools with multiple modes (cass, frankensearch)
  "fallback_tier":        null,                 // null or "lexical-only", "cache-only", etc.
  "fallback_reason":      null,                 // reason for degradation
  "phase_status": {                             // for two-phase / async mega-commands
    "phase_1": "computed_ms_3",
    "phase_2": {
      "pagerank":    "computed_ms_240",
      "betweenness": "timeout_ms_500"
    }
  }
}
```

Agents read `meta.search_mode` to know if they got semantic or lexical results. `meta.data_hash` lets them cache by content.

---

## Per-verb schema in `capabilities`

For each verb, declare the output schema in capabilities:

```jsonc
{
  "commands": {
    "list": {
      "description": "List items.",
      "mutates": false,
      "json": true,
      "stdin": null,
      "output_schema": {
        "type": "object",
        "properties": {
          "ok":      {"type": "boolean", "const": true},
          "data": {
            "type": "object",
            "properties": {
              "items": {
                "type": "array",
                "items": {"$ref": "#/definitions/Item"}
              },
              "total": {"type": "integer"}
            },
            "required": ["items", "total"]
          },
          "meta":     {"$ref": "#/definitions/Meta"},
          "warnings": {"type": "array"},
          "commands": {"type": "array"}
        },
        "required": ["ok", "data", "meta"]
      }
    }
  },
  "definitions": {
    "Item": {
      "type": "object",
      "properties": {
        "id":         {"type": "string"},
        "title":      {"type": "string"},
        "status":     {"type": "string", "enum": ["open", "closed", "blocked"]},
        "created_at": {"type": "string", "format": "date-time"}
      },
      "required": ["id", "title", "status"]
    },
    "Meta": {
      "type": "object",
      "properties": {
        "request_id":       {"type": "string"},
        "ts_iso":           {"type": "string", "format": "date-time"},
        "data_hash":        {"type": "string"},
        "contract_version": {"type": "string"},
        "elapsed_ms":       {"type": "integer"}
      }
    }
  }
}
```

Agents that consume the tool can validate output against this schema (cheap correctness check).

---

## Schema export: `<tool> schema --json`

A dedicated subcommand that returns just the schemas:

```bash
$ mytool schema --json
{
  "tool":       "mytool",
  "version":    "0.4.1",
  "schemas":    { /* per-verb output_schema */ },
  "envelope":   { /* universal envelope schema */ },
  "definitions": { /* shared types */ }
}
```

```bash
$ mytool schema --command=list --json
# returns just the list verb's output_schema
```

---

## Stable handles + content addressing

Every JSON record should have a stable, deterministic ID:

```jsonc
{
  "id": "X-001",           // stable across runs
  "_hash": "sha256:abc",   // content hash; deterministic from inputs
  "_etag": "v3"            // optional: revision number for optimistic concurrency
}
```

Agents use `_hash` to skip re-fetching unchanged records.

---

## Stream output (NDJSON)

For verbs that emit large or unbounded streams, use NDJSON (one JSON record per line):

```bash
$ mytool watch --json
{"ok":true,"data":{"event":"started","ts_iso":"2026-05-06T12:00:00Z"}}
{"ok":true,"data":{"event":"item_added","id":"X-001","ts_iso":"2026-05-06T12:00:01Z"}}
{"ok":true,"data":{"event":"complete","total":42,"ts_iso":"2026-05-06T12:00:42Z"}}
```

Document NDJSON in capabilities:

```jsonc
"watch": {
  "json": true,
  "output_format": "ndjson",
  "output_schema": { /* per-line schema */ },
  "stream_terminator": {"event": "complete"}
}
```

Agents reading NDJSON streams know to parse line-by-line and stop on the terminator event.

---

## Pagination schema

For verbs that return large result sets:

```jsonc
{
  "ok": true,
  "data": {
    "items":    [...],
    "total":    1547,
    "limit":    100,
    "cursor":   {"current": "...", "next": "...", "previous": null}
  },
  "meta": { ... }
}
```

Agents fetch the next page with:

```bash
$ mytool list --json --cursor=<next>
```

The cursor is opaque (the agent shouldn't parse it; it's a black-box token). The tool can encode whatever pagination state it wants.

---

## Sparse field selection

For verbs with rich records, allow agents to request only the fields they need:

```bash
$ mytool list --json --fields=id,status
{"ok":true,"data":{"items":[{"id":"X-001","status":"open"},{"id":"X-002","status":"closed"}]}}
```

Document `--fields` syntax in capabilities:

```jsonc
"list": {
  "supports_fields": true,
  "default_fields": ["id", "title", "status", "created_at"],
  "available_fields": ["id", "title", "status", "created_at", "updated_at", "tags", "labels", "_hash"]
}
```

Saves bandwidth + parse time for agents that only need a few fields.

---

## Versioning the schema

Use `contract_version` per `meta.contract_version`:

- Stage 0 (current): `contract_version: "1"`
- Schema change → `contract_version: "1.1"` (additive: new optional fields)
- Breaking change → `contract_version: "2"` (renames, removals, semantic shifts)

Agents reading `--json` output should:

1. Read `meta.contract_version`.
2. If major version diverges from what they expect, fall back to a compatibility branch OR error.

For heavy-stakes schema changes, ship `<tool> migrate-schema --from=1 --to=2 < input.json` to translate.

---

## Errors in JSON output

When the verb errors, `ok: false` AND populate `errors[]`:

```jsonc
{
  "ok":           false,
  "tool_version": "0.4.1",
  "data":         null,
  "meta":         {"request_id": "req_abc", "elapsed_ms": 12},
  "errors": [
    {
      "code":       "INVALID_INPUT",
      "message":    "field 'status' must be one of: open, closed, blocked",
      "path":       "$.data.items[0].status",
      "remediation": "use 'open' | 'closed' | 'blocked'; got 'pending'",
      "exit_code":  1
    }
  ]
}
```

Important: also write `errors[0].message` to **stderr** (in addition to JSON stdout). Agents reading stderr see the error; agents parsing stdout JSON also see it. Both audiences served.

For fatal errors that prevent JSON output entirely, fall back to stderr-only error message:

```bash
$ mytool list --json
error: cannot connect to backend at api.example.com:443
  is the service up?  mytool doctor --component=remote
  see: mytool capabilities --json | jq '.commands.list'
exit 4 (transient-failure; retry safe)
```

(Stdout is empty; exit code is 4.)

---

## Discriminated unions

When a value can be one of multiple shapes, use a `kind` discriminator:

```jsonc
{
  "data": {
    "events": [
      {"kind": "item_added",   "id": "X-001", "title": "..."},
      {"kind": "item_updated", "id": "X-001", "field": "status", "from": "open", "to": "closed"},
      {"kind": "item_deleted", "id": "X-002", "reason": "spam"}
    ]
  }
}
```

In the schema:

```jsonc
"events": {
  "type": "array",
  "items": {
    "oneOf": [
      {"$ref": "#/definitions/EventItemAdded"},
      {"$ref": "#/definitions/EventItemUpdated"},
      {"$ref": "#/definitions/EventItemDeleted"}
    ]
  }
}
```

Agents branch on `kind`. The discriminator pattern is far easier to handle than untagged unions.

---

## Time fields

- ISO 8601 in JSON: `"2026-05-06T12:00:00Z"` (always UTC, always with Z)
- Honor `SOURCE_DATE_EPOCH` for reproducibility
- For relative time references, use `_relative` field for human display, `_iso` for machine:

```jsonc
{
  "created_at_iso":      "2026-05-06T12:00:00Z",
  "created_at_relative": "5 minutes ago"  // optional; for human display only
}
```

---

## Numeric fields

- Integers as JSON numbers
- Currency as string with explicit unit: `"price": "9.99 USD"` or `"price": {"amount": "9.99", "currency": "USD"}`
- Avoid floats for money / counts (use integer cents)
- Never trust JSON's number precision for big integers (>2^53); use strings

---

## Boolean fields

- Use explicit booleans, not `0` / `1` / `"yes"` / `"no"`
- `null` if unknown / not yet determined; `false` if explicitly false
- For tri-state, use enum: `"acknowledged" | "rejected" | "pending"`

---

## Optional fields

Two conventions:

**Convention A** — omit field if absent:
```jsonc
{"items": [{"id": "X-001", "title": "..."}]}            // status omitted = default "open"
```

**Convention B** — include with `null`:
```jsonc
{"items": [{"id": "X-001", "title": "...", "status": null}]}
```

Pick one and use consistently. Convention B is easier for parsers; Convention A is easier on bandwidth. Document in capabilities which one applies.

---

## Schema-pin regression test

```bash
# audit/regression_tests/SCHEMA-001__capabilities_envelope_schema.test.sh
set -euo pipefail
TOOL="${TOOL_BIN}"

# capabilities itself has a stable schema
caps=$("$TOOL" capabilities --json)

# Validate envelope keys present
for k in version contract_version features commands exit_codes env_vars; do
  echo "$caps" | jq -e ".$k" > /dev/null || {
    echo "FAIL: capabilities.$k missing" >&2; exit 1; }
done

# Validate every verb has output_schema
echo "$caps" | jq -r '.commands | to_entries[] | .key' | while read -r v; do
  has_schema=$(echo "$caps" | jq ".commands.\"$v\".output_schema // null")
  if [ "$has_schema" = "null" ]; then
    echo "WARN: verb '$v' has no output_schema in capabilities" >&2
  fi
done

echo "OK"
```

---

## Schema design anti-patterns

- **Per-verb envelope inconsistency.** `list --json` returns `{items: [...]}`; `show --json` returns `{data: {...}}`. Standardize.
- **Free-form prose in JSON.** No `"explanation": "Here's what I think you should do..."` — that belongs in robot-docs guide.
- **Mixing structured + unstructured.** Either everything in `data` is structured, or it's a free-text field clearly labeled `_freetext`.
- **Pinning ANSI codes in JSON.** ANSI is for human terminals; if you want decorated text, use a separate `display` field with `text` and `style` properties.
- **Big integers as JSON numbers.** Use strings for IDs > 2^53 OR document the agent must parse with bignum-aware library.
- **Exposing internal IDs.** UUIDs and internal DB IDs are leaky. Use stable handles like `X-001` or content hashes.
- **Schemas without versioning.** Without `contract_version`, you can't make breaking changes safely.
- **Missing `ok` field.** Without `ok`, agents must parse `data` to know success — fragile.

---

## Tools to validate schema conformance

```bash
# JSON Schema validation via ajv-cli
mytool list --json | ajv validate -s <(mytool schema --command=list --json) -d /dev/stdin

# Python jsonschema
mytool list --json | python -c "import sys,json,jsonschema; jsonschema.validate(json.load(sys.stdin), json.load(open('schema.json')))"

# Rust schemars / typify can generate type definitions from the schema export
```

The schema export endpoint enables ecosystem tooling — agents, dashboards, integrations — to validate without copy-pasting schema definitions.

---

## Related

- `MEGA-COMMAND-DESIGN.md` — JSON shapes for the four canonical mega-commands
- `references/rubric/REGRESSION-TEST-PATTERNS.md` § Pattern 9 (schema-pin tests)
- `methodology/DEPRECATION-PATTERNS.md` § Pattern D-4 (changing JSON schema)
