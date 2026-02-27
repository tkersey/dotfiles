#!/usr/bin/env bash
set -euo pipefail

ST_MARKER="st.zig"
ST_FORMULA="tkersey/tap/st"
BREW_BIN=""

if command -v brew >/dev/null 2>&1; then
  BREW_BIN="$(command -v brew)"
elif [ -x /opt/homebrew/bin/brew ]; then
  BREW_BIN="/opt/homebrew/bin/brew"
elif [ -x /usr/local/bin/brew ]; then
  BREW_BIN="/usr/local/bin/brew"
fi

resolve_st_bin() {
  if command -v st >/dev/null 2>&1; then
    command -v st
    return 0
  fi

  if [ -n "$BREW_BIN" ]; then
    local brew_prefix brew_st
    brew_prefix="$("$BREW_BIN" --prefix 2>/dev/null || true)"
    brew_st="${brew_prefix%/}/bin/st"
    if [ -x "$brew_st" ]; then
      printf '%s\n' "$brew_st"
      return 0
    fi
  fi

  return 1
}

is_compatible_st() {
  local st_bin="$1"
  "$st_bin" --help 2>&1 | grep -q "$ST_MARKER"
}

run_st() {
  local st_bin=""

  if st_bin="$(resolve_st_bin)" && is_compatible_st "$st_bin"; then
    "$st_bin" "$@"
    return 0
  fi

  if [ "$(uname -s)" = "Darwin" ] && [ -n "$BREW_BIN" ]; then
    if ! "$BREW_BIN" install "$ST_FORMULA"; then
      echo "brew install $ST_FORMULA failed; refusing fallback." >&2
      return 1
    fi

    if st_bin="$(resolve_st_bin)" && is_compatible_st "$st_bin"; then
      "$st_bin" "$@"
      return 0
    fi

    echo "brew install $ST_FORMULA did not produce a compatible st binary." >&2
    return 1
  fi

  echo "st binary missing or incompatible (marker $ST_MARKER not found)." >&2
  if [ "$(uname -s)" = "Darwin" ] && [ -z "$BREW_BIN" ]; then
    echo "brew not found in PATH or standard locations (/opt/homebrew/bin, /usr/local/bin)." >&2
  fi
  return 1
}

run_st "$@"
