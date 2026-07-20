import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent
REPO = ROOT.parents[2]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


SKILL = read(ROOT / "SKILL.md")
OWNERS = read(ROOT / "references" / "artifact-kernel.md")
CONSTRUCTION = read(ROOT / "references" / "construction-contract.md")
REVIEW = read(ROOT / "references" / "review-contract.md")
REVIEW_CONTRACT = json.loads(read(ROOT / "references" / "review-contract.json"))
EVIDENCE = read(ROOT / "references" / "evidence-ledger.md")
CLOSURE = read(ROOT / "references" / "closure.md")
DECISION = read(ROOT / "references" / "decision-contract.yaml")
LEDGER = read(SKILLS / "ledger" / "SKILL.md")
SHIP = read(SKILLS / "ship" / "SKILL.md")
PROOF_PATCH = read(SKILLS / "proof-patch" / "SKILL.md")
EVIDENCE_FOLD = read(SKILLS / "evidence-fold" / "SKILL.md")
ONE_SEAM_OPERATOR = read(REPO / "codex" / "agents" / "one-seam-operator.toml")
REVIEW_REDUCER = read(REPO / "codex" / "agents" / "review-reducer.toml")
FLAT_SKILL = " ".join(SKILL.split())
FLAT_OWNERS = " ".join(OWNERS.split())
FLAT_CONSTRUCTION = " ".join(CONSTRUCTION.split())
FLAT_REVIEW = " ".join(REVIEW.split())
FLAT_EVIDENCE = " ".join(EVIDENCE.split())
FLAT_LEDGER = " ".join(LEDGER.split())
FLAT_REVIEW_REDUCER = " ".join(REVIEW_REDUCER.split())


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


class ArtifactKernelContractTests(unittest.TestCase):
    def test_all_public_modes_and_safe_review_default_remain(self) -> None:
        for mode in (
            "Bare `$actuating`",
            "`$actuating implement`",
            "`$actuating triage`",
            "`$actuating remediation-plan`",
            "`$actuating review-closeout`",
        ):
            self.assertIn(mode, SKILL)
        self.assertIn("unqualified request to review, inspect, audit, or classify selects `triage`", SKILL)

    def test_four_families_have_one_semantic_owner_each(self) -> None:
        expected = {
            "goal-contract/v3": "$goal-contract",
            "counterexample-set/v1": "$review-fold",
            "construction-contract/v1": "$actuating",
            "actuating-evidence-event/v1": "domain owner",
        }
        for family, owner in expected.items():
            with self.subTest(family=family):
                self.assertIn(family, OWNERS)
                self.assertIn(owner, OWNERS)
        for phrase in (
            "sole semantic-authority artifact",
            "sole classified-bug artifact",
            "sole architecture-selection artifact",
            "sole mutable per-goal truth",
        ):
            self.assertIn(phrase, FLAT_OWNERS)

    def test_full_goal_construction_realization_proof_intent_remains(self) -> None:
        for phrase in (
            "Compile the accepted source",
            "Select the smallest non-dominated Construction",
            "Actuating selects one exact operation",
            "exact verifier and falsifier observations",
            "Actuating selects the next operation",
            "select -> prepare -> effect -> observe -> evaluate",
        ):
            self.assertIn(phrase, FLAT_SKILL)
        self.assertIn("strongest feasible proof mode", FLAT_CONSTRUCTION)
        self.assertIn("witnessed Counterexample -> intended law -> canonical owner", FLAT_CONSTRUCTION)
        self.assertIn("State machine or lifecycle", CONSTRUCTION)
        self.assertIn("Public API or CLI affordance", CONSTRUCTION)
        self.assertIn("Every retirement names an absence verifier", FLAT_CONSTRUCTION)

    def test_goal_and_construction_are_registered_before_operations(self) -> None:
        for phrase in (
            "goal_contract_registered",
            "append --input <construction-contract.json>",
            "construction_contract_registered",
            "Only the returned artifact is the current Construction",
        ):
            self.assertIn(phrase, FLAT_SKILL)
        self.assertLess(
            FLAT_SKILL.index("append --input <construction-contract.json>"),
            FLAT_SKILL.index("For each repository effect"),
        )
        self.assertIn("Ledger identifies and registers", FLAT_CONSTRUCTION)
        self.assertIn("it never selects or revises the Construction", FLAT_CONSTRUCTION)

    def test_operation_subject_is_rechecked_before_effect(self) -> None:
        for phrase in (
            "expected_subject_digest",
            "pre_effect_subject_digest",
            "A mismatch takes `operation_aborted` without performing the effect",
            "never invokes Git",
        ):
            self.assertIn(phrase, FLAT_EVIDENCE)
        self.assertIn("A mismatch aborts without effect", FLAT_SKILL)
        self.assertIn("Every selected operation carries", FLAT_CONSTRUCTION)

    def test_counterexample_successor_and_review_intent_remains(self) -> None:
        for phrase in (
            "passes through `$review-fold` before repair",
            "realization defect",
            "architecture defect",
            "ablation defect",
            "successor records falsified and preserved predecessor claims",
        ):
            self.assertIn(phrase, SKILL)
        self.assertIn("Every material implementation has one current Construction", CONSTRUCTION)

    def test_review_topology_recovery_and_reset_are_exact(self) -> None:
        for phrase in (
            "standard plus four auxiliary CAS requests concurrently",
            "never cancels a launched sibling",
            "reruns the exact request once",
            "distinct attempt B",
            "clean attempt one",
            "five consecutive distinct clean attempts",
            "all review credit resets",
            "No review credit crosses a material subject change",
            'principalStrength == "strong"',
            'accountFingerprintReducedProtection == false',
            'backendClass == "cas-start-wait"',
            "Any other subject-digest change is material",
            "new immutable Review Contract identity and digest",
            "maps the current published subject to CAS `--base <bound-base>`",
            "must not select `--uncommitted` for a clean published checkout",
        ):
            self.assertIn(phrase, FLAT_REVIEW)

    def test_static_review_contract_and_campaign_identity_are_canonical(self) -> None:
        for phrase in (
            "review_contract_digest = sha256(canonical_json(review_contract with contract_digest = null))",
            '"actuating-review-campaign/v1" || 0x00',
            "goal_id || 0x00",
            "construction_ref || 0x00",
            "subject_digest || 0x00",
            "`review_contract_digest` in every `counterexample-set/v1` subject binds",
            "does not require a review campaign before classification or repair",
        ):
            self.assertIn(phrase, FLAT_REVIEW)

    def test_review_reducer_requires_counterexample_subject_bindings(self) -> None:
        for phrase in (
            "static Review Contract digest",
            "originating campaign",
            "require its Review Contract digest to match the supplied static digest",
            "non-review falsifier requires no campaign",
            "never invent one",
        ):
            self.assertIn(phrase, FLAT_REVIEW_REDUCER)

    def test_executor_and_evidence_fold_preserve_prepared_step_identity(self) -> None:
        for surface in (ONE_SEAM_OPERATOR, EVIDENCE_FOLD):
            self.assertIn("step_id", surface)
            self.assertNotIn("operation_id", surface)

    def test_checked_in_review_contract_and_lens_packages_recompute(self) -> None:
        self.assertEqual(
            set(REVIEW_CONTRACT),
            {"lens_contract_manifests", "review_contract"},
        )
        contract = REVIEW_CONTRACT["review_contract"]
        manifests = REVIEW_CONTRACT["lens_contract_manifests"]
        self.assertEqual(
            set(contract),
            {
                "attempt_quality",
                "contract_digest",
                "contract_id",
                "initial_wave",
                "material_change",
                "required_lenses",
                "schema",
                "standard_convergence",
                "transport_recovery",
            },
        )
        self.assertEqual(contract["schema"], "actuating-review-contract/v1")
        self.assertTrue(contract["contract_id"].strip())
        self.assertEqual(
            [lens["name"] for lens in contract["required_lenses"]],
            [
                "standard",
                "footgun-finder",
                "invariant-ace",
                "complexity-mitigator",
                "fresh-eyes",
            ],
        )
        self.assertEqual(
            [lens["role"] for lens in contract["required_lenses"]],
            ["standard", "auxiliary", "auxiliary", "auxiliary", "auxiliary"],
        )
        self.assertEqual(set(manifests), {lens["name"] for lens in contract["required_lenses"]})

        for lens in contract["required_lenses"]:
            with self.subTest(lens=lens["name"]):
                self.assertEqual(
                    set(lens),
                    {"contract_digest", "contract_ref", "name", "role"},
                )
                manifest = manifests[lens["name"]]
                self.assertEqual(set(manifest), {"resources"})
                resources = manifest["resources"]
                paths = [resource["path"] for resource in resources]
                self.assertTrue(lens["contract_ref"].strip())
                self.assertIn(lens["contract_ref"], paths)
                self.assertEqual(paths, sorted(set(paths)))
                basis = b"actuating-lens-contract/v1\0"
                for resource in resources:
                    path = resource["path"]
                    expected_file_digest = sha256((REPO / path).read_bytes())
                    self.assertEqual(resource["digest"], expected_file_digest)
                    basis += (
                        path.encode("utf-8")
                        + b"\0"
                        + expected_file_digest.encode("ascii")
                        + b"\0"
                    )
                self.assertEqual(lens["contract_digest"], sha256(basis))

        aggregate_basis = dict(contract)
        aggregate_basis["contract_digest"] = None
        self.assertEqual(contract["contract_digest"], sha256(canonical_json(aggregate_basis)))

    def test_request_identity_binds_every_semantic_input_and_exact_echo(self) -> None:
        for phrase in (
            '"actuating-review-request/v1" || 0x00',
            "goal_id || 0x00 || campaign_id || 0x00 || subject_digest || 0x00",
            "request_id || 0x00 || lens_name || 0x00 || role || 0x00",
            "lens_contract_digest || 0x00 || instruction_digest",
            "must echo both unchanged",
            "`baseSha`, `headSha`, and `targetFingerprint`",
            "exact UTF-8 `developerInstructions` bytes supplied to CAS",
            "workflow-binding echo alone is insufficient proof",
        ):
            self.assertIn(phrase, FLAT_REVIEW)

    def test_evidence_adapter_shapes_capability_and_runtime_gate_are_exact(self) -> None:
        for phrase in (
            "ledger --version >= 0.11.0",
            "append prepare state project doctor path",
            "cas --version >= 0.2.83",
            "exactly `run`, `start`, and `wait`",
            "review_session",
            "review-session",
            '"schema": "actuating-evidence-event/v1"',
            '"schema": "actuating-operation/v1"',
            '"schema": "actuating-evidence-input/v1"',
            'schema:"review-attempt-started/v1"',
            "review_attempt_started.receipt_ref",
            "Every `finding_refs` entry",
            "capabilityless recovery path",
            "reject any raw capability",
            "terminate the pending operation and invalidate its stored capability digest",
            "authority_granted:false",
            "semantic_decision_established:false",
            "never executes work, dispatches or interprets reviews, computes credit",
            "schema: actuating-verifier-receipt/v1",
            "receipt's `verifier.argv` to equal the current Construction obligation",
            "Missing or unresolvable attachment bytes block proof",
        ):
            self.assertIn(phrase, FLAT_EVIDENCE)
        for kind in (
            "goal_contract_registered",
            "counterexample_set_registered",
            "construction_contract_registered",
            "operation_prepared",
            "effect_recorded",
            "operation_observed",
            "operation_aborted",
            "publication_observed",
            "review_campaign_started",
            "review_request_bound",
            "review_attempt_started",
            "review_attempt_completed",
            "review_transport_failed",
        ):
            self.assertIn(kind, EVIDENCE)
        for body_schema in (
            'schema:"effect-recorded/v1"',
            'schema:"operation-observed/v1"',
            'schema:"operation-aborted/v1"',
            'schema:"publication-observed/v1"',
            'schema:"review-campaign-started/v1"',
            'schema:"review-request-bound/v1"',
            'schema:"review-attempt-started/v1"',
            'schema:"review-attempt-completed/v1"',
            'schema:"review-transport-failed/v1"',
        ):
            self.assertIn(body_schema, EVIDENCE)
        self.assertIn("standalone Goal Contract or Review Fold handoff", FLAT_EVIDENCE)
        self.assertIn("`follow-up` classes remain recorded and routed", FLAT_EVIDENCE)
        self.assertIn("do not block the current Goal", FLAT_EVIDENCE)

    def test_construction_dominance_covers_every_act_ak_dimension(self) -> None:
        for phrase in (
            "no worse in every ACT-AK dimension",
            "every required law satisfied by `B`",
            "every required observation preserved by `B`",
            "every Counterexample excluded by `B`",
            "no more independent law owners",
            "no more parallel semantic representations",
            "no more bypasses",
            "no more semantic mechanisms",
            "no more dominated residue",
            "no greater resource burden",
            "strictly better in at least one dimension",
            "prove `separate-laws`",
        ):
            self.assertIn(phrase, FLAT_CONSTRUCTION)

    def test_actuating_owns_decisions_and_ledger_is_non_executing(self) -> None:
        for phrase in (
            "correct-by-construction implementation",
            "Counterexample evaluation",
            "Construction selection",
            "the next action",
            "semantic evaluation of CAS owner facts and review credit",
            "authorship of its semantic receipt",
        ):
            self.assertIn(phrase, SKILL + OWNERS)
        for phrase in (
            "executes or edits repository work",
            "dispatches reviews or reads CAS verdict semantics",
            "computes review credit",
            "interprets Ship receipts",
            "selects a Construction or proof strategy",
            "emits `continue`, `ready-to-ship`, `complete`, or `blocked`",
            "authors an `actuating-closure-receipt/v1`",
        ):
            self.assertIn(phrase, FLAT_LEDGER)

    def test_ship_alone_owns_public_effects(self) -> None:
        self.assertIn("sole owner of public PR or tracker effects", SKILL)
        self.assertIn("sole public-effect owner", SHIP)
        self.assertIn("Ship never appends Actuating Evidence", SHIP)

    def test_closure_remains_a_current_semantic_theorem(self) -> None:
        self.assertIn("Closure is Actuating's deterministic semantic theorem", CLOSURE)
        self.assertIn("Actuating alone applies it", CLOSURE)
        self.assertIn("authors the resulting\n`actuating-closure-receipt/v1`", CLOSURE)
        self.assertIn("continue | ready-to-ship | complete | blocked", CLOSURE)
        self.assertIn("closure_route: local-implementation | final-closeout", CLOSURE)
        self.assertIn("must not infer applicability\nfrom absent fields", CLOSURE)
        self.assertIn("A `ready-to-ship` judgment deliberately omits this premise", CLOSURE)
        self.assertIn("evidence that only Ship can produce from that handoff", CLOSURE)
        self.assertIn("five consecutive distinct", CLOSURE)
        self.assertIn("Ledger validation, replay, `state`, or `project`", CLOSURE)
        self.assertIn("must not construct it, populate its verdict, or emit it", CLOSURE)

    def test_closure_route_applicability_is_cross_owner_exact(self) -> None:
        for phrase in (
            "A `ready-to-ship` judgment deliberately omits this premise",
            "A `ready-to-ship` judgment also omits this premise",
            "`ready-to-ship` is legal only on this route",
        ):
            self.assertIn(phrase, CLOSURE)
        flat_ship = " ".join(SHIP.split())
        flat_proof_patch = " ".join(PROOF_PATCH.split())
        self.assertIn("closure_route: final-closeout", flat_ship)
        self.assertIn("Reject `local-implementation` receipts", flat_ship)
        self.assertIn(
            "reject any supplied review-result or Ship-receipt payload",
            flat_proof_patch,
        )
        self.assertIn("require current Ship evidence when true", flat_proof_patch)
        self.assertIn(
            "A `ready-to-ship` verdict requires neither publication nor review evidence",
            FLAT_SKILL,
        )

    def test_review_contract_is_input_not_hardcoded_ledger_policy(self) -> None:
        for phrase in (
            "Actuating constructs and supplies the exact canonical Review Contract",
            "recompute `contract_digest`",
            "must not substitute an internal hardcoded contract",
            "Actuating decides whether the matched evidence earns credit",
        ):
            self.assertIn(phrase, FLAT_REVIEW)
        self.assertIn("Actuating-owned actuating-review-contract/v1", DECISION)
        self.assertIn("Ledger computes review credit", DECISION)
        self.assertIn("Ledger hardcodes the Review Contract", DECISION)

    def test_actuating_authors_semantic_closure_receipt(self) -> None:
        self.assertIn(
            "Actuating applies the closure theorem and authors actuating-closure-receipt/v1",
            DECISION,
        )
        self.assertIn("Ledger emits a semantic closure verdict or receipt", DECISION)

    def test_removed_peer_surfaces_do_not_exist(self) -> None:
        for relative in (
            "references/kernel-commands.md",
            "references/live-semantics.yaml",
            "references/review-policy.md",
            "references/review-resolution.md",
            "references/legacy-actuating-v1.md",
            "references/legacy-closure.md",
            "references/legacy-decision-contract.yaml",
            "references/legacy-live-semantics.yaml",
            "tests/test_review_policy_contract.py",
        ):
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_no_retired_authority_names_remain_in_current_doctrine(self) -> None:
        doctrine = "\n".join((SKILL, OWNERS, CONSTRUCTION, REVIEW, CLOSURE, DECISION))
        for retired in (
            "GC-v2",
            "RF-v2",
            "actuation-review-policy/v2",
            "review-resolution/v1",
            "closure-decision/v1",
            "legacy-actuating-v1",
            "actuating-legacy-cutover",
            "auxiliary-remediation carry",
            "Closure is a deterministic projection",
            "closure views",
        ):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, doctrine)

    def test_actuating_package_stays_below_budget(self) -> None:
        total = sum(
            len(path.read_text(encoding="utf-8").splitlines())
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".json", ".md", ".yaml", ".py"}
        )
        self.assertLess(total, 1956, total)


if __name__ == "__main__":
    unittest.main()
