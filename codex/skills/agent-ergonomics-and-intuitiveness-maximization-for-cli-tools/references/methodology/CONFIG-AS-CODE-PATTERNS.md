# CONFIG-AS-CODE-PATTERNS — Agent-friendly config file design

Most CLIs read config from files (`~/.config/<tool>/config.toml`, `.toolrc`, `package.json` keys, etc.). Config files are agent surfaces too — agents read them, write them, validate them, and migrate them across versions.

This file gives the patterns for config-file design that agents can actually work with.

---

## The agent's needs vs the human's needs

Humans want config files that are:
- Concise
- Comment-friendly
- Forgiving (defaults for missing fields)
- Editable in any text editor

Agents want config files that are:
- **Validatable** against a schema
- **Self-documenting** (every key has a known meaning)
- **Stable across versions** (or with explicit migrations)
- **Programmatically readable AND writable** (the agent updates them, not just reads)

The two needs aren't in conflict — both want the same thing, expressed differently.

---

## Format choice: TOML vs YAML vs JSON

For agent-friendly CLIs:

| Format | Pros | Cons |
|--------|------|------|
| **TOML** | Reasonable defaults; comment support; section-friendly; Rust + Python ecosystems prefer | Edge cases with nested tables; less universal |
| **YAML** | Universal; very flexible | Surprising parsing (Norway problem); whitespace-sensitive |
| **JSON5** | Adds comments + trailing commas to JSON | Less ecosystem support |
| **JSON** | Universal; strictly parseable | No comments; less human-friendly |
| **Custom INI** | Simple | No standard; agents need bespoke parser |

**Recommendation by archetype:**

- Rust CLIs: **TOML** (matches Cargo.toml convention)
- Python CLIs: **TOML** (PEP 518 set the precedent) or YAML (legacy)
- Go CLIs: **YAML** or **TOML** (cobra+viper supports both)
- TypeScript CLIs: **JSON** in package.json key, OR **YAML** for richer config
- For agent-only configs: **JSON** (most universal; no parsing edge cases)

---

## Schema discoverability

The agent must be able to introspect the config schema without reading source. Pattern:

```bash
$ <tool> config schema --json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "default_target":  {"type": "string", "description": "Default target for ...", "default": "."},
    "color":           {"type": "string", "enum": ["auto", "never", "always"], "default": "auto"},
    "robot":           {"type": "boolean", "default": false},
    ...
  },
  "additionalProperties": false
}
```

Agents validate config against this schema before writing.

---

## Config validation

Tool exposes:

```bash
$ <tool> config validate
config OK at /home/user/.config/mytool/config.toml

$ <tool> config validate --file=/path/to/test-config.toml
config OK at /path/to/test-config.toml

$ <tool> config validate --json --file=bad.toml
{"ok": false, "errors": [{"path": "$.color", "message": "expected enum but got 'reds'", "did_you_mean": "red"}]}
```

Validation errors include `did_you_mean` for typo'd keys (Operator ⟁).

---

## Config show

Tool exposes the *effective* config (after merging defaults + env + flag overrides):

```bash
$ <tool> config show --json
{
  "ok": true,
  "data": {
    "default_target":   ".",
    "color":            "auto",
    "robot":            false,
    "_provenance": {
      "default_target": "default",
      "color":          "config_file",
      "robot":          "env (MYTOOL_ROBOT)"
    }
  }
}
```

The `_provenance` field tells the agent **where each value came from**. Hugely valuable for debugging "why is `color` not what I set in the file?"

---

## Config init / write

Tool can initialize a config from defaults:

```bash
$ <tool> config init --output ~/.config/mytool/config.toml
created config at ~/.config/mytool/config.toml

$ <tool> config init --json --dry-run
{"ok": true, "data": {"path": "/home/user/.config/mytool/config.toml", "content": "..."}}
```

And write a single key:

```bash
$ <tool> config set color always
$ <tool> config get color
always
$ <tool> config get --json
{"key": "color", "value": "always", "from": "config_file"}
```

Agents can update config without parsing TOML/YAML by hand.

---

## Config search path

Document the search path explicitly:

```bash
$ <tool> config show --json | jq '.meta.search_path'
[
  "<arg via --config>",
  "$XDG_CONFIG_HOME/mytool/config.toml",
  "$HOME/.config/mytool/config.toml",
  "$HOME/.mytoolrc",
  "/etc/mytool/config.toml"
]
```

Agents can iterate the path manually if needed.

---

## Versioning the config schema

Add a `_schema_version` field at top of every config:

```toml
_schema_version = "1"

color = "auto"
robot = false
```

When the tool loads a config:

```rust
let cfg: Config = toml::from_str(&content)?;
match cfg._schema_version.as_str() {
    "1" => /* current */,
    "0" | "" => migrate_from_v0(&cfg),
    other => bail!("unsupported config schema version: {} (expected 1; migrate via `mytool config migrate-schema`)", other),
}
```

Surface in capabilities:

```jsonc
"config": {
  "schema_version":     "1",
  "supports_versions":  ["0", "1"],
  "schema_uri":         "<tool> config schema --json",
  "search_path":        ["~/.config/mytool/config.toml", ...]
}
```

---

## Config migration

Provide a migration command:

```bash
$ <tool> config migrate-schema --from=0 --to=1 --dry-run
plan: rename 'colour' → 'color'; remove deprecated 'old_field'
$ <tool> config migrate-schema --from=0 --to=1 --yes
migrated config to schema v1
```

---

## Config diff / patch

For agents updating config in-place:

```bash
# Get current config as JSON for jq manipulation
$ <tool> config show --json --raw > current.json

# Modify with jq
$ jq '.color = "always"' current.json > new.json

# Apply
$ <tool> config apply --file=new.json --dry-run
$ <tool> config apply --file=new.json --yes
```

Or via a patch operation:

```bash
$ <tool> config patch '{"color": "always"}'
$ <tool> config patch --remove '["old_field"]'
```

---

## Comments and human-friendliness

For TOML/YAML configs, support comments AND preserve them on programmatic writes:

- TOML: use `toml_edit` (Rust) which preserves comments + ordering
- YAML: use `ruamel.yaml` (Python) which round-trips comments
- JSON: use JSON5 if comments are needed, OR keep comments out of config

Tools that **destroy comments on write** lose user trust quickly.

---

## Sensitive values

Config sometimes holds sensitive values (API keys, tokens). Patterns:

1. **Reference, don't embed**: `api_token = "$ENV:MYTOOL_TOKEN"` (resolved at load time)
2. **Keychain integration**: `api_token = "$KEYCHAIN:mytool/token"`
3. **Per-environment**: `[profiles.prod]` vs `[profiles.dev]`
4. **Never**: store plaintext secrets in config files committed to git

Document in capabilities:

```jsonc
"sensitive_keys": ["api_token", "webhook_secret"],
"sensitive_resolution": ["env", "keychain", "1password://", "explicit"],
"never_log": true
```

---

## Multi-profile configs

For tools with multiple environments / accounts:

```toml
default_profile = "dev"

[profiles.dev]
api_url = "https://dev.api.example.com"
api_token = "$ENV:MYTOOL_DEV_TOKEN"

[profiles.prod]
api_url = "https://api.example.com"
api_token = "$KEYCHAIN:mytool/prod"
```

CLI:

```bash
$ <tool> --profile=prod list
$ <tool> profile list --json
$ <tool> profile use prod
```

---

## Hierarchical configs

Some tools want global + workspace + repo config layered:

```
/etc/mytool/config.toml         # system-wide (lowest priority)
~/.config/mytool/config.toml    # user global
./mytool.toml                   # project (highest)
```

Document the merge order in capabilities. `config show --json` outputs the merged result with `_provenance`.

---

## Config-as-code pitfalls

### Pitfall 1: Implicit defaults

If `config show` doesn't output a key (because it's at default), agents can't tell "is this the default?" from "is this missing?". Always include all keys with their resolved values + provenance.

### Pitfall 2: Silent fallthrough

If `~/.toolrc` is malformed and `~/.config/mytool/config.toml` is also present, does the tool fall through silently or error? Document and surface.

### Pitfall 3: Race conditions

Multi-agent scenarios can have agents writing config simultaneously. Use file locks (advisory) AND atomic writes (write to tempfile, then rename).

### Pitfall 4: Auto-update on read

Some tools auto-write config on load (e.g. add new default keys). Surprises agents. Make this opt-in: `<tool> config upgrade --yes`.

### Pitfall 5: ENV beats config beats flag (or vice versa)

Document the precedence explicitly. Common: flag > env > config > default. Tools that diverge confuse agents.

---

## Config-as-code regression tests

```bash
# audit/regression_tests/CONFIG-001__schema_export.test.sh
schema=$("$TOOL_BIN" config schema --json)
echo "$schema" | jq -e '."$schema"' > /dev/null || {
  echo "REGRESSION: config schema --json missing \$schema field" >&2; exit 1; }
```

```bash
# audit/regression_tests/CONFIG-002__provenance.test.sh
out=$("$TOOL_BIN" config show --json)
echo "$out" | jq -e '.data._provenance' > /dev/null || {
  echo "REGRESSION: config show --json missing _provenance field" >&2; exit 1; }
```

```bash
# audit/regression_tests/CONFIG-003__validate_typo_hint.test.sh
echo 'colour = "red"' > /tmp/bad.toml
err=$("$TOOL_BIN" config validate --file=/tmp/bad.toml --json 2>&1)
echo "$err" | grep -qE 'did_you_mean.*color' || {
  echo "REGRESSION: typo'd config key didn't suggest correct spelling" >&2; exit 1; }
```

---

## Per-archetype recommendations

| Archetype | Config emphasis |
|-----------|-----------------|
| Search tool | Default index location; ignore globs; thread count |
| Package manager | Registry URLs; lockfile mode; install strategy |
| Build tool | Default target; cache settings; parallel jobs |
| Daemon CLI | Server endpoint; auth method; timeout |
| Hook tool | Pack list; allowlist; severity threshold |
| Issue tracker | Default project; priority sort order; ready-filter |

Each archetype has 2-5 canonical config keys; docent these as required vs optional.

---

## Capabilities mention

Don't forget to surface config in capabilities:

```jsonc
{
  "config": {
    "schema_uri":         "<tool> config schema --json",
    "show_uri":           "<tool> config show --json",
    "search_path":        [...],
    "schema_version":     "1",
    "supports_versions":  ["0", "1"],
    "format":             "toml",
    "supports_profiles":  true,
    "supports_env_overrides": true,
    "env_var_prefix":     "MYTOOL_"
  }
}
```

---

## Related

- `LANGUAGE-RECIPES.md` — config-loading code snippets per language
- `JSON-SCHEMA-PATTERNS.md` — for the config schema export
- `SCHEMA-EVOLUTION.md` — for migrating config schema across versions
