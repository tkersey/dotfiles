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
        [sys.executable, str(TOOLS / tool), *map(str, args)],
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
    packet = run("packet_gate.py", ASSETS / "specialist-packet.example.json")
    assert packet.returncode == 0, packet.stdout + packet.stderr

    proof_packet = run(
        "packet_gate.py", ASSETS / "proof-mapper-packet.example.json"
    )
    assert proof_packet.returncode == 0, proof_packet.stdout + proof_packet.stderr
    assert (
        json.loads(proof_packet.stdout)["packet_gate"]["worker"]
        == "codebase_doctrine_proof_mapper"
    )

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)

        bad = json.loads(
            (ASSETS / "codebase-doctrine.example.json").read_text()
        )
        bad["codebase_doctrine"]["focused_skill_candidates"][0]["candidacy"][
            "better_as_code"
        ] = "yes"
        path = temp / "bad-doctrine.json"
        path.write_text(json.dumps(bad))
        result = run("doctrine_gate.py", "--require-intent", path)
        assert result.returncode == 2
        assert "accepted-with-failed-gate" in result.stdout

        packet_bad = json.loads(
            (ASSETS / "specialist-packet.example.json").read_text()
        )
        packet_bad["codebase_doctrine_packet"]["stale"] = "yes"
        path = temp / "stale-packet.json"
        path.write_text(json.dumps(packet_bad))
        result = run("packet_gate.py", path)
        assert result.returncode == 2
        assert "stale:true" in result.stdout

        legacy = json.loads(
            (ASSETS / "proof-mapper-packet.example.json").read_text()
        )
        legacy["codebase_doctrine_packet"]["worker"] = "proof_surface_mapper"
        path = temp / "legacy-packet.json"
        path.write_text(json.dumps(legacy))
        result = run("packet_gate.py", path)
        assert result.returncode == 2
        assert (
            "worker:renamed:proof_surface_mapper"
            "->codebase_doctrine_proof_mapper"
        ) in result.stdout

        duplicate_root = temp / "agents-duplicate"
        duplicate_root.mkdir()
        write_agent(duplicate_root / "one.toml", "proof_surface_mapper")
        write_agent(duplicate_root / "two.toml", "proof_surface_mapper")
        result = run(
            "agent_identity_check.py", "--agents-root", duplicate_root
        )
        assert result.returncode == 2
        assert "duplicate:proof_surface_mapper" in result.stdout

        fixed_root = temp / "agents-fixed"
        fixed_root.mkdir()
        write_agent(fixed_root / "proof_surface_mapper.toml", "proof_surface_mapper")
        write_agent(
            fixed_root / "codebase-doctrine-proof-mapper.toml",
            "codebase_doctrine_proof_mapper",
        )
        result = run(
            "agent_identity_check.py",
            "--agents-root",
            fixed_root,
            "--require-codebase-doctrine-proof-mapper",
        )
        assert result.returncode == 0, result.stdout + result.stderr

    print("codebase-doctrine tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
