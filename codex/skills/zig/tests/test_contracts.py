"""Structural integrity and runner classification, not model-efficacy tests."""
import json
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest
from test_tools import Fixture
from toolchain import ZIG_VERSION

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def test_decision_contract_references_are_closed_and_unique(self):
        contract = json.loads((ROOT / "references" / "decision-contract.json").read_text())["skill_decision_contract"]
        triggers = [t["trigger_id"] for t in contract["triggers"]]
        routes = [r["route_id"] for r in contract["routes"]]
        clauses = [c["clause_id"] for c in contract["clauses"]]
        for names in (triggers, routes, clauses):
            self.assertEqual(len(names), len(set(names)))
        for clause in contract["clauses"]:
            self.assertTrue(set(clause["trigger_refs"]) <= set(triggers))
            self.assertTrue(set(clause["expected_routes"] + clause["prohibited_routes"]) <= set(routes))
            self.assertFalse(set(clause["expected_routes"]) & set(clause["prohibited_routes"]))

    def test_constructive_and_narrow_work_do_not_require_packets(self):
        contract = json.loads((ROOT / "references" / "decision-contract.json").read_text())["skill_decision_contract"]
        self.assertEqual(contract["instrumentation"]["decision_receipt"], "optional")
        for clause in contract["clauses"]:
            self.assertEqual(clause["required_artifacts"], [], clause["clause_id"])
        routes = {r["route_id"] for r in contract["routes"]}
        self.assertIn("ZIG-ROUTE-CONSTRUCT", routes)
        self.assertIn("ZIG-ROUTE-SKIP", routes)

    def test_specialist_is_read_only_without_an_independent_effort_override(self):
        path = ROOT.parents[1] / "agents" / "zig-semantic-failure-auditor.toml"
        with path.open("rb") as handle:
            agent = tomllib.load(handle)
        self.assertEqual(agent["sandbox_mode"], "read-only")
        self.assertNotIn("model", agent)
        self.assertNotIn("model_reasoning_effort", agent)


FAKE_ZIG = '''import os, pathlib, re, sys
if sys.argv[1] == 'version':
    print(os.environ.get('FAKE_VERSION', '@VERSION@'))
    raise SystemExit(0)
for arg in sys.argv:
    if arg.startswith('-femit-bin='):
        pathlib.Path(arg.split('=', 1)[1]).write_bytes(b'obj')
if sys.argv[1] == 'test' and pathlib.Path(sys.argv[2]).name == 'negative.zig':
    mode = os.environ.get('FAKE_NEGATIVE', 'reject')
    if mode == 'accept': raise SystemExit(0)
    if mode == 'unrelated':
        print('negative.zig:1:1: error: missing import', file=sys.stderr)
    else:
        expected = re.search(r'// EXPECT: (.+)', pathlib.Path(sys.argv[2]).read_text())[1]
        print('negative.zig:3:1: error: ' + expected, file=sys.stderr)
    raise SystemExit(1)
if os.environ.get('FAKE_POSITIVE') == 'reject':
    print('example.zig:1:1: error: positive failed', file=sys.stderr)
    raise SystemExit(1)
'''.replace('@VERSION@', ZIG_VERSION)


class RunnerTests(Fixture):
    def checker(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "tests" / "check_zig_examples.py"), *args],
                              env=self.env, capture_output=True, text=True, timeout=120)

    def test_missing_compiler_is_unavailable_not_passed(self):
        result = self.checker("--zig", str(self.base / "absent"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("COMPTIME_PROOF_UNAVAILABLE", result.stderr)

    def test_wrong_version_is_unavailable(self):
        self.stub("zig", FAKE_ZIG)
        for version in ("0.15.2", "0.16.0", "0.17.0-dev.1+abc", "0.18.0"):
            with self.subTest(version=version):
                self.env["FAKE_VERSION"] = version
                result = self.checker()
                self.assertEqual(result.returncode, 2)
                self.assertIn("VERSION_MISMATCH", result.stderr)

    def test_negative_success_is_a_failure(self):
        self.stub("zig", FAKE_ZIG)
        self.env["FAKE_NEGATIVE"] = "accept"
        self.assertEqual(self.checker().returncode, 1)

    def test_unrelated_compiler_error_is_not_a_negative_pass(self):
        self.stub("zig", FAKE_ZIG)
        self.env["FAKE_NEGATIVE"] = "unrelated"
        result = self.checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected intentional diagnostic", result.stderr)

    def test_diagnostic_matching_positive_control(self):
        self.stub("zig", FAKE_ZIG)
        result = self.checker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("4 forced compile-fail cases", result.stdout)
        for source in (ROOT / "references").glob("*.zig"):
            self.assertIn(f"PASS positive: {source.name}", result.stdout)

    def test_positive_failure_is_not_success(self):
        self.stub("zig", FAKE_ZIG)
        self.env["FAKE_POSITIVE"] = "reject"
        result = self.checker()
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL positive", result.stderr)

    def test_new_references_are_discovered_without_a_registry_edit(self):
        self.stub("zig", FAKE_ZIG)
        self.file("references/new_example.zig", '// fixture\n')
        self.file("tests/compile_fail/bad.zig", '// EXPECT: intentional\n')
        result = self.checker("--skill-root", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS positive: new_example.zig", result.stdout)
        self.assertIn("1 positive files and 1 forced", result.stdout)

    def test_empty_reference_inventory_is_failure(self):
        self.stub("zig", FAKE_ZIG)
        self.file("tests/compile_fail/bad.zig", '// EXPECT: intentional\n')
        result = self.checker("--skill-root", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("INVALID_TEST_INPUT", result.stderr)

    def test_compile_only_does_not_claim_runtime_execution(self):
        self.stub("zig", FAKE_ZIG)
        result = self.checker("--compile-only", "--target", "aarch64_be-linux-musl", "--optimize", "safe")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--test-no-exec", result.stdout)
        self.assertIn("-target aarch64_be-linux-musl", result.stdout)
        self.assertIn("compile-only; no runtime evidence", result.stdout)
        self.assertNotIn("native execution", result.stdout)
        self.assertNotIn("(executed)", result.stdout)

    def test_cross_target_requires_explicit_compile_only(self):
        result = self.checker("--target", "aarch64-linux-musl")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires --compile-only", result.stderr)

    def test_modes_use_canonical_017_tags(self):
        self.stub("zig", FAKE_ZIG)
        result = self.checker("--optimize", "small")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-O small", result.stdout)
        self.assertEqual(self.checker("--optimize", "ReleaseSmall").returncode, 2)

    def test_nonfinite_timeouts_are_rejected(self):
        for value in ("nan", "inf", "0", "-1"):
            with self.subTest(value=value):
                self.assertEqual(self.checker("--timeout", value).returncode, 2)

    def test_measurement_driver_records_only_measured_metrics(self):
        self.stub("zig", FAKE_ZIG)
        result = subprocess.run([sys.executable, str(ROOT / "tests" / "measure_comptime.py"),
                                 "--sizes", "8", "--samples", "1", "--cpu", "baseline"],
                                env=self.env, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        body = json.loads(result.stdout)
        self.assertEqual(len(body["samples"]), 3)
        self.assertTrue(all(r["object_bytes"] == 3 for r in body["samples"]))
        self.assertTrue(all("-mcpu=baseline" in r["command"] for r in body["samples"]))
        self.assertEqual(body["zig_version"], ZIG_VERSION)
        self.assertIsNone(body["runtime_latency"])
        self.assertIsNone(body["compiler_peak_memory"])


class MigrationScanTests(Fixture):
    def scan(self):
        return subprocess.run(["sh", str(ROOT / "scripts" / "zig_0_17_audit_rg.sh")],
                              cwd=self.root, env=self.env, capture_output=True, text=True, timeout=30)

    def test_locator_preserves_no_match_success(self):
        self.stub("rg", 'raise SystemExit(1)')
        self.assertEqual(self.scan().returncode, 0)

    def test_locator_propagates_search_errors(self):
        self.stub("rg", 'raise SystemExit(2)')
        self.assertEqual(self.scan().returncode, 2)

    def test_locator_excludes_nested_generated_and_dependency_trees(self):
        self.stub("rg", 'import sys\nprint("\\n".join(sys.argv[1:]))')
        result = self.scan()
        self.assertEqual(result.returncode, 0)
        for name in (".zig-cache", "zig-cache", "zig-out", "zig-pkg", "vendor", "node_modules"):
            self.assertIn(f"!**/{name}/**", result.stdout)


if __name__ == "__main__":
    unittest.main()
