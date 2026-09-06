#!/usr/bin/env python3
"""Exercise the real Ledger binary; never implement task or graph semantics here.

Default runs include the still-red graph acceptance tests. --lifecycle-only is
an explicit partial qualification, not acceptance of the task-graph application.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "definitions" / "ledger" / "task-protocol.json"
LEDGER = ""
EVIDENCE: list[dict] = []
EVIDENCE_LOCK = threading.Lock()


def invoke(*args: str, payload: dict | None = None, definition: Path = DEFINITION):
    command = [LEDGER, *args, "--definition", str(definition), "--format", "json"]
    process = subprocess.run(
        command, input=None if payload is None else json.dumps(payload),
        text=True, capture_output=True, timeout=30, check=False,
    )
    try:
        result = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(
            f"Ledger returned no JSON envelope: {command}\n"
            f"exit={process.returncode}\n{process.stdout}\n{process.stderr}"
        ) from error
    with EVIDENCE_LOCK:
        EVIDENCE.append(result)
    return process.returncode, result


class Workspace(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ergon-test-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = self.temporary.name
        self.request_number = 0

    def project(self, name="current", **parameters):
        args = ["project", "--projection", name, "--repo", self.repo]
        for key, value in parameters.items():
            args += ["--param", f"{key}={value}"]
        code, result = invoke(*args)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["schema"], "ledger-projection-result/v1")
        self.assertFalse(result["authority_granted"])
        self.assertFalse(result["storage_mutated"])
        self.assertEqual(result["limitations"], [], result)
        self.assertEqual(result["stats"]["records_emitted"],
                         result["stats"]["records_matched"], result)
        return result

    def submit(self, operation, ident="A", title="Task A", *, request=None,
               revision=None, extra=None, include_request=True):
        if request is None:
            self.request_number += 1
            request = f"req-{self.request_number}"
        args = ["transact", "--operation", operation, "--repo", self.repo,
                "--input", "submission=-"]
        if include_request:
            args += ["--param", f"request={request}"]
        if operation != "create":
            if revision is None:
                revision = self.project()["store"]["revision"]
            args += ["--param", f"revision={revision}"]
        payload = {"id": ident, "record": {"title": title}}
        if extra:
            payload.update(extra)
        return invoke(*args, payload=payload)

    def accept(self, operation, ident="A", title="Task A", **kwargs):
        code, result = self.submit(operation, ident, title, **kwargs)
        self.assertEqual(code, 0, result)
        self.assertEqual(result["schema"], "ledger-transaction-result/v1")
        self.assertTrue(result["valid"])
        self.assertFalse(result["semantic_authority_granted"])
        return result

    def reject_unchanged(self, operation, ident="A", title="Task A", **kwargs):
        before, history = self.project(), self.project("history")
        code, result = self.submit(operation, ident, title, **kwargs)
        self.assertNotEqual(code, 0, result)
        after = self.project()
        self.assertEqual(before["store"], after["store"])
        self.assertEqual(before["data"], after["data"])
        self.assertEqual(history["data"], self.project("history")["data"])
        # Rejected operations may write custody metadata. Do not erase or
        # reinterpret Ledger's storage_mutated claim as "no filesystem writes".
        return result


class Lifecycle(Workspace):
    def test_definition_and_manifest(self):
        manifest = json.loads((ROOT / "definitions" / "manifest.json").read_text())
        self.assertEqual(manifest["skill"], "ergon")
        self.assertEqual(manifest["ledger"], [
            {"id": "ergon/task-protocol", "path": "ledger/task-protocol.json"}
        ])
        code, checked = invoke("definition", "check")
        self.assertEqual(code, 0, checked)
        self.assertTrue(checked["valid"])
        code, description = invoke("definition", "describe")
        self.assertEqual(code, 0, description)
        self.assertEqual(checked["definition"]["digest"], description["definition"]["digest"])
        self.assertEqual(description["definition"]["owner"], "ergon")

    def test_lifecycle_and_fresh_process_replay(self):
        self.accept("create", "B", "Task B")
        self.accept("create")
        self.assertEqual([row["id"] for row in self.project("open")["data"]], ["A", "B"])
        self.accept("close")
        self.assertEqual([row["id"] for row in self.project("open")["data"]], ["B"])
        self.accept("reopen")
        # Every invocation is a new process. These are native projections,
        # not a Python reducer or a persisted expected-state cache.
        current = self.project()
        self.assertEqual(current["data"], [
            {"id": "A", "status": "open", "task": {"title": "Task A"}, "event_count": 3},
            {"id": "B", "status": "open", "task": {"title": "Task B"}, "event_count": 1},
        ])
        replayed = self.project()
        self.assertEqual(current["data"], replayed["data"])
        self.assertEqual(current["store"], replayed["store"])
        self.assertEqual(current["definition"], replayed["definition"])
        self.assertEqual(len(self.project("history")["data"]), 4)
        self.assertEqual(self.project("task", id="A")["data"][0]["event_count"], 3)
        code, doctor = invoke("doctor", "--repo", self.repo)
        self.assertEqual(code, 0, doctor)
        self.assertTrue(doctor["healthy"])
        self.assertEqual(doctor["slots"][0]["revision"], current["store"]["revision"])

    def test_invalid_transitions_do_not_change_domain_state(self):
        self.reject_unchanged("close")
        self.reject_unchanged("reopen")
        self.accept("create")
        self.reject_unchanged("create")
        self.reject_unchanged("reopen")
        self.accept("close")
        self.reject_unchanged("close")

    def test_identity_title_and_closed_input_shapes(self):
        self.accept("create")
        self.reject_unchanged("close", title="Silently renamed")
        self.reject_unchanged("create", ident="B", title=" ")
        self.reject_unchanged("create", ident="B", title="x" * 513)
        self.reject_unchanged("create", ident="../escape")
        self.reject_unchanged("create", ident="B", extra={"ready": True})
        self.reject_unchanged("create", ident="B", extra={"dependencies": ["A"]})
        self.accept("create", "B", "b" * 512)

    def test_duplicate_requests_and_conflicting_reuse(self):
        first = self.accept("create", request="create-a")
        before = self.project()
        repeated = self.accept("create", request="create-a")
        self.assertEqual(repeated["effects"][0]["result"], "idempotent")
        self.assertEqual(before["data"], self.project()["data"])
        self.assertEqual(first["effects"][0]["revision_after"],
                         self.project()["store"]["revision"])
        self.reject_unchanged("create", "B", "Task B", request="create-a")
        self.reject_unchanged("create", "B", "Task B", include_request=False)

    def test_revision_checks_precede_operation_scoped_idempotency(self):
        self.accept("create", request="same-key")
        revision = self.project()["store"]["revision"]
        # Native keys are operation-scoped, not global application identities.
        self.accept("close", request="same-key", revision=revision)
        result = self.reject_unchanged("close", request="same-key", revision=revision)
        self.assertEqual(result["code"], "RevisionMismatch")
        before = self.project()
        repeated = self.accept("close", request="same-key")
        self.assertEqual(repeated["effects"][0]["result"], "idempotent")
        self.assertEqual(before["store"], self.project()["store"])
        self.assertEqual(before["data"], self.project()["data"])

    def test_stale_revision_and_competing_writers(self):
        self.accept("create")
        revision = self.project()["store"]["revision"]
        code, result = invoke(
            "transact", "--operation", "close", "--repo", self.repo,
            "--input", "submission=-", "--param", "request=missing-revision",
            payload={"id": "A", "record": {"title": "Task A"}},
        )
        self.assertNotEqual(code, 0, result)
        self.assertEqual(self.project()["store"]["revision"], revision)
        barrier = threading.Barrier(2)

        def close(request):
            barrier.wait(timeout=10)
            return self.submit("close", request=request, revision=revision)

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(close, ["writer-1", "writer-2"]))
        self.assertEqual(sum(code == 0 for code, _ in outcomes), 1, outcomes)
        self.assertEqual(self.project("task", id="A")["data"][0]["status"], "closed")
        self.assertEqual(len(self.project("history")["data"]), 2)
        self.accept("reopen")
        self.reject_unchanged("close", request="stale-after-reopen", revision=revision)


class GraphAcceptance(Workspace):
    def edge(self, operation, task, prerequisite, *, revision=None, request=None):
        if request is None:
            self.request_number += 1
            request = f"edge-{self.request_number}"
        if revision is None:
            revision = self.project()["store"]["revision"]
        return invoke(
            "transact", "--operation", operation, "--repo", self.repo,
            "--input", "submission=-", "--param", f"request={request}",
            "--param", f"revision={revision}",
            payload={"id": task, "prerequisite": prerequisite},
        )

    def accept_edge(self, task, prerequisite, **kwargs):
        code, result = self.edge("add-dependency", task, prerequisite, **kwargs)
        self.assertEqual(code, 0, f"Graph acceptance is BLOCKED: {result}")
        return result

    def reject_edge_unchanged(self, task, prerequisite):
        current, history = self.project(), self.project("history")
        code, result = self.edge("add-dependency", task, prerequisite)
        self.assertNotEqual(code, 0, result)
        after = self.project()
        self.assertEqual(current["store"], after["store"])
        self.assertEqual(current["data"], after["data"])
        self.assertEqual(history["data"], self.project("history")["data"])

    def test_dependency_lifecycle_required_before_real_use(self):
        self.accept("create")
        self.accept("create", "B", "Task B")
        revision = self.project()["store"]["revision"]
        self.accept_edge("B", "A", revision=revision, request="b-requires-a")
        history = self.project("history")["data"]
        repeated = self.accept_edge("B", "A", request="b-requires-a")
        self.assertEqual(repeated["effects"][0]["result"], "idempotent")
        self.assertEqual(history, self.project("history")["data"])
        self.assertEqual([row["id"] for row in self.project("ready")["data"]], ["A"])
        self.accept("close")
        self.assertEqual([row["id"] for row in self.project("ready")["data"]], ["B"])
        self.accept("reopen")
        self.assertEqual([row["id"] for row in self.project("ready")["data"]], ["A"])
        code, result = self.edge("remove-dependency", "B", "A")
        self.assertEqual(code, 0, result)
        self.assertEqual([row["id"] for row in self.project("ready")["data"]], ["A", "B"])
        # Each projection is another process; no local graph or ready cache exists.
        self.assertEqual(self.project("ready")["data"], self.project("ready")["data"])

    def test_dangling_self_and_long_cycle_rejection(self):
        for ident in ["A", "B", "C"]:
            self.accept("create", ident, f"Task {ident}")
        # A valid neighboring edge must succeed before a rejection can count
        # as evidence; UnknownOperation is never mistaken for cycle detection.
        self.accept_edge("B", "A")
        self.reject_edge_unchanged("A", "A")
        self.reject_edge_unchanged("A", "missing")
        self.reject_edge_unchanged("missing", "A")
        self.reject_edge_unchanged("A", "B")
        self.accept_edge("C", "B")
        self.reject_edge_unchanged("A", "C")

    def test_opposite_edges_cannot_both_be_admitted(self):
        for ident in ["A", "B", "C"]:
            self.accept("create", ident, f"Task {ident}")
        self.accept_edge("C", "A")
        code, result = self.edge("remove-dependency", "C", "A")
        self.assertEqual(code, 0, result)
        revision = self.project()["store"]["revision"]
        history_count = len(self.project("history")["data"])
        barrier = threading.Barrier(2)

        def add(pair):
            task, prerequisite = pair
            barrier.wait(timeout=10)
            return self.edge("add-dependency", task, prerequisite,
                             revision=revision, request=f"{task}-requires-{prerequisite}")

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(add, [("A", "B"), ("B", "A")]))
        self.assertEqual(sum(code == 0 for code, _ in outcomes), 1, outcomes)
        self.assertEqual(len(self.project("history")["data"]), history_count + 1)
        ready = [row["id"] for row in self.project("ready")["data"]]
        self.assertIn(ready, [["A", "C"], ["B", "C"]])


def main() -> int:
    global LEDGER
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lifecycle-only", action="store_true",
                        help="Run the partial lifecycle qualification, not full acceptance")
    parser.add_argument("--evidence", type=Path,
                        help="Write the unchanged native result envelopes as JSONL")
    options = parser.parse_args()
    evidence = options.evidence.resolve() if options.evidence else None
    if evidence is not None and (".ledger" in evidence.parts or evidence.exists()):
        parser.error("Evidence must be a new file outside .ledger")
    bootstrap = ROOT.parent / "ledger" / "scripts" / "ensure-ledger"
    result = subprocess.run(["bash", str(bootstrap)], capture_output=True,
                            text=True, timeout=30, check=False)
    if result.returncode:
        sys.stderr.write(result.stderr)
        return result.returncode
    ready = json.loads(result.stdout)
    if ready.get("schema") != "ledger-bootstrap-ready/v1" or ready.get("status") != "ready":
        raise RuntimeError(f"Unexpected bootstrap result: {ready}")
    LEDGER = ready["path"]
    print(result.stdout, end="")
    suites = [unittest.defaultTestLoader.loadTestsFromTestCase(Lifecycle)]
    if not options.lifecycle_only:
        suites.append(unittest.defaultTestLoader.loadTestsFromTestCase(GraphAcceptance))
    checked = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(suites))
    if evidence is not None:
        with evidence.open("x") as output:
            for row in EVIDENCE:
                output.write(json.dumps(row, separators=(",", ":")) + "\n")
    print("Qualification: lifecycle-only; graph acceptance remains blocked."
          if options.lifecycle_only else "Qualification: includes required graph acceptance.")
    return 0 if checked.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
