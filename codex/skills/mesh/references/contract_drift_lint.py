#!/usr/bin/env -S uv run python
"""Streaming mesh contract drift lint."""

from __future__ import annotations

from pathlib import Path


REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "codex/AGENTS.md": [
        "streaming per-unit state machine",
        "write_scope reservations",
        "locksmith -> applier -> prover",
        "Lane completeness gate (default)",
        "Collapse override gate",
    ],
    "codex/skills/mesh/SKILL.md": [
        "streaming per-unit state machine",
        "no global wave barrier",
        "locksmith -> applier -> prover",
        "Compliance Guardrails (Fail-Closed)",
        "Anti-pattern gate: a coder-only wave",
        "lane_completeness_lint.py",
    ],
    "codex/skills/mesh/agents/openai.yaml": [
        "Streaming orchestration",
        "coder x2 + reducer x1",
        "Fail closed",
    ],
    "codex/skills/mesh/references/output-contract.md": [
        "Mesh Output Contract v2 (Streaming)",
        "write_scope",
        "proof_evidence",
        "Run-Level Invariants (Fail-Closed)",
        "Do not claim `$mesh` orchestration",
    ],
    "codex/skills/mesh/references/lane_completeness_lint.py": [
        "lane_completeness_lint:",
        "coder-only",
    ],
    "codex/agents/coder.toml": [
        "Do not run proof in the coder lane",
        "write_scope",
    ],
    "codex/agents/integrator.toml": [
        "Default mode is `patch_first`",
        "git am",
    ],
    "codex/config.toml": [
        "[agents.locksmith]",
        "[agents.applier]",
        "[agents.prover]",
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
