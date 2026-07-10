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
    diff_hunk_ids,
    expected_review_admission,
    live_artifact,
    live_changed_paths,
    live_hunk_ids,
    live_path_states,
    load_semantics,
    path_allowed,
    path_allowed_root,
    paths_overlap,
    resolution_digest_payload,
    review_contract_payload,
    ship_errors,
    validate_review_folds,
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
        self.admit_review_step(run)
        (self.repo / "file.txt").write_text("changed\n", encoding="utf-8")
        return self.finish_step(run, ["file.txt"])

    def admit_review_step(self, run: dict) -> None:
        step = run["execution"]["steps"][0]
        if (
            run["review"]["required"]
            and step.get("effect") == "edit"
            and "review_admission" not in step
        ):
            errors, derived = validate_run(
                run,
                self.repo,
                self.material_resolution(run),
            )
            if errors:
                raise AssertionError(errors)
            step["review_admission"] = derived["review_admission"]

    def finish_step(self, run: dict, changed_paths: list[str]) -> dict:
        step = run["execution"]["steps"][0]
        if run["review"]["required"] and step.get("effect") == "edit":
            if "review_admission" not in step:
                raise AssertionError("review edit mutated without admission")
        after = self.artifact()
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

    def add_submodule(self, filename: str, revisions: int) -> list[str]:
        source_temp = tempfile.TemporaryDirectory()
        self.addCleanup(source_temp.cleanup)
        source = Path(source_temp.name)
        subprocess.run(["git", "init", "-q"], cwd=source, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=source,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"], cwd=source, check=True
        )
        commits = []
        tracked = source / filename
        for index in range(1, revisions + 1):
            tracked.write_text(f"revision-{index}\n", encoding="utf-8")
            subprocess.run(["git", "add", filename], cwd=source, check=True)
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
            ["git", "add", ".gitmodules", "sm"], cwd=self.repo, check=True
        )
        subprocess.run(
            ["git", "commit", "-qm", "add submodule"], cwd=self.repo, check=True
        )
        self.base = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True
        ).strip()
        return commits

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

    def material_resolution(
        self,
        run: dict,
        *,
        finding_id: str = "finding-1",
        node_id: str = "step-1",
        status: str = "pending",
    ) -> dict:
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, [finding_id])
        decision = self.decision(run, finding_ids=[finding_id])
        selected_step = next(
            step
            for step in run["execution"]["steps"]
            if step["step_id"] == node_id
        )
        decision["owner_boundary"] = selected_step["owner_boundary"]
        decision["selected_work_node"] = {
            "node_id": node_id,
            "run_id": run["run_id"],
            "owner_boundary": selected_step["owner_boundary"],
            "paths": selected_step["paths"],
            "verifier": selected_step["verifier"],
        }
        resolution["decisions"] = [decision]
        resolution["outcome"]["status"] = status
        resolution["outcome"]["semantic_balance"]["covered_liabilities"] = [
            "invariant-gap"
        ]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        return resolution

    def redigest_admission(self, admission: dict) -> dict:
        observations = admission["observations"]
        return expected_review_admission(
            admission["review_resolution"],
            observations["review_source_refs"],
            observations["changed_paths"],
            observations["hunk_ids"],
            admission["ship_receipt"],
        )

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
        admission = run["execution"]["steps"][0].get("review_admission")
        review_refs = (
            [f"review-admission:{admission['admission_digest']}"]
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

    def ship_record(self, run: dict) -> dict:
        return {
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
                "actuation_binding": {
                    "actuation_run_id": run["run_id"],
                    "state_fingerprint": run["artifact"]["state_fingerprint"],
                },
            }
        }

    def updated_ship_record(self, run: dict, prior_ship: dict) -> dict:
        value = self.ship_record(run)
        prior_url = prior_ship["ship_record"]["action"]["pr_url"]
        record = value["ship_record"]
        record["existing_pr"] = {
            "exists": True,
            "url": prior_url,
            "draft": False,
        }
        record["pr_readiness"]["mode"] = "update-existing"
        record["action"] = {
            "command": "gh pr edit",
            "result": "updated",
            "pr_url": prior_url,
        }
        return value

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
        resolution_digest = resolution["outcome"]["resolution_digest"]
        ship_receipt = run.get("review", {}).get("ship_receipt")
        if isinstance(ship_receipt, dict):
            resolution_digest = canonical_digest(
                {
                    "resolution_digest": resolution_digest,
                    "publication_epoch": canonical_digest(ship_receipt),
                }
            )
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
                "resolutionDigest": resolution_digest,
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
        run = self.commit_step(self.complete_step(self.run_value(selected=True)))
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
        run["execution"]["steps"][0].pop("review_admission", None)
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-review-resolution-missing", errors)

        resolution = self.material_resolution(run)
        step = run["execution"]["steps"][0]
        errors, derived = validate_run(run, self.repo, resolution)
        self.assertEqual(errors, [])
        self.assertEqual(
            derived["review_admission"],
            expected_review_admission(
                resolution,
                ["local:audit-1"],
                [],
                live_hunk_ids(self.repo, run["artifact"]["base_sha"]),
            ),
        )
        valid_admission = copy.deepcopy(derived["review_admission"])
        step["review_admission"] = copy.deepcopy(valid_admission)
        errors, _ = validate_run(run, self.repo, resolution)
        self.assertEqual(errors, [])

        invalid_resolution = copy.deepcopy(resolution)
        invalid_resolution["outcome"]["resolution_digest"] = "sha256:" + "0" * 64
        errors, derived = validate_run(run, self.repo, invalid_resolution)
        self.assertIn("blocked-review-resolution-digest", errors)
        self.assertIsNone(derived["review_admission"])

        mismatched_node = copy.deepcopy(resolution)
        mismatched_node["decisions"][0]["selected_work_node"]["node_id"] = (
            "other-step"
        )
        mismatched_node["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(mismatched_node)
        )
        errors, derived = validate_run(run, self.repo, mismatched_node)
        self.assertIn("blocked-resolution-node-unexecuted", errors)
        self.assertIsNone(derived["review_admission"])

        run["execution"]["steps"][0]["review_admission"]["review_resolution"][
            "outcome"
        ]["resolution_digest"] = "sha256:" + "0" * 64
        errors, _ = validate_run(run, self.repo, resolution)
        self.assertIn("blocked-resolution-binding", errors)
        step["review_admission"] = copy.deepcopy(valid_admission)

        run["execution"]["steps"][0]["effect"] = "verify"
        errors, _ = validate_run(run, self.repo, resolution)
        self.assertIn("blocked-resolution-node-unexecuted", errors)

    def test_gate_derived_admission_closes_under_later_resolution(self) -> None:
        run = self.run_value(review=True, selected=True)
        pending = self.material_resolution(run)

        errors, derived = validate_run(run, self.repo, pending)
        self.assertEqual(errors, [])
        admission = derived["review_admission"]
        self.assertIsNotNone(admission)
        run["execution"]["steps"][0]["review_admission"] = admission
        run = self.complete_step(run)

        terminal = self.resolution(run)
        decision, code = decide(
            run,
            terminal,
            [self.evidence(run)],
            self.review_records(run, terminal),
            None,
            self.repo,
        )
        self.assertEqual(code, 0, decision)
        self.assertEqual(decision["closure_decision"]["verdict"], "complete")

    def test_publication_review_admission_requires_prior_ship(self) -> None:
        run = self.run_value(review=True, selected=True)
        run["review"]["publication_requested"] = True
        pending = self.material_resolution(run)

        errors, derived = validate_run(run, self.repo, pending)
        self.assertIn("blocked-ship-missing", errors)
        self.assertIsNone(derived["review_admission"])

        run["review"]["ship_receipt"] = self.ship_record(run)
        errors, derived = validate_run(run, self.repo, pending)
        self.assertEqual(errors, [])
        self.assertIsNotNone(derived["review_admission"])

    def test_publication_edit_requires_reship_before_final_cas(self) -> None:
        run = self.run_value(review=True, selected=True)
        run["review"]["publication_requested"] = True
        prior_ship = self.ship_record(run)
        run["review"]["ship_receipt"] = prior_ship
        historical_pr = self.pr_metadata(
            self.repo, prior_ship["ship_record"]["action"]["pr_url"]
        )
        pending = self.material_resolution(run)
        errors, derived = validate_run(run, self.repo, pending)
        self.assertEqual(errors, [])
        admission = derived["review_admission"]
        self.assertEqual(
            admission["ship_receipt"], prior_ship
        )
        run["execution"]["steps"][0]["review_admission"] = admission
        run = self.complete_step(run)

        current = self.material_resolution(run, status="resolved")
        evidence = self.evidence(run)

        forged_history = copy.deepcopy(run)
        forged_admission = copy.deepcopy(
            forged_history["execution"]["steps"][0]["review_admission"]
        )
        forged_admission["ship_receipt"] = self.ship_record(run)
        forged_history["execution"]["steps"][0]["review_admission"] = (
            self.redigest_admission(forged_admission)
        )
        blocked, code = decide(
            forged_history,
            current,
            [self.evidence(forged_history)],
            [],
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-resolution-binding", blocked["closure_decision"]["reasons"]
        )

        missing_history = copy.deepcopy(run)
        missing_history["review"].pop("ship_receipt")
        blocked, code = decide(
            missing_history,
            current,
            [evidence],
            [],
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-ship-missing", blocked["closure_decision"]["reasons"]
        )

        self.live_pr_override = historical_pr
        handback, code = decide(
            run,
            current,
            [evidence],
            [],
            None,
            self.repo,
        )
        self.live_pr_override = None
        self.assertEqual(code, 0, handback)
        self.assertEqual(handback["closure_decision"]["verdict"], "ready-to-ship")
        self.assertEqual(
            handback["closure_decision"]["outcomes"]["next_owner"], "ship"
        )
        self.assertEqual(handback["closure_decision"]["review_basis"], [])

        resolution_errors, pre_ship_derived = validate_resolution(
            run, current, self.repo
        )
        self.assertEqual(resolution_errors, [])
        pre_ship_snapshot = self.review_records(run, current)[0]
        cas_problems, _ = cas_errors(
            pre_ship_snapshot, run, current, pre_ship_derived
        )
        self.assertEqual(cas_problems, [])

        duplicate_ship = self.ship_record(run)
        duplicate_ship["ship_record"]["action"]["pr_url"] = (
            "https://github.com/example/repo/pull/2"
        )
        duplicate_pr = copy.deepcopy(run)
        duplicate_pr["review"]["ship_receipt"] = duplicate_ship
        blocked, code = decide(
            duplicate_pr,
            current,
            [evidence],
            self.review_records(run, current),
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-ship-pr-continuity",
            blocked["closure_decision"]["reasons"],
        )

        fresh_ship = self.updated_ship_record(run, prior_ship)
        self.assertNotEqual(canonical_digest(fresh_ship), canonical_digest(prior_ship))
        run["review"]["ship_receipt"] = fresh_ship
        resolution_errors, post_ship_derived = validate_resolution(
            run, current, self.repo
        )
        self.assertEqual(resolution_errors, [])
        self.assertNotEqual(
            pre_ship_derived["resolution_digest"],
            post_ship_derived["resolution_digest"],
        )
        cas_problems, basis = cas_errors(
            pre_ship_snapshot, run, current, post_ship_derived
        )
        self.assertIn("blocked-cas-clean-streak", cas_problems)
        self.assertEqual(basis, [])

        next_run = copy.deepcopy(run)
        next_run["execution"]["kind"] = "iterative"
        next_run["execution"]["selected_step_id"] = "step-2"
        next_run["execution"]["steps"].append(
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
        next_pending = self.material_resolution(
            next_run,
            finding_id="finding-2",
            node_id="step-2",
        )
        errors, derived = validate_run(
            next_run,
            self.repo,
            next_pending,
            [self.evidence(run)],
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            derived["review_admission"]["ship_receipt"],
            fresh_ship,
        )

        final, code = decide(
            run,
            current,
            [evidence],
            self.review_records(run, current),
            None,
            self.repo,
        )
        self.assertEqual(code, 0, final)
        self.assertEqual(final["closure_decision"]["verdict"], "complete")

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
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-local-repair-growth", errors)

    def test_abstraction_cannot_be_retained_and_retired(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        self.bind_resolution_findings(run, resolution, ["finding-1"])
        decision = self.decision(run)
        decision["abstraction_account"].append(
            {
                "abstraction": "gate",
                "disposition": "retire",
                "obligation_id": "mutation-admission",
            }
        )
        resolution["decisions"] = [decision]
        resolution["outcome"]["status"] = "resolved"
        balance = resolution["outcome"]["semantic_balance"]
        balance["covered_liabilities"] = ["invariant-gap"]
        balance["required_retirements"] = ["gate"]
        balance["completed_retirements"] = ["gate"]
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertIn("blocked-abstraction-disposition", errors)

    def test_resolved_node_must_match_completed_admitted_step(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.material_resolution(run, status="resolved")
        errors, _ = validate_resolution(run, resolution, self.repo)
        self.assertEqual(errors, [])

        resolution["decisions"][0]["selected_work_node"]["node_id"] = (
            "never-executed"
        )
        resolution["outcome"]["resolution_digest"] = canonical_digest(
            resolution_digest_payload(resolution)
        )
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

    def test_receipt_enum_containers_fail_closed(self) -> None:
        containers = ([], {})
        run = self.complete_step(self.run_value(review=True, selected=True))

        for container in containers:
            fold = self.review_fold(run, ["finding-1"])
            fold["findings"][0]["intent_relation"] = container
            errors, _ = validate_review_folds(run, [fold])
            with self.subTest(field="intent_relation", container=type(container)):
                self.assertIn("blocked-review-fold-finding", errors)

        resolution = self.resolution(run)
        resolution_errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(resolution_errors, [])
        for field, expected in (
            ("phase", "blocked-cas-attempt-identity"),
            ("status", "blocked-cas-unit-unnormalized"),
        ):
            for container in containers:
                snapshot = self.review_records(run, resolution)[0]
                record = snapshot["records"][0]
                target = record["attempt"] if field == "phase" else record["verdict"]
                target[field] = container
                errors, _ = cas_errors(snapshot, run, resolution, derived)
                with self.subTest(field=field, container=type(container)):
                    self.assertIn(expected, errors)

        ship_run = copy.deepcopy(run)
        ship_run["review"]["publication_requested"] = True
        for field, expected in (
            ("mode", "blocked-ship-readiness"),
            ("result", "blocked-ship-result"),
        ):
            for container in containers:
                ship = self.ship_record(ship_run)
                record = ship["ship_record"]
                target = (
                    record["pr_readiness"] if field == "mode" else record["action"]
                )
                target[field] = container
                errors, _ = ship_errors(ship, ship_run)
                with self.subTest(field=field, container=type(container)):
                    self.assertIn(expected, errors)

        plan_run = self.triage_run()
        plan_run["mode"] = "remediation-plan"
        for container in containers:
            closure, code = decide(
                plan_run,
                {"outcome": {"status": container}},
                [],
                [],
                None,
                self.repo,
            )
            with self.subTest(field="outcome.status", container=type(container)):
                self.assertEqual(code, 2)
                self.assertIn(
                    "blocked-review-resolution-open",
                    closure["closure_decision"]["reasons"],
                )

    def test_live_multi_path_change_updates_review_contract(self) -> None:
        run = self.run_value(review=True, selected=True)
        run["authority"]["allowed_paths"] = ["file.txt", "decoy.txt"]
        run["execution"]["steps"][0]["paths"] = ["file.txt", "decoy.txt"]
        self.admit_review_step(run)
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
        missing["execution"]["steps"][0].pop("review_admission")
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

        for field, value in (
            ("version", "review-admission/v0"),
            ("admission_digest", "sha256:" + "0" * 64),
        ):
            tampered = copy.deepcopy(run)
            tampered["execution"]["steps"][0]["review_admission"][field] = value
            decision, code = decide(
                tampered,
                resolution,
                [evidence],
                records,
                None,
                self.repo,
            )
            with self.subTest(field=field):
                self.assertEqual(code, 2)
                self.assertIn(
                    "blocked-resolution-binding",
                    decision["closure_decision"]["reasons"],
                )

        original = run["execution"]["steps"][0]["review_admission"]
        fabricated: list[tuple[str, dict]] = []

        later_resolution = copy.deepcopy(original)
        later_resolution["review_resolution"] = resolution
        fabricated.append(
            ("later-resolution", self.redigest_admission(later_resolution))
        )

        wrong_sources = copy.deepcopy(original)
        wrong_sources["observations"]["review_source_refs"] = ["local:other"]
        fabricated.append(("review-source-refs", self.redigest_admission(wrong_sources)))

        wrong_paths = copy.deepcopy(original)
        wrong_paths["observations"]["changed_paths"] = ["file.txt", "other.txt"]
        fabricated.append(("changed-paths", self.redigest_admission(wrong_paths)))

        wrong_hunks = copy.deepcopy(original)
        wrong_hunks["observations"]["hunk_ids"] = ["sha256:" + "0" * 64]
        fabricated.append(("hunk-ids", self.redigest_admission(wrong_hunks)))

        extra_field = copy.deepcopy(original)
        extra_field["resolution_id"] = "forged-redundant-scalar"
        extra_field["admission_digest"] = canonical_digest(
            {
                key: value
                for key, value in extra_field.items()
                if key != "admission_digest"
            }
        )
        fabricated.append(("extra-field", extra_field))

        for label, admission in fabricated:
            tampered = copy.deepcopy(run)
            tampered["execution"]["steps"][0]["review_admission"] = admission
            tampered_evidence = self.evidence(tampered)
            decision, code = decide(
                tampered,
                resolution,
                [tampered_evidence],
                records,
                None,
                self.repo,
            )
            with self.subTest(label=label):
                self.assertEqual(code, 2)
                self.assertIn(
                    "blocked-resolution-binding",
                    decision["closure_decision"]["reasons"],
                )

        wrong_ref = self.evidence(run)
        wrong_ref["evidence_fold"]["evidence"]["review_refs"] = [
            "review-admission:sha256:" + "0" * 64
        ]
        decision, code = decide(
            run,
            resolution,
            [wrong_ref],
            records,
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-evidence-fold-mismatch",
            decision["closure_decision"]["reasons"],
        )

    def test_review_required_history_cannot_be_relabelled_as_implement(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        terminal = self.resolution(run)
        records = self.review_records(run, terminal)
        run["mode"] = "implement"
        run["execution"]["steps"][0].pop("review_admission")
        evidence = self.evidence(run)

        decision, code = decide(
            run,
            terminal,
            [evidence],
            records,
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-review-required-shape",
            decision["closure_decision"]["reasons"],
        )
        self.assertIn(
            "blocked-resolution-binding",
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

    def test_freshness_precedes_proof_credit_filter(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        resolution_errors, derived = validate_resolution(run, resolution, self.repo)
        self.assertEqual(resolution_errors, [])
        snapshot = self.cas_snapshot(
            [
                self.cas_record(run, resolution, "standard", ordinal)
                for ordinal in range(1, 5)
            ]
        )[0]
        snapshot["records"][1]["command"]["brokerDecision"][
            "freshAttemptRequired"
        ] = False
        snapshot["recordRefs"][0]["proofCreditEligible"] = False

        errors, basis = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-unit-replayed", errors)
        self.assertNotIn("blocked-cas-clean-streak", errors)
        self.assertEqual(
            basis,
            [row["recordId"] for row in snapshot["records"][1:]],
        )

        snapshot["records"][0]["verdict"] = {
            "tupleVerdictExists": True,
            "status": "findings",
            "clean": False,
            "findingCount": 1,
            "findings": [{"title": "visible finding"}],
        }
        errors, _ = cas_errors(snapshot, run, resolution, derived)
        self.assertIn("blocked-cas-findings-unresolved", errors)
        self.assertIn("blocked-cas-unit-replayed", errors)

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
        evidence["evidence_fold"]["evidence"] = None
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

    def test_cli_canonicalizes_nested_repo_before_path_authorization(self) -> None:
        nested = self.repo / "nested"
        nested.mkdir()
        with tempfile.TemporaryDirectory() as outside:
            os.symlink(outside, self.repo / "escape")
            run = self.run_value(selected=True)
            run["authority"]["allowed_paths"] = ["."]
            run["execution"]["steps"][0]["paths"] = ["escape/secret.txt"]
            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOLS / "actuating_gate.py"),
                    "validate-run",
                    "--run",
                    "-",
                    "--repo",
                    str(nested),
                ],
                input=json.dumps(run),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        self.assertEqual(result.returncode, 2, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(
            "blocked-step-out-of-scope",
            payload["actuating_gate"]["errors"],
        )

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

    def test_iterative_step_cannot_borrow_an_earlier_path_delta(self) -> None:
        run = self.run_value(selected=True)
        run["execution"]["kind"] = "iterative"
        (self.repo / "file.txt").write_text("first\n", encoding="utf-8")
        run = self.commit_step(self.finish_step(run, ["file.txt"]))
        run["execution"]["steps"][0]["verdict"] = "continue"

        before = run["artifact"]
        second = copy.deepcopy(run["execution"]["steps"][0])
        second.update(
            step_id="step-2",
            state_before=before,
            state_after=before,
            evidence_fold_ref="ef-2",
            verdict="ready-for-closure",
        )
        run["execution"]["steps"].append(second)

        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_iterative_selection_rejects_unclaimed_carried_delta(self) -> None:
        run = self.run_value(selected=True)
        run["execution"]["kind"] = "iterative"
        run["authority"]["allowed_paths"] = ["file.txt", "other.txt"]

        (self.repo / "file.txt").write_text("first\n", encoding="utf-8")
        (self.repo / "other.txt").write_text("carried\n", encoding="utf-8")
        run = self.commit_step(self.finish_step(run, ["file.txt"]))
        run["execution"]["steps"][0]["verdict"] = "continue"
        run["execution"]["selected_step_id"] = "step-2"
        run["execution"]["steps"].append(
            {
                "step_id": "step-2",
                "run_id": run["run_id"],
                "selected_by": "lead",
                "owner_boundary": "actuating",
                "effect": "edit",
                "paths": ["other.txt"],
                "verifier": ["test"],
                "changed_paths": [],
                "status": "selected",
                "state_before": run["artifact"],
                "parent_completion_claimed": False,
                "performed_public_effects": [],
            }
        )

        errors, _ = validate_run(run, self.repo, evidence_values=[self.evidence(run)])
        self.assertEqual(errors, ["blocked-step-change-mismatch"])

    def test_iterative_committed_revert_preserves_exact_step_evidence(self) -> None:
        run = self.run_value(selected=True)
        run["execution"]["kind"] = "iterative"
        (self.repo / "file.txt").write_text("first\n", encoding="utf-8")
        run = self.commit_step(self.finish_step(run, ["file.txt"]))
        run["execution"]["steps"][0]["verdict"] = "continue"

        before = run["artifact"]
        (self.repo / "file.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "revert selected step"],
            cwd=self.repo,
            check=True,
        )
        after = self.artifact()
        second = copy.deepcopy(run["execution"]["steps"][0])
        second.update(
            step_id="step-2",
            state_before=before,
            state_after=after,
            evidence_fold_ref="ef-2",
            verdict="ready-for-closure",
        )
        run["execution"]["steps"].append(second)
        run["artifact"] = after

        errors, _ = validate_run(run, self.repo)
        self.assertEqual(errors, [])

    def test_non_edit_step_preserves_the_complete_artifact(self) -> None:
        run = self.run_value(selected=True)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-qm", "history mutation"],
            cwd=self.repo,
            check=True,
        )
        run["artifact"] = self.artifact()
        run = self.finish_verify_step(run)

        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

    def test_direct_committed_edit_requires_descendant_history(self) -> None:
        (self.repo / "file.txt").write_text("first\n", encoding="utf-8")
        subprocess.run(["git", "commit", "-qam", "first branch"], cwd=self.repo, check=True)
        run = self.run_value(selected=True)

        subprocess.run(["git", "reset", "--hard", "HEAD^"], cwd=self.repo, check=True)
        (self.repo / "file.txt").write_text("sibling\n", encoding="utf-8")
        run = self.commit_step(self.finish_step(run, ["file.txt"]))

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
        commits = self.add_submodule("tracked.txt", 3)
        subprocess.run(
            ["git", "-C", "sm", "checkout", "-q", commits[0]],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(["git", "add", "sm"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "pin first revision"],
            cwd=self.repo,
            check=True,
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

    def test_iterative_commit_delta_overrides_submodule_diff_config(self) -> None:
        commits = self.add_submodule("tracked.txt", 3)
        run = self.run_value(selected=True)
        run["execution"]["kind"] = "iterative"

        states = []
        for index, commit in enumerate((commits[0], commits[-1]), start=1):
            subprocess.run(
                ["git", "-C", "sm", "checkout", "-q", commit],
                cwd=self.repo,
                check=True,
            )
            (self.repo / "file.txt").write_text(f"step-{index}\n", encoding="utf-8")
            subprocess.run(["git", "add", "file.txt", "sm"], cwd=self.repo, check=True)
            subprocess.run(
                ["git", "commit", "-qm", f"step {index}"],
                cwd=self.repo,
                check=True,
            )
            states.append(self.artifact())

        first = run["execution"]["steps"][0]
        first.update(
            changed_paths=["file.txt"],
            status="completed",
            state_after=states[0],
            evidence_fold_ref="ef-1",
            verdict="continue",
        )
        second = copy.deepcopy(first)
        second.update(
            step_id="step-2",
            state_before=states[0],
            state_after=states[1],
            evidence_fold_ref="ef-2",
            verdict="ready-for-closure",
        )
        run["execution"]["steps"].append(second)
        run["execution"]["selected_step_id"] = None
        run["artifact"] = states[1]
        subprocess.run(
            ["git", "config", "diff.ignoreSubmodules", "all"],
            cwd=self.repo,
            check=True,
        )

        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-step-change-mismatch", errors)

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

    def test_index_observer_flags_are_rejected(self) -> None:
        for flag, clear in (
            ("--assume-unchanged", "--no-assume-unchanged"),
            ("--skip-worktree", "--no-skip-worktree"),
        ):
            run = self.run_value(selected=True)
            subprocess.run(
                ["git", "update-index", flag, "file.txt"],
                cwd=self.repo,
                check=True,
            )
            try:
                (self.repo / "file.txt").write_text("hidden edit\n", encoding="utf-8")
                errors, _ = validate_run(run, self.repo)
                with self.subTest(flag=flag):
                    self.assertIn("blocked-index-observer-flags", errors)
            finally:
                subprocess.run(
                    ["git", "update-index", clear, "file.txt"],
                    cwd=self.repo,
                    check=True,
                )
                subprocess.run(
                    ["git", "restore", "file.txt"], cwd=self.repo, check=True
                )

    def test_git_clean_raw_aliases_are_rejected(self) -> None:
        (self.repo / ".gitattributes").write_text(
            "file.txt filter=normalize\n", encoding="utf-8"
        )
        subprocess.run(
            ["git", "config", "filter.normalize.clean", "sed 's/RAW//g'"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(
            ["git", "config", "filter.normalize.smudge", "cat"],
            cwd=self.repo,
            check=True,
        )
        subprocess.run(["git", "add", ".gitattributes"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "configure clean filter"],
            cwd=self.repo,
            check=True,
        )
        self.base = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True
        ).strip()

        artifact = self.artifact()
        (self.repo / "file.txt").write_text("RAWbase\n", encoding="utf-8")
        self.assertEqual(live_changed_paths(self.repo, "HEAD"), set())
        errors, _ = binding_errors(artifact, self.repo, "blocked-run")
        self.assertIn("blocked-worktree-observer-alias", errors)
        (self.repo / "file.txt").write_text("base\n", encoding="utf-8")

        subprocess.run(
            ["git", "config", "core.fileMode", "true"], cwd=self.repo, check=True
        )
        (self.repo / "file.txt").chmod(0o755)
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "executable"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "config", "core.fileMode", "false"], cwd=self.repo, check=True
        )
        artifact = self.artifact()
        (self.repo / "file.txt").chmod(0o655)
        errors, _ = binding_errors(artifact, self.repo, "blocked-run")
        self.assertIn("blocked-worktree-observer-alias", errors)

        subprocess.run(
            ["git", "config", "core.fileMode", "true"], cwd=self.repo, check=True
        )
        (self.repo / "file.txt").chmod(0o644)
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "nonexecutable"], cwd=self.repo, check=True
        )
        subprocess.run(
            ["git", "config", "core.fileMode", "false"], cwd=self.repo, check=True
        )
        artifact = self.artifact()
        (self.repo / "file.txt").chmod(0o654)
        errors, _ = binding_errors(artifact, self.repo, "blocked-run")
        self.assertNotIn("blocked-worktree-observer-alias", errors)

    def test_artifact_base_is_canonical_commit_identity(self) -> None:
        original = self.base
        subprocess.run(["git", "tag", "moving-base", original], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-qm", "same tree"],
            cwd=self.repo,
            check=True,
        )
        artifact = live_artifact(self.repo, "moving-base")
        self.assertEqual(artifact["base_sha"], original)

        subprocess.run(
            ["git", "tag", "-f", "moving-base", "HEAD"],
            cwd=self.repo,
            check=True,
            stdout=subprocess.DEVNULL,
        )
        self.assertNotEqual(
            live_artifact(self.repo, "moving-base")["base_sha"],
            artifact["base_sha"],
        )
        errors, _ = binding_errors(artifact, self.repo, "blocked-run")
        self.assertEqual(errors, [])

    def test_patch_body_cannot_impersonate_file_headers(self) -> None:
        (self.repo / "file.txt").write_text(
            "zero\n-- old-marker\ntwo\nthree\nfour\n", encoding="utf-8"
        )
        subprocess.run(["git", "add", "file.txt"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "hunk base"], cwd=self.repo, check=True)
        (self.repo / "file.txt").write_text(
            "zero\n++ new-marker\ntwo\nthree\nchanged\n", encoding="utf-8"
        )
        self.assertEqual(
            diff_hunk_ids(self.repo, "worktree"),
            [
                "file.txt:worktree:@@ -2 +2 @@",
                "file.txt:worktree:@@ -5 +5 @@",
            ],
        )
        for key in ("diff.noprefix", "diff.mnemonicPrefix"):
            subprocess.run(["git", "config", key, "true"], cwd=self.repo, check=True)
            with self.subTest(config=key):
                self.assertEqual(len(diff_hunk_ids(self.repo, "worktree")), 2)
            subprocess.run(["git", "config", "--unset", key], cwd=self.repo, check=True)

    def test_quoted_patch_path_cannot_fabricate_a_header(self) -> None:
        raw_path = b"odd\x80\tname.txt"
        path = os.fsdecode(raw_path)
        original = subprocess.check_output(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=self.repo,
            input=b"zero\nold\ntwo\nthree\nfour\n",
        ).strip()
        subprocess.run(
            ["git", "update-index", "-z", "--index-info"],
            cwd=self.repo,
            input=b"100644 " + original + b"\t" + raw_path + b"\0",
            check=True,
        )
        subprocess.run(["git", "commit", "-qm", "quoted path"], cwd=self.repo, check=True)
        changed = subprocess.check_output(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=self.repo,
            input=b"zero\n++ b/fabricated.txt\ntwo\nthree\nchanged\n",
        ).strip()
        subprocess.run(
            ["git", "update-index", "-z", "--index-info"],
            cwd=self.repo,
            input=b"100644 " + changed + b"\t" + raw_path + b"\0",
            check=True,
        )
        self.assertEqual(
            diff_hunk_ids(self.repo, "index", "--cached", "HEAD"),
            [
                f"{path}:index:@@ -2 +2 @@",
                f"{path}:index:@@ -5 +5 @@",
            ],
        )

    def test_submodule_diff_config_cannot_multiply_root_sections(self) -> None:
        self.add_submodule("one.txt", 1)
        submodule = self.repo / "sm"
        (submodule / "two.txt").write_text("two\n", encoding="utf-8")
        subprocess.run(["git", "add", "two.txt"], cwd=submodule, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "add second file"],
            cwd=submodule,
            check=True,
        )
        (self.repo / "z.txt").write_text(
            "zero\none\ntwo\nthree\nfour\n", encoding="utf-8"
        )
        subprocess.run(["git", "add", "sm", "z.txt"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "root baseline"],
            cwd=self.repo,
            check=True,
        )

        (submodule / "one.txt").write_text("changed-one\n", encoding="utf-8")
        (submodule / "two.txt").write_text("changed-two\n", encoding="utf-8")
        (self.repo / "z.txt").write_text(
            "changed-zero\none\ntwo\nthree\nchanged-four\n", encoding="utf-8"
        )
        subprocess.run(
            ["git", "config", "diff.submodule", "diff"],
            cwd=self.repo,
            check=True,
        )

        self.assertEqual(
            diff_hunk_ids(self.repo, "worktree"),
            [
                "sm:worktree:@@ -1 +1 @@",
                "z.txt:worktree:@@ -1 +1 @@",
                "z.txt:worktree:@@ -5 +5 @@",
            ],
        )

    def test_unmerged_index_is_rejected_before_hunk_admission(self) -> None:
        base_blob = subprocess.check_output(
            ["git", "rev-parse", "HEAD:file.txt"], cwd=self.repo
        ).strip()
        ours_blob = subprocess.check_output(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=self.repo,
            input=b"ours\n",
        ).strip()
        theirs_blob = subprocess.check_output(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=self.repo,
            input=b"theirs\n",
        ).strip()
        subprocess.run(
            ["git", "update-index", "-z", "--index-info"],
            cwd=self.repo,
            input=(
                b"0 "
                + (b"0" * 40)
                + b"\tfile.txt\0"
                + b"100644 "
                + base_blob
                + b" 1\tfile.txt\0"
                + b"100644 "
                + ours_blob
                + b" 2\tfile.txt\0"
                + b"100644 "
                + theirs_blob
                + b" 3\tfile.txt\0"
            ),
            check=True,
        )

        artifact = self.artifact()
        errors, _ = binding_errors(artifact, self.repo, "blocked-run")
        self.assertEqual(errors, ["blocked-unmerged-index"])

    def test_retained_head_gitlink_remains_in_the_fingerprint(self) -> None:
        self.add_submodule("tracked.txt", 1)
        subprocess.run(
            ["git", "rm", "--cached", "-q", "sm"], cwd=self.repo, check=True
        )
        before = live_artifact(self.repo, self.base)

        (self.repo / "sm/tracked.txt").write_text(
            "retained worktree edit\n", encoding="utf-8"
        )

        after = live_artifact(self.repo, self.base)
        self.assertNotEqual(before["state_fingerprint"], after["state_fingerprint"])

    def test_initialized_gitlink_index_flags_are_rejected(self) -> None:
        self.add_submodule("nested.txt", 1)
        run = self.run_value(selected=True)
        subprocess.run(
            ["git", "update-index", "--skip-worktree", "nested.txt"],
            cwd=self.repo / "sm",
            check=True,
        )
        (self.repo / "sm/nested.txt").write_text(
            "hidden submodule edit\n", encoding="utf-8"
        )
        errors, _ = validate_run(run, self.repo)
        self.assertIn("blocked-index-observer-flags", errors)

        subprocess.run(
            ["git", "submodule", "--quiet", "deinit", "--force", "sm"],
            cwd=self.repo,
            check=True,
        )
        errors, _ = validate_run(self.run_value(selected=True), self.repo)
        self.assertNotIn("blocked-index-observer-flags", errors)

    def test_unreadable_observer_subtree_fails_closed(self) -> None:
        with patch("actuating_gate.os.scandir", side_effect=PermissionError):
            errors, _ = validate_run(self.run_value(selected=True), self.repo)
        self.assertIn("blocked-nested-gitlink-observer", errors)

    def test_nested_gitlink_declaration_is_outside_the_observer_domain(self) -> None:
        nested_temp = tempfile.TemporaryDirectory()
        self.addCleanup(nested_temp.cleanup)
        nested = Path(nested_temp.name)
        subprocess.run(["git", "init", "-q"], cwd=nested, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"], cwd=nested, check=True
        )
        subprocess.run(["git", "config", "user.name", "Test"], cwd=nested, check=True)
        (nested / "nested.txt").write_text("nested\n", encoding="utf-8")
        subprocess.run(["git", "add", "nested.txt"], cwd=nested, check=True)
        subprocess.run(["git", "commit", "-qm", "nested"], cwd=nested, check=True)

        self.add_submodule("direct.txt", 1)
        direct = self.repo / "sm"
        subprocess.run(
            [
                "git",
                "-c",
                "protocol.file.allow=always",
                "submodule",
                "add",
                "-q",
                str(nested),
                "vendor/nested",
            ],
            cwd=direct,
            check=True,
        )
        subprocess.run(["git", "commit", "-qam", "add nested"], cwd=direct, check=True)

        errors, _ = validate_run(self.run_value(selected=True), self.repo)
        self.assertIn("blocked-nested-gitlink-observer", errors)

        subprocess.run(
            ["git", "rm", "--cached", "-q", "vendor/nested"],
            cwd=direct,
            check=True,
        )
        errors, _ = validate_run(self.run_value(selected=True), self.repo)
        self.assertIn("blocked-nested-gitlink-observer", errors)

        subprocess.run(
            ["git", "commit", "-qm", "remove nested declaration"],
            cwd=direct,
            check=True,
        )
        errors, _ = validate_run(self.run_value(selected=True), self.repo)
        self.assertIn("blocked-nested-gitlink-observer", errors)

        (direct / ".gitignore").write_text("vendor/\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore"], cwd=direct, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "ignore retained repository"],
            cwd=direct,
            check=True,
        )
        errors, _ = validate_run(self.run_value(selected=True), self.repo)
        self.assertIn("blocked-nested-gitlink-observer", errors)

    def test_final_rebind_rejects_late_index_observer_flag(self) -> None:
        run = self.complete_step(self.run_value(review=True, selected=True))
        resolution = self.resolution(run)
        records = self.review_records(run, resolution)
        snapshot = records[0]

        def hide_edit(*_args: object) -> dict:
            subprocess.run(
                ["git", "update-index", "--assume-unchanged", "file.txt"],
                cwd=self.repo,
                check=True,
            )
            (self.repo / "file.txt").write_text("late hidden edit\n", encoding="utf-8")
            return snapshot

        self.live_cas_mock.side_effect = hide_edit
        try:
            decision, code = decide(
                run,
                resolution,
                [self.evidence(run)],
                records,
                None,
                self.repo,
            )
        finally:
            subprocess.run(
                ["git", "update-index", "--no-assume-unchanged", "file.txt"],
                cwd=self.repo,
                check=True,
            )
            subprocess.run(
                ["git", "restore", "file.txt"], cwd=self.repo, check=True
            )
            self.live_cas_mock.side_effect = lambda *_: self.live_cas_snapshot
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-index-observer-flags",
            decision["closure_decision"]["reasons"],
        )

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
                "actuation_binding": {
                    "actuation_run_id": run["run_id"],
                    "state_fingerprint": run["artifact"]["state_fingerprint"],
                },
                "action": {"result": "created"},
            }
        }
        errors, basis = ship_errors(ship, run)
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
            {"ship_record": {"actuation_binding": {}}}, run
        )
        self.assertIn("blocked-ship-binding", ship_problems)
        self.assertEqual(basis, [])

    def test_complete_actuation_ship_record_is_accepted(self) -> None:
        run = self.commit_step(self.complete_step(self.run_value(selected=True)))
        run["review"]["publication_requested"] = True
        ship = self.ship_record(run)
        errors, basis = ship_errors(ship, run)
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
        self.assertEqual(code, 2, decision)
        self.assertEqual(decision["closure_decision"]["verdict"], "continue")
        self.assertEqual(
            decision["closure_decision"]["outcomes"],
            {
                "goal_outcome": "continue",
                "implementation_outcome": "complete",
                "next_owner": "goal-actuating",
            },
        )
        self.assertIsNone(decision["closure_decision"]["resolution_digest"])

        review_run = self.finish_verify_step(
            self.run_value(review=True, selected=True)
        )
        review_run["review"]["publication_requested"] = True
        review_run["review"]["ship_receipt"] = ship
        resolution = self.resolution(review_run)
        evidence = self.evidence(review_run)
        evidence["evidence_fold"]["artifact_state"]["changed_paths"] = []
        records = self.review_records(review_run, resolution)

        embedded_final, code = decide(
            review_run,
            resolution,
            [evidence],
            records,
            None,
            self.repo,
        )
        self.assertEqual(code, 0, embedded_final)
        self.assertEqual(embedded_final["closure_decision"]["verdict"], "complete")

        external_final, code = decide(
            review_run,
            resolution,
            [evidence],
            records,
            ship,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-unexpected-input",
            external_final["closure_decision"]["reasons"],
        )

        relabeled = copy.deepcopy(ship)
        relabeled_binding = relabeled["ship_record"]["actuation_binding"]
        relabeled_binding["review_epoch"] = resolution["outcome"][
            "resolution_digest"
        ]
        errors, _ = ship_errors(relabeled, review_run)
        self.assertIn("blocked-ship-binding", errors)
        relabeled_run = copy.deepcopy(review_run)
        relabeled_run["review"]["ship_receipt"] = relabeled
        relabeled_records = self.review_records(relabeled_run, resolution)
        mismatched_final, code = decide(
            relabeled_run,
            resolution,
            [evidence],
            relabeled_records,
            None,
            self.repo,
        )
        self.assertEqual(code, 2)
        self.assertIn(
            "blocked-ship-binding",
            mismatched_final["closure_decision"]["reasons"],
        )

        for key in ("actuation_run_id", "state_fingerprint"):
            incomplete = copy.deepcopy(ship)
            incomplete["ship_record"]["actuation_binding"].pop(key)
            errors, _ = ship_errors(incomplete, run)
            with self.subTest(missing_ship_field=key):
                self.assertIn("blocked-ship-binding", errors)

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
                errors, _ = ship_errors(invalid_ship, run)
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
                errors, basis = ship_errors(ship, run)
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
        errors, _ = ship_errors(mismatched, run)
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
