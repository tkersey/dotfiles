# Existing-publication observation

## Existing-publication observation

`observe-existing` is Actuating-only and read-only.

Require:

- the supplied head ref is the provider's current default branch;
- the supplied head SHA equals the live default-branch tip;
- base and head differ and base is an ancestor;
- base and head refs normalize to the same default-branch ref;
- no open exact repository/base/head PR exists;
- release input is null.

Return immutable `SHIP-OBSERVATION-v2` with:

```text
repository
canonical default-branch ref
base SHA
head SHA
provider readback
goal context digest
review contract digest
observed time
mutation_performed = false
```

Actuating computes the receipt digest and includes it in the review context and
every review request fingerprint before dispatch. Require the selected executor's
binding to that dispatch and result: the native Codex invocation/thread/turn and original result, or native subagent
assignment/result attribution. A digest alone does not establish that the exact
observation preceded review.

No Actuating event ordering or wall-clock comparison is needed.

## Existing-publication adoption

`adopt-existing` is Actuating-only and read-only.

Require a non-null `publication_observation_ref` resolving to the exact
`SHIP-OBSERVATION-v2` used in the current review context. Exact-match:

- repository and canonical default-branch ref;
- immutable base and reviewed head;
- Goal context digest and Review Contract digest;
- current provider branch readback;
- selected-executor review-context binding supplied by Actuating.

If the exact observation was not bound before the current review, do not adopt a
historical campaign. Obtain a fresh observation and run a fresh review wave.

For an optional release, require current provider state `published`,
`draft: false`, tag target equal to the adopted head, unique asset names, equal
cardinality and exact set equality with the live inventory, and exact asset
name, size, and SHA-256 digest matches.

Return immutable `SHIP-ADOPTION-v2`. It ratifies current public state; it does
not manufacture publication history or decide Actuating closure.
