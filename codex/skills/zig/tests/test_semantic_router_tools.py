#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(cwd: Path, tool: str, *args: str, env: dict[str, str] | None = None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / tool), *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )


def git(cwd: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)


def init_repo(root: Path) -> None:
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Test")


def test_route_gate(tmp: Path) -> None:
    route = {
        "zig_semantic_route": {
            "route_version": "ZSR-v1",
            "artifact_state": {
                "repository_root": str(tmp),
                "head": "abc",
                "dirty_fingerprint": "sha256:abc",
                "zig_version": "0.16.0",
            },
            "task_surfaces": ["allocator/ownership/lifetime"],
            "material": "yes",
            "active_families": ["lifetime-escape"],
            "no_family_reason": "",
            "owner": "ParsedResult",
            "concrete_counterexample": "returned run_id outlives parse arena",
            "selected_repair_boundary": "duplicate into returned owner",
            "forbidden_shortcuts": ["document dangling borrow"],
            "required_proof": ["escape table", "lifetime regression"],
            "proof_epoch_required": "yes",
            "family_contracts": {
                "lifetime-escape": {
                    "question": "Who owns each escaping slice?",
                    "proof": ["escape table", "deinit regression"],
                }
            },
            "gate": {
                "classified_before_first_edit": "yes",
                "mutation_allowed": "yes",
            },
        }
    }
    path = tmp / "route.json"
    path.write_text(json.dumps(route), encoding="utf-8")
    result = run(tmp, "zig_semantic_route_gate.py", str(path))
    assert result.returncode == 0, result.stdout + result.stderr

    route["zig_semantic_route"]["family_contracts"] = {}
    path.write_text(json.dumps(route), encoding="utf-8")
    failed = run(tmp, "zig_semantic_route_gate.py", str(path))
    assert failed.returncode == 2
    assert "family_contracts.lifetime-escape:missing" in failed.stdout


def test_repo_closure(tmp: Path) -> None:
    repo = tmp / "closure"
    repo.mkdir()
    init_repo(repo)
    (repo / "src").mkdir()
    (repo / "src" / "a.zig").write_text("pub fn a() void {}\n", encoding="utf-8")
    (repo / "repo_zig_paths.txt").write_text("src/a.zig\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")

    (repo / "src" / "b.zig").write_text("pub fn b() void {}\n", encoding="utf-8")
    failed = run(
        repo,
        "zig_repo_closure_scan.py",
        "--root",
        ".",
        "--strict",
    )
    assert failed.returncode == 2, failed.stdout + failed.stderr
    payload = json.loads(failed.stdout)["zig_repo_closure_scan"]
    assert "src/b.zig" in payload["likely_unregistered_paths"]

    (repo / "repo_zig_paths.txt").write_text("src/a.zig\nsrc/b.zig\n", encoding="utf-8")
    passed = run(
        repo,
        "zig_repo_closure_scan.py",
        "--root",
        ".",
        "--strict",
    )
    assert passed.returncode == 0, passed.stdout + passed.stderr
    payload = json.loads(passed.stdout)["zig_repo_closure_scan"]
    assert "src/b.zig" not in payload["likely_unregistered_paths"]


def test_proof_epoch(tmp: Path) -> None:
    repo = tmp / "epoch"
    repo.mkdir()
    init_repo(repo)
    (repo / "x.txt").write_text("one\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")

    fake_bin = tmp / "bin"
    fake_bin.mkdir()
    zig = fake_bin / "zig"
    zig.write_text("#!/bin/sh\nif [ \"$1\" = version ]; then echo 0.16.0; exit 0; fi\nexit 0\n", encoding="utf-8")
    zig.chmod(0o755)
    env = dict(os.environ)
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")

    epoch = repo / "epoch.json"
    result = run(
        repo,
        "zig_proof_epoch.py",
        "run",
        "--output",
        str(epoch),
        "--",
        sys.executable,
        "-c",
        "print('proof')",
        env=env,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    check = run(
        repo,
        "zig_proof_epoch.py",
        "check",
        "--epoch",
        str(epoch),
        env=env,
    )
    assert check.returncode == 0, check.stdout + check.stderr

    (repo / "x.txt").write_text("two\n", encoding="utf-8")
    stale = run(
        repo,
        "zig_proof_epoch.py",
        "check",
        "--epoch",
        str(epoch),
        env=env,
    )
    assert stale.returncode == 2
    assert "tree-changed" in stale.stdout


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        test_route_gate(tmp)
        test_repo_closure(tmp)
        test_proof_epoch(tmp)
    print("zig semantic router tools: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
