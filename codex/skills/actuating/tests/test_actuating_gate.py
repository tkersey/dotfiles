from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from actuating_gate import (  # noqa: E402
    binding_errors,
    cas_errors,
    canonical_digest,
    decide,
    live_artifact,
    live_hunk_ids,
    live_path_states,
    load_semantics,
    path_allowed,
    path_allowed_root,
    paths_overlap,
    resolution_digest_payload,
    review_contract_payload,
    ship_errors,
    validate_resolution,
    validate_run,
)


class GateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=self.repo,
            check=True,
        )
        (self.repo / "file.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "base"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(["git", "branch", "-M", "main"], cwd=self.repo, check=True)
        self.base = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo,
            text=True,
        ).strip()
        self.live_cas_snapshot: dict = {
            "schema": "CAS-LIST-v1",
            "records": [],
            "recordRefs": [],
        }
        self.live_cas_patch = patch(
            "actuating_gate.live_cas_list",
            side_effect=lambda *_: self.live_cas_snapshot,
        )
        self.live_cas_mock = self.live_cas_patch.start()
        self.live_pr_override: dict | None = None
        self.live_pr_patch = patch(
            "actuating_gate.live_pr_metadata",
            side_effect=self.pr_metadata,
        )
        self.live_pr_mock = self.live_pr_patch.start()

    def tearDown(self) -> None:
        self.live_pr_patch.stop()
        self.live_cas_patch.stop()
        self.temp.cleanup()

    def artifact(self) -> dict:
        return live_artifact(self.repo, self.base)

    def pr_metadata(self, _repo: Path, url: str) -> dict:
        if self.live_pr_override is not None:
            return self.live_pr_override
        artifact = self.artifact()
        return {
            "repository": {
                "nameWithOwner": "example/repo",
                "url": "https://github.com/example/repo",
            },
            "pull_request": {
                "url": url,
                "baseRefName": "main",
                "baseRefOid": artifact["base_sha"],
                "headRefName": artifact["branch"],
                "headRefOid": artifact["head_sha"],
                "headRepository": {"nameWithOwner": "example/repo"},
                "isDraft": False,
                "state": "OPEN",
            },
        }

    def run_value(self, *, review: bool = False, selected: bool = False) -> dict:
        artifact = self.artifact()
        steps = []
        selected_id = None
        if selected:
            selected_id = "step-1"
            steps = [
                {
                    "step_id": "step-1",
                    "run_id": "run-1",
                    "selected_by": "lead",
                    "owner_boundary": "actuating",
                    "effect": "edit",
                    "paths": ["file.txt"],
                    "verifier": ["test"],
                    "changed_paths": [],
                    "status": "selected",
                    "state_before": artifact,
                    "parent_completion_claimed": False,
                    "performed_public_effects": [],
                }
            ]
            if review:
                steps[0]["review_resolution"] = {
                    "resolution_id": "resolution-at-admission",
                    "resolution_digest": "sha256:" + "a" * 64,
                }
        return {
            "version": "actuation-run/v1",
            "run_id": "run-1",
            "mode": "review-closeout" if review else "implement",
            "source": {
                "kind": "direct-goal",
                "scope_source_ref": "user:goal",
                "execution_authority_ref": "user:implement",
                "authority_owner": "user",
                "current": True,
            },
            "authority": {
                "mutation_allowed": True,
                "allowed_paths": ["file.txt"],
                "public_effects_allowed": ["ship-handoff"],
                "unsupported_coordination_required": False,
            },
            "artifact_initial": artifact,
            "artifact_initial_path_states": live_path_states(
                self.repo, artifact["base_sha"]
            ),
            "artifact": artifact,
            "execution": {
                "kind": "direct" if selected else "iterative",
                "selected_step_id": selected_id,
                "steps": steps,
            },
            "review": {
                "required": review,
                "source_refs": ["local:audit-1"] if review else [],
                "codex_thread_id": "thread-test" if review else None,
                "publication_requested": False,
            },
        }

    def complete_step(self, run: dict) -> dict:
        (self.repo / "file.txt").write_text("changed\n", encoding="utf-8")
        return self.finish_step(run, ["file.txt"])

    def finish_step(self, run: dict, changed_paths: list[str]) -> dict:
        after = self.artifact()
        step = run["execution"]["steps"][0]
        step.update(
            {
                "status": "completed",
                "changed_paths": changed_paths,
                "state_after": after,
                "evidence_fold_ref": "ef-1",
                "verdict": "ready-for-closure",
            }
        )
        run["execution"]["selected_step_id"] = None
        run["artifact"] = after
        if run["review"]["required"]:
            return self.commit_step(run)
        return run

    def finish_verify_step(self, run: dict) -> dict:
        step = run["execution"]["steps"][0]
        step.update(
            {
                "effect": "verify",
                "changed_paths": [],
                "status": "completed",
                "state_after": run["artifact"],
                "evidence_fold_ref": "ef-1",
                "verdict": "ready-for-closure",
            }
        )
        run["execution"]["selected_step_id"] = None
        return run

    def commit_step(self, run: dict) -> dict:
        step = run["execution"]["steps"][0]
        subprocess.run(
            ["git", "add", "--", *step["changed_paths"]],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-qm", "complete selected step"],
            cwd=self.repo,
            check=True,
        )
        after = self.artifact()
        step["state_after"] = after
        run["artifact"] = after
        return run

    def triage_run(self) -> dict:
        run = self.run_value()
        run["mode"] = "triage"
        run["authority"]["mutation_allowed"] = False
        run["execution"] = {
            "kind": "none",
            "selected_step_id": None,
            "steps": [],
        }
        run["review"]["source_refs"] = ["local:audit-1"]
        return run

    def initial_dirty_run(self) -> dict:
        (self.repo / "file.txt").write_text("user-dirty\n", encoding="utf-8")
        run = self.run_value(selected=True)
        run["authority"]["allowed_paths"] = ["file.txt", "decoy.txt"]
        run["execution"]["steps"][0]["paths"] = ["decoy.txt"]
        return run

    def review_fold(self, run: dict, finding_ids: list[str] | None = None) -> dict:
        finding_ids = [] if finding_ids is None else finding_ids
        findings = [
            {
                "finding_id": finding_id,
                "source_ref": f"local:{finding_id}",
                "claim": "the gate misses an inverse",
                "observed_fact": "a counterexample closes",
                "suggested_repair": "enforce the owner law",
                "validity": "valid",
                "liability": "invariant-gap",
                "intent_relation": "core",
                "novelty": "new-class",
                "disposition": "resolution-input",
                "quotient_key": "gate-inverse",
                "owner_boundary": "actuating",
                "law_family": "closure",
                "falsifier": "counterexample still closes",
                "evidence_refs": [f"test:{finding_id}"],
                "mutation_authority": {
                    "allowed": False,
                    "reason": "classification never grants mutation",
                },
            }
            for finding_id in finding_ids
        ]
        return {
            "version": "RF-v2",
            "fold_id": "rf-1",
            "goal_id": run["run_id"],
            "source": {
                "backend": "local-audit",
                "source_batch_id": "audit-1",
                "source_state": "findings" if findings else "clean",
                "artifact": {
                    key: run["artifact"][key]
                    for key in (
                        "repo",
                        "base_sha",
                        "branch",
                        "head_sha",
                        "state_fingerprint",
                    )
                },
                "source_ref": "local:audit-1",
            },
            "intent_anchor": {
                "original_goal": "exercise inverse laws",
                "accepted_scope": ["actuating"],
                "non_goals": [],
            },
            "findings": findings,
            "compression": {
                "equivalence_classes": (
                    [
                        {
                            "quotient_key": "gate-inverse",
                            "finding_ids": finding_ids,
                            "owner_boundary": "actuating",
                            "law_family": "closure",
                        }
                    ]
                    if findings
                    else []
                )
            },
            "routing_obligations": (
                [
                    {
                        "trigger": "invariant-gap",
                        "finding_ids": finding_ids,
                        "owner_lens": "invariant-ace",
                    }
                ]
                if findings
                else []
            ),
        }

    def resolution(self, run: dict) -> dict:
        surfaces = [
            "public-interface",
            "state-and-transitions",
            "abstraction-change",
        ]
        semantics = load_semantics()
        lenses = ["standard"]
        profile = {
            "selected_lenses": lenses,
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload(surfaces, lenses, semantics)
            ),
        }
        value = {
            "version": "review-resolution/v1",
            "resolution_id": "resolution-1",
            "run_id": run["run_id"],
            "artifact": run["artifact"],
            "review_folds": [self.review_fold(run)],
            "finding_ids": [],
            "change_surfaces": surfaces,
            "review_profile": profile,
            "decisions": [],
            "outcome": {
                "status": "clean",
                "semantic_balance": {
                    "accounted_hunks": live_hunk_ids(
                        self.repo, run["artifact"]["base_sha"]
                    ),
                    "unaccounted_hunks": [],
                    "covered_liabilities": [],
                    "uncovered_liabilities": [],
                    "added_constructs": [],
                    "required_retirements": [],
                    "completed_retirements": [],
                    "dominated_remaining": [],
                },
            },
        }
        value["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(value)
        )
        return value

    def bind_resolution_findings(
        self,
        run: dict,
        resolution: dict,
        finding_ids: list[str],
    ) -> None:
        resolution["finding_ids"] = finding_ids
        resolution["review_folds"] = [self.review_fold(run, finding_ids)]

    def bind_completed_resolution(self, run: dict, resolution: dict) -> None:
        run["execution"]["steps"][0]["review_resolution"] = {
            "resolution_id": resolution["resolution_id"],
            "resolution_digest": resolution["outcome"]["resolution_digest"],
        }

    def cas_review_fold(self, run: dict, record: dict) -> dict:
        producer_findings = record["verdict"]["findings"]
        fold = self.review_fold(
            run,
            [f"classified-{index}" for index in range(1, len(producer_findings) + 1)],
        )
        record_id = record["recordId"]
        fold["fold_id"] = f"rf-{record_id}"
        fold["source"].update(
            {
                "backend": "cas",
                "source_batch_id": record_id,
                "source_state": "findings",
                "source_ref": record_id,
            }
        )
        for index, finding in enumerate(fold["findings"], start=1):
            producer = producer_findings[index - 1]
            finding["source_ref"] = (
                producer.get("findingId") or f"{record_id}#{index}"
            )
        return fold

    def evidence(self, run: dict) -> dict:
        admission = run["execution"]["steps"][0].get("review_resolution")
        review_refs = (
            [
                "review-resolution:"
                f"{admission['resolution_id']}:{admission['resolution_digest']}"
            ]
            if isinstance(admission, dict)
            else []
        )
        return {
            "evidence_fold": {
                "version": "EF-v1",
                "evidence_id": "ef-1",
                "run_id": run["run_id"],
                "step_id": "step-1",
                "artifact_state": {
                    **run["artifact"],
                    "changed_paths": ["file.txt"],
                },
                "evidence": {
                    "observed": ["current diff and test result"],
                    "commands": {
                        "passed": ["test"],
                        "failed": [],
                        "unavailable": [],
                    },
                    "artifacts_inspected": ["file.txt"],
                    "review_refs": review_refs,
                },
                "progress": {
                    "status": "done",
                    "score_before": 0,
                    "score_after": 1,
                    "largest_remaining_failure": None,
                    "next_frontier": None,
                },
                "proof": {
                    "supports_done_claim": "yes",
                    "proof_gaps": [],
                    "stale_or_missing_artifact_binding": "no",
                },
                "anti_gaming": {
                    "tests_deleted": "no",
                    "assertions_weakened": "no",
                    "checks_skipped": "no",
                    "coverage_reduced": "no",
                    "behavior_outside_goal_changed": "no",
                },
                "recommendation": {
                    "action": "stop",
                    "reason": "selected step is proven",
                },
            }
        }

    def decision(
        self,
        run: dict,
        *,
        strategy: str = "local-repair",
        finding_ids: list[str] | None = None,
        path: str = "file.txt",
    ) -> dict:
        finding_ids = ["finding-1"] if finding_ids is None else finding_ids
        return {
            "decision_id": "decision-1",
            "owner_boundary": "actuating",
            "finding_ids": finding_ids,
            "liability_classes": ["invariant-gap"],
            "strategy": strategy,
            "alternatives_considered": ["no-change"],
            "falsifier": "focused regression fails",
            "abstraction_account": [
                {
                    "abstraction": "gate",
                    "disposition": "retain",
                    "obligation_id": "mutation-admission",
                }
            ],
            "selected_work_node": (
                {
                    "node_id": "step-1",
                    "run_id": run["run_id"],
                    "owner_boundary": "actuating",
                    "paths": [path],
                    "verifier": ["test"],
                }
                if strategy in {"local-repair", "replacement-kernel"}
                else None
            ),
            "blockers": ["missing authority"] if strategy == "blocked" else [],
        }

    def cas_record(
        self,
        run: dict,
        resolution: dict,
        lane: str,
        ordinal: int,
    ) -> dict:
        lens_contracts = load_semantics()["lens_contracts"]
        return {
            "schema": "CAS-RER-v1",
            "recordId": f"rer_{lane}_{ordinal}",
            "createdAt": f"unix-ns:{ordinal}",
            "updatedAt": f"unix-ns:{ordinal}",
            "command": {
                "surface": "run",
                "backendSelected": "cas-run",
                "brokerDecision": {
                    "action": "created_new",
                    "reason": "test",
                    "freshAttemptRequired": ordinal > 1,
                },
            },
            "tuple": {
                "repoRealpath": run["artifact"]["repo"],
                "baseSha": run["artifact"]["base_sha"],
                "headSha": run["artifact"]["head_sha"],
                "targetFingerprint": "target=native;head=current;base=accepted",
                "tupleCurrentAtRecordTime": True,
            },
            "workflowBinding": {
                "actuationRunId": run["run_id"],
                "artifactStateFingerprint": run["artifact"]["state_fingerprint"],
                "reviewContractFingerprint": resolution["review_profile"][
                    "review_contract_fingerprint"
                ],
                "resolutionDigest": resolution["outcome"]["resolution_digest"],
                "selectedLenses": resolution["review_profile"]["selected_lenses"],
                "reviewLane": lane,
                "lensContract": lens_contracts[lane],
            },
            "attempt": {
                "exists": True,
                "attemptId": f"attempt-{lane}-{ordinal}",
                "phase": "normalized_verdict",
                "reviewThreadId": f"thread-{lane}-{ordinal}",
                "reviewTurnId": f"turn-{lane}-{ordinal}",
            },
            "verdict": {
                "tupleVerdictExists": True,
                "status": "clean",
                "clean": True,
                "findingCount": 0,
                "findings": [],
            },
            "failure": {
                "failureCode": None,
                "failureClass": None,
                "retryableSameTupleNow": None,
            },
            "principal": {
                "kind": "strong",
                "accountFingerprint": "acct:test",
                "proofUsable": True,
                "reduced": False,
                "fallbackUsed": False,
                "source": "cas-run",
            },
        }

    def test_selected_step_allows_mutation(self) -> None:
        errors, derived = validate_run(
            self.run_value(selected=True),
            self.repo,
        )
        self.assertEqual(errors, [])
        self.assertEqual(derived["selected_step_id"], "step-1")

    def test_verifier_commands_must_be_substantive(self) -> None:
        for verifier in ("", "   "):
            run = self.run_value(selected=True)
            run["execution"]["steps"][0]["verifier"] = [verifier]
            with self.subTest(verifier=verifier):
                errors, _ = validate_run(run, self.repo)
                self.assertIn("blocked-step-verifier", errors)

    def test_completed_step_requires_current_evidence_reference(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        errors, _ = validate_run(run, self.repo)
        self.assertEqual(errors, [])
        run["execution"]["steps"][0]["evidence_fold_ref"] = ""
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-evidence-fold-missing", errors)

    def test_failed_step_cannot_admit_a_following_step(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        run["execution"]["kind"] = "iterative"
        run["execution"]["steps"][0]["verdict"] = "regress"
        run["execution"]["steps"].append(
            {
                "step_id": "step-2",
                "run_id": run["run_id"],
                "selected_by": "lead",
                "owner_boundary": "actuating",
                "effect": "edit",
                "paths": ["file.txt"],
                "verifier": ["test"],
                "changed_paths": [],
                "status": "selected",
                "state_before": run["artifact"],
                "parent_completion_claimed": False,
                "performed_public_effects": [],
            }
        )
        run["execution"]["selected_step_id"] = "step-2"
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-continuation", errors)

    def test_continuation_resolves_prior_evidence(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        run["execution"]["kind"] = "iterative"
        run["execution"]["steps"][0]["verdict"] = "continue"
        run["execution"]["steps"].append(
            {
                "step_id": "step-2",
                "run_id": run["run_id"],
                "selected_by": "lead",
                "owner_boundary": "actuating",
                "effect": "edit",
                "paths": ["file.txt"],
                "verifier": ["test"],
                "changed_paths": [],
                "status": "selected",
                "state_before": run["artifact"],
                "parent_completion_claimed": False,
                "performed_public_effects": [],
            }
        )
        run["execution"]["selected_step_id"] = "step-2"
        errors, _ = validate_run(run, self.repo, evidence_values=[self.evidence(run)])
        self.assertEqual(errors, [])

    def test_authority_negative_matrix(self) -> None:
        cases = []
        value = self.run_value(selected=True)
        value["source"]["execution_authority_ref"] = ""
        cases.append((value, "blocked-authority-missing:execution_authority_ref"))
        value = self.run_value(selected=True)
        value["source"]["current"] = False
        cases.append((value, "blocked-authority-stale"))
        value = self.run_value(selected=True)
        value["authority"]["unsupported_coordination_required"] = True
        cases.append((value, "blocked-unsupported-controller"))
        value = self.run_value(selected=True)
        value["execution"]["steps"][0]["selected_by"] = "subagent"
        cases.append((value, "blocked-step-owner"))
        for candidate, expected in cases:
            with self.subTest(expected=expected):
                errors, _ = validate_run(candidate, self.repo)
                self.assertIn(expected, errors)

    def test_no_code_mode_cannot_select_work(self) -> None:
        run = self.run_value(selected=True)
        run["mode"] = "triage"
        run["authority"]["mutation_allowed"] = False
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-no-code-mutation", errors)

    def test_implementation_requires_a_real_step(self) -> None:
        errors, _ = validate_run(self.run_value(), self.repo)
        self.assertIn("blocked-step-missing", errors)
        errors, _ = validate_run(self.run_value(review=True), self.repo)
        self.assertIn("blocked-step-missing", errors)

    def test_review_closeout_selection_requires_bound_resolution(self) -> None:
        run = self.run_value(review=True, selected=True)
        run["execution"]["steps"][0].pop("review_resolution")
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-review-resolution-missing", errors)
        self.assertIn("blocked-resolution-binding", errors)

        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run)]
        resolution["outcome"]["status"] = "pending"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        run["execution"]["steps"][0]["review_resolution"] = {
            "resolution_id": resolution["resolution_id"],
            "resolution_digest": resolution["outcome"]["resolution_digest"],
        }
        errors, _ = validate_run(run, self.repo, resolution)
        self.assertEqual(errors, [])

        run["execution"]["steps"][0]["review_resolution"][
            "resolution_digest"
        ] = "sha256:" + "0" * 64
        errors, _ = validate_run(run, self.repo, resolution)
        self.assertIn("blocked-resolution-binding", errors)
        run["execution"]["steps"][0]["review_resolution"][
            "resolution_digest"
        ] = resolution["outcome"]["resolution_digest"]

        run["execution"]["steps"][0]["effect"] = "verify"
        errors, _ = validate_run(run, self.repo, resolution)
        self.assertIn("blocked-resolution-node-unexecuted", errors)

    def test_resolution_rejects_local_growth(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run)]
        resolution["decisions"][0]["abstraction_account"] = [
            {
                "abstraction": "old-helper",
                "disposition": "replace",
                "obligation_id": "mutation-admission",
            }
        ]
        balance = resolution["outcome"]["semantic_balance"]
        balance["covered_liabilities"] = ["invariant-gap"]
        resolution["outcome"]["status"] = "resolved"
        balance["added_constructs"] = [
            {
                "name": "new-helper",
                "obligation_id": "mutation-admission",
                "obligation_ref": "goal:mutation-admission",
                "replaces": "old-helper",
            }
        ]
        balance["required_retirements"] = ["old-helper"]
        balance["completed_retirements"] = ["old-helper"]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        self.bind_completed_resolution(run, resolution)
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-local-repair-growth", errors)

    def test_resolved_node_must_match_completed_review_step(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run)]
        resolution["outcome"]["status"] = "resolved"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        self.bind_completed_resolution(run, resolution)
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])

        resolution["decisions"][0]["selected_work_node"]["node_id"] = (
            "never-executed"
        )
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        self.bind_completed_resolution(run, resolution)
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-resolution-node-unexecuted", errors)

    def test_replacement_kernel_accepts_domain_obligation_reference(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        decision = self.decision(run, strategy="replacement-kernel")
        decision["abstraction_account"] = [
            {
                "abstraction": "old-gate",
                "disposition": "replace",
                "obligation_id": "domain:valid-transition",
            }
        ]
        resolution["decisions"] = [decision]
        resolution["outcome"]["status"] = "resolved"
        balance = resolution["outcome"]["semantic_balance"]
        balance["covered_liabilities"] = ["invariant-gap"]
        balance["added_constructs"] = [
            {
                "name": "new-gate",
                "obligation_id": "domain:valid-transition",
                "obligation_ref": "spec:valid-transition",
                "replaces": "old-gate",
            }
        ]
        balance["required_retirements"] = ["old-gate"]
        balance["completed_retirements"] = ["old-gate"]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        surfaces = sorted(
            set(resolution["change_surfaces"] + ["replacement-kernel"])
        )
        semantics = load_semantics()
        lenses = ["standard"]
        resolution["review_profile"] = {
            "selected_lenses": lenses,
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload(surfaces, lenses, semantics)
            ),
        }
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        self.bind_completed_resolution(run, resolution)
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])

    def test_replacement_kernel_changes_review_contract_surface(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["change_surfaces"] = ["state-and-transitions"]
        semantics = load_semantics()
        lenses = ["standard"]
        resolution["review_profile"] = {
            "selected_lenses": lenses,
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload(
                    resolution["change_surfaces"], lenses, semantics
                )
            ),
        }
        resolution["decisions"] = [
            self.decision(run, strategy="replacement-kernel")
        ]
        resolution["outcome"]["status"] = "pending"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-cas-contract-mismatch", errors)

    def test_resolution_inverses_reject_orphans_and_self_attestation(
        self,
    ) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        cases = []

        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run, finding_ids=[])]
        resolution["outcome"]["status"] = "resolved"
        cases.append((resolution, "blocked-resolution-finding-coverage"))

        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run)]
        resolution["decisions"][0]["abstraction_account"][0].pop("abstraction")
        resolution["outcome"]["status"] = "resolved"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        cases.append((resolution, "blocked-abstraction-account"))

        resolution = self.resolution(run)
        hunks = resolution["outcome"]["semantic_balance"]["accounted_hunks"]
        resolution["outcome"]["semantic_balance"]["accounted_hunks"] = hunks + hunks
        cases.append((resolution, "blocked-semantic-hunks"))

        for resolution, expected in cases:
            resolution["outcome"]["resolution_digest"] = canonical_digest(
                resolution_digest_payload(resolution)
            )
            with self.subTest(expected=expected):
                errors, _ = validate_resolution(run, resolution, self.repo)
                self.assertIn(expected, errors)

    def test_resolution_rejects_mixed_lists_and_open_review_folds(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        cases = []

        resolution = self.resolution(run)
        resolution["finding_ids"] = ["finding-1", 0]
        cases.append((resolution, "blocked-resolution-finding-shape"))

        resolution = self.resolution(run)
        resolution["change_surfaces"] = ["public-interface", 0]
        cases.append((resolution, "blocked-review-surface"))

        resolution = self.resolution(run)
        fold = self.review_fold(run, ["finding-1"])
        fold["findings"][0]["disposition"] = "blocked"
        fold["findings"][0]["validity"] = "unproven"
        resolution["review_folds"] = [fold]
        cases.append((resolution, "blocked-review-fold-open"))

        resolution = self.resolution(run)
        resolution["review_folds"][0].pop("intent_anchor")
        cases.append((resolution, "blocked-review-fold-invalid"))

        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["review_folds"][0]["findings"][0].pop("observed_fact")
        cases.append((resolution, "blocked-review-fold-invalid"))

        for resolution, expected in cases:
            resolution["outcome"]["resolution_digest"] = canonical_digest(
                resolution_digest_payload(resolution)
            )
            with self.subTest(expected=expected):
                errors, _ = validate_resolution(run, resolution, self.repo)
                self.assertIn(expected, errors)

    def test_live_multi_path_change_updates_review_contract(self) -> None:
        run = self.run_value(review=True, selected=True)
        run["authority"]["allowed_paths"] = ["file.txt", "decoy.txt"]
        run["execution"]["steps"][0]["paths"] = ["file.txt", "decoy.txt"]
        (self.repo / "file.txt").write_text("changed\n", encoding="utf-8")
        (self.repo / "decoy.txt").write_text("added\n", encoding="utf-8")
        run = self.finish_step(run, ["file.txt", "decoy.txt"])
        resolution = self.resolution(run)
        resolution["change_surfaces"] = []
        semantics = load_semantics()
        resolution["review_profile"] = {
            "selected_lenses": ["standard"],
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload([], ["standard"], semantics)
            ),
        }
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-cas-contract-mismatch", errors)

        surfaces = ["multi-live-path"]
        lenses = ["standard"]
        resolution["review_profile"] = {
            "selected_lenses": lenses,
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload(surfaces, lenses, semantics)
            ),
        }
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertNotIn("blocked-cas-contract-mismatch", errors)

    def test_review_fold_sources_exactly_match_declared_sources(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        resolution["review_folds"][0]["source"]["source_ref"] = "local:other"
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-review-fold-source", errors)

        run["review"]["source_refs"] = ["local:audit-1", "local:audit-1"]
        resolution = self.resolution(run)
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-review-fold-source", errors)

    def test_triage_requires_current_review_fold_evidence(self) -> None:
        run = self.triage_run()
        decision, code = decide(run, None, [], [], None, self.repo)
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-review-fold-missing",
            decision["closure_decision"]["reasons"],
        )

        fold = self.review_fold(run)
        decision, code = decide(run, None, [], [], None, self.repo, [fold])
        self.assertEqual(code, 0, decision)
        closure = decision["closure_decision"]
        self.assertEqual(
            closure["outcomes"]["implementation_outcome"], "not-applicable"
        )
        self.assertEqual(closure["review_basis"], [canonical_digest(fold)])

        changed = copy.deepcopy(fold)
        changed["intent_anchor"]["original_goal"] = "changed review goal"
        changed_decision, code = decide(run, None, [], [], None, self.repo, [changed])
        self.assertEqual(code, 0, changed_decision)
        self.assertNotEqual(
            closure["decision_id"],
            changed_decision["closure_decision"]["decision_id"],
        )

    def test_ask_human_triage_preserves_the_human_owner(self) -> None:
        run = self.triage_run()
        fold = self.review_fold(run, ["finding-1"])
        fold["findings"][0]["disposition"] = "ask-human"
        decision, code = decide(run, None, [], [], None, self.repo, [fold])
        self.assertEqual(code, 2)
        closure = decision["closure_decision"]
        self.assertEqual(closure["verdict"], "continue")
        self.assertEqual(closure["outcomes"]["goal_outcome"], "continue")
        self.assertEqual(closure["outcomes"]["implementation_outcome"], "not-applicable")
        self.assertEqual(closure["outcomes"]["next_owner"], "human")

        blocked = copy.deepcopy(fold)
        blocked["findings"][0]["disposition"] = "blocked"
        blocked["findings"][0]["validity"] = "unproven"
        decision, code = decide(run, None, [], [], None, self.repo, [blocked])
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-review-fold-open",
            decision["closure_decision"]["reasons"],
        )
        self.assertEqual(
            decision["closure_decision"]["outcomes"]["next_owner"],
            "goal-actuating",
        )

        review_run = self.run_value(review=True, selected=True)
        resolution = self.resolution(review_run)
        ask_fold = self.review_fold(review_run, ["finding-1"])
        ask_fold["findings"][0]["disposition"] = "ask-human"
        resolution["review_folds"] = [ask_fold]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(review_run, resolution, self.repo)
        self.assertIn("blocked-review-fold-open", errors)

    def test_blocked_resolution_cannot_complete(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run, strategy="blocked")]
        resolution["outcome"]["status"] = "blocked"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        decision, code = self.review_decision(
            run, resolution, self.review_records(run, resolution)
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-review-resolution-open",
            decision["closure_decision"]["reasons"],
        )

    def test_resolution_status_is_digest_bound(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        clean_digest = canonical_digest(resolution_digest_payload(resolution))
        resolution["outcome"]["status"] = "pending"
        self.assertNotEqual(
            clean_digest,
            canonical_digest(resolution_digest_payload(resolution)),
        )

    def test_completed_review_step_retains_its_admission_resolution(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        records = self.review_records(run, resolution)
        evidence = self.evidence(run)
        decision, code = decide(
            run,
            resolution,
            [evidence],
            records,
            None,
            self.repo,
        )
        self.assertEqual(code, 0, decision)

        missing = copy.deepcopy(run)
        missing["execution"]["steps"][0].pop("review_resolution")
        decision, code = decide(
            missing,
            resolution,
            [evidence],
            records,
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-resolution-binding",
            decision["closure_decision"]["reasons"],
        )

        tampered = copy.deepcopy(run)
        tampered["execution"]["steps"][0]["review_resolution"][
            "resolution_digest"
        ] = "sha256:" + "0" * 64
        decision, code = decide(
            tampered,
            resolution,
            [evidence],
            records,
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-evidence-fold-mismatch",
            decision["closure_decision"]["reasons"],
        )

    def test_pending_multi_owner_resolution_selects_one_current_node(self) -> None:
        run = self.run_value(review=True, selected=True)
        resolution = self.resolution(run)
        fold = self.review_fold(run, ["finding-1", "finding-2"])
        fold["findings"][0]["quotient_key"] = "owner-one"
        fold["findings"][1]["quotient_key"] = "owner-two"
        fold["findings"][1]["owner_boundary"] = "other-owner"
        fold["compression"]["equivalence_classes"] = [
            {
                "quotient_key": "owner-one",
                "finding_ids": ["finding-1"],
                "owner_boundary": "actuating",
                "law_family": "closure",
            },
            {
                "quotient_key": "owner-two",
                "finding_ids": ["finding-2"],
                "owner_boundary": "other-owner",
                "law_family": "closure",
            },
        ]
        resolution["review_folds"] = [fold]
        resolution["finding_ids"] = ["finding-1", "finding-2"]
        first = self.decision(run, finding_ids=["finding-1"])
        second = self.decision(run, finding_ids=["finding-2"])
        second["decision_id"] = "decision-2"
        second["owner_boundary"] = "other-owner"
        second["selected_work_node"] = None
        resolution["decisions"] = [first, second]
        resolution["outcome"]["status"] = "pending"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])
        self.assertEqual(derived["selected_work_nodes"], ["step-1"])

        second["strategy"] = "blocked"
        second["blockers"] = ["human decision required"]
        resolution["outcome"]["status"] = "blocked"
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-resolution-node-under-blocker", errors)

        second["strategy"] = "local-repair"
        second["blockers"] = []
        resolution["outcome"]["status"] = "pending"

        second["selected_work_node"] = {
            "node_id": "step-2",
            "run_id": run["run_id"],
            "owner_boundary": "other-owner",
            "paths": ["file.txt"],
            "verifier": ["test"],
        }
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-resolution-node-multiple", errors)

        resolution["outcome"]["status"] = "resolved"
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        completed = [
            {
                "step_id": node_id,
                "effect": "edit",
                "owner_boundary": owner,
                "paths": ["file.txt"],
                "verifier": ["test"],
                "review_resolution": {
                    "resolution_id": resolution["resolution_id"],
                    "resolution_digest": "sha256:" + "a" * 64,
                },
            }
            for node_id, owner in (
                ("step-1", "actuating"),
                ("step-2", "other-owner"),
            )
        ]
        with patch(
            "actuating_gate.validate_run",
            return_value=(
                [],
                {"live_changed_paths": ["file.txt"], "completed_steps": completed},
            ),
        ):
            errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])
        self.assertEqual(derived["selected_work_nodes"], ["step-1", "step-2"])

    def test_replacement_addition_is_scoped_to_its_owner_decision(self) -> None:
        run = self.run_value(review=True, selected=True)
        resolution = self.resolution(run)
        fold = self.review_fold(run, ["finding-1", "finding-2"])
        fold["findings"][0]["quotient_key"] = "local-owner"
        fold["findings"][1]["quotient_key"] = "replacement-owner"
        fold["findings"][1]["owner_boundary"] = "other-owner"
        fold["compression"]["equivalence_classes"] = [
            {
                "quotient_key": "local-owner",
                "finding_ids": ["finding-1"],
                "owner_boundary": "actuating",
                "law_family": "closure",
            },
            {
                "quotient_key": "replacement-owner",
                "finding_ids": ["finding-2"],
                "owner_boundary": "other-owner",
                "law_family": "closure",
            },
        ]
        resolution["review_folds"] = [fold]
        resolution["finding_ids"] = ["finding-1", "finding-2"]
        local = self.decision(run, finding_ids=["finding-1"])
        replacement = self.decision(
            run, strategy="replacement-kernel", finding_ids=["finding-2"]
        )
        replacement["decision_id"] = "decision-2"
        replacement["owner_boundary"] = "other-owner"
        replacement["selected_work_node"] = None
        replacement["abstraction_account"] = [
            {
                "abstraction": "old-helper",
                "disposition": "replace",
                "obligation_id": "owner-law",
            }
        ]
        resolution["decisions"] = [local, replacement]
        resolution["outcome"]["status"] = "pending"
        balance = resolution["outcome"]["semantic_balance"]
        balance["covered_liabilities"] = ["invariant-gap"]
        balance["added_constructs"] = [
            {
                "name": "replacement-kernel",
                "obligation_id": "owner-law",
                "obligation_ref": "goal:owner-law",
                "replaces": "old-helper",
            }
        ]
        balance["required_retirements"] = ["old-helper"]
        balance["completed_retirements"] = ["old-helper"]
        surfaces = sorted(set(resolution["change_surfaces"] + ["replacement-kernel"]))
        semantics = load_semantics()
        lenses = ["standard"]
        resolution["review_profile"] = {
            "selected_lenses": lenses,
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload(surfaces, lenses, semantics)
            ),
        }
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])

    def test_pending_replacement_accounts_for_retirement_debt(self) -> None:
        run = self.run_value(review=True, selected=True)
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        decision = self.decision(run, strategy="replacement-kernel")
        decision["abstraction_account"] = [
            {
                "abstraction": "old-gate",
                "disposition": "replace",
                "obligation_id": "artifact-currentness",
            }
        ]
        resolution["decisions"] = [decision]
        resolution["outcome"]["status"] = "pending"
        balance = resolution["outcome"]["semantic_balance"]
        balance["covered_liabilities"] = ["invariant-gap"]
        balance["added_constructs"] = [
            {
                "name": "path-state-map",
                "obligation_id": "artifact-currentness",
                "obligation_ref": "goal:preserve-live-state",
                "replaces": "old-gate",
            }
        ]
        balance["required_retirements"] = ["old-gate"]
        balance["completed_retirements"] = []
        balance["dominated_remaining"] = ["old-gate"]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        surfaces = sorted(
            set(resolution["change_surfaces"] + ["replacement-kernel"])
        )
        semantics = load_semantics()
        lenses = ["standard"]
        resolution["review_profile"] = {
            "selected_lenses": lenses,
            "review_contract_fingerprint": canonical_digest(
                review_contract_payload(surfaces, lenses, semantics)
            ),
        }
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])

        resolution["outcome"]["status"] = "resolved"
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-semantic-retirements", errors)

    def test_remediation_plan_cannot_select_executable_node(self) -> None:
        run = self.run_value()
        run["mode"] = "remediation-plan"
        run["authority"]["mutation_allowed"] = False
        run["execution"] = {
            "kind": "none",
            "selected_step_id": None,
            "steps": [],
        }
        run["review"]["source_refs"] = ["review:1"]
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        resolution["decisions"] = [self.decision(run, path="file.txt/../outside.txt")]
        resolution["outcome"]["status"] = "resolved"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-no-code-mutation", errors)

    def test_pending_remediation_plan_is_a_terminal_no_code_outcome(self) -> None:
        run = self.run_value()
        run["mode"] = "remediation-plan"
        run["authority"]["mutation_allowed"] = False
        run["execution"] = {
            "kind": "none",
            "selected_step_id": None,
            "steps": [],
        }
        run["review"]["source_refs"] = ["local:audit-1"]
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        decision = self.decision(run)
        decision["selected_work_node"] = None
        resolution["decisions"] = [decision]
        resolution["outcome"]["status"] = "pending"
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )

        closure, code = decide(run, resolution, [], [], None, self.repo)
        self.assertEqual(code, 0, closure)
        self.assertEqual(closure["closure_decision"]["verdict"], "complete")
        self.assertEqual(
            closure["closure_decision"]["outcomes"]["implementation_outcome"],
            "not-applicable",
        )

        material_run = self.complete_step(
            self.run_value(review=True, selected=True)
        )
        material_resolution = self.resolution(material_run)
        self.bind_resolution_findings(
            material_run,
            material_resolution,
            ["finding-1"],
        )
        material_resolution["decisions"] = [self.decision(material_run)]
        material_resolution["outcome"]["status"] = "pending"
        material_resolution["outcome"]["semantic_balance"][
            "covered_liabilities"
        ] = ["invariant-gap"]
        material_resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(material_resolution)
        )
        closure, code = self.review_decision(
            material_run,
            material_resolution,
            self.review_records(material_run, material_resolution),
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-review-resolution-open",
            closure["closure_decision"]["reasons"],
        )

    def review_records(
        self,
        run: dict,
        resolution: dict,
    ) -> list[dict]:
        return self.cas_snapshot(
            [
                self.cas_record(run, resolution, "standard", ordinal)
                for ordinal in (1, 2, 3)
            ]
        )

    def cas_snapshot(self, rows: list[dict]) -> list[dict]:
        snapshot = {
            "schema": "CAS-LIST-v1",
            "records": rows,
            "recordRefs": [
                {
                    "recordId": row["recordId"],
                    "recordPath": f"/ledger/{row['recordId']}.json",
                    "proofCreditEligible": True,
                }
                for row in rows
            ],
        }
        self.live_cas_snapshot = snapshot
        return [snapshot]

    def review_decision(
        self, run: dict, resolution: dict, records: list[dict]
    ) -> tuple[dict, int]:
        return decide(
            run,
            resolution,
            [self.evidence(run)],
            records,
            None,
            self.repo,
        )

    def test_three_distinct_standard_units_close(
        self,
    ) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        decision, code = self.review_decision(
            run, resolution, self.review_records(run, resolution)
        )
        self.assertEqual(code, 0, decision)
        self.assertEqual(
            decision["closure_decision"]["verdict"],
            "complete",
        )
        self.assertEqual(
            len(decision["closure_decision"]["review_basis"]),
            3,
        )

    def test_artifact_is_rebound_after_live_cas_query(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        records = self.review_records(run, resolution)

        def mutate_during_cas(*_args: object) -> dict:
            (self.repo / "file.txt").write_text("late mutation\n", encoding="utf-8")
            return self.live_cas_snapshot

        self.live_cas_mock.side_effect = mutate_during_cas
        try:
            decision, code = self.review_decision(run, resolution, records)
        finally:
            subprocess.run(
                ["git", "restore", "file.txt"], cwd=self.repo, check=True
            )
            self.live_cas_mock.side_effect = lambda *_: self.live_cas_snapshot
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-run-stale:state_fingerprint",
            decision["closure_decision"]["reasons"],
        )

    def test_gate_fixture_matches_installed_cas_rer_schema(self) -> None:
        if shutil.which("cas") is None:
            self.skipTest("cas is not installed")
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        path = self.repo / "cas-rer.json"
        record = self.cas_record(run, resolution, "standard", 1)
        record.pop("workflowBinding")
        path.write_text(json.dumps(record), encoding="utf-8")
        result = subprocess.run(
            [
                "cas",
                "review_session",
                "validate-record",
                "--record",
                str(path),
                "--json",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_producer_real_unbound_cas_cannot_close_actuation(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        records = self.review_records(run, resolution)
        records[0]["records"][0].pop("workflowBinding")
        decision, code = self.review_decision(run, resolution, records)
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-cas-workflow-unbound",
            decision["closure_decision"]["reasons"],
        )

    def test_individual_cas_records_are_not_an_exhaustive_snapshot(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        rows = self.review_records(run, resolution)[0]["records"]
        decision, code = self.review_decision(run, resolution, rows)
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-cas-evidence-set-incomplete",
            decision["closure_decision"]["reasons"],
        )

    def test_duplicate_or_wrong_contract_cas_is_rejected(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        records = self.review_records(run, resolution)
        rows = records[0]["records"]
        rows[1]["recordId"] = rows[0]["recordId"]
        rows[2]["workflowBinding"]["selectedLenses"] = [
            "footgun-finder",
            "standard",
        ]
        decision, code = self.review_decision(run, resolution, records)
        self.assertEqual(code, 2)
        reasons = decision["closure_decision"]["reasons"]
        self.assertIn("blocked-cas-unit-duplicate", reasons)
        self.assertIn("blocked-cas-contract-mismatch", reasons)

    def test_caller_relabelled_standard_record_gets_no_auxiliary_credit(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        rows = self.review_records(run, resolution)[0]["records"]
        relabelled = copy.deepcopy(rows[-1])
        relabelled["recordId"] = "rer_relabelled_auxiliary"
        relabelled["createdAt"] = "unix-ns:7"
        relabelled["updatedAt"] = "unix-ns:7"
        relabelled["attempt"]["attemptId"] = "attempt-relabelled-auxiliary"
        relabelled["workflowBinding"]["reviewLane"] = "footgun-finder"
        relabelled["workflowBinding"]["lensContract"] = "footgun-lens-v1"
        records = self.cas_snapshot([*rows, relabelled])
        decision, code = self.review_decision(run, resolution, records)
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-cas-lane",
            decision["closure_decision"]["reasons"],
        )

    def test_current_epoch_findings_cannot_be_cleared_by_clean_suffix(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        finding = self.cas_record(run, resolution, "standard", 1)
        finding["verdict"] = {
            "tupleVerdictExists": True,
            "status": "findings",
            "clean": False,
            "findingCount": 1,
            "findings": [{"title": "unresolved standard finding"}],
        }
        clean = [
            self.cas_record(run, resolution, "standard", ordinal)
            for ordinal in range(2, 5)
        ]
        decision, code = self.review_decision(
            run, resolution, self.cas_snapshot([finding, *clean])
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-cas-findings-unresolved",
            decision["closure_decision"]["reasons"],
        )

    def test_superseded_epoch_is_partitioned_before_credit(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        resolution_errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(resolution_errors, [])
        current = self.review_records(run, resolution)[0]["records"]

        old_clean = self.cas_record(run, resolution, "standard", 0)
        old_clean["workflowBinding"]["resolutionDigest"] = "sha256:superseded"
        snapshot = self.cas_snapshot([old_clean, *current])[0]
        errors, basis = cas_errors(snapshot, run, resolution, derived)
        self.assertEqual(errors, [])
        self.assertNotIn(old_clean["recordId"], basis)

        old_finding = copy.deepcopy(old_clean)
        old_finding["recordId"] = "rer_superseded_finding"
        old_finding["attempt"]["attemptId"] = "attempt-superseded-finding"
        old_finding["verdict"] = {
            "tupleVerdictExists": True,
            "status": "findings",
            "clean": False,
            "findingCount": 1,
            "findings": [{"title": "old finding"}],
        }
        snapshot = self.cas_snapshot([old_finding, *current])[0]
        errors, _ = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-findings-unresolved", errors)

        run["review"]["source_refs"] = [old_finding["recordId"]]
        clean_fold = self.review_fold(run)
        clean_fold["source"].update(
            {
                "backend": "cas",
                "source_batch_id": old_finding["recordId"],
                "source_state": "clean",
                "source_ref": old_finding["recordId"],
            }
        )
        resolution["review_folds"].append(clean_fold)
        errors, _ = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-findings-unresolved", errors)

        resolution["review_folds"][-1] = self.cas_review_fold(run, old_finding)
        errors, basis = cas_errors(snapshot, run, resolution, derived)
        self.assertEqual(errors, [])
        self.assertNotIn(old_finding["recordId"], basis)

        resolution["review_folds"][-1]["findings"][0]["source_ref"] = (
            "wrong-finding"
        )
        errors, _ = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-findings-unresolved", errors)

    def test_foreign_run_is_ignored_before_tuple_accounting(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        resolution_errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(resolution_errors, [])
        current = self.review_records(run, resolution)[0]["records"]
        foreign = copy.deepcopy(current[-1])
        foreign["recordId"] = "rer_foreign_run"
        foreign["createdAt"] = "unix-ns:7"
        foreign["attempt"]["attemptId"] = "attempt-foreign-run"
        foreign["workflowBinding"]["actuationRunId"] = "another-run"
        foreign["tuple"].update(
            {
                "repoRealpath": "/another/repo",
                "baseSha": "foreign-base",
                "headSha": "foreign-head",
                "targetFingerprint": "target=foreign",
                "tupleCurrentAtRecordTime": False,
            }
        )
        foreign["verdict"] = {
            "tupleVerdictExists": True,
            "status": "findings",
            "clean": False,
            "findingCount": 1,
            "findings": [{"title": "foreign finding"}],
        }
        snapshot = self.cas_snapshot([*current, foreign])[0]
        errors, basis = cas_errors(snapshot, run, resolution, derived)
        self.assertEqual(errors, [])
        self.assertEqual(basis, [row["recordId"] for row in current])

    def test_current_proof_credit_filters_clean_not_findings(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        resolution_errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(resolution_errors, [])
        snapshot = self.review_records(run, resolution)[0]
        standard = [
            row
            for row in snapshot["records"]
            if row["workflowBinding"]["reviewLane"] == "standard"
        ]
        latest = standard[-1]
        ref = next(
            row
            for row in snapshot["recordRefs"]
            if row["recordId"] == latest["recordId"]
        )
        ref["proofCreditEligible"] = False
        errors, basis = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-clean-streak", errors)
        self.assertNotIn(latest["recordId"], basis)

        latest["verdict"] = {
            "tupleVerdictExists": True,
            "status": "findings",
            "clean": False,
            "findingCount": 1,
            "findings": [{"title": "drifted finding remains visible"}],
        }
        errors, _ = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-findings-unresolved", errors)

    def test_saved_cas_snapshot_must_equal_live_list(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        saved = copy.deepcopy(self.review_records(run, resolution))
        rows = self.live_cas_snapshot["records"]
        later = self.cas_record(run, resolution, "standard", 7)
        later["verdict"] = {
            "tupleVerdictExists": True,
            "status": "findings",
            "clean": False,
            "findingCount": 1,
            "findings": [{"title": "later finding"}],
        }
        self.cas_snapshot(rows + [later])
        decision, code = self.review_decision(run, resolution, saved)
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-cas-evidence-set-incomplete",
            decision["closure_decision"]["reasons"],
        )

    def test_cas_attempt_identity_and_lane_are_strict(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        cases = []

        records = self.review_records(run, resolution)
        records[0]["records"][0]["createdAt"] = True
        cases.append((records, "blocked-cas-attempt-identity"))

        records = self.review_records(run, resolution)
        rows = records[0]["records"]
        rows[1]["createdAt"] = rows[0]["createdAt"]
        cases.append((records, "blocked-cas-attempt-identity"))

        records = self.review_records(run, resolution)
        records[0]["records"][1]["workflowBinding"]["reviewLane"] = "unknown-lane"
        cases.append((records, "blocked-cas-lane"))

        records = self.review_records(run, resolution)
        records[0]["records"][0]["workflowBinding"]["artifactStateFingerprint"] = (
            "sha256:stale"
        )
        cases.append((records, "blocked-cas-clean-streak"))

        records = self.review_records(run, resolution)
        records[0]["records"][0]["tuple"]["targetFingerprint"] = (
            "target=different;head=current;base=accepted"
        )
        cases.append((records, "blocked-cas-evidence-set-incomplete"))

        records = self.review_records(run, resolution)
        records[0]["records"][0]["verdict"]["findingCount"] = 1
        records[0]["records"][0]["verdict"]["findings"] = [{"title": "hidden"}]
        cases.append((records, "blocked-cas-unit-unnormalized"))

        records = self.review_records(run, resolution)
        records[0]["records"][0]["principal"]["accountFingerprint"] = None
        cases.append((records, "blocked-cas-source-invalid"))

        for records, expected in cases:
            self.live_cas_snapshot = records[0]
            decision, code = self.review_decision(run, resolution, records)
            with self.subTest(expected=expected):
                self.assertEqual(code, 2)
                self.assertIn(expected, decision["closure_decision"]["reasons"])

    def test_scalar_clean_count_has_no_effect(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        run["review"]["standard_clean_runs_count"] = 3
        resolution = self.resolution(run)
        decision, code = self.review_decision(run, resolution, [])
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-cas-evidence-set-incomplete",
            decision["closure_decision"]["reasons"],
        )

    def test_continuation_verdict_cannot_complete_goal(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        run["execution"]["steps"][0]["verdict"] = "continue"
        decision, code = decide(
            run,
            None,
            [self.evidence(run)],
            [],
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-step-not-ready-for-closure",
            decision["closure_decision"]["reasons"],
        )

    def test_failed_review_closeout_step_cannot_complete_goal(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        run["execution"]["steps"][0]["verdict"] = "regress"
        resolution = self.resolution(run)
        decision, code = self.review_decision(
            run, resolution, self.review_records(run, resolution)
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-step-not-ready-for-closure",
            decision["closure_decision"]["reasons"],
        )

    def test_evidence_must_match_the_completed_step(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        evidence = self.evidence(run)
        evidence["evidence_fold"]["step_id"] = "other-step"
        decision, code = decide(
            run,
            None,
            [evidence],
            [],
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-evidence-fold-mismatch",
            decision["closure_decision"]["reasons"],
        )

    def test_evidence_requires_full_current_binding_and_proof_shape(
        self,
    ) -> None:
        run = self.complete_step(self.run_value(selected=True))
        cases = []

        evidence = self.evidence(run)
        evidence["evidence_fold"].pop("version")
        cases.append((evidence, "blocked-evidence-fold-version"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["artifact_state"]["repo"] = "wrong"
        cases.append((evidence, "blocked-evidence-fold-stale"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["proof"].pop("proof_gaps")
        cases.append((evidence, "blocked-evidence-fold-incomplete"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["artifact_state"]["changed_paths"] = []
        cases.append((evidence, "blocked-evidence-fold-change-mismatch"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["progress"]["status"] = "regress"
        cases.append((evidence, "blocked-evidence-fold-incomplete"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["evidence"]["commands"]["passed"] = []
        cases.append((evidence, "blocked-evidence-fold-incomplete"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["evidence"]["commands"]["failed"] = ["test"]
        cases.append((evidence, "blocked-evidence-fold-incomplete"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["evidence"]["commands"]["passed"] = ["   "]
        cases.append((evidence, "blocked-evidence-fold-incomplete"))

        evidence = self.evidence(run)
        evidence["evidence_fold"]["evidence"]["observed"] = []
        cases.append((evidence, "blocked-evidence-fold-shape"))

        evidence = self.evidence(run)
        orphan = copy.deepcopy(evidence)
        orphan["evidence_fold"]["evidence_id"] = "orphan"
        cases.append(
            (
                [evidence, orphan],
                "blocked-evidence-fold-orphan",
            )
        )

        for evidence_value, expected in cases:
            values = (
                evidence_value if isinstance(evidence_value, list) else [evidence_value]
            )
            decision, code = decide(
                run,
                None,
                values,
                [],
                None,
                self.repo,
            )
            with self.subTest(expected=expected):
                self.assertEqual(code, 2)
                self.assertIn(expected, decision["closure_decision"]["reasons"])

    def test_scope_traversal_and_scalar_public_effect_are_rejected(
        self,
    ) -> None:
        run = self.run_value(selected=True)
        run["execution"]["steps"][0]["paths"] = ["file.txt/../outside.txt"]
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-out-of-scope", errors)

        run = self.run_value(selected=True)
        run["execution"]["steps"][0]["performed_public_effects"] = ["pr-update"]
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-public-effect-shape", errors)

        run = self.run_value(selected=True)
        run["execution"]["steps"][0]["paths"] = []
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-paths-missing", errors)

        run = self.complete_step(self.run_value(selected=True))
        run["authority"]["allowed_paths"] = ["file.txt", "outside.txt"]
        run["execution"]["steps"][0]["changed_paths"] = ["outside.txt"]
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_mutation_paths_stay_inside_the_artifact_observer(self) -> None:
        run = self.run_value(selected=True)
        run["authority"]["allowed_paths"] = ["."]
        errors, _ = validate_run(run, self.repo)
        self.assertEqual(errors, [])
        self.assertTrue(path_allowed_root(".", self.repo))
        self.assertTrue(path_allowed("file.txt", ["."], self.repo))

        run["execution"]["steps"][0]["paths"] = [".git/hooks/pre-commit"]
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-out-of-scope", errors)

        with tempfile.TemporaryDirectory() as outside:
            os.symlink(outside, self.repo / "escape")
            for target in ("escape", "escape/secret.txt"):
                run = self.run_value(selected=True)
                run["authority"]["allowed_paths"] = ["."]
                run["execution"]["steps"][0]["paths"] = [target]
                errors, _ = validate_run(run, self.repo)
                with self.subTest(target=target):
                    self.assertIn("blocked-step-out-of-scope", errors)

            run = self.run_value(review=True, selected=True)
            run["authority"]["allowed_paths"] = ["."]
            resolution = self.resolution(run)
            self.bind_resolution_findings(run, resolution, ["finding-1"])
            resolution["decisions"] = [
                self.decision(run, path="escape/secret.txt")
            ]
            resolution["outcome"]["status"] = "pending"
            resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
                "invariant-gap"
            ]
            resolution["outcome"]["resolution_digest"] = canonical_digest(
                resolution_digest_payload(resolution)
            )
            errors, _ = validate_resolution(run, resolution, self.repo)
            self.assertIn("blocked-resolution-out-of-scope", errors)

    def test_dirty_scope_overlap_is_symmetric_and_filesystem_aware(self) -> None:
        scope = self.repo / "scope"
        scope.mkdir()
        os.symlink("../file.txt", scope / "link")
        self.assertTrue(paths_overlap("scope/link", "scope", self.repo))
        self.assertFalse(path_allowed("scope/link", ["scope"], self.repo))

        self.assertTrue(paths_overlap("sm", "sm/tracked.txt", self.repo))
        self.assertTrue(paths_overlap("sm/tracked.txt", "sm", self.repo))

        canonical = self.repo / "CaseScope"
        canonical.mkdir()
        case_alias = self.repo / "casescope"
        if not case_alias.exists():
            os.symlink("CaseScope", case_alias)
        self.assertTrue(paths_overlap("CaseScope", "casescope/file.txt", self.repo))

        distinct = self.repo / "Distinct"
        distinct.mkdir()
        distinct_alias = self.repo / "distinct"
        if not distinct_alias.exists():
            distinct_alias.mkdir()
            self.assertFalse(
                paths_overlap("Distinct", "distinct/file.txt", self.repo)
            )

    def test_dirty_symlink_descendant_blocks_full_closure(self) -> None:
        scope = self.repo / "scope"
        scope.mkdir()
        os.symlink("../file.txt", scope / "link")
        run = self.run_value(review=True, selected=True)
        run["authority"]["allowed_paths"] = ["scope"]
        run["execution"]["steps"][0]["paths"] = ["scope"]
        run = self.finish_verify_step(run)
        resolution = self.resolution(run)
        evidence = self.evidence(run)
        evidence["evidence_fold"]["artifact_state"]["changed_paths"] = []

        decision, code = decide(
            run,
            resolution,
            [evidence],
            self.review_records(run, resolution),
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-artifact-uncommitted",
            decision["closure_decision"]["reasons"],
        )

    def test_unclaimed_live_path_change_is_rejected(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        (self.repo / "outside.txt").write_text("outside\n", encoding="utf-8")
        current = self.artifact()
        run["artifact"] = current
        run["execution"]["steps"][0]["state_after"] = current
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_claimed_noop_edit_is_rejected(self) -> None:
        run = self.finish_step(self.run_value(selected=True), ["file.txt"])
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_dangling_untracked_symlink_changes_state_fingerprint(self) -> None:
        before = self.artifact()["state_fingerprint"]
        os.symlink("missing-target", self.repo / "dangling-link")
        after = self.artifact()["state_fingerprint"]
        self.assertNotEqual(before, after)

    def test_untracked_fingerprint_is_length_framed_and_repo_rooted(self) -> None:
        (self.repo / "a").write_bytes(b"X\0UNTRACKED\0b\0Y")
        first = self.artifact()
        (self.repo / "a").write_bytes(b"X")
        (self.repo / "b").write_bytes(b"Y")
        second = self.artifact()
        self.assertNotEqual(first["state_fingerprint"], second["state_fingerprint"])

        subdir = self.repo / "subdir"
        subdir.mkdir()
        from_subdir = live_artifact(subdir, self.base)
        self.assertEqual(from_subdir["repo"], str(self.repo.resolve()))
        self.assertEqual(
            from_subdir["state_fingerprint"],
            self.artifact()["state_fingerprint"],
        )

    def test_untracked_executable_mode_changes_state_fingerprint(self) -> None:
        path = self.repo / "script"
        path.write_text("exit 0\n", encoding="utf-8")
        path.chmod(0o644)
        before = self.artifact()["state_fingerprint"]
        path.chmod(0o755)
        after = self.artifact()["state_fingerprint"]
        self.assertNotEqual(before, after)

    def test_submodule_revision_and_dirty_content_change_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as source_dir:
            source = Path(source_dir)
            subprocess.run(["git", "init", "-q"], cwd=source, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=source,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=source, check=True
            )
            tracked = source / "tracked.txt"
            commits = []
            for index in range(1, 4):
                tracked.write_text(f"revision-{index}\n", encoding="utf-8")
                subprocess.run(["git", "add", "tracked.txt"], cwd=source, check=True)
                subprocess.run(
                    ["git", "commit", "-qm", f"revision {index}"],
                    cwd=source,
                    check=True,
                )
                commits.append(
                    subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], cwd=source, text=True
                    ).strip()
                )

            subprocess.run(
                [
                    "git",
                    "-c",
                    "protocol.file.allow=always",
                    "submodule",
                    "add",
                    "-q",
                    str(source),
                    "sm",
                ],
                cwd=self.repo,
                check=True,
            )
            subprocess.run(
                ["git", "-C", "sm", "checkout", "-q", commits[0]],
                cwd=self.repo,
                check=True,
            )
            subprocess.run(
                ["git", "add", ".gitmodules", "sm"], cwd=self.repo, check=True
            )
            subprocess.run(
                ["git", "commit", "-qm", "add submodule"], cwd=self.repo, check=True
            )
            self.base = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True
            ).strip()

            fingerprints = []
            for commit in commits[1:]:
                subprocess.run(
                    ["git", "-C", "sm", "checkout", "-q", commit],
                    cwd=self.repo,
                    check=True,
                )
                fingerprints.append(self.artifact()["state_fingerprint"])
            self.assertNotEqual(*fingerprints)

            dirty = self.repo / "sm" / "tracked.txt"
            dirty.write_text("dirty-a\n", encoding="utf-8")
            dirty_a = self.artifact()["state_fingerprint"]
            dirty.write_text("dirty-b\n", encoding="utf-8")
            dirty_b = self.artifact()["state_fingerprint"]
            self.assertNotEqual(dirty_a, dirty_b)

    def test_index_transition_changes_state_and_hunk_layer(self) -> None:
        path = self.repo / "file.txt"
        path.write_text("changed\n", encoding="utf-8")
        before = self.artifact()
        self.assertTrue(
            any(":worktree:" in hunk for hunk in live_hunk_ids(self.repo, self.base))
        )
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        after = self.artifact()
        self.assertNotEqual(before["state_fingerprint"], after["state_fingerprint"])
        self.assertIn(
            "blocked-run-stale:state_fingerprint",
            binding_errors(before, self.repo, "blocked-run")[0],
        )
        self.assertTrue(
            any(":index:" in hunk for hunk in live_hunk_ids(self.repo, self.base))
        )
        subprocess.run(["git", "reset", "--", "file.txt"], cwd=self.repo, check=True)
        self.assertEqual(
            before["state_fingerprint"], self.artifact()["state_fingerprint"]
        )

    def test_rename_inventory_preserves_both_path_identities(self) -> None:
        source = self.repo / "outside" / "source.txt"
        source.parent.mkdir()
        source.write_text("source\n", encoding="utf-8")
        subprocess.run(["git", "add", "outside/source.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "add rename source"],
            cwd=self.repo,
            check=True,
        )
        self.base = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True
        ).strip()

        run = self.run_value(selected=True)
        destination = self.repo / "allowed" / "destination.txt"
        destination.parent.mkdir()
        subprocess.run(
            ["git", "mv", "outside/source.txt", "allowed/destination.txt"],
            cwd=self.repo,
            check=True,
        )
        run["authority"]["allowed_paths"] = ["allowed/destination.txt"]
        step = run["execution"]["steps"][0]
        step["paths"] = ["allowed/destination.txt"]
        run = self.finish_step(run, ["allowed/destination.txt"])

        states = live_path_states(self.repo, self.base)
        self.assertEqual(
            set(states),
            {"allowed/destination.txt", "outside/source.txt"},
        )
        hunks = live_hunk_ids(self.repo, self.base)
        self.assertTrue(any(row.startswith("allowed/destination.txt:") for row in hunks))
        self.assertTrue(any(row.startswith("outside/source.txt:") for row in hunks))
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_committing_pre_staged_path_changes_its_state(self) -> None:
        outside = self.repo / "outside.txt"
        outside.write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "outside.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "add outside path"],
            cwd=self.repo,
            check=True,
        )
        self.base = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True
        ).strip()

        outside.write_text("user staged\n", encoding="utf-8")
        subprocess.run(["git", "add", "outside.txt"], cwd=self.repo, check=True)
        run = self.run_value(selected=True)
        initial_outside = run["artifact_initial_path_states"]["outside.txt"]
        (self.repo / "file.txt").write_text("claimed\n", encoding="utf-8")
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "commit selected step"],
            cwd=self.repo,
            check=True,
        )
        run = self.finish_step(run, ["file.txt"])

        self.assertNotEqual(
            initial_outside,
            live_path_states(self.repo, self.base)["outside.txt"],
        )
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_initial_dirty_path_mutation_must_be_claimed(self) -> None:
        for final_content in ("overwritten\n", "base\n"):
            with self.subTest(final_content=final_content):
                run = self.initial_dirty_run()
                (self.repo / "decoy.txt").write_text("claimed\n", encoding="utf-8")
                (self.repo / "file.txt").write_text(final_content, encoding="utf-8")
                errors, _ = validate_run(
                    self.finish_step(run, ["decoy.txt"]), self.repo
                )
                self.assertIn("blocked-step-change-mismatch", errors)
                (self.repo / "decoy.txt").unlink()
                (self.repo / "file.txt").write_text("base\n", encoding="utf-8")

    def test_untouched_initial_dirty_path_remains_user_owned(self) -> None:
        run = self.initial_dirty_run()
        (self.repo / "decoy.txt").write_text("claimed\n", encoding="utf-8")
        run = self.finish_step(run, ["decoy.txt"])
        errors, _ = validate_run(run, self.repo)
        self.assertNotIn("blocked-step-change-mismatch", errors)

    def test_initial_path_state_map_is_fingerprint_bound(self) -> None:
        (self.repo / "file.txt").write_text("user-dirty\n", encoding="utf-8")
        run = self.run_value(selected=True)
        run["artifact_initial_path_states"]["file.txt"] = "sha256:" + "0" * 64
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-run-initial-artifact", errors)

    def test_initial_repo_base_and_branch_remain_authoritative(self) -> None:
        for field, value in (
            ("repo", "/tmp/other"),
            ("base_sha", "0" * 40),
            ("branch", "other"),
        ):
            run = self.run_value(selected=True)
            run["artifact_initial"] = copy.deepcopy(run["artifact_initial"])
            run["artifact_initial"][field] = value
            errors, _ = validate_run(run, self.repo)
            with self.subTest(field=field):
                self.assertIn("blocked-run-stale", errors)

    def test_publication_hands_off_to_ship(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        run["review"]["publication_requested"] = True
        decision, code = decide(
            run,
            None,
            [self.evidence(run)],
            [],
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-artifact-uncommitted",
            decision["closure_decision"]["reasons"],
        )

        run = self.commit_step(run)
        decision, code = decide(
            run,
            None,
            [self.evidence(run)],
            [],
            None,
            self.repo,
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            decision["closure_decision"]["verdict"],
            "ready-to-ship",
        )
        self.assertEqual(
            decision["closure_decision"]["outcomes"]["next_owner"],
            "ship",
        )

    def test_publication_requires_ship_handoff_authority(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        run["authority"]["public_effects_allowed"] = []
        run["review"]["publication_requested"] = True
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-publication-intent", errors)

    def test_publication_intent_requires_exact_boolean(self) -> None:
        run = self.run_value(selected=True)
        run["review"]["publication_requested"] = 1
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-publication-intent", errors)

    def test_no_code_modes_cannot_request_publication(self) -> None:
        for mode in ("triage", "remediation-plan"):
            run = self.triage_run()
            run["mode"] = mode
            run["review"]["publication_requested"] = True
            errors, _ = validate_run(run, self.repo)
            with self.subTest(mode=mode):
                self.assertIn("blocked-publication-intent", errors)

    def test_review_and_ship_reject_uncommitted_step_paths(self) -> None:
        review_run = self.complete_step(self.run_value(review=True, selected=True))
        review_resolution = self.resolution(review_run)
        (self.repo / "file.txt").write_text("dirty after review\n", encoding="utf-8")
        decision, code = self.review_decision(
            review_run,
            review_resolution,
            self.review_records(review_run, review_resolution),
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-artifact-uncommitted",
            decision["closure_decision"]["reasons"],
        )

        subprocess.run(["git", "restore", "file.txt"], cwd=self.repo, check=True)
        ship_run = self.run_value(selected=True)
        (self.repo / "file.txt").write_text("ship dirty\n", encoding="utf-8")
        ship_run = self.finish_step(ship_run, ["file.txt"])
        ship_run["review"]["publication_requested"] = True
        decision, code = decide(
            ship_run,
            None,
            [self.evidence(ship_run)],
            [],
            {"ship_record": {}},
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-artifact-uncommitted",
            decision["closure_decision"]["reasons"],
        )

    def test_verify_only_review_rejects_dirty_target_not_unrelated_dirt(self) -> None:
        def completed_verify_run() -> dict:
            return self.finish_verify_step(
                self.run_value(review=True, selected=True)
            )

        (self.repo / "file.txt").write_text("initial target dirt\n", encoding="utf-8")
        run = completed_verify_run()
        resolution = self.resolution(run)
        evidence = self.evidence(run)
        evidence["evidence_fold"]["artifact_state"]["changed_paths"] = []
        decision, code = decide(
            run,
            resolution,
            [evidence],
            self.review_records(run, resolution),
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-artifact-uncommitted",
            decision["closure_decision"]["reasons"],
        )

        subprocess.run(["git", "restore", "file.txt"], cwd=self.repo, check=True)
        (self.repo / "outside.txt").write_text("user-owned\n", encoding="utf-8")
        run = completed_verify_run()
        resolution = self.resolution(run)
        evidence = self.evidence(run)
        evidence["evidence_fold"]["artifact_state"]["changed_paths"] = []
        decision, code = decide(
            run,
            resolution,
            [evidence],
            self.review_records(run, resolution),
            None,
            self.repo,
        )
        self.assertEqual(code, 0, decision)

    def test_unrequested_resolution_and_ship_are_not_ignored(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        decision, code = decide(
            run,
            {"outcome": {"status": "blocked"}},
            [self.evidence(run)],
            [],
            {"ship_record": {}},
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-unexpected-input",
            decision["closure_decision"]["reasons"],
        )

    def test_supplied_ship_result_requires_a_pr_url(self) -> None:
        run = self.complete_step(self.run_value(selected=True))
        ship = {
            "ship_record": {
                "record_version": "SHIP-v1",
                "actuation_review": {
                    "actuation_run_id": run["run_id"],
                    "state_fingerprint": run["artifact"]["state_fingerprint"],
                    "review_contract_fingerprint": None,
                    "resolution_digest": None,
                    "selected_lenses": [],
                    "cas_rer_record_ids": [],
                },
                "action": {"result": "created"},
            }
        }
        errors, basis = ship_errors(ship, run, {}, [])
        self.assertIn("blocked-ship-result", errors)
        self.assertEqual(basis, [])

    def test_closure_joins_guard_truthy_non_object_run_artifact(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        resolution_errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(resolution_errors, [])
        snapshot = self.review_records(run, resolution)[0]
        run["artifact"] = ["malformed-but-truthy"]

        cas_problems, _ = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-unit-stale", cas_problems)
        ship_problems, basis = ship_errors(
            {"ship_record": {"actuation_review": {}}}, run, derived, []
        )
        self.assertIn("blocked-ship-binding", ship_problems)
        self.assertEqual(basis, [])

    def test_complete_actuation_ship_record_is_accepted(self) -> None:
        run = self.commit_step(self.complete_step(self.run_value(selected=True)))
        run["review"]["publication_requested"] = True
        ship = {
            "ship_record": {
                "record_version": "SHIP-v1",
                "source": "actuation",
                "branch": run["artifact"]["branch"],
                "base_branch": "main",
                "head_sha": run["artifact"]["head_sha"],
                "existing_pr": {"exists": False, "url": None, "draft": False},
                "validation": {
                    "build": "pass",
                    "lint": "pass",
                    "tests": "pass",
                    "language_specific": "pass",
                    "acceptance": "pass",
                },
                "pr_readiness": {
                    "mode": "ready",
                    "reason": "all proof is current",
                    "draft_allowed_reason": None,
                },
                "action": {
                    "command": "gh pr create",
                    "result": "created",
                    "pr_url": "https://github.com/example/repo/pull/1",
                },
                "actuation_review": {
                    "actuation_run_id": run["run_id"],
                    "state_fingerprint": run["artifact"]["state_fingerprint"],
                    "review_contract_fingerprint": None,
                    "resolution_ref": None,
                    "resolution_digest": None,
                    "selected_lenses": [],
                    "cas_rer_record_ids": [],
                },
            }
        }
        errors, basis = ship_errors(ship, run, {}, [])
        self.assertEqual(errors, [])
        self.assertEqual(basis, ["https://github.com/example/repo/pull/1"])
        decision, code = decide(
            run,
            None,
            [self.evidence(run)],
            [],
            ship,
            self.repo,
        )
        self.assertEqual(code, 0, decision)
        self.assertEqual(decision["closure_decision"]["verdict"], "complete")
        self.assertIsNone(decision["closure_decision"]["resolution_digest"])

        def mutate_during_pr(repo: Path, url: str) -> dict:
            (self.repo / "file.txt").write_text("late mutation\n", encoding="utf-8")
            return self.pr_metadata(repo, url)

        self.live_pr_mock.side_effect = mutate_during_pr
        try:
            decision, code = decide(
                run,
                None,
                [self.evidence(run)],
                [],
                ship,
                self.repo,
            )
        finally:
            subprocess.run(
                ["git", "restore", "file.txt"], cwd=self.repo, check=True
            )
            self.live_pr_mock.side_effect = self.pr_metadata
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-run-stale:state_fingerprint",
            decision["closure_decision"]["reasons"],
        )

        for invalid in ("passed", "fail", "missing", "not-run", True, {}, "other"):
            invalid_ship = copy.deepcopy(ship)
            invalid_ship["ship_record"]["validation"]["tests"] = invalid
            with self.subTest(validation=invalid):
                errors, _ = ship_errors(invalid_ship, run, {}, [])
                self.assertIn("blocked-ship-validation", errors)

        for field in ("baseRefOid", "headRefOid", "headRepository"):
            self.live_pr_override = self.pr_metadata(
                self.repo, "https://github.com/example/repo/pull/1"
            )
            pull_request = self.live_pr_override["pull_request"]
            pull_request[field] = (
                {"nameWithOwner": "other/repo"}
                if field == "headRepository"
                else "other-sha"
            )
            with self.subTest(live_pr_field=field):
                errors, basis = ship_errors(ship, run, {}, [])
                self.assertIn("blocked-ship-live-pr-mismatch", errors)
                self.assertEqual(basis, [])
            self.live_pr_override = None

        mismatched = copy.deepcopy(ship)
        record = mismatched["ship_record"]
        record["existing_pr"] = {
            "exists": True,
            "url": "https://github.com/example/repo/pull/1",
            "draft": False,
        }
        record["pr_readiness"]["mode"] = "update-existing"
        record["action"]["result"] = "updated"
        record["action"]["pr_url"] = "https://github.com/example/repo/pull/2"
        errors, _ = ship_errors(mismatched, run, {}, [])
        self.assertIn("blocked-ship-result", errors)

    def test_cli_non_object_artifact_is_a_structured_block(self) -> None:
        run = self.run_value(review=True, selected=True)
        resolution = self.resolution(run)
        run["artifact"] = ["bad-artifact"]
        resolution["artifact"] = ["bad-artifact"]
        run_path = self.repo / "run.json"
        resolution_path = self.repo / "resolution.json"
        run_path.write_text(json.dumps(run), encoding="utf-8")
        resolution_path.write_text(json.dumps(resolution), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "actuating_gate.py"),
                "validate-resolution",
                "--run",
                str(run_path),
                "--resolution",
                str(resolution_path),
                "--repo",
                str(self.repo),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("blocked-run-missing", payload["actuating_gate"]["errors"])
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_malformed_input_exits_two(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "actuating_gate.py"),
                "validate-run",
                "--run",
                "-",
                "--repo",
                str(self.repo),
            ],
            input="not: [valid",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("malformed", result.stdout)

        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "actuating_gate.py"),
                "validate-run",
                "--run",
                "-",
                "--repo",
                str(self.repo),
            ],
            input="when: 2026-07-09\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("input contains non-JSON values", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
