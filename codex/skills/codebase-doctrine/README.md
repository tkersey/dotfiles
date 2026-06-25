# Codebase Doctrine v2.0.1

This package is a direct replacement for the existing Codebase Doctrine skill.

## Install

Extract the drop-in ZIP at the dotfiles repository root:

```bash
unzip -o codebase-doctrine-dropin-v2.0.1.zip
```

## Validate

```bash
uv run --with pyyaml python \
  codex/skills/codebase-doctrine/tools/quick_validate.py
```

## v2.0.1 assertion

DIG-v2 now contains an explicit `gate.intent_route`. When `grill_required: yes`,
the route must be `grill-me`, `hard_stop: yes`, and `next_action: activate_grill_me`;
Codebase Doctrine may not continue until a bound `$grill-me` closure returns
`plan_allowed: true`.

## Main changes

- narrow root implicit routing is now consistent with `agents/openai.yaml`;
- DIG-v2 deterministically compiles to CDI-v2;
- intent records a correctness question rather than assuming a repository law;
- CBD-v2 is validated as a closed, artifact-bound evidence graph;
- current, intended, target, proposed, contradicted, and retired doctrine are distinct;
- zero skills is valid; root skills are optional;
- candidate criteria require evidence and new skills normally begin as trials;
- canonical negative-ledger provenance is required for durable route exclusion;
- proof surfaces distinguish design from current execution receipts;
- survey, refresh, portfolio, and audit use separate artifacts;
- specialist packets require bounded assignments and worker-specific authority;
- deep-mode fanout is adaptive;
- CBSH-v2 requires explicit user authorization and source-doctrine validation.

## v1 artifacts

Existing DIG-v1, CDI-v1, CBD-v1, CBDP-v1, and CBSH-v1 files remain historical
evidence. Generate new material through the v2 compilers rather than editing v1
artifacts into v2 by hand.
