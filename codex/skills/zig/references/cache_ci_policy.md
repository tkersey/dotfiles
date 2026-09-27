# CI cache policy

Prefer an ephemeral local cache per job; do not share mutable local caches across
concurrent jobs without a tested access protocol. Share global cache objects only
under an explicit key/TTL policy. Include compiler version, host/target, relevant
build/options/generated inputs, and dependency/fork identity where they affect
compatibility. A cache hit is an optimization, not validation evidence.

Do not persist dependency working state that jobs mutate as a disposable cache.
`zig-pkg` and global package storage may contain valuable edits or local commits.
The bundled drain helper preserves packages and refuses unknown cache layouts;
it is not a general filesystem garbage collector. Stop writers before cleanup,
apply the identity/age checks in [cache hygiene](cache_hygiene_playbook.md), and
report actual outcomes rather than requested flags.

After a deliberately authorized repository-specific dependency reset, restore
its pinned dependencies with the repository's supported fetch/build command and
validate the intended artifact. Never claim this helper verified a rebuild.
Reuse validation according to [evidence context](evidence_context_playbook.md),
not merely because a cache key or commit label stayed the same.
