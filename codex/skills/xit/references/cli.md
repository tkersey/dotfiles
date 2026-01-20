# xit CLI reference

## Quick start
```
xit init myrepo
cd myrepo
xit config add user.name "Your Name"
xit config add user.email "you@example.com"

# work, then
xit add path/to/file
xit commit -m "message"
```

Also useful in a fresh repo:
```
xit status --cli
xit diff --cli
```

## Common command mapping (git -> xit)
| Intent (git) | xit | Notes |
| --- | --- | --- |
| status | `xit status --cli` | Text output. |
| diff (working tree) | `xit diff --cli` | Text output. |
| diff --cached | `xit diff-added --cli` | Index vs last commit. |
| add | `xit add <path>` | Stage file contents. |
| reset HEAD <path> | `xit unadd <path>` | Unstage changes for a path. |
| rm --cached | `xit untrack <path>` | Stop tracking but keep in work dir. |
| rm | `xit rm <path>` | Stop tracking and delete from work dir. |
| commit | `xit commit -m "msg"` |  |
| log | `xit log --cli` | Text output. |
| branch list | `xit branch list` |  |
| branch add | `xit branch add <name>` |  |
| branch delete | `xit branch rm <name>` |  |
| switch/checkout | `xit switch <name-or-oid>` | Updates index + work dir. |
| reset --mixed | `xit reset <ref-or-oid>` | Updates index only. |
| reset --hard | `xit reset-dir <ref-or-oid>` | Updates index + work dir. |
| reset --soft | `xit reset-add <ref-or-oid>` | Updates refs only. |
| restore | `xit restore <path>` | Restore file(s) in work dir. |
| merge | `xit merge <branch-or-oid>` | Patch-based merge default. |
| cherry-pick | `xit cherry-pick <oid>` |  |
| tag add | `xit tag add <name>` |  |
| tag rm | `xit tag rm <name>` |  |
| tag list | `xit tag list` |  |
| config | `xit config add|rm|list ...` | Add/remove/list config. |
| remote | `xit remote add|rm|list ...` | Manage remotes. |
| clone | `xit clone <url> <dir>` |  |
| fetch | `xit fetch <remote>` |  |
| push | `xit push <remote> <branch>` |  |
| pull | (not implemented) | Use `xit fetch <remote>` + `xit merge <remote-ref>`. |

## Common workflows

### Inspect changes
```
xit status --cli
xit diff --cli
xit diff-added --cli
```

### Commit cycle
```
xit add README.md
xit diff-added --cli
xit commit -m "update README"
```

### Branching and merging
```
xit branch add feature-x
xit switch feature-x
# edit files
xit add .
xit commit -m "feature x"
xit switch master
xit merge feature-x
```

### Cherry-pick a commit
```
xit cherry-pick <commit-oid>
```

### Reset / restore / unadd
```
# unstage a file
xit unadd path/to/file

# restore a file in the working dir
xit restore path/to/file

# move branch pointer (index updated, work dir untouched)
xit reset <ref-or-oid>

# move branch pointer and update work dir
xit reset-dir <ref-or-oid>

# move branch pointer only (soft reset)
xit reset-add <ref-or-oid>
```

### Remove from tracking
```
# stop tracking but keep file
xit untrack path/to/file

# stop tracking and delete file
xit rm path/to/file
```

### Tags
```
xit tag add v1.2.3
xit tag list
xit tag rm v1.2.3
```

### Remotes: fetch + merge (pull equivalent)
```
xit remote add origin <url-or-path>
xit fetch origin
xit merge refs/remotes/origin/master
```

### Push
```
xit push origin master
```

## Patch-based merge controls
- `xit patch on` enables patch-based merge (default behavior).
- `xit patch off` disables patch-based merge (falls back to three-way merge).
- `xit patch all` precomputes patches for all commits.

## Networking
- `xit clone` supports git URLs and local paths.
- `xit fetch` downloads objects and refs.
- `xit push` updates remote refs along with objects.

## Converting between git and xit
- Git to xit (local): `xit clone /path/to/git/repo /path/to/xit/repo`
- xit to git (local):
  1. `xit remote add origin /path/to/git/repo`
  2. `xit push origin master`

## Limitations to flag
- `pull` is not available; use fetch + merge.
- If a requested command is not listed in `xit --help`, explain and ask for direction.
