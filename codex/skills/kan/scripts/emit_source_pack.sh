#!/usr/bin/env bash
set -euo pipefail
track="${1:-foundations}"
case "$track" in
  foundations) echo 'Use Riehl/Mac Lane/nLab for Kan extension/lift foundations.' ;;
  yoneda) echo 'Use Yoneda/Coyoneda as observation/deferred-generation representation lenses.' ;;
  defunctionalization|defun) echo 'Use Danvy-Nielsen/Reynolds for defunctionalization as functions-to-constructors-plus-apply.' ;;
  freyd) echo 'Use Freyd/AFT as an architecture diagnostic, not theorem proof, unless the model is formal.' ;;
  codensity|codensity-presentation)
    cat <<OUT
# Source pack: codensity presentation

Use for right-Kan/codensity presentations, dense probe worlds, duality/observation bridges, and semantic reconstruction.

Safe claims:
- codensity is a right-Kan construction;
- codensity can be used as a presentation mode when a small probe functor presents a large semantic behavior;
- architecture claims require explicit probe laws and domain-specific assumptions.
OUT
    ;;
  *) echo 'Mark claims as mathematical, programming, architecture inference, or repo observation.' ;;
esac
