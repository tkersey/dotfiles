# Repository closure and change scope

Use when adding, moving, removing or generating Zig files, build steps, fixtures,
examples, goldens, expected output, headers/constants, path registries, manifests,
or checked documentation. A compiling file may still be omitted by aggregate CI.

Find the actual owner: build enumeration, package paths, lint/fmt lists, generator,
compile-fail harness, expected diagnostics, release manifest, or aggregate check.
Do not assume one repository's registry filename or an exact string reference is
universal. Dynamic discovery and globs need inspection, not forced registration.

## Optional locator

Resolve `zig_skill_root` to this loaded skill's directory. Run the bundled scanner
when name/reference matching helps locate affected contracts. It is read-only and
is not proof of closure or a required gate.

```bash
# Uncommitted working-tree state relative to HEAD, plus untracked files.
uv run python3 "$zig_skill_root/scripts/zig_repo_closure_scan.py" --root .

# A committed PR/review range; checkout must be clean and match the reviewed head.
uv run python3 "$zig_skill_root/scripts/zig_repo_closure_scan.py" \
  --root . --base "$review_base" --head "$review_head"
```

Use the task's actual base/head, not an invented `HEAD~1`. Review mode compares the
merge base with head and refuses mixed snapshots. Working-tree mode on a clean
branch sees no uncommitted changes; it has not reviewed that branch's commits.
For an unborn repository, staged and untracked paths are inspected.

Git paths are NUL-delimited, including rename/copy pairs. Changes away from a Zig
suffix remain relevant through the old path. Inspect `scope`, `coverage`, `skipped`,
and `limitations`, not merely the process exit code. The contract fingerprint
covers only inspected candidate files, not all repository inputs.

`--strict` exits 1 for incomplete/error coverage and 2 for likely unregistered
paths. A likely gap is a review lead, not a demonstrated bug. Size limits,
symlinks and unreadable contracts are disclosed. Excluded dependency/cache/output
trees and dynamic generation remain outside the locator's advertised coverage.

Use the repository's aggregate commands to validate the actual build/registry/
generation contract. Apply [evidence context](evidence_context_playbook.md) when
inputs change; avoid rerunning unrelated checks solely for a new receipt.
