# Zig Proof Epoch

A proof result is valid only for the exact context in which it ran.

## ZPE-v1

```yaml
zig_proof_epoch:
  epoch_version: ZPE-v1
  epoch_id:
  command: []
  cwd:
  repository_root:
  branch:
  head:
  dirty_fingerprint:
  zig_version:
  target:
  optimize_mode:
  build_options: []
  dependency_fingerprint:
  fork_overrides: []
  generated_artifact_fingerprint:
  cache_environment:
  started_at:
  ended_at:
  exit_code:
  result: pass | fail | blocked
  state_after:
  invalidators: []
  log_ref:
```

## Invalidators

```text
file edit
zig fmt
generated artifact rewrite
commit/amend/rebase/merge
head/worktree change
dependency/build.zig.zon/fork change
target or optimize change
build option change
proof command change
different Zig version
```

Cache contents should not change correctness, but cache path/permission failures belong in the transport record.

## Command wrapper

```bash
python3 codex/skills/zig/scripts/zig_proof_epoch.py run \
  --output .zig-proof/epoch.json \
  --log .zig-proof/test.log \
  -- zig build test --summary all
```

Check later:

```bash
python3 codex/skills/zig/scripts/zig_proof_epoch.py check \
  --epoch .zig-proof/epoch.json
```

## Long-running proof

A shell-tool yield or timeout is not automatically failure.

Keep the same process alive and poll to completion.

If source/context changes while proof runs, terminate that stale process and restart the exact required command.

## Closure

Focused proof may narrow a failure.

Final closure requires a passing epoch matching the final repository state, target, optimize mode, dependencies, generated artifacts, and command.
