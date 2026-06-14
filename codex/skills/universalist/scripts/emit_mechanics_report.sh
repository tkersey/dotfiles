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
- freyd
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

Examples:
  ./scripts/emit_mechanics_report.sh kan-lift typescript
  ./scripts/emit_mechanics_report.sh codensity-presentation agnostic
  ./scripts/emit_mechanics_report.sh cql-context agnostic
OUT
    ;;
  kan-extension|kan-lift|kan)
    ./scripts/emit_kan_stub.sh "$topic" "$language" ;;
  boundary-kind|boundary)
    ./scripts/emit_boundary_kind_map.sh "$language" ;;
  freyd|aft|free-builder)
    ./scripts/emit_freyd_pass.sh boundary-diagnostic "$language" ;;
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
  pushout|pushout-reconciliation)
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
  *)
    echo "Unknown mechanics topic: $topic" >&2
    echo "Run ./scripts/emit_mechanics_report.sh index" >&2
    exit 2
    ;;
esac
