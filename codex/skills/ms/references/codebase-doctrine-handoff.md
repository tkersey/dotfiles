# Codebase Doctrine Handoff

Use `$ms` only after `$codebase-doctrine` produces a valid `CBSH-v2` and the
user explicitly authorizes the exact package creation.

The handoff binds:

```text
CBD-v2 doctrine, CDI-v2 intent, and artifact-state IDs
candidate ID, status, and proposed name
governing law IDs
triggers and non-triggers
consequential decisions
canonical prohibited route IDs
required artifacts
success and failure signals
protected doctrine IDs
allowed package
explicit user authorization
validation
future empirical evaluation
```

Validate before authoring:

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/handoff_gate.py \
  handoff.yaml \
  --doctrine doctrine.yaml
```

Do not create rejected candidates.

A repository may validly have no root skill and no focused skills. Do not create
a root skill merely because it is the repository root.

A `recommended_for_trial` candidate may be created only under explicit user
authorization and must retain its trial status until empirical decision episodes
justify acceptance.

Preserve governing law IDs in the package decision contract without requiring
the full CBD artifact at runtime.
