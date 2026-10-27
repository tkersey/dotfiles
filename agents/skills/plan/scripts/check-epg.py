#!/usr/bin/env python3
"""Check export provenance and graph relations not covered by the legacy ABI.

Run after native Ledger validation. This reads a bounded artifact only; it does not
replace Ledger shape validation, execute actions, or prove semantic completeness.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import sys

MAX_BYTES = 16 * 1024 * 1024


def check(document: dict, specification: str | None = None) -> list[str]:
    """Return graph/provenance defects in a natively shape-validated EPG."""
    graph = document["execution_policy_graph"]
    errors: list[str] = []
    source = graph["source"]
    text = source["execution_specification"]
    if not isinstance(text, str):
        raise ValueError("embedded execution specification must be text")
    if not text.startswith("<proposed_plan>\n") or not text.endswith("</proposed_plan>\n"):
        errors.append("embedded source must be the complete proposed_plan block with a trailing newline")
    if text.count("<proposed_plan>") != 1 or text.count("</proposed_plan>") != 1:
        errors.append("embedded source must contain exactly one proposed_plan block")
    digest = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
    if source["source_digest"] != digest:
        errors.append("source_digest does not bind the exact embedded specification bytes")
    if specification is not None and text != specification:
        errors.append("exported specification differs from the supplied primary block")

    actions = graph["actions"]
    by_id = {action["action_id"]: action for action in actions}
    if len(by_id) != len(actions):
        errors.append("duplicate action IDs")
    indegree = dict.fromkeys(by_id, 0)
    successors: dict[str, list[str]] = {key: [] for key in by_id}
    for action in actions:
        aid = action["action_id"]
        for dependency in set(action["requires_actions"]):
            if dependency not in by_id:
                errors.append(f"{aid}: unknown prerequisite {dependency}")
                continue
            successors[dependency].append(aid)
            indegree[aid] += 1
    ready = deque(key for key, count in indegree.items() if count == 0)
    visited = 0
    while ready:
        aid = ready.popleft()
        visited += 1
        for successor in successors[aid]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    if visited != len(by_id):
        errors.append("cyclic action prerequisites; model recurrence as an observed branch instead")

    factor_seams: dict[str, str] = {}
    for seam in graph["architectonic"]["seams"]:
        for factor in seam["factors"]:
            fid = factor["factor_id"]
            if fid in factor_seams:
                errors.append(f"globally duplicated factor ID: {fid}")
            factor_seams[fid] = seam["seam_id"]
    for action in actions:
        seams = set(action.get("architectonic_seam_refs", []))
        for field in ("realizes_factor_refs", "retires_factor_refs"):
            for fid in action.get(field, []):
                owner = factor_seams.get(fid)
                if owner is None or owner not in seams:
                    errors.append(f"{action['action_id']}: {field} {fid} lacks its owning seam")
    return errors


def read_text(path: Path) -> str:
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"{path}: exceeds {MAX_BYTES}-byte input limit")
    return data.decode("utf-8")


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", type=Path)
    parser.add_argument("--specification", type=Path,
                        help="exact primary proposed_plan block, without status/export metadata")
    args = parser.parse_args()
    try:
        document = json.loads(read_text(args.policy), object_pairs_hook=unique_object)
        specification = read_text(args.specification) if args.specification else None
        errors = check(document, specification)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as error:
        print(f"EPG graph check failed: {error}. Native Ledger validation is required first.", file=sys.stderr)
        return 2
    if errors:
        for error in errors[:256]:
            print(error, file=sys.stderr)
        return 1
    print("EPG provenance and graph relations checked; not semantic or runtime validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
