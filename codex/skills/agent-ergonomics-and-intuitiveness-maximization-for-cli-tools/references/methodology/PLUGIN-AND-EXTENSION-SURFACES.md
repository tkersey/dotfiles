# PLUGIN-AND-EXTENSION-SURFACES — Auditing tools that load plugins

Many CLIs are extensible via plugins (cargo `cargo-X`, kubectl `kubectl-plugin`, npm `npm-X`, helm plugins, gh extensions). When a tool loads plugins, those plugins are agent-facing surfaces too. The tool inherits responsibility for them.

This file extends the methodology for plugin-aware audits.

---

## Why plugin surfaces matter

For an agent, calling `cargo audit` is identical to calling `cargo build` — both look like cargo subcommands. But:

- `cargo build` is a built-in (Rust + clap defines it)
- `cargo audit` is a plugin (a separate binary `cargo-audit` that cargo finds via PATH)

If `cargo-audit`'s ergonomics differ from cargo's (different exit codes, different `--json` shape, different verb naming), the agent gets confused. Plugin surfaces should align with the host's conventions.

The **host** has a duty to either:
1. Enforce plugin alignment (verify each plugin meets a contract), OR
2. Document the divergences (so agents can branch)

Most tools do neither today. The audit catches the gap.

---

## Plugin discovery

### How plugins are discovered (by archetype)

| Tool | Plugin discovery |
|------|------------------|
| cargo | `cargo-X` binaries on PATH |
| kubectl | `kubectl-X` binaries on PATH |
| gh | `gh extension install <repo>` (managed list) |
| npm | local `node_modules/.bin/npm-X` (rare today) |
| helm | `helm plugin install` (managed list, similar to gh) |
| git | `git-X` binaries on PATH |

### Plugin enumeration verb

Every plugin-aware tool should expose:

```bash
$ <host> plugin list --json
{
  "plugins": [
    {"name": "audit",   "binary": "/usr/local/bin/cargo-audit",   "version": "0.18.3"},
    {"name": "deny",    "binary": "/usr/local/bin/cargo-deny",    "version": "0.14.0"},
    {"name": "machete", "binary": "/usr/local/bin/cargo-machete", "version": "0.6.2"}
  ]
}
```

This is the agent-introspection equivalent of `<host> capabilities --json` for plugins.

---

## Inventorying plugin surfaces in Phase 1

Phase 1 must enumerate plugin surfaces too. The inventorist:

1. Calls `<host> plugin list --json` (or equivalent enumeration)
2. For each plugin, treats it as a **subtree** of the host
3. Walks the plugin's surfaces using the same methodology
4. Marks each surface with `is_plugin: true` and `plugin_name: "<name>"`

```jsonc
{
  "surface_id": "verb__cargo_audit",
  "subtree": "audit",
  "kind": "verb",
  "name": "audit",
  "is_plugin": true,
  "plugin_name": "cargo-audit",
  "plugin_version": "0.18.3",
  "host_tool": "cargo"
}
```

---

## The plugin alignment dimension

For plugin-aware audits, add a **meta-dimension** when scoring the host:

> **plugin_alignment**: How consistent are plugin surfaces with the host's conventions?

Anchors:

- 0: Each plugin invents its own conventions (different exit codes, JSON shapes, error formats)
- 250: Most plugins follow basic conventions but exit codes drift
- 500: Most plugins follow conventions; some divergences documented
- 750: All plugins follow conventions; host validates plugins on install
- 1000: Host enforces a plugin contract (capabilities-pin); divergent plugins fail to load

This is similar to **cross-cut consistency** in MULTI-TOOL-FAMILY-AUDIT.md but specific to plugin/extension architectures.

---

## Plugin contract design

A plugin contract is a manifest the plugin advertises:

```jsonc
// Hypothetical: cargo-audit/cargo-plugin.json
{
  "host":             "cargo",
  "plugin_name":      "audit",
  "version":          "0.18.3",
  "host_min_version": "1.65",
  "exit_codes":       {"0": "no-vulns", "1": "user-input-error", "3": "vulns-found"},
  "supports": {
    "json_output":      true,
    "robot_meta":       false,
    "deterministic":    true
  },
  "envelope": "universal" | "custom" | "host-aligned"
}
```

The host loads plugins, reads each manifest, and:
- Lists them via `<host> plugin list --json`
- Routes invocations
- Surfaces incompatibilities (e.g. "plugin foo needs cargo >= 1.70; you have 1.65")

This is aspirational — most plugin systems today don't enforce manifests. But the audit can flag "plugin lacks manifest" as a finding.

---

## Plugin parity audit

Like MCP-CLI parity (in MCP-SERVER-AUDIT.md), plugin parity asks:

- Does the plugin support the host's conventions?
  - `--json` output?
  - Universal envelope?
  - Host's exit-code dictionary?
  - Plugin-version compatibility?

Run via:

```bash
$ <host> plugin verify --json
[
  {"plugin": "audit",   "json_output": true,  "envelope": "universal", "exit_codes": "host-aligned", "warnings": []},
  {"plugin": "deny",    "json_output": true,  "envelope": "custom",    "exit_codes": "host-aligned", "warnings": ["envelope diverges from host"]},
  {"plugin": "machete", "json_output": false, "envelope": "n/a",       "exit_codes": "ad-hoc",       "warnings": ["no --json", "exit codes don't follow host dictionary"]}
]
```

Findings flow to Phase 4 as recs.

---

## Plugin recommendations (common)

After auditing a plugin family, common recs:

| Rec class | Description |
|-----------|-------------|
| **Enforce envelope** | All plugins emit `{ok, data, meta, warnings, commands}` |
| **Align exit codes** | Plugins use the host's exit-code dictionary |
| **Add capabilities** | Plugins expose `<plugin> capabilities --json` accessible via `<host> <plugin> capabilities --json` |
| **Plugin manifest** | Plugins advertise what they support (host can verify) |
| **Cross-plugin discovery** | `<host> --help` mentions plugins as a list |

---

## Per-host plugin-audit sketches

### cargo

- `cargo --list` shows plugins; not JSON-exportable today
- Each `cargo-X` is independent; no contract enforcement
- The MULTI-TOOL-FAMILY-AUDIT.md treats this as a family

**Top recs:** `cargo plugin list --json`, manifest contract for plugins, alignment of `cargo-audit` + `cargo-deny` + `cargo-machete` envelopes.

### kubectl

- `kubectl plugin list` shows plugins; partial discovery
- Each `kubectl-X` plugin can have its own conventions
- Plugins often use `-o json` consistent with kubectl, but not always

**Top recs:** kubectl plugin contract; verify plugins use `-o json` and kubectl's exit codes.

### gh

- `gh extension list` shows extensions; managed install
- Extensions can use any output format
- gh emits warnings if extension is incompatible with current gh version (good)

**Top recs:** standardize extension output format; add `gh extension verify`.

### git

- `git --list-cmds=others` shows external `git-X` commands
- Almost no contract; each plugin invents conventions
- Highest plugin-divergence in the ecosystem

**Top recs:** start a plugin contract conversation in the git ecosystem (slow; multi-year).

---

## Plugins as a security surface

Plugins also affect safety dimension:

- Each plugin runs with the user's full privileges
- A malicious plugin can exfiltrate / mutate / brick state
- Plugin discovery via PATH means any binary named `<host>-X` is loaded

The audit should flag:
- "Host loads plugins from PATH without verification" — security warning
- "Host doesn't track plugin signatures" — supply-chain warning
- "Host doesn't allow disabling plugin discovery" — flexibility warning

These don't kill the audit but should be in `audit/recommendations.jsonl` as P2 / P3 security recs.

---

## Plugin-friendly capabilities schema

Extend `capabilities --json` to include plugin info:

```jsonc
{
  "version":          "1.65.0",
  "contract_version": "1",
  "supports_plugins": true,
  "plugin_discovery": {
    "method":    "PATH",
    "prefix":    "cargo-",
    "list_uri":  "cargo plugin list --json"
  },
  "plugins": [
    {"name": "audit",   "version": "0.18.3", "envelope": "universal"},
    {"name": "deny",    "version": "0.14.0", "envelope": "host-aligned"}
  ]
}
```

---

## Plugin self-application

Plugins themselves can be audited individually. The audit treats them as **separate CLIs** with the host as their parent. Per-plugin Pass-1 audit yields per-plugin scorecards.

Then a **family cross-cut** (MULTI-TOOL-FAMILY-AUDIT.md) measures cross-plugin alignment.

---

## When NOT to audit plugins

If the user is auditing only the host (e.g. just `cargo`), plugins can be out of scope. Document in `phase0_scope_decision.md`:

```yaml
plugins_in_scope: false
plugin_audit_deferred_to: pass_2
```

This is the appropriate default for first passes — host alone is enough work.

---

## Related

- `MULTI-TOOL-FAMILY-AUDIT.md` — auditing multi-binary toolkits (orthogonal but overlapping)
- `methodology/CLI-ARCHETYPES.md` § 15 (Multi-binary toolkit) — covers similar ground
- `methodology/SCHEMA-EVOLUTION.md` — for plugin contract version drift
- `methodology/JSON-SCHEMA-PATTERNS.md` — for the universal envelope plugins should adopt
