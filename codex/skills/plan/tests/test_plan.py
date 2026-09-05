"""Artifact regressions, not a claim about model effectiveness.

Run: uv run codex/skills/plan/tests/test_plan.py
Native admission tests require the installed Ledger bootstrap; they never substitute
a Python implementation for Ledger. Graph/provenance tests run without Ledger.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location("check_epg", ROOT / "scripts/check-epg.py")
assert module_spec and module_spec.loader
checker = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(checker)
EXAMPLE = ROOT / "assets/execution-policy.complex.example.json"


def load() -> dict:
    return json.loads(EXAMPLE.read_text())


class GraphTests(unittest.TestCase):
    def test_valid_example_and_exact_primary_block(self):
        block = (ROOT / "assets/human.adaptive.example.md").read_text()
        self.assertEqual(checker.check(load(), block), [])

    def test_source_digest_and_projection_mutations(self):
        data = load()
        data["execution_policy_graph"]["source"]["execution_specification"] += "different"
        self.assertTrue(any("source_digest" in x for x in checker.check(data)))
        self.assertTrue(any("differs" in x for x in checker.check(load(), "omitted source")))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"source": 1, "source": 2}', object_pairs_hook=checker.unique_object)

    def test_self_two_and_three_action_cycles(self):
        for count in (1, 2, 3):
            with self.subTest(count=count):
                data = load()
                actions = data["execution_policy_graph"]["actions"]
                for i in range(count):
                    actions[i]["requires_actions"] = [actions[(i + 1) % count]["action_id"]]
                self.assertTrue(any("cyclic" in x for x in checker.check(data)))

    def test_forward_references_in_a_dag_are_legal(self):
        data = load()
        data["execution_policy_graph"]["actions"].reverse()
        self.assertEqual(checker.check(data), [])

    def test_foreign_seam_realization_and_retirement(self):
        for field in ("realizes_factor_refs", "retires_factor_refs"):
            with self.subTest(field=field):
                data = load()
                graph = data["execution_policy_graph"]
                original = graph["architectonic"]["seams"][0]
                fid = graph["actions"][1][field][0]
                factor = next(f for f in original["factors"] if f["factor_id"] == fid)
                original["factors"].remove(factor)
                foreign = deepcopy(original)
                foreign["seam_id"] = "FOREIGN"
                foreign["factors"] = [factor]
                graph["architectonic"]["seams"].append(foreign)
                # Every seam is referenced globally, but the implementing action
                # still lacks the factor's owning seam: existence is insufficient.
                graph["actions"][0]["architectonic_seam_refs"].append("FOREIGN")
                self.assertTrue(any(field in x for x in checker.check(data)))

    def test_factor_ids_are_globally_unique(self):
        data = load()
        graph = data["execution_policy_graph"]
        foreign = deepcopy(graph["architectonic"]["seams"][0])
        foreign["seam_id"] = "FOREIGN"
        graph["architectonic"]["seams"].append(foreign)
        self.assertTrue(any("globally duplicated" in x for x in checker.check(data)))

    def test_common_final_proof_closes_both_alternative_routes(self):
        graph = load()["execution_policy_graph"]
        actions = {a["action_id"]: a for a in graph["actions"]}
        for oid in ("OBL-IMPL", "OBL-FINAL"):
            self.assertIn(oid, actions["ACTION-FINAL"]["expected_effects"]["obligations_closed"])
        common = {p["proof_id"] for p in actions["ACTION-FINAL"]["proof_obligations"]}
        for obligation in graph["goal"]["obligations"]:
            self.assertLessEqual(set(obligation["proof_refs"]), common)
        for branch in ("A", "B"):
            self.assertEqual(actions[f"ACTION-{branch}"]["expected_effects"]["obligations_closed"], [])
            self.assertIn(f"obs:OBS-{branch}=pass", actions["ACTION-FINAL"]["preconditions"]["any"])
        self.assertNotIn("spec-pipeline", EXAMPLE.read_text())

    def test_cli_reports_only_its_actual_check(self):
        result = subprocess.run([shutil.which("python3") or "python3",
                                 str(ROOT / "scripts/check-epg.py"), str(EXAMPLE)],
                                capture_output=True, text=True, check=True)
        self.assertIn("not semantic or runtime validation", result.stdout)


class NativeAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("ledger") is None:
            raise unittest.SkipTest("native Ledger unavailable; no substitute validator used")
        bootstrap = ROOT.parent / "ledger/scripts/ensure-ledger"
        subprocess.run([str(bootstrap)], check=True, capture_output=True, text=True)
        cls.definition = ROOT / "definitions/ledger/execution-policy-export.json"
        result = subprocess.run(["ledger", "definition", "check", "--definition",
                                 str(cls.definition), "--format", "json"],
                                check=True, capture_output=True, text=True)
        if json.loads(result.stdout).get("valid") is not True:
            raise AssertionError("native definition check did not validate the export definition")

    def validate(self, data, valid):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps(data, indent=2) + "\n")
            result = subprocess.run(["ledger", "validate", "--definition", str(self.definition),
                                     "--input", f"policy={path}", "--format", "json"],
                                    capture_output=True, text=True)
            envelope = json.loads(result.stdout)
            self.assertEqual(envelope["schema"], "ledger-validation-result/v1")
            self.assertIs(envelope["valid"], valid, result.stdout + result.stderr)
            self.assertEqual(result.returncode == 0, valid)

    def test_new_export_valid(self):
        self.validate(load(), True)

    def test_missing_owner_boundary_lock_rollback_or_source(self):
        for field in ("owner", "mutation_boundary", "lock_roots", "rollback"):
            with self.subTest(field=field):
                data = load()
                del data["execution_policy_graph"]["actions"][1][field]
                self.validate(data, False)
        data = load()
        del data["execution_policy_graph"]["source"]["execution_specification"]
        self.validate(data, False)

    def test_empty_paths_locks_and_retirement(self):
        for field in ("paths", "locks", "retirement"):
            with self.subTest(field=field):
                data = load()
                actions = data["execution_policy_graph"]["actions"]
                if field == "paths":
                    actions[1]["mutation_boundary"]["paths"] = []
                elif field == "locks":
                    actions[1]["lock_roots"] = []
                else:
                    for action in actions:
                        action["retires_factor_refs"] = []
                self.validate(data, False)

    def test_probe_label_does_not_hide_repository_effects(self):
        data = load()
        action = data["execution_policy_graph"]["actions"][1]
        action["kind"] = "probe"
        del action["rollback"]
        self.validate(data, False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
