# DSL-AND-SDK-AUDIT — Auditing tools with embedded DSLs and library/SDK surfaces

Some tools ship more than just a CLI:
- An **embedded DSL** that users program in (jq's filter language, awk's program language, kubectl's JSONPath, terraform's HCL)
- A **library/SDK** for programmatic use (cargo as a Rust crate, kubectl-sdk, aws-sdk, Stripe SDK)

Each of these is an agent-facing surface. This file extends the methodology.

---

## Why DSLs and SDKs matter

For an agent:

- **DSL** is a sub-language the agent must learn/generate. If it's poorly documented, agents can't use the tool's full power. (jq filters are hard for naive agents.)
- **SDK** is a library API the agent must call. If it's not aligned with the CLI's conventions, agents writing wrappers get confused.

Tools that diverge between CLI / SDK / DSL fail composability for agents who use any 2 of the 3.

---

## Auditing the embedded DSL

### Phase 1 inventory adjustments

For tools with DSLs, inventory:

- **DSL syntax categories**: literals, expressions, functions, operators, comments
- **Built-in functions / operators**: each is a surface
- **Error categories**: parse errors, runtime errors, type errors
- **Optimization patterns**: short-circuits, lazy evaluation, etc.

```jsonc
{
  "surface_id": "dsl_function__jq__map",
  "kind": "dsl_function",
  "name": "map",
  "description": "Apply a filter to each element of input array",
  "documented_in": "jq manual / man page",
  "is_dsl_surface": true
}
```

### Phase 2 scoring adjustments

For DSL surfaces, the dims translate as:

| Dim | DSL meaning |
|-----|-------------|
| 1 intuitiveness | Does the DSL syntax match agent expectations from similar DSLs (jq vs jsonpath)? |
| 2 ergonomics | Min keystrokes to express common operations? |
| 3 ease_of_use | Are functions discoverable from `<tool> --help` or `<tool> functions`? |
| 4 parseability | DSL programs themselves parseable? Errors include line:col? |
| 5 error_pedagogy | Parse error messages name the expected token? |
| 6 intent_inference | DSL handles common typos / misorderings? |
| 7 safety | Side-effecting DSL operators gated? |
| 8 determinism | Same DSL program → same result? |
| 9 self_documentation | Tool exposes function catalog as JSON? |
| 10 composability | DSL output composes into other DSL programs? |
| 11 regression_resistance | Tests pin DSL semantics across versions? |

### DSL recommendation patterns

Common recs for DSL-shipping tools:

| Rec | Description |
|-----|-------------|
| DSL-1 | `<tool> functions --json` exposes built-in catalog with signatures |
| DSL-2 | DSL parse errors include `file:line:col – message + suggestion` |
| DSL-3 | DSL supports `<tool> --validate-program=<file>` for pre-flight checking |
| DSL-4 | DSL has a stable contract version (different from CLI's contract_version) |
| DSL-5 | DSL fragments are parseable in isolation (for embedding in agent-generated programs) |

### Worked example: jq

`jq`'s DSL is excellent on most dims. Below-bar:

- No `jq functions --json` (would expose `keys`, `values`, `length`, `map`, etc. with signatures)
- Parse errors don't always include col-pos
- DSL contract_version not exposed

Phase 4 recs for jq's DSL: `jq functions --json`, structured parse errors, contract_version exposure.

### Worked example: kubectl JSONPath

`kubectl -o jsonpath='{.items[*].metadata.name}'` uses a JSONPath dialect specific to kubectl. Concerns:

- JSONPath dialect differs from spec (kubectl is custom)
- No `kubectl jsonpath functions` to introspect
- Errors are sometimes opaque

Recs: dialect documentation, function introspection, structured errors.

---

## Auditing the SDK / library surface

### Phase 1 inventory adjustments

For tools that ship a library:

- **Public types / structs / classes**: each is a surface
- **Public methods / functions**: each is a surface
- **Configuration types**: e.g. `ClientConfig`, `Options`
- **Error types**: each variant is a surface
- **Constants / enums**: each is a surface

```jsonc
{
  "surface_id": "sdk_method__github__client_create_issue",
  "kind": "sdk_method",
  "language": "rust",
  "module": "github::client::Client",
  "name": "create_issue",
  "signature": "fn create_issue(&self, repo: &str, title: &str, body: Option<&str>) -> Result<Issue>",
  "is_sdk_surface": true
}
```

### Phase 2 scoring adjustments

For SDK surfaces:

| Dim | SDK meaning |
|-----|-------------|
| 1 intuitiveness | Method names match expectations? Overloading consistent? |
| 2 ergonomics | Common operations are 1-liner; not 5-step builder ceremony? |
| 3 ease_of_use | Doc-comments on every public item? Examples in docstrings? |
| 4 parseability | Return types are structured (not strings to parse)? |
| 5 error_pedagogy | Error variants are typed (not string)? Messages teach? |
| 6 intent_inference | Method aliases for common alternatives? |
| 7 safety | Type system gates dangerous ops (typestate, builder pattern)? |
| 8 determinism | Idempotency keys for mutations? |
| 9 self_documentation | Auto-generated docs (rustdoc / godoc) complete? |
| 10 composability | SDK results compose with std types (iterators, futures, streams)? |
| 11 regression_resistance | Cross-version tests; semver discipline? |

### SDK recommendation patterns

| Rec | Description |
|-----|-------------|
| SDK-1 | Doc-comments on every public item (rustdoc/godoc) |
| SDK-2 | Examples in doc-comments (executable as doctests) |
| SDK-3 | Builder pattern for complex configurations |
| SDK-4 | Typed error variants (not opaque strings) |
| SDK-5 | Async-first APIs in async languages (Rust + Go + TS) |
| SDK-6 | Idempotency-key support for mutating methods |
| SDK-7 | SDK and CLI share canonical examples in docs |
| SDK-8 | SDK contract_version aligned with CLI's |

### Worked example: cargo (as SDK)

Cargo can be used as a library (`cargo` crate) by other Rust tools. Concerns:

- The crate's API is partly internal-only; not all CLI verbs are exposed as library functions
- Docstrings vary (some methods have rich examples; others have one-liners)
- Error types are opaque in places

Recs: complete docstrings, expose more verbs as library functions, typed errors.

### Worked example: aws-sdk-rust

The aws-sdk-rust shows off modern SDK design:
- Builder pattern (`Client::builder().region(...).build()`)
- Async-first
- Typed errors per service
- Strong rustdoc

Audit would find: SDK-1, SDK-2, SDK-3, SDK-4 mostly satisfied. Below-bar: cross-service consistency (each service's client has slightly different patterns).

---

## CLI-DSL-SDK alignment audit

For tools that ship all three surfaces (cargo, kubectl, terraform-as-library):

Add a meta-dimension `cross_surface_alignment` to the audit:

```
0:    Each surface invents its own conventions; no cross-references
250:  Some shared concepts; documentation per-surface separate
500:  CLI uses SDK internally; DSL has separate-but-coherent docs
750:  All of 500 PLUS: capabilities exposes which surface is canonical for which use case;
      cross-surface examples in docs
1000: All of 750 PLUS: schema-pin tests across surfaces; surface drift detected at PR time
```

This is the **trinity audit**. Tools that ship CLI + SDK + DSL should aim for cross-surface alignment.

---

## Auditing the SDK's docstrings

For Rust SDKs:

```bash
# Extract every public item
cargo doc --no-deps --document-private-items --json > docs.json

# Count public items without doc-comments
no_docs=$(jq '[.[] | select(.docs == null)] | length' docs.json)
```

For Python SDKs:

```bash
python -c "
import inspect
import importlib
mod = importlib.import_module('mytool')
no_docs = 0
for name, obj in inspect.getmembers(mod):
    if not name.startswith('_') and inspect.getdoc(obj) is None:
        no_docs += 1
print(no_docs)
"
```

Each undocumented public item is a finding.

---

## Auditing examples / doctests

The SDK should ship examples that:

1. Compile (or run) — auto-tested via doctests / `cargo test --doc`
2. Cover the canonical agent use cases
3. Mirror the CLI's canonical-task list

If `mytool list` is a canonical CLI task, the SDK should have:

```rust
//! # Example: list items
//!
//! ```
//! use mytool::Client;
//! # async fn doc() -> Result<(), Box<dyn std::error::Error>> {
//! let client = Client::new();
//! let items = client.list_items().await?;
//! for item in items { println!("{}", item.id); }
//! # Ok(())
//! # }
//! ```
```

---

## DSL parser-error pedagogy

DSL errors are notoriously bad. Anchors for the rubric:

```
0:    "syntax error" — no location, no suggestion
250:  "parse error at line 3" — location only
500:  "parse error at line 3, col 12: expected ',' got '='" — col + expected
750:  "parse error at line 3, col 12: expected ',' got '='. Did you mean: ..." — + suggestion
1000: All of 750 PLUS: incremental parse with squiggly underlines pointing to the error in the
      source; relevant grammar rule cited
```

jq, awk, and most DSL-shipping tools score around 250–500. Phase 4 recs typically target 750.

---

## SDK + CLI + DSK testing harness

For tools that ship all three:

```bash
# Per-surface tests
cargo test --lib                  # SDK tests
cargo test --tests --bin <bin>    # CLI tests
audit/regression_tests/dsl/*.test.sh  # DSL tests

# Cross-surface alignment tests
audit/regression_tests/parity/*.test.sh  # SDK-CLI parity
audit/regression_tests/dsl-cli-parity/*.test.sh  # DSL-CLI parity
```

Each test pins the contract for its surface AND for cross-surface alignment.

---

## When NOT to audit DSL/SDK

- The tool is a thin wrapper (no real DSL or SDK)
- The DSL is a one-off configuration syntax (e.g. systemd unit files; not really a DSL)
- The SDK is internal-only (not exposed as a public crate)

In these cases, the CLI surface is the only audit-worthy surface.

---

## Cross-references

- `methodology/MULTI-TOOL-FAMILY-AUDIT.md` — orthogonal axis (multiple binaries vs single binary with multiple surfaces)
- `methodology/MCP-SERVER-AUDIT.md` — for MCP-based programmatic surfaces
- `methodology/CONFIG-AS-CODE-PATTERNS.md` — overlaps with DSL for config-language tools
- `references/methodology/CLI-ARCHETYPES.md` § Multi-binary toolkit (related)
