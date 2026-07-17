#!/usr/bin/env bash
set -euo pipefail
topic="${1:-index}"
language="${2:-agnostic}"
case "$topic" in
  index|help)
    cat <<'OUT'
# Universalist Mechanics Report Index

Use after universalist has selected the signal, seam, canonical artifact, witness, law, and certificate type.

Available mechanics topics:
- kan-extension
- kan-lift
- boundary-kind
- freyd-aft
- freyd-category
- operad
- composition-geometry
- pullback
- pushout
- pullback-pushout
- double-pushout
- comonad-space
- density-comonad
- halo
- continuous-comonad-map
- yoneda
- defunctionalization
- codensity-presentation
- context-compilation
- cql-context
- pushout-reconciliation
- verified-context-publication
- composition-certificate
- sheafification
- abstraction-replacement
- category-pivot
- syntax-semantics
- domain-algebra
- law-discovery
- property-tests

Examples:
  ./scripts/emit_mechanics_report.sh pullback typescript
  ./scripts/emit_mechanics_report.sh pushout agnostic
  ./scripts/emit_mechanics_report.sh double-pushout agnostic
  ./scripts/emit_mechanics_report.sh comonad-space typescript
  ./scripts/emit_mechanics_report.sh density-comonad agnostic
  ./scripts/emit_mechanics_report.sh halo typescript
  ./scripts/emit_mechanics_report.sh continuous-comonad-map agnostic
  ./scripts/emit_mechanics_report.sh kan-lift typescript
  ./scripts/emit_mechanics_report.sh codensity-presentation agnostic
  ./scripts/emit_mechanics_report.sh cql-context agnostic
OUT
    ;;
  kan-extension|kan-lift|kan)
    ./scripts/emit_kan_stub.sh "$topic" "$language" ;;
  boundary-kind|boundary)
    ./scripts/emit_boundary_kind_map.sh "$language" ;;
  freyd-aft|aft|free-builder)
    ./scripts/emit_freyd_pass.sh boundary-diagnostic "$language" ;;
  freyd-category|premonoidal|effect-order)
    ./scripts/emit_freyd_category.sh effect-boundary "$language" ;;
  operad|operads|operadic|component-wiring)
    ./scripts/emit_operadic_architecture.sh component-wiring "$language" ;;
  composition-geometry|geometry)
    cat references/composition-geometry.md ;;
  pullback|pullbacks)
    bash ./scripts/emit_pullback_pushout_report.sh pullback "$language" ;;
  pushout|pushouts)
    bash ./scripts/emit_pullback_pushout_report.sh pushout "$language" ;;
  pullback-pushout|pullbacks-pushouts|limit-colimit-square)
    bash ./scripts/emit_pullback_pushout_report.sh compare "$language" ;;
  double-pushout|dpo|graph-rewrite)
    bash ./scripts/emit_pullback_pushout_report.sh dpo "$language" ;;
  comonad-space|comonads-as-spaces|spatiality|spatial-world)
    ./scripts/emit_comonadic_spatiality.sh space "$language" ;;
  density-comonad|density-comonads|subbasis|basis)
    ./scripts/emit_comonadic_spatiality.sh density "$language" ;;
  halo|halos|labelled-halo|labeled-halo|germ|germs)
    ./scripts/emit_comonadic_spatiality.sh halo "$language" ;;
  continuous-comonad-map|continuous-comonadic-map|locality-preserving|spatial-continuity)
    ./scripts/emit_comonadic_spatiality.sh continuous "$language" ;;
  freyd)
    echo "Ambiguous mechanics topic: freyd" >&2
    echo "Use 'freyd-aft' for the adjoint-functor/free-builder diagnostic or 'freyd-category' for effectful call-by-value composition." >&2
    exit 2 ;;
  yoneda|coyoneda|representation)
    ./scripts/emit_yoneda_pass.sh mixed "$language" ;;
  defunctionalization|defun)
    ./scripts/emit_defun_pass.sh boundary-ir "$language" ;;
  codensity|codensity-presentation)
    ./scripts/emit_codensity_presentation.sh report "$language" ;;
  context|context-compilation)
    ./scripts/emit_context_compilation_report.sh report "$language" ;;
  cql|cql-context)
    ./scripts/emit_cql_context_report.sh context-publication "$language" ;;
  pushout-reconciliation)
    ./scripts/emit_pushout_reconciliation_plan.sh context-merge "$language" ;;
  verified-context|verified-context-publication)
    ./scripts/emit_verified_context_publication_plan.sh publication-boundary "$language" ;;
  composition-certificate|certificate)
    ./scripts/emit_composition_certificate_kan.sh boundary "$language" ;;
  sheafification)
    ./scripts/emit_sheafification_kan.sh abstraction "$language" ;;
  abstraction-replacement)
    ./scripts/emit_abstraction_replacement_kan.sh abstraction "$language" ;;
  category-pivot|easy-world)
    ./scripts/emit_category_pivot.sh syntax "$language" ;;
  syntax-semantics|syntax|semantics)
    ./scripts/emit_syntax_semantics_certificate.sh ToolOperation "$language" ;;
  domain-algebra|add)
    ./scripts/emit_domain_algebra_card.sh domain "$language" ;;
  law-discovery|laws|non-laws)
    ./scripts/emit_law_table.sh Carrier "$language" ;;
  property-tests|property-test)
    ./scripts/emit_property_test_plan.sh law "$language" ;;
  *)
    echo "Unknown mechanics topic: $topic" >&2
    echo "Run ./scripts/emit_mechanics_report.sh index" >&2
    exit 2
    ;;
esac