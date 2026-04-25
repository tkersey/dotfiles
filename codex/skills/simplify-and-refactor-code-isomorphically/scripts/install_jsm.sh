#!/usr/bin/env bash
# install_jsm.sh — offer to install jsm (jeffreys-skills.md CLI).
# User-consent-gated; exits 0 on declination.
#
# Usage: install_jsm.sh
# Downloads from https://jeffreys-skills.md/install.sh

set -euo pipefail

if command -v jsm >/dev/null 2>&1; then
  echo "jsm already installed: $(jsm --version 2>&1 | head -1)"
  exit 0
fi

echo "jsm is not installed."
echo "This skill references many sibling skills. If you have a paid jeffreys-skills.md"
echo "subscription (\$20/month), jsm lets you install any missing sibling in one command."
echo ""
echo "Without jsm, this skill still runs end-to-end — every sibling has an inline fallback."
echo ""

if [[ "${JSM_AUTO_INSTALL:-}" != "1" ]]; then
  read -r -p "Install jsm now via the official installer? [y/N] " reply
  if [[ ! "$reply" =~ ^[Yy]$ ]]; then
    echo "Skipped. Proceeding with inline fallbacks."
    exit 0
  fi
fi

echo ""
echo "Running: curl -fsSL https://jeffreys-skills.md/install.sh | bash"
echo ""

if ! command -v curl >/dev/null 2>&1; then
  echo "error: curl not found. Install curl first or use the manual install from https://jeffreys-skills.md"
  exit 0
fi

if curl -fsSL https://jeffreys-skills.md/install.sh | bash; then
  echo ""
  echo "jsm installed."
  # PATH shim
  if [[ -x "$HOME/.local/bin/jsm" ]] && ! command -v jsm >/dev/null 2>&1; then
    echo "Add \$HOME/.local/bin to your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "Persist in ~/.bashrc or ~/.zshrc."
  fi
  echo ""
  echo "Next steps:"
  echo "  jsm --version           # verify"
  echo "  jsm doctor              # health check"
  echo "  jsm login               # authenticate (browser OAuth)"
  echo "  ./scripts/install_missing_skills.sh refactor/artifacts/<run-id>"
else
  echo ""
  echo "Installer returned non-zero. Check your network and https://jeffreys-skills.md ."
  echo "Proceeding with inline fallbacks for all sibling skills."
  exit 0
fi
