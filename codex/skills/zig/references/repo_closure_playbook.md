# Repository Contract Closure

Use when files or generated outputs are added, moved, renamed, removed, or semantically regenerated.

## Objective

A local file change is complete only when every repository-owned enumeration, generator, registry, golden, and aggregate proof surface is synchronized.

## Discovery

Search repository-specific contracts:

```text
build.zig / build.zig.zon
path lists and manifests
source registries
compile-fail fixture lists
examples/docs checked by CI
goldens and expected stdout/stderr
generated constants/headers/tables
lint/format path lists
release/package manifests
checksum or fingerprint files
```

Suggested broad search:

```bash
rg -n \
  "manifest|registry|paths?|golden|expected|compile[-_ ]fail|generated|fixture|zig fmt --check|zig build lint|run-.*example" .
```

Then inspect neighboring files and build logic rather than trusting names.

## Changed-file closure table

```yaml
repo_closure:
  changed_path:
  change_kind: add | modify | move | remove | generate
  owners:
    - build step
    - registry
    - generator
    - golden
    - aggregate check
  synchronized: yes | no | not-applicable
  proof:
```

## Rules

- Do not hardcode one repository’s path registry as universal.
- A new `.zig` file may need build, lint, fmt, package, docs, or path-manifest updates.
- A new compile-fail fixture may need explicit registration and expected diagnostic output.
- Generated output changes invalidate proof that ran before regeneration.
- A constant compared only against another generated/stale constant is not an independent proof.
- Renames require searching both old and new names.
- Deletions require proving no registry/build/golden still references the path.
- Run the repository aggregate lint/build/test lane after synchronization.

Use `zig_repo_closure_scan.py` as a locator, not as a substitute for repository-specific judgment.
