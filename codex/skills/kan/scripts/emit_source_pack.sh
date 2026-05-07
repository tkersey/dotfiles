#!/usr/bin/env bash
set -euo pipefail
track="${1:-foundations}"
focus="${2:-general}"
case "$track" in
  foundations)
    cat <<'OUT'
# Source pack: foundations

- [KAN-RIEHL-CTIC]: universal properties, Lan/Ran adjunctions around precomposition, pointwise colimit/limit formulas.
- [KAN-MACLANE-CWM]: classic background, ends/coends, density/codensity.

Safe claims:
- Nat(Lan_K F, G) ≅ Nat(F, G.K)
- Nat(G, Ran_K F) ≅ Nat(G.K, F)
- Lan_K ⊣ K* ⊣ Ran_K when they exist for fixed K
- pointwise Lan/Ran via comma-category colimits/limits
OUT
    ;;
  programming)
    cat <<'OUT'
# Source pack: programming

- [KAN-HINZE-2012]: right Kan extensions, continuations, codensity monad, CPS-style optimization, Church representations.
- [KAN-MILEWSKI-2017]: Haskell encodings of Ran/Lan via forall/exists.
- [KAN-HASKELL-KAN-EXTENSIONS]: package vocabulary for Ran, Lan, Yoneda, Coyoneda, Codensity, Density.

Safe claims:
- Codensity/CPS can implement right-Kan-shaped optimizations.
- Haskell encodings approximate end/coend formulas.

Unsafe:
- performance guarantees without benchmarks.
OUT
    ;;
  migration|data)
    cat <<'OUT'
# Source pack: data migration

- [KAN-SPIVAK-WISNESKY-FQL-2014]: schemas as categories, instances as functors.
- [KAN-SCHULTZ-WISNESKY-AQL-2015]: Sigma/Delta/Pi migration framework.
- [KAN-RIEHL-CTIC]: mathematical basis for Lan/Ran and precomposition.

Safe claims:
- Delta is precomposition/restriction.
- Sigma is left Kan extension when it exists.
- Pi is right Kan extension when it exists.
OUT
    ;;
  skills)
    cat <<'OUT'
# Source pack: skills

- [OPENAI-CODEX-SKILLS]: Codex skill folders, progressive disclosure, SKILL.md name/description, optional references/scripts/assets.
- [OPENAI-API-SKILLS]: OpenAI API skill upload as directory or zip with a single top-level folder.
- [AGENT-SKILLS-SPEC]: portable SKILL.md conventions.
OUT
    ;;
  *) echo "Unknown track: $track (focus: $focus)" >&2; exit 2 ;;
esac
printf '\nFocus: %s\n' "$focus"
