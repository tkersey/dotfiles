#!/usr/bin/env bash
set -euo pipefail
track="${1:-foundations}"
case "$track" in
  foundations) echo 'Use Riehl/Mac Lane/nLab for Kan extension/lift foundations.' ;;
  yoneda) echo 'Use Yoneda/Coyoneda as observation/deferred-generation representation lenses.' ;;
  defunctionalization|defun) echo 'Use Danvy-Nielsen/Reynolds for defunctionalization as functions-to-constructors-plus-apply.' ;;
  freyd) echo 'Use Freyd/AFT as an architecture diagnostic, not theorem proof, unless the model is formal.' ;;
  *) echo 'Mark claims as mathematical, programming, architecture inference, or repo observation.' ;;
esac
