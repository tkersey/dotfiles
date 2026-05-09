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
- [KAN-NLAB-LIFT]: Kan lifts as postcomposition universal properties.

Safe claims:
- Nat(Lan_K F, G) ≅ Nat(F, G.K)
- Nat(G, Ran_K F) ≅ Nat(G.K, F)
- Lan_K ⊣ K* ⊣ Ran_K when they exist for fixed K
- Lft_P ⊣ P_* ⊣ Rft_P when they exist for fixed P
- pointwise Lan/Ran via comma-category colimits/limits
OUT
    ;;
  lifts|kan-lifts)
    cat <<'OUT'
# Source pack: Kan lifts

- [KAN-NLAB-LIFT]: left/right Kan lift definitions, postcomposition framing, right-lift/residual intuition.

Safe claims:
- P_* maps G : A -> B to P.G : A -> C.
- A left Kan lift has comparison F -> P.Lft_P F.
- A right Kan lift has comparison P.Rft_P F -> F.
- Lift notation varies; define notation locally.

Unsafe:
- claiming minimal/weakest/strongest behavior without specifying the order or 2-cell direction.
- claiming a codebase has a Kan lift without explicit A, B, C, P, F, and a witness comparison.
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
  defunctionalization|defun)
    cat <<'OUT'
# Source pack: defunctionalization

- [KAN-REYNOLDS-1972]: origin/background for defunctionalization in definitional interpreters.
- [KAN-DANVY-NIELSEN-2001]: defunctionalization as higher-order to first-order transformation, constructors plus apply function.
- [KAN-DANVY-FILINSKI-1990]: CPS/control background when continuations are being exposed before defunctionalization.
- [KAN-HINZE-2012]: codensity/right-Kan/CPS programming overlap.

Safe claims:
- Defunctionalization turns a closed set of function shapes into first-order cases plus an apply/interpreter.
- It can make Kan-shaped boundary functions inspectable and testable.

Unsafe:
- saying defunctionalization is itself a Kan extension or Kan lift.
- replacing genuinely open extension points without an escape hatch.
OUT
    ;;
  lift-playbook|outside-in|obligations)
    cat <<'OUT'
# Source pack: Kan lift architecture playbook

Mathematical basis:
- [KAN-NLAB-LIFT]: Kan lifts as postcomposition universal properties and residual/best-approximation intuition.

Architecture inferences:
- Lift-shaped refactors are outside-in: public commitments determine internal architecture.
- `P : B -> C` must be a concrete projection from internals to observable behavior.
- `F : A -> C` should be backed by contract cases, golden tests, reports, policies, or trace expectations.
- Left-lift mode synthesizes/chooses an implementation-side realizer.
- Right-lift mode derives residual obligations, missing capabilities, and no-exact-lift obstructions.

Required witness:
- A, B, C, P, F;
- one witness a in A;
- exact/covering/sound/no-exact-lift classification;
- projection law test;
- obligation ledger if any observation is missing.

Unsafe:
- claiming an exact lift when P cannot produce a required observation;
- using minimal/weakest language without an order or comparison relation;
- refactoring internals before writing projection tests.
OUT
    ;;
  architecture)
    cat <<'OUT'
# Source pack: architecture interpretation

Mathematical basis:
- [KAN-RIEHL-CTIC] for Kan extensions.
- [KAN-NLAB-LIFT] for Kan lifts.

Architecture inferences:
- Lan: free/generative pushforward across a boundary.
- Ran: coherent/contextual structure determined by observations.
- Lft: synthesize implementation behind a projection.
- Rft: derive residual obligations behind a projection.

Required witness:
- extension needs C, D, K, F and unit/counit test.
- lift needs A, B, C, P, F and comparison-cell test.
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

Lift-aware note:
- view-update or reverse-migration problems are often lift-shaped through a fixed projection P from source states to views.
OUT
    ;;
  yoneda|coyoneda|representation)
    cat <<'OUT'
# Source pack: Yoneda/Coyoneda boundary representation

- [KAN-MILEWSKI-YONEDA]: Yoneda/Coyoneda intuition and Haskell-shaped representations.
- [KAN-HASKELL-YONEDA]: library vocabulary for Yoneda representation and lift/lower/map operations.
- [KAN-HASKELL-COYONEDA]: library vocabulary for Coyoneda as free-functor/deferred-map representation.
- [KAN-HASKELL-KAN-EXTENSIONS]: package-level grouping of Kan extensions, lifts, Yoneda, Coyoneda, codensity, and density tools.

Safe claims:
- Yoneda is useful as an observation-heavy representation lens.
- Coyoneda is useful as a generation-heavy/deferred-map representation lens.
- In architecture, these are representation passes, not replacements for identifying the real K or P boundary.

Unsafe:
- claiming a mainstream-language wrapper is a lawful Yoneda/Coyoneda encoding without laws.
- using the names when they do not change code shape, tests, provenance, or observer centralization.
OUT
    ;;
  freyd|aft|freyd-aft|free-builder)
    cat <<'OUT'
# Source pack: Freyd/AFT boundary diagnostics

Mathematical basis:
- [KAN-RIEHL-CTIC]: adjoint functor theorem, continuous functors, solution-set condition.
- [KAN-NLAB-AFT]: adjoint functor theorem as conditions for a functor to be a right adjoint.
- [KAN-NLAB-SOLUTION-SET]: solution-set condition as a weak candidate-family condition.
- [KAN-NLAB-LIFT]: Kan lifts as postcomposition universal properties.

Architecture inferences:
- For a lift-shaped refactor, the projection P : B -> C should be concrete and testable.
- Freyd/AFT practice asks whether P preserves constraints and admits a bounded template menu.
- If plausible, define Free : C -> B and use L = Free . F as a candidate lift.

Required witness:
- A, B, C, P, F;
- constraints available in B;
- one preservation test for P;
- solution-set-like implementation templates;
- exact/embedding/covering/sound/approximate/no-exact-lift classification;
- projection law for P(Free(F(a))).

Unsafe:
- theorem claims about a codebase without explicit categorical modeling;
- calling Free canonical without a projection law;
- assuming free means smallest or production-optimal.
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
