#!/usr/bin/env -S uv run --with pyyaml python
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ASSETS = ROOT / "assets"
EVALS = ROOT / "evals"
sys.path.insert(0, str(TOOLS))

import doctrine_diff
import doctrine_gate


def set_path(value, path: str, replacement) -> None:
    current = value
    parts = path.split(".")
    for part in parts[:-1]:
        current = current[int(part)] if isinstance(current, list) else current[part]
    last = parts[-1]
    if isinstance(current, list):
        current[int(last)] = replacement
    else:
        current[last] = replacement


class DoctrineToolsTests(unittest.TestCase):
    def load_yaml(self, name: str):
        return yaml.safe_load((ASSETS / name).read_text(encoding="utf-8"))

    def test_example_is_closed_and_saturated(self) -> None:
        errors, warnings, counts = doctrine_gate.validate_value(
            self.load_yaml("codebase-doctrine.example.yaml"),
            require_saturated=True,
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(counts["active_root_skills"], 0)
        self.assertEqual(counts["active_focused_skills"], 1)

    def test_graph_integrity_corpus(self) -> None:
        corpus = json.loads((EVALS / "graph-integrity-cases.json").read_text())
        base = self.load_yaml("codebase-doctrine.example.yaml")
        for case in corpus["cases"]:
            with self.subTest(case=case["id"]):
                mutated = copy.deepcopy(base)
                set_path(mutated, case["path"], case["value"])
                errors, _warnings, _counts = doctrine_gate.validate_value(mutated)
                self.assertTrue(
                    any(case["expected_error"] in item for item in errors),
                    f"{case['id']}: {errors}",
                )

    def test_zero_skills_is_valid(self) -> None:
        value = self.load_yaml("codebase-doctrine.example.yaml")
        body = value["codebase_doctrine"]
        body["focused_skill_candidates"] = []
        body["rejected_skill_candidates"] = []
        body["knowledge_routes"][1]["secondary_destinations"] = []
        errors, _warnings, _counts = doctrine_gate.validate_value(value)
        self.assertEqual(errors, [])

    def test_current_and_target_status_are_required(self) -> None:
        value = self.load_yaml("codebase-doctrine.example.yaml")
        law = value["codebase_doctrine"]["governing_laws"][0]
        del law["doctrine_status"]
        errors, _warnings, _counts = doctrine_gate.validate_value(value)
        self.assertTrue(any("doctrine_status" in item for item in errors))

    def test_negative_route_must_be_canonical_before_prohibition(self) -> None:
        value = self.load_yaml("codebase-doctrine.example.yaml")
        value["codebase_doctrine"]["negative_routes"][0]["status"] = "witnessed"
        errors, _warnings, _counts = doctrine_gate.validate_value(value)
        self.assertTrue(any("prohibited_route_ids:unknown" in item for item in errors))

    def test_delta_partitions_are_disjoint(self) -> None:
        prior = self.load_yaml("codebase-doctrine.example.yaml")
        new = self.load_yaml("codebase-doctrine.refreshed.example.yaml")
        delta = doctrine_diff.compile_delta(prior, new, ["src/store.zig"])
        body = delta["codebase_doctrine_delta"]
        sets = [
            set(body["invalidated_ids"]),
            set(body["retained_ids"]),
            set(body["added_ids"]),
            set(body["modified_ids"]),
        ]
        for i, left in enumerate(sets):
            for right in sets[i + 1 :]:
                self.assertFalse(left & right)


if __name__ == "__main__":
    unittest.main()
