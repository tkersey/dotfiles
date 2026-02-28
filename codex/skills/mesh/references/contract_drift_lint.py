#!/usr/bin/env -S uv run python
"""Dual-author contract drift lint for mesh/reducer docs and prompts."""

from __future__ import annotations

from pathlib import Path


REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "codex/AGENTS.md": [
        "`coder + reducer -> fixer -> integrator`",
        "`coder x2`, `reducer x1`, `fixer x3`, `integrator x3`",
    ],
    "codex/skills/mesh/SKILL.md": [
        "`coder + reducer -> fixer -> integrator`",
        "`coder x2`, `reducer x1`, `fixer x3`, and `integrator x3`",
    ],
    "codex/skills/mesh/agents/openai.yaml": [
        "coder x2 + reducer x1",
    ],
    "codex/skills/mesh/references/output-contract.md": [
        "Reducer lane (propose abstraction cut, no proof):",
        "`reduce_record`",
    ],
    "codex/agents/reducer.toml": [
        "Invoke `$reduce` first",
        "`target_abstraction`",
    ],
    "codex/agents/fixer.toml": [
        "Deterministically adjudicate coder/reducer candidates",
        "Selected candidate:",
    ],
    "codex/config.toml": [
        "Run `$reduce` to cut high-cost abstractions",
    ],
}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[4]
    missing: list[str] = []

    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        file_path = repo_root / relative_path
        if not file_path.exists():
            missing.append(f"{relative_path}: file missing")
            continue

        content = file_path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in content:
                missing.append(f"{relative_path}: missing snippet -> {snippet}")

    if missing:
        print("contract_drift_lint: FAIL")
        for item in missing:
            print(f"- {item}")
        return 1

    print("contract_drift_lint: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
