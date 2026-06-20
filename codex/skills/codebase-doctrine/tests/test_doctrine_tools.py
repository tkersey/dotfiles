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


def main() -> int:
    packet = run("packet_gate.py", str(ASSETS / "specialist-packet.example.json"))
    assert packet.returncode == 0, packet.stdout + packet.stderr
    packet_result = json.loads(packet.stdout)["packet_gate"]
    assert packet_result["verdict"] == "pass"

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
        bad_path = Path(td) / "bad.json"
        bad = json.loads(
            (ASSETS / "codebase-doctrine.example.json").read_text(encoding="utf-8")
        )
        candidate = bad["codebase_doctrine"]["focused_skill_candidates"][0]
        candidate["candidacy"]["better_as_code"] = "yes"
        bad_path.write_text(json.dumps(bad), encoding="utf-8")
        failed = run("doctrine_gate.py", str(bad_path))
        assert failed.returncode == 2
        assert "accepted-with-failed-gate" in failed.stdout

        packet_bad_path = Path(td) / "packet-bad.json"
        packet_bad = json.loads(
            (ASSETS / "specialist-packet.example.json").read_text(encoding="utf-8")
        )
        packet_bad["codebase_doctrine_packet"]["stale"] = "yes"
        packet_bad_path.write_text(json.dumps(packet_bad), encoding="utf-8")
        failed_packet = run("packet_gate.py", str(packet_bad_path))
        assert failed_packet.returncode == 2
        assert "stale:true" in failed_packet.stdout

    print("codebase-doctrine tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
