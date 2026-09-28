#!/usr/bin/env python3
"""Freeze installed Elenctic policy and semantic lens projections into private scratch."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from typing import Any

SCHEMA = "elenctic-policy/v1"
OUTPUT_BOUNDARY = "\n## Native output (Actuating only)\n"


def sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"unsafe policy path: {value!r}")
    return str(path)


def runtime_paths(root: Path) -> list[str]:
    package = root / "elenctic"
    paths = ["elenctic/SKILL.md"]
    for folder in ("references", "agents", "scripts", "assets"):
        paths += [p.relative_to(root).as_posix() for p in (package / folder).rglob("*")
                  if p.is_file() and p.suffix in {".md", ".yaml", ".json", ".py", ".html"}]
    return sorted(set(paths))


def capture(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Read and recheck one source set before publishing; no subject-repo discovery."""
    manifest_path = "actuating/references/review-contract.json"
    inputs = {p: (root / p).read_bytes() for p in runtime_paths(root)}
    required = {"elenctic/SKILL.md", "elenctic/references/worker-review.md", "elenctic/references/campaign.md"}
    if not required.issubset(inputs):
        raise ValueError("installed Elenctic contracts are incomplete")
    inputs[manifest_path] = (root / manifest_path).read_bytes()
    contract = json.loads(inputs[manifest_path])
    lenses = [item for item in contract["required_lenses"] if item["role"] == "auxiliary"]
    if not lenses:
        raise ValueError("no auxiliary review questions in the installed contract")
    files = dict(inputs)
    selected = []
    names = set()
    for lens in lenses:
        name = lens["name"]
        if not isinstance(name, str) or name in names:
            raise ValueError("auxiliary lens names must be unique strings")
        names.add(name)
        ref = lens["instructions_ref"]
        if not isinstance(ref, str) or not ref.startswith("codex/skills/"):
            raise ValueError("lens source must be an installed codex/skills reference")
        path = relative(ref.removeprefix("codex/skills/"))
        raw = (root / path).read_bytes()
        if path in inputs and inputs[path] != raw:
            raise ValueError("source changed during policy capture")
        inputs[path] = raw
        body = raw.decode("utf-8")
        if body.count(OUTPUT_BOUNDARY) != 1:
            raise ValueError(f"{path}: expected one explicit semantic/output boundary")
        questions = body.split(OUTPUT_BOUNDARY, 1)[0].rstrip() + "\n"
        if not questions.strip():
            raise ValueError(f"{path}: empty semantic questions")
        files[path] = questions.encode("utf-8")
        selected.append({"name": name, "path": path})
    if runtime_paths(root) != sorted(p for p in inputs if p.startswith("elenctic/")):
        raise ValueError("installed package inventory changed during policy capture")
    for path, raw in inputs.items():
        if (root / path).read_bytes() != raw:
            raise ValueError(f"{path}: source changed during policy capture; retry after installation settles")
    entries = [{"path": p, "source_sha256": sha(inputs[p]), "snapshot_sha256": sha(files[p])}
               for p in sorted(files)]
    body = {"schema": SCHEMA, "files": entries, "lenses": selected}
    return files, {**body, "policy_id": sha(encoded(body))}


def freeze(root: Path, destination: Path | None = None) -> tuple[Path, str]:
    files, manifest = capture(root.absolute())
    if destination is not None:
        destination = destination.absolute()
        if destination.exists() or destination.is_symlink():
            raise ValueError("policy destination must not exist; snapshots are never overwritten")
        destination.mkdir(mode=0o700)
    else:
        destination = Path(tempfile.mkdtemp(prefix="elenctic-policy-"))
    try:
        for name, content in files.items():
            path = destination / relative(name)
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(0o400)
        manifest_path = destination / "policy.json"
        manifest_path.write_bytes(encoded(manifest) + b"\n")
        manifest_path.chmod(0o400)
        verify(destination, manifest["policy_id"])
    except Exception:
        shutil.rmtree(destination)
        raise
    return destination, manifest["policy_id"]


def verify(root: Path, expected: str) -> dict[str, Any]:
    """Validate against the externally bound identity, not merely a self-reported hash."""
    manifest_path = root / "policy.json"
    if manifest_path.is_symlink():
        raise ValueError("policy manifest must not be a symlink")
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("schema") != SCHEMA or manifest.get("policy_id") != expected:
        raise ValueError("wrong policy identity")
    body = {k: v for k, v in manifest.items() if k != "policy_id"}
    if sha(encoded(body)) != expected:
        raise ValueError("policy manifest content differs from the bound identity")
    paths = set()
    for entry in manifest["files"]:
        name = relative(entry["path"])
        if name in paths:
            raise ValueError("duplicate snapshot path")
        paths.add(name)
        path = root / name
        parts = PurePosixPath(name).parts
        if any(root.joinpath(*parts[:i]).is_symlink() for i in range(1, len(parts) + 1)):
            raise ValueError("snapshot paths must not traverse symlinks")
        if sha(path.read_bytes()) != entry["snapshot_sha256"]:
            raise ValueError(f"{name}: frozen policy bytes changed")
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and p != manifest_path and "__pycache__" not in p.parts}
    if actual != paths:
        raise ValueError("snapshot inventory differs from the bound policy")
    if any(lens["path"] not in paths for lens in manifest["lenses"]):
        raise ValueError("a required lens is absent from the snapshot")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--skills-root", required=True, type=Path)
    create.add_argument("--output", type=Path)
    check = commands.add_parser("verify")
    check.add_argument("--root", required=True, type=Path)
    check.add_argument("--policy-id", required=True)
    args = parser.parse_args()
    try:
        if args.command == "create":
            root, policy_id = freeze(args.skills_root, args.output)
        else:
            root, policy_id = args.root.absolute(), args.policy_id
            verify(root, policy_id)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"elenctic policy: {error}\n")
    print(json.dumps({"policy_root": str(root), "policy_id": policy_id, "verified": True}))


if __name__ == "__main__":
    main()
