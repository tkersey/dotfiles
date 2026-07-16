#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def load_module():
    path = Path(__file__).with_name("zig_tiger_style_gate.py")
    spec = importlib.util.spec_from_file_location("zig_tiger_style_gate", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def valid_contract(self):
        return {
            "style_version": "ZTS-v1",
            "artifact_state": {
                "repository_root": "/repo",
                "head": "abc",
                "dirty_fingerprint": "sha256:abc",
                "zig_version": "0.16.0",
            },
            "material": True,
            "priority_order": [
                "safety",
                "performance",
                "developer-experience",
            ],
            "bounds": [
                {
                    "operation": "scan input",
                    "resource": "bytes",
                    "limit": "4 MiB",
                    "failure": "error.InputTooLarge",
                }
            ],
            "bounds_not_applicable_reason": None,
            "assertion_pairs": [
                {
                    "invariant": "sequence increases",
                    "positive_site": "before append",
                    "negative_site": "after reload",
                }
            ],
            "assertions_not_applicable_reason": None,
            "control_flow": {
                "recursion": "none",
                "unbounded_loops": False,
                "function_growth_reviewed": True,
            },
            "errors": {
                "operating_errors_handled": True,
                "programmer_errors_asserted": True,
                "best_effort_sites": [],
            },
            "performance_sketch": {
                "network": "none",
                "disk": "one read",
                "memory": "4 MiB",
                "cpu": "one linear pass",
            },
            "performance_not_applicable_reason": None,
            "exceptions": [],
            "gate": {
                "classified_before_first_edit": True,
                "mutation_allowed": True,
            },
        }

    def test_material_contract_passes(self):
        report = self.mod.validate_zts(self.valid_contract())
        body = report["zig_tiger_style_gate"]
        self.assertEqual("pass", body["verdict"])
        self.assertEqual([], body["errors"])

    def test_material_contract_requires_evidence_or_reason(self):
        contract = self.valid_contract()
        contract["bounds"] = []
        contract["bounds_not_applicable_reason"] = None
        contract["gate"]["mutation_allowed"] = False
        report = self.mod.validate_zts(contract)
        errors = report["zig_tiger_style_gate"]["errors"]
        self.assertIn("bounds:evidence-or-reason-required", errors)

    def test_nonmaterial_contract_requires_reason(self):
        contract = self.valid_contract()
        contract["material"] = False
        contract["nonmaterial_reason"] = ""
        contract["gate"]["mutation_allowed"] = False
        report = self.mod.validate_zts(contract)
        self.assertIn(
            "nonmaterial_reason:missing",
            report["zig_tiger_style_gate"]["errors"],
        )


class SourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def audit(self, current: str, base: str | None = None):
        lines = current.splitlines()
        snapshot = self.mod.FileSnapshot(
            path="src/main.zig",
            text=current,
            base_text=base,
            changed_lines=frozenset(range(1, len(lines) + 1)),
        )
        return self.mod.audit_snapshots(
            [snapshot],
            mode="test",
            base="BASE" if base is not None else None,
            head="WORKTREE",
        )

    def codes(self, report):
        return {item["code"] for item in report["diagnostics"]}

    def test_diff_parser_records_new_line_ranges(self):
        diff = """\
diff --git a/src/main.zig b/src/main.zig
--- a/src/main.zig
+++ b/src/main.zig
@@ -2,0 +3,2 @@
+one
+two
"""
        parsed = self.mod.parse_unified_diff(diff)
        self.assertEqual(frozenset({3, 4}), parsed["src/main.zig"].changed_lines)

    def test_function_span_parser_handles_multiline_signature(self):
        source = """\
fn parseThing(
    bytes: []const u8,
) !void {
    _ = bytes;
}
"""
        spans = self.mod.find_function_spans(source)
        self.assertEqual(1, len(spans))
        self.assertEqual("parseThing", spans[0].name)
        self.assertEqual(5, spans[0].length)

    def test_unbounded_loop_and_catch_unreachable_fail(self):
        report = self.audit(
            """\
fn run() !void {
    while (true) {
        risky() catch unreachable;
    }
}
"""
        )
        codes = self.codes(report)
        self.assertIn("unbounded_loop", codes)
        self.assertIn("catch_unreachable", codes)
        self.assertGreaterEqual(report["summary"]["errors"], 2)

    def test_adjacent_exceptions_are_narrow(self):
        report = self.audit(
            """\
fn run() !void {
    // tiger-style: allow(loop) reason=The permanent loop admits one bounded message per iteration.
    while (true) {
        // tiger-style: allow(catch-unreachable) reason=The error set is empty after comptime specialization proof.
        risky() catch unreachable;
    }
}
"""
        )
        codes = self.codes(report)
        self.assertNotIn("unbounded_loop", codes)
        self.assertNotIn("catch_unreachable", codes)

    def test_invalid_exception_is_an_error(self):
        report = self.audit(
            """\
fn run() void {
    // tiger-style: allow(loop) reason=todo
    while (true) {}
}
"""
        )
        self.assertIn("invalid_exception", self.codes(report))

    def test_direct_recursion_fails(self):
        report = self.audit(
            """\
fn descend(value: u32) void {
    if (value > 0) descend(value - 1);
}
"""
        )
        self.assertIn("direct_recursion", self.codes(report))

    def test_boundary_function_warns_without_assertion_pair(self):
        report = self.audit(
            """\
fn validateRecord(record: Record) !void {
    if (!record.ok) return error.Invalid;
}
"""
        )
        self.assertIn("paired_assertions_missing", self.codes(report))

    def test_new_long_function_fails(self):
        body = "\n".join("    _ = value;" for _ in range(70))
        source = f"fn large(value: u8) void {{\n{body}\n}}\n"
        report = self.audit(source)
        self.assertIn("function_too_long", self.codes(report))

    def test_legacy_long_function_may_shrink_but_not_grow(self):
        base_body = "\n".join("    _ = value;" for _ in range(70))
        current_body = "\n".join("    _ = value;" for _ in range(71))
        base = f"fn large(value: u8) void {{\n{base_body}\n}}\n"
        current = f"fn large(value: u8) void {{\n{current_body}\n}}\n"
        report = self.audit(current, base)
        self.assertIn("function_grew_over_limit", self.codes(report))

    def test_long_url_comment_is_exempt_from_column_limit(self):
        source = "// https://example.invalid/" + "a" * 120 + "\nfn main() void {}\n"
        report = self.audit(source)
        self.assertNotIn("line_too_long", self.codes(report))


class CliIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = Path(__file__).with_name("zig_tiger_style_gate.py")

    def run_git(self, root: Path, *args: str):
        subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_worktree_diff_emits_structured_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.run_git(root, "init", "-q")
            self.run_git(root, "config", "user.name", "Test")
            self.run_git(root, "config", "user.email", "test@example.invalid")
            source = root / "main.zig"
            source.write_text("fn main() void {}\n", encoding="utf-8")
            self.run_git(root, "add", "main.zig")
            self.run_git(root, "commit", "-qm", "base")
            source.write_text(
                "fn main() void {\n    while (true) {}\n}\n",
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(self.script),
                    "audit",
                    "--root",
                    str(root),
                    "--base",
                    "HEAD",
                    "--head",
                    "WORKTREE",
                    "--format",
                    "json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, proc.returncode)
            payload = json.loads(proc.stdout)
            self.assertEqual("zig-tiger-style-report/v1", payload["schema"])
            self.assertEqual(1, payload["summary"]["errors"])
            self.assertEqual("unbounded_loop", payload["diagnostics"][0]["code"])


if __name__ == "__main__":
    unittest.main()
