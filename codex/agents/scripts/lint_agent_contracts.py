#!/usr/bin/env -S uv run python
"""Lint the custom agent contract surface."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "codex/config.toml"
AGENTS_DIR = ROOT / "codex/agents"
SCRIPTS_DIR = AGENTS_DIR / "scripts"

ACTIVE_ROLE_PHRASES = {
    "selector.toml": [
        "Use this role only for explicit source shaping or wave selection; keep ad hoc planning local.",
        "Emit exactly: OrchPlan v1 YAML, then a plaintext Decision Trace. No extra prose.",
    ],
    "coder.toml": [
        "Use this role only when the parent has already decided a custom specialist is worth the overhead.",
        "If `approach=reduce`, do the reduction work here instead of spawning `reducer`.",
        "Produce one apply_patch-format candidate artifact or `NO_DIFF:<reason>`.",
    ],
    "fixer.toml": [
        "Absorb mentor-style doctrine scoring inside one review pass",
        "Always emit doctrine-fit scores inline; do not require a separate `mentor` role.",
    ],
    "prover.toml": [
        "Own both transient patch application and proof execution so the parent does not need a separate `applier` hop.",
        "If a patch artifact is provided (e.g. `patch` or `patch_text`), apply it in the assigned worktree before proving.",
    ],
    "integrator.toml": [
        "Own delivery packaging and scope-safe materialization; do not re-adjudicate candidate safety.",
        "If materializing commits from patch artifacts, use `git am` only.",
    ],
    "joiner.toml": [
        "Use `gh` only (`gh pr`, `gh run`, `gh api`, `gh repo`). Never run `git` or any non-`gh` command.",
        "Do not emit any other text before/after the JSON object(s).",
    ],
}

DEPRECATED_ROLE_REDIRECTS = {
    "reducer.toml": "DEPRECATED_ROLE:coder",
    "mentor.toml": "DEPRECATED_ROLE:fixer",
    "locksmith.toml": "DEPRECATED_ROLE:integrator",
    "applier.toml": "DEPRECATED_ROLE:prover",
}

EXECUTABLE_SCRIPTS = [
    "lint_agent_contracts.py",
    "run_role_bakeoff.py",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_contains(text: str, needle: str, label: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: missing phrase: {needle}")


def main() -> int:
    errors: list[str] = []

    if not CONFIG_PATH.exists():
        print(f"[FAIL] missing config: {CONFIG_PATH}", file=sys.stderr)
        return 1

    config = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    agent_config = config.get("agents", {})

    expected_roles = set(name.removesuffix(".toml") for name in ACTIVE_ROLE_PHRASES)
    expected_roles.update(name.removesuffix(".toml") for name in DEPRECATED_ROLE_REDIRECTS)

    missing_roles = sorted(expected_roles - set(agent_config))
    if missing_roles:
        errors.append(f"config.toml: missing agent sections: {', '.join(missing_roles)}")

    for filename, phrases in ACTIVE_ROLE_PHRASES.items():
        path = AGENTS_DIR / filename
        if not path.exists():
            errors.append(f"missing active role file: {path}")
            continue
        text = read_text(path)
        for phrase in phrases:
            require_contains(text, phrase, filename, errors)
        if "DEPRECATED_ROLE:" in text:
            errors.append(f"{filename}: active role contains deprecated redirect marker")

    for filename, redirect in DEPRECATED_ROLE_REDIRECTS.items():
        path = AGENTS_DIR / filename
        if not path.exists():
            errors.append(f"missing deprecated role file: {path}")
            continue
        text = read_text(path)
        require_contains(text, "This role is retired.", filename, errors)
        require_contains(
            text,
            "keep the substantive body limited to this redirect block.",
            filename,
            errors,
        )
        require_contains(text, redirect, filename, errors)

    deprecated_descriptions = {
        "reducer": "Deprecated redirect shim",
        "mentor": "Deprecated redirect shim",
        "locksmith": "Deprecated redirect shim",
        "applier": "Deprecated redirect shim",
    }
    for role, prefix in deprecated_descriptions.items():
        description = agent_config.get(role, {}).get("description", "")
        if not description.startswith(prefix):
            errors.append(f"config.toml: {role} description must start with '{prefix}'")

    for script_name in EXECUTABLE_SCRIPTS:
        path = SCRIPTS_DIR / script_name
        if not path.exists():
            errors.append(f"missing agent script: {path}")
            continue
        if not path.stat().st_mode & 0o111:
            errors.append(f"{path}: expected executable bit to be set")

    if errors:
        print("[FAIL] agent contract lint errors:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(f"[OK] agent contract checks passed: {AGENTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
