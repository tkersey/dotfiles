#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"


def run(tool: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / tool), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def write_agent(path: Path, name: str) -> None:
    path.write_text(
        f'name = "{name}"\n'
        'description = "fixture"\n'
        'sandbox_mode = "read-only"\n',
        encoding="utf-8",
    )


def main() -> int:
    # Existing general packet still passes.
    packet = run("packet_gate.py", str(ASSETS / "specialist-packet.example.json"))
    assert packet.returncode == 0, packet.stdout + packet.stderr
    packet_result = json.loads(packet.stdout)["packet_gate"]
    assert packet_result["verdict"] == "pass"

    # The workflow-scoped proof worker passes.
    proof_packet = run(
        "packet_gate.py",
        str(ASSETS / "proof-mapper-packet.example.json"),
    )
    assert proof_packet.returncode == 0, proof_packet.stdout + proof_packet.stderr
    proof_result = json.loads(proof_packet.stdout)["packet_gate"]
    assert proof_result["worker"] == "codebase_doctrine_proof_mapper"

    doctrine = run(
        "doctrine_gate.py",
        "--require-saturated",
        str(ASSETS / "codebase-doctrine.example.json"),
    )
    assert doctrine.returncode == 0, doctrine.stdout + doctrine.stderr
    result = json.loads(doctrine.stdout)["doctrine_gate"]
    assert result["verdict"] == "pass"
    assert result["counts"]["accepted_focused_skills"] == 1

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        bad_path = temp / "bad.json"
        bad = json.loads(
            (ASSETS / "codebase-doctrine.example.json").read_text(encoding="utf-8")
        )
        candidate = bad["codebase_doctrine"]["focused_skill_candidates"][0]
        candidate["candidacy"]["better_as_code"] = "yes"
        bad_path.write_text(json.dumps(bad), encoding="utf-8")
        failed = run("doctrine_gate.py", str(bad_path))
        assert failed.returncode == 2
        assert "accepted-with-failed-gate" in failed.stdout

        packet_bad_path = temp / "packet-bad.json"
        packet_bad = json.loads(
            (ASSETS / "specialist-packet.example.json").read_text(encoding="utf-8")
        )
        packet_bad["codebase_doctrine_packet"]["stale"] = "yes"
        packet_bad_path.write_text(json.dumps(packet_bad), encoding="utf-8")
        failed_packet = run("packet_gate.py", str(packet_bad_path))
        assert failed_packet.returncode == 2
        assert "stale:true" in failed_packet.stdout

        # The old generic identity is rejected for Codebase Doctrine packets
        # with a precise migration diagnostic.
        legacy_path = temp / "legacy-proof-packet.json"
        legacy = json.loads(
            (ASSETS / "proof-mapper-packet.example.json").read_text(encoding="utf-8")
        )
        legacy["codebase_doctrine_packet"]["worker"] = "proof_surface_mapper"
        legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
        legacy_result = run("packet_gate.py", str(legacy_path))
        assert legacy_result.returncode == 2
        assert (
            "worker:renamed:proof_surface_mapper"
            "->codebase_doctrine_proof_mapper"
        ) in legacy_result.stdout

        # Duplicate global agent identities fail.
        duplicate_root = temp / "agents-duplicate"
        duplicate_root.mkdir()
        write_agent(duplicate_root / "proof_surface_mapper.toml", "proof_surface_mapper")
        write_agent(duplicate_root / "proof-surface-mapper.toml", "proof_surface_mapper")
        duplicate = run(
            "agent_identity_check.py",
            "--agents-root",
            str(duplicate_root),
        )
        assert duplicate.returncode == 2
        assert "duplicate:proof_surface_mapper" in duplicate.stdout

        # The manually corrected identity passes and coexists with the
        # existing general-purpose proof_surface_mapper.
        fixed_root = temp / "agents-fixed"
        fixed_root.mkdir()
        write_agent(fixed_root / "proof_surface_mapper.toml", "proof_surface_mapper")
        write_agent(
            fixed_root / "codebase-doctrine-proof-mapper.toml",
            "codebase_doctrine_proof_mapper",
        )
        fixed = run(
            "agent_identity_check.py",
            "--agents-root",
            str(fixed_root),
            "--require-codebase-doctrine-proof-mapper",
        )
        assert fixed.returncode == 0, fixed.stdout + fixed.stderr
        fixed_result = json.loads(fixed.stdout)["agent_identity_check"]
        assert fixed_result["verdict"] == "pass"
        assert fixed_result["codebase_doctrine_proof_mapper"] == "present"

    print("codebase-doctrine tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
