#!/usr/bin/env python3
"""Persist and resume validated ASL-v1 control state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from common import load_document, unwrap
from actuation_slice_gate import validate_slice


def now_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def digest(value: dict[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def git_head(repo: Path) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def write_slice(args: argparse.Namespace) -> int:
    body = unwrap(load_document(args.input), "actuation_slice")
    errors, warnings = validate_slice(body)
    if errors:
        print(json.dumps({
            "actuation_checkpoint": {
                "verdict": "fail",
                "operation": "write",
                "errors": errors,
                "warnings": warnings,
            }
        }, indent=2, sort_keys=True))
        return 2

    root = Path(args.root).expanduser().resolve()
    run_dir = root / body["run_id"]
    history = run_dir / "history" / f"{now_slug()}-{body['slice_id']}.json"
    wrapper = {
        "checkpoint_version": "ACP-v1",
        "checkpoint_digest": digest(body),
        "written_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "actuation_slice": body,
    }
    atomic_json(history, wrapper)
    atomic_json(run_dir / "current.json", wrapper)

    print(json.dumps({
        "actuation_checkpoint": {
            "verdict": "pass",
            "operation": "write",
            "run_id": body["run_id"],
            "slice_id": body["slice_id"],
            "state": body["state"],
            "current_ref": str(run_dir / "current.json"),
            "history_ref": str(history),
            "checkpoint_digest": wrapper["checkpoint_digest"],
            "warnings": warnings,
        }
    }, indent=2, sort_keys=True))
    return 0


def load_current(root: Path, run_id: str) -> tuple[dict[str, Any], Path]:
    path = root / run_id / "current.json"
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    body = wrapper.get("actuation_slice")
    if not isinstance(body, dict):
        raise ValueError("current checkpoint has no actuation_slice")
    return body, path


def resume(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    try:
        body, path = load_current(root, args.run_id)
        errors, warnings = validate_slice(body)
    except Exception as exc:
        print(json.dumps({
            "actuation_resume_packet": {
                "verdict": "fail",
                "run_id": args.run_id,
                "errors": [str(exc)],
            }
        }, indent=2, sort_keys=True))
        return 2

    stale_reasons: list[str] = []
    if args.repo:
        observed = git_head(Path(args.repo).expanduser().resolve())
        expected = body.get("artifact_state", {}).get("head")
        if observed and expected and observed != expected:
            stale_reasons.append(f"head:{expected}->{observed}")

    task = body.get("task_control", {})
    semantic = body.get("semantic_control", {})
    decision = body.get("decision", {})
    proof = body.get("proof", {})
    packet = {
        "actuation_resume_packet": {
            "packet_version": "ARP-v1",
            "verdict": "pass" if not errors and not stale_reasons else "stale",
            "run_id": body.get("run_id"),
            "slice_id": body.get("slice_id"),
            "state": body.get("state"),
            "checkpoint_ref": str(path),
            "artifact_state": body.get("artifact_state"),
            "graph_control": {
                "authority_id": task.get("authority_id"),
                "authority_ref": task.get("authority_ref"),
                "authority_seq": task.get("authority_seq"),
                "authority_current": task.get("authority_current"),
                "execution_allowed": task.get("execution_allowed"),
                "selected_task_ids": task.get("selected_task_ids", []),
            },
            "semantic_frontier": {
                "owner": semantic.get("owner"),
                "invariant": semantic.get("invariant"),
                "matrix_ref": semantic.get("matrix_ref"),
                "selected_rows": semantic.get("selected_rows", []),
                "open_rows": semantic.get("open_rows", []),
                "new_observations": semantic.get("new_observations", []),
            },
            "decision": {
                "selected_route": decision.get("selected_route"),
                "selected_normal_form": decision.get("selected_normal_form"),
                "patch_boundary": decision.get("patch_boundary"),
                "forbidden_actions": decision.get("forbidden_actions", []),
            },
            "proof": {
                "proof_dag_ref": proof.get("proof_dag_ref"),
                "focused_gate": proof.get("focused_gate"),
                "wave_gate": proof.get("wave_gate"),
                "final_gate": proof.get("final_gate"),
            },
            "active_skill_contracts": body.get("active_skill_contracts", []),
            "next_frontier": body.get("next_frontier"),
            "stale_reasons": stale_reasons,
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0 if packet["actuation_resume_packet"]["verdict"] == "pass" else 2


def check(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    try:
        body, path = load_current(root, args.run_id)
        errors, warnings = validate_slice(body)
    except Exception as exc:
        errors, warnings, path, body = [str(exc)], [], root / args.run_id / "current.json", {}
    print(json.dumps({
        "actuation_checkpoint": {
            "verdict": "pass" if not errors else "fail",
            "operation": "check",
            "run_id": args.run_id,
            "slice_id": body.get("slice_id"),
            "current_ref": str(path),
            "errors": errors,
            "warnings": warnings,
        }
    }, indent=2, sort_keys=True))
    return 0 if not errors else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_write = sub.add_parser("write")
    p_write.add_argument("--input", required=True)
    p_write.add_argument("--root", default=".ledger/actuating")
    p_write.set_defaults(func=write_slice)

    p_resume = sub.add_parser("resume")
    p_resume.add_argument("--root", default=".ledger/actuating")
    p_resume.add_argument("--run-id", required=True)
    p_resume.add_argument("--repo")
    p_resume.set_defaults(func=resume)

    p_check = sub.add_parser("check")
    p_check.add_argument("--root", default=".ledger/actuating")
    p_check.add_argument("--run-id", required=True)
    p_check.set_defaults(func=check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
