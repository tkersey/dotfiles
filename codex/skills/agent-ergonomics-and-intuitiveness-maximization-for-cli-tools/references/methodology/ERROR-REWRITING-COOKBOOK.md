# ERROR-REWRITING-COOKBOOK — Before/After Translations

Every error message is a teaching opportunity OR a moment of friction. This cookbook shows the before/after for the most common error-message anti-patterns.

Use during Phase 5 application: when a recommendation says "improve error message X," consult this file for the translation.

The grading scale (per `INTENT-CORPUS-GENERATION.md`):

- 🚫 **silent_fail** — exit 0, nothing said
- 😤 **useless_error** — error fired, but no path forward
- 🤝 **useful_hint** — error names the right flag/command/env-var
- 🎯 **inferred_and_acted** — tool inferred intent and proceeded with a warning

The translations below show how to climb the ladder.

---

## Translation 1 — Unknown flag

### 🚫 silent_fail (worst)

```bash
$ mytool list --jsno
$ echo $?
0
# Tool exited 0, did nothing, no error. Agent thinks it worked.
```

### 😤 useless_error

```bash
$ mytool list --jsno
error: unrecognized arguments: --jsno
$ echo $?
2
# Agent learns nothing about how to fix it.
```

### 🤝 useful_hint

```bash
$ mytool list --jsno
error: unknown flag '--jsno'
  did you mean '--json'?
  see: mytool list --help
$ echo $?
1
```

**Rust + clap:**

```rust
// Wrap clap's UnknownArgument error
fn map_unknown_flag(token: &str) -> String {
    if let Some(suggestion) = closest_known_flag(token) {
        format!("error: unknown flag '{}'\n  did you mean '--{}'?\n  see: mytool --help", token, suggestion)
    } else {
        format!("error: unknown flag '{}'\n  see: mytool --help (or 'mytool capabilities --json' for the full flag list)", token)
    }
}
```

**Python + argparse:**

```python
class HintingArgParser(argparse.ArgumentParser):
    def error(self, message):
        if "unrecognized arguments:" in message:
            bad = message.split("unrecognized arguments:")[1].split()[0]
            if (s := closest_known(bad)):
                self.exit(1, f"error: unknown flag '{bad}'\n  did you mean '--{s}'?\n  see: {self.prog} --help\n")
        super().error(message)
```

### 🎯 inferred_and_acted

```bash
$ mytool list --jsno
warning: '--jsno' interpreted as '--json' (typo correction; use canonical form to suppress warning)
{"ok":true,"items":[...]}
$ echo $?
0
```

**Use sparingly.** Only enable inferred-and-acted for typo-distance == 1 AND the corrected flag is non-destructive AND the canonical form has been the same for ≥ 1 release. Destructive flags should NEVER be auto-corrected — agents must type the canonical form.

---

## Translation 2 — Missing required argument

### 😤 useless_error

```bash
$ mytool delete
error: the following required arguments were not provided: <ITEM_ID>
Usage: mytool delete <ITEM_ID> [OPTIONS]
For more information, try '--help'.
```

Already passable, but missable. Improve by naming the *expected source* of the missing arg:

### 🤝 useful_hint

```bash
$ mytool delete
error: 'delete' requires <ITEM_ID>
  syntax:    mytool delete <ITEM_ID>
  example:   mytool delete X-001 --dry-run
  to find an ID: mytool list --json | jq '.items[].id'
  see: mytool delete --help
```

The "to find an ID" hint is gold — it tells the agent the canonical way to discover the value it needs.

---

## Translation 3 — Destructive op without confirmation

### 😤 useless_error

```bash
$ mytool delete X-001
error: refusing to run without confirmation
```

### 🤝 useful_hint

```bash
$ mytool delete X-001
error: 'delete' is destructive; refusing without confirmation
  preview the change:  mytool delete X-001 --dry-run
  perform the change:  mytool delete X-001 --yes
  safer alternative:   mytool archive X-001  (reversible; later 'mytool restore X-001')
  see: mytool delete --help

note: per <project>/CONTRIBUTING.md, prefer 'archive' for items < 7 days old
```

This is the canonical `dcg`-style block message. Always: (a) name the safe alternative, (b) name the explicit go-ahead, (c) name a less-destructive alternative if one exists.

---

## Translation 4 — Network / environment failure

### 😤 useless_error

```bash
$ mytool sync
error: connection refused
```

### 🤝 useful_hint

```bash
$ mytool sync
error: failed to connect to <api.example.com:443>: connection refused (after 2 retries)
  is the service up?      mytool doctor --component=remote
  retry with longer timeout: mytool sync --timeout=60
  use offline mode:        mytool sync --offline (cached data only)
  configured endpoint:     api.example.com:443 (set via MYTOOL_API or --api flag)
  see: mytool capabilities --json | jq '.commands.sync'

exit 4 (transient-failure; retry safe)
```

The `exit 4` is not just an exit code; it's communicated to the agent so retry logic can branch on `exit_code_kind: transient-failure`.

---

## Translation 5 — Bad config

### 😤 useless_error

```bash
$ mytool start
Error parsing config
```

### 🤝 useful_hint

```bash
$ mytool start
error: invalid config at /home/user/.config/mytool/config.toml:14:5
  expected:  default_target = "string"
  found:     default_target = 42 (number)
  schema:    mytool capabilities --json | jq '.config_schema'
  edit:      $EDITOR /home/user/.config/mytool/config.toml
  validate:  mytool config validate
  reset:     mytool config init --force (overwrites with defaults)

exit 3 (tool-environment-error)
```

Always cite file:line. Always show the expected vs found types. Always tell the agent how to validate.

---

## Translation 6 — Stale lock / concurrent operation

### 😤 useless_error

```bash
$ mytool reindex
error: lock acquisition failed
```

### 🤝 useful_hint

```bash
$ mytool reindex
error: lock /var/run/mytool.lock held by PID 12345 (started 2 minutes ago)
  another mytool process is running:
    pid:     12345
    cmd:     mytool reindex --full
    started: 2 minutes ago
  options:
    wait:    mytool reindex --wait=300 (waits up to 5 min)
    retry:   re-run after current op completes
    force:   mytool reindex --force-unlock (DANGEROUS; only if PID 12345 is dead)

exit 4 (transient-failure; retry safe after wait)
```

Lock errors are agent-friction unless they tell the agent (a) who's holding the lock, (b) when, (c) how to wait, (d) how to force unlock as last resort.

---

## Translation 7 — Empty result

### 🚫 silent_fail (worst)

```bash
$ mytool search "foo"
$ echo $?
0
# Empty stdout. Agent doesn't know if the tool ran or didn't.
```

### 🤝 useful_hint

```bash
$ mytool search "foo"
{"ok":true,"items":[],"total":0,"query":"foo","hint":"no matches; try broader query or 'mytool search --recent' for last 7 days"}
$ echo $?
0
```

OR for non-JSON mode:

```bash
$ mytool search "foo"
no matches for 'foo' (search took 23ms)
hint: try broader query, or 'mytool search --recent' for last 7 days
```

The empty-result case must be **distinguishable** from "tool didn't run." Agents read the `total` field or the explicit "no matches" message.

---

## Translation 8 — Wrong subcommand alias / family confusion

### 😤 useless_error

```bash
$ mytool ls
error: 'ls' is not a mytool command
```

### 🤝 useful_hint

```bash
$ mytool ls
error: 'ls' is not a mytool command
  did you mean 'mytool list'?  (Unix-style alias; mytool uses POSIX verbs)
  similar: mytool list, mytool show, mytool find
  see: mytool --help
```

### 🎯 inferred_and_acted

```bash
$ mytool ls
note: 'ls' interpreted as 'list' (alias)
[output of mytool list]
```

The alias should work AND warn so the agent learns the canonical form (silently aliasing teaches nothing).

---

## Translation 9 — Permission / authorization

### 😤 useless_error

```bash
$ mytool admin reset-keys
Permission denied
```

### 🤝 useful_hint

```bash
$ mytool admin reset-keys
error: 'admin reset-keys' requires admin role; current user has 'reader' role
  current identity:    user@example.com (role: reader)
  needed:              admin role
  to elevate:          contact your admin OR use 'mytool login --as=admin'
  to check your role:  mytool whoami --json
  see: mytool capabilities --json | jq '.commands."admin reset-keys"'

exit 1 (user-input-error: insufficient privileges)
```

---

## Translation 10 — Schema drift / version mismatch

### 😤 useless_error

```bash
$ mytool import data.json
error: parse failure at line 23
```

### 🤝 useful_hint

```bash
$ mytool import data.json
error: schema mismatch in data.json:23 — found 'old_field_name' but expected 'new_field_name'
  schema version in file:    1.0 (deprecated since mytool v0.4.0)
  schema version we expect:  2.0 (current)
  migrate:                   mytool migrate-schema data.json --to=2.0
  validate:                  mytool import data.json --dry-run --json
  schema reference:          mytool schema --version=2.0 --json
  see: <project>/CHANGELOG.md § "Schema 2.0 migration"

exit 1 (user-input-error)
```

---

## Translation 11 — Resource limit hit

### 😤 useless_error

```bash
$ mytool list
error: too many results
```

### 🤝 useful_hint

```bash
$ mytool list
error: query returned 15234 results; default limit is 10000
  raise limit:    mytool list --limit=20000  (max: 100000; see capabilities.limits.max_items_per_list)
  paginate:       mytool list --limit=1000 --cursor=START (then follow .meta.next_cursor)
  filter:         mytool list --filter=active  (returns 4521 results)
  count only:     mytool list --count  (just returns the total)
  see: mytool list --help

exit 1 (user-input-error)
```

The agent gets multiple paths forward AND learns the relevant capability limit.

---

## Translation 12 — Deprecated flag still in use

### 🚫 silent_fail (worst — flag is silently ignored)

```bash
$ mytool list --colour
[output without color]
$ echo $?
0
# --colour was the old name for --color; tool ignored it silently.
```

### 🤝 useful_hint with proceed

```bash
$ mytool list --colour
warning: '--colour' is deprecated since v0.4.0 (use '--color')
[output with color]
$ echo $?
0
```

OR if the deprecation has reached the removal stage:

```bash
$ mytool list --colour
error: '--colour' was removed in v0.5.0
  use '--color' instead (canonical since v0.4.0)
  changelog: <project>/CHANGELOG.md § "v0.5.0"
  to migrate scripts: sed -i 's/--colour/--color/g' your-script.sh

exit 1 (user-input-error)
```

Never silently drop a deprecated flag. Either proceed-with-warning OR error-with-migration-recipe. Silent-drop is a bug.

---

## Translation 13 — Mismatched verb conventions across siblings

### 🚫 silent_fail

```bash
$ mytool destroy X-001    # In sibling tool, 'destroy' is the canonical verb
[hangs because mytool's 'destroy' silently means something else]
```

### 🤝 useful_hint

```bash
$ mytool destroy X-001
error: 'destroy' is a mytool subcommand but operates on plans, not items
  for items, use:    mytool delete X-001  (with --yes or --dry-run)
  for plans, use:    mytool destroy <PLAN_ID>  (current invocation)
  to disambiguate:   mytool destroy --type=item X-001 OR mytool delete X-001

exit 1 (user-input-error)
```

This is a "wrong tool, right intent" hint. Agents that have used a sibling tool with a different verb hierarchy benefit hugely.

---

## Translation 14 — Complex pipeline error

### 😤 useless_error

```bash
$ mytool list --json | jq '.foo'
error: jq: error (at <stdin>:1): Cannot index array with string "foo"
```

The error is jq's, but the agent's intent was probably wrong: the schema is `{"items": [...]}` not `{"foo": ...}`. The CLI can help by including a hint in `mytool list --json` output OR by exposing schema:

### 🤝 useful_hint (via output schema discoverability)

```bash
$ mytool schema --command=list --json
{
  "command": "list",
  "stdout_schema": {
    "type": "object",
    "properties": {
      "ok": {"type": "boolean"},
      "items": {"type": "array", "items": {"$ref": "#/definitions/Item"}},
      "total": {"type": "number"}
    },
    "required": ["ok", "items"]
  }
}
```

Pattern: ship a `<tool> schema --command=<verb> --json` endpoint so agents can validate their parsing intent before running pipelines.

---

## Translation 15 — Wrong env var

### 🚫 silent_fail

```bash
$ MYTOOL_HOMEDIR=/tmp/foo mytool init
$ echo $?
0
# MYTOOL_HOMEDIR is a typo for MYTOOL_HOME; ignored silently.
```

### 🤝 useful_hint (best-effort warning at startup)

```bash
$ MYTOOL_HOMEDIR=/tmp/foo mytool init
warning: env var 'MYTOOL_HOMEDIR' looks like a typo
  did you mean 'MYTOOL_HOME'? (set via 'export MYTOOL_HOME=/tmp/foo')
  to suppress this warning:    mytool init --no-env-warn
  list of recognized env vars: mytool capabilities --json | jq '.env_vars'

[normal init proceeds with default config]
```

Only emit the warning when an env var with the tool's prefix doesn't match a known one.

---

## Translation 16 — Race condition / TOCTOU error

### 😤 useless_error

```bash
$ mytool update X-001 --field=status --value=closed
error: precondition failed
```

### 🤝 useful_hint

```bash
$ mytool update X-001 --field=status --value=closed
error: precondition failed: X-001's status changed since you read it
  read at:    2026-05-06T12:00:00Z (revision 4)
  current:    revision 5 (changed by 'agent-b' at 12:00:15Z)
  resolve:    mytool show X-001 --json   # see current state
              mytool update X-001 --field=status --value=closed --revision=5

exit 4 (transient-failure)
```

Concurrency-aware errors that name the conflicting actor + revision are gold for multi-agent coordination.

---

## Translation 17 — Subagent reservation conflict

### 😤 useless_error

```bash
$ mytool work X-001
error: lock conflict
```

### 🤝 useful_hint

```bash
$ mytool work X-001
error: file reservation conflict on X-001
  X-001 is reserved by:    'agent-a' (since 2 minutes ago, ttl 1800s)
  reservation reason:      'beads-1234'
  options:
    wait for release:      mytool work X-001 --wait=300  (TTL ends in 28 min)
    pick another item:     mytool --robot-triage  (skips reserved items)
    contact agent-a:       agent-mail send 'agent-a' --thread='beads-1234'
    force release:         mytool work X-001 --force  (DANGEROUS; only if agent-a is dead)

exit 4 (transient-failure; retry after wait)
```

For multi-agent workflows, error messages should explicitly name the other agent and the canonical "wait / talk / pick another / force" options. See [Q-800].

---

## Universal pattern for error rewriting

Every "useful_hint"-class error message follows the same shape:

```
error: <what failed> [at <where>]
  <one-line WHY>
  <one or more named REMEDIATIONS, each as a paste-ready command or path>
  see: <pointer to capabilities / robot-docs / project-docs>

exit <N> (<exit_code_kind>)
```

When in doubt, use the template above. Agents learn quickly to parse it.

---

## Hooking the error layer

In each language, the goal is to wrap the framework's default error-emission with this template:

- **Rust + clap**: `clap::Error::with_cmd().apply()` overridden via `Result<(), Error>` flow; map `clap::error::ErrorKind` to project-specific messages
- **Go + cobra**: `cmd.SetFlagErrorFunc(...)`, `cmd.SilenceErrors = true; cmd.SilenceUsage = true` and emit your own
- **Python + argparse**: subclass `ArgumentParser` and override `error()`
- **Python + click/typer**: catch `UsageError` via decorator
- **TypeScript + commander**: `program.exitOverride()` + try/catch around `program.parse()`
- **TypeScript + yargs**: `.fail((msg, err, y) => {...})`
- **Bash**: hand-rolled at every error site

---

## Anti-patterns to avoid in error messages

1. **Don't cite the framework**: "clap parse error" is meaningless to the agent. Use project-specific language.
2. **Don't emit a stack trace** (unless `--debug` is set): stack traces are noise.
3. **Don't say "see --help" without naming the right flag**: "see --help" is one step better than no message; "see `mytool list --help` for `--filter` syntax" is many steps better.
4. **Don't include emojis or ANSI in error messages going to non-TTY**: agents grepping the message will get noise. Honor NO_COLOR.
5. **Don't log to stdout from an error path**: stderr only.
6. **Don't include the user's input verbatim if it might be malicious shell**: escape, or omit and reference position only.
7. **Don't write a 30-line error**: 5–10 lines max. If you need more, link to docs.
8. **Don't prompt for confirmation on a destructive op without `--yes`**: error and exit; let agents drive the flow.

---

## Pin error messages with regression tests

For every Phase 5 rec that improves an error message, add a regression test using Pattern 4 from `REGRESSION-TEST-PATTERNS.md`:

```bash
# audit/regression_tests/R-NNN__<error>_hint.test.sh
stderr=$("$TOOL" <bad-invocation> 2>&1 >/dev/null) || true
echo "$stderr" | grep -qE 'did you mean|use [`'\'']?-{1,2}[a-z]' || {
  echo "REGRESSION: error no longer includes a 'did you mean' or 'use --X' hint" >&2
  exit 1
}
```

This catches drift if a future refactor accidentally drops the hint.
