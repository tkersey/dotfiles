#!/usr/bin/env python3
"""Validate proof_dag / PDAG-v1."""

from __future__ import annotations

import argparse
import json

from common import load_document, require_list, require_object, unwrap, yes, no

KINDS = {"focused", "wave", "final"}
STATES = {"missing", "running", "pass", "fail", "stale", "blocked"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        body = unwrap(load_document(args.file), "proof_dag")
    except Exception as exc:
        body = {}
        errors.append(str(exc))

    if body.get("dag_version") != "PDAG-v1":
        errors.append("dag_version")
    if not body.get("dag_id"):
        errors.append("dag_id")
    require_object(body, "artifact_state", errors)

    nodes = require_list(body, "nodes", errors)
    by_id: dict[str, dict] = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"nodes[{index}]")
            continue
        pid = node.get("proof_id")
        if not pid:
            errors.append(f"nodes[{index}].proof_id")
            continue
        if pid in by_id:
            errors.append(f"nodes:duplicate:{pid}")
        by_id[pid] = node
        if node.get("kind") not in KINDS:
            errors.append(f"nodes[{index}].kind")
        if not node.get("command"):
            errors.append(f"nodes[{index}].command")
        covers = require_object(node, "covers", errors)
        total_coverage = 0
        for key in ("st_obligations", "matrix_rows", "files", "semantic_laws"):
            values = require_list(covers, key, errors)
            total_coverage += len(values)
        if total_coverage == 0:
            errors.append(f"nodes[{index}].covers:empty")
        require_list(node, "depends_on", errors)
        if node.get("state") not in STATES:
            errors.append(f"nodes[{index}].state")
        require_list(node, "invalidators", errors)
        if node.get("state") == "pass" and not node.get("epoch_ref"):
            warnings.append(f"nodes[{index}].epoch_ref:missing-for-pass")
        if node.get("state") == "pass" and not node.get("evidence_ref"):
            errors.append(f"nodes[{index}].evidence_ref:missing-for-pass")

    for pid, node in by_id.items():
        for dep in node.get("depends_on", []):
            if dep not in by_id:
                errors.append(f"nodes.{pid}:unknown-dependency:{dep}")
        if node.get("state") == "pass":
            bad = [
                dep for dep in node.get("depends_on", [])
                if dep in by_id and by_id[dep].get("state") != "pass"
            ]
            if bad:
                errors.append(f"nodes.{pid}:pass-with-nonpass-dependencies:{','.join(bad)}")

    # Cycle detection.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(pid: str) -> None:
        if pid in visited:
            return
        if pid in visiting:
            errors.append(f"cycle:{pid}")
            return
        visiting.add(pid)
        for dep in by_id.get(pid, {}).get("depends_on", []):
            if dep in by_id:
                visit(dep)
        visiting.remove(pid)
        visited.add(pid)

    for pid in by_id:
        visit(pid)

    gates = require_object(body, "gates", errors)
    for gate_name in ("focused", "wave", "final"):
        gate = require_object(gates, gate_name, errors)
        required = require_list(gate, "required_nodes", errors)
        if not (yes(gate.get("pass")) or no(gate.get("pass"))):
            errors.append(f"gates.{gate_name}.pass")
        for pid in required:
            if pid not in by_id:
                errors.append(f"gates.{gate_name}:unknown-node:{pid}")
        actual = bool(required) and all(
            pid in by_id and by_id[pid].get("state") == "pass" for pid in required
        )
        if yes(gate.get("pass")) and not actual:
            errors.append(f"gates.{gate_name}:pass-contradicted")
        if no(gate.get("pass")) and actual:
            warnings.append(f"gates.{gate_name}:could-pass")

    result = {
        "proof_dag_gate": {
            "verdict": "pass" if not errors else "fail",
            "dag_id": body.get("dag_id"),
            "node_count": len(by_id),
            "errors": errors,
            "warnings": warnings,
        }
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
