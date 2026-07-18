#!/usr/bin/env -S uv run python
from __future__ import annotations

import copy
import json
import os
import re
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
ORCHESTRATION = ROOT / "references" / "orchestration.md"
CONTRACTS = ROOT / "references" / "contracts.md"
GRADING = ROOT / "references" / "grading-and-progression.md"
SURFACE_CHECKER = ROOT / "scripts" / "check-operator-surface"
NATIVE_SURFACE_LOCK = ROOT / "native-surface.lock.json"
OPERATOR_CONTRACT_WORKFLOW = ROOT.parents[2] / ".github" / "workflows" / "hylo-operator-contract.yml"
SURFACE_MANIFEST_ENV = "HYLO_OPERATOR_SURFACE_MANIFEST"
NATIVE_SURFACE_LOCK_SCHEMA = "hylo-native-surface-lock/v1"
EXPECTED_ROUTE_SCHEMA = "hylo-operator-recipe-expectation/v1"
EXPECTED_ROUTE_SEMANTIC_KEYS = (
    "trial_boundary",
    "execution_authorities",
    "routes",
    "allocation",
    "sealed_product_boundary",
    "candidate_lifecycle",
)
SHARED_VERSION_PROBES = frozenset(
    {
        "cas --version",
        "ledger --version",
        "seq --version",
    }
)
ALLOWED_OWNER_SURFACE_PROBES = SHARED_VERSION_PROBES | {
    "ledger --source hylo --help",
}
SUPPORTING_OWNER_SECTIONS = (
    (ROOT.parent / "seq" / "SKILL.md", "Hylo CRF/HCTP product surface"),
    (ROOT.parent / "cas" / "SKILL.md", "HCTP trial execution"),
    (ROOT.parent / "ledger" / "SKILL.md", "Hylo CRF/HCTP authority"),
    (ROOT.parent / "retrace" / "SKILL.md", "HCTP historical lane bridge"),
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def markdown_section(text: str, heading: str) -> str:
    heading_match = re.search(
        rf"^(?P<marks>#{{2,6}})\s+{re.escape(heading)}\s*$",
        text,
        flags=re.MULTILINE,
    )
    if heading_match is None:
        raise ValueError(f"missing Markdown section: {heading}")
    level = len(heading_match.group("marks"))
    start = heading_match.end()
    next_heading = re.search(rf"^#{{1,{level}}}\s+", text[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def shell_blocks(text: str) -> str:
    return "\n".join(
        match.group("body")
        for match in re.finditer(
            r"^```(?:bash|sh|shell|zsh)\s*$\n(?P<body>.*?)^```\s*$",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    )


def shell_command_identity(line: str) -> str | None:
    tokens = line.strip().removesuffix("\\").split()
    if not tokens or tokens[0] not in {"cas", "ledger", "seq"}:
        return None

    component = tokens[0]
    if len(tokens) == 1:
        return component
    if tokens[1] == "--version":
        return f"{component} --version"

    if component == "ledger":
        if tokens[1:3] == ["--source", "hylo"]:
            return " ".join(tokens[:4])
        if tokens[1] == "validate" and len(tokens) >= 3:
            return " ".join(tokens[:3])
        return " ".join(tokens[:2])

    if component == "seq" and tokens[1] == "hctp-source" and len(tokens) >= 3:
        return " ".join(tokens[:3])
    if component == "cas" and tokens[1] == "trial" and len(tokens) >= 3:
        return " ".join(tokens[:3])
    return " ".join(tokens[:2])


def documented_shell_command_inventory(
    text: str,
) -> tuple[set[str], set[str]]:
    commands: set[str] = set()
    shared_probes: set[str] = set()
    for line in shell_blocks(text).splitlines():
        identity = shell_command_identity(line)
        if identity is None:
            continue
        if identity in SHARED_VERSION_PROBES:
            shared_probes.add(identity)
        else:
            commands.add(identity)
    return commands, shared_probes


def command_component(identity: str) -> str | None:
    if identity.startswith("ledger --source hylo "):
        return "ledger-hylo"
    if identity == "ledger validate" or identity.startswith("ledger validate "):
        return "ledger-validator"
    if identity == "seq" or identity.startswith("seq "):
        return "seq"
    if identity == "cas" or identity.startswith("cas "):
        return "cas"
    return None


def documented_owner_command_inventory(
    texts: tuple[str, ...],
) -> tuple[dict[str, set[str]], set[str]]:
    commands: dict[str, set[str]] = {}
    probes: set[str] = set()
    for text in texts:
        for line in shell_blocks(text).splitlines():
            identity = shell_command_identity(line)
            if identity is None:
                continue
            if identity in ALLOWED_OWNER_SURFACE_PROBES:
                probes.add(identity)
                continue
            component = command_component(identity)
            if component is None:
                continue
            commands.setdefault(component, set()).add(identity)
    return commands, probes


def native_recipe_bindings(orchestration: str) -> tuple[tuple[str, str], ...]:
    section = markdown_section(orchestration, "Native operator-recipe binding")
    bindings: list[tuple[str, str]] = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().split("|")[1:-1]]
        if len(cells) != 2 or not all(
            len(cell) >= 2 and cell.startswith("`") and cell.endswith("`")
            for cell in cells
        ):
            continue
        bindings.append((cells[0][1:-1], cells[1][1:-1]))
    return tuple(bindings)


def native_recipe_semantic_binding(orchestration: str) -> dict[str, object]:
    section = markdown_section(orchestration, "Native semantic binding")
    blocks = re.findall(
        r"^```json\s*$\n(?P<body>.*?)^```\s*$",
        section,
        flags=re.MULTILINE | re.DOTALL,
    )
    if len(blocks) != 1:
        raise ValueError("Native semantic binding must contain exactly one JSON block")
    payload = json.loads(blocks[0])
    if not isinstance(payload, dict):
        raise ValueError("Native semantic binding JSON must contain an object")
    return payload


def flatten_json(
    value: object, prefix: tuple[str, ...] = ()
) -> dict[str, tuple[str, object]]:
    path = ".".join(prefix) if prefix else "$"
    flattened: dict[str, tuple[str, object]] = {}
    if isinstance(value, dict):
        flattened[path] = ("object", len(value))
        for key in sorted(value):
            flattened.update(flatten_json(value[key], (*prefix, key)))
    elif isinstance(value, list):
        flattened[path] = ("array", len(value))
        for index, item in enumerate(value):
            flattened.update(flatten_json(item, (*prefix, f"[{index}]")))
    else:
        flattened[path] = (type(value).__name__, value)
    return flattened


def validate_native_semantic_binding(
    expected_route: dict[str, object], documented: dict[str, object]
) -> None:
    expected_top_level = {
        "schema",
        "portable_sequence",
        *EXPECTED_ROUTE_SEMANTIC_KEYS,
    }
    if set(expected_route) != expected_top_level:
        raise ValueError(
            "pinned expected route has an unbound or missing top-level semantic object"
        )
    if set(documented) != set(EXPECTED_ROUTE_SEMANTIC_KEYS):
        raise ValueError(
            "documented semantic binding must contain every pinned semantic object"
        )

    expected = {
        key: expected_route[key] for key in EXPECTED_ROUTE_SEMANTIC_KEYS
    }
    expected_flat = flatten_json(expected)
    documented_flat = flatten_json(documented)
    if documented_flat == expected_flat:
        return

    changed_paths = sorted(
        path
        for path in set(expected_flat) | set(documented_flat)
        if expected_flat.get(path) != documented_flat.get(path)
    )
    raise ValueError(
        "documented semantic binding does not exactly match the pinned native route: "
        + ", ".join(changed_paths)
    )


def load_expected_route(surface_manifest: dict[str, object]) -> dict[str, object]:
    path = Path(str(surface_manifest["path"])).with_name("expected-route.json")
    payload = json.loads(read(path))
    if not isinstance(payload, dict):
        raise ValueError("pinned expected-route.json must contain an object")
    return {
        "path": str(path.resolve(strict=True)),
        "payload": payload,
    }


def validate_native_recipe_binding(
    expected_route: dict[str, object],
    bindings: tuple[tuple[str, str], ...],
    surface_manifest: dict[str, object],
) -> None:
    if expected_route.get("schema") != EXPECTED_ROUTE_SCHEMA:
        raise ValueError(f"expected route schema must be {EXPECTED_ROUTE_SCHEMA}")
    expected_steps = expected_route.get("portable_sequence")
    if not isinstance(expected_steps, list) or not all(
        isinstance(step, str) and step for step in expected_steps
    ):
        raise ValueError("expected route portable_sequence must be a string array")
    documented_steps = [step for step, _ in bindings]
    if documented_steps != expected_steps:
        raise ValueError(
            "documented recipe steps do not exactly match the pinned portable sequence"
        )

    command_owners: dict[str, str] = {}
    for command in surface_manifest["commands"]:
        identity = command["documented_command"]
        owner = command["component"]
        prior = command_owners.setdefault(identity, owner)
        if prior != owner:
            raise ValueError(f"manifest command has multiple owners: {identity}")
    for step, identity in bindings:
        documented_owner = command_component(identity)
        manifest_owner = command_owners.get(identity)
        if documented_owner is None or manifest_owner != documented_owner:
            raise ValueError(
                f"recipe step {step} uses an unmanifested owner command: {identity}"
            )


class HyloOperatorRecipeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read(SKILL)
        cls.orchestration = read(ORCHESTRATION)
        cls.contracts = read(CONTRACTS)
        cls.grading = read(GRADING)
        cls.documentation = "\n".join(
            (cls.skill, cls.orchestration, cls.contracts, cls.grading)
        )
        cls.supporting_owner_documentation = tuple(
            markdown_section(read(path), heading)
            for path, heading in SUPPORTING_OWNER_SECTIONS
        )
        cls.checker = runpy.run_path(str(SURFACE_CHECKER))
        manifest_path = os.environ.get(SURFACE_MANIFEST_ENV)
        cls.surface_manifest = (
            cls.checker["load_surface_manifest"](manifest_path)
            if manifest_path
            else None
        )
        cls.expected_route = (
            load_expected_route(cls.surface_manifest)
            if cls.surface_manifest is not None
            else None
        )

    def require_surface_manifest(self) -> dict[str, object]:
        if self.surface_manifest is None:
            self.skipTest(
                f"set {SURFACE_MANIFEST_ENV} to the pinned skills-zig manifest"
            )
        return self.surface_manifest

    def require_expected_route(self) -> dict[str, object]:
        if self.expected_route is None:
            self.skipTest(
                f"set {SURFACE_MANIFEST_ENV} to the pinned skills-zig manifest"
            )
        return self.expected_route

    def test_operator_route_has_stable_owner_sections(self) -> None:
        for heading in (
            "Execution graph",
            "Native operator-recipe binding",
            "Source route table",
            "Registration order",
            "Lane execution",
            "Allocation and chronology",
            "Sealed assurance",
            "Candidate lifecycle",
        ):
            with self.subTest(heading=heading):
                self.assertRegex(
                    self.orchestration,
                    rf"(?m)^#{{2,3}}\s+{re.escape(heading)}\s*$",
                )

        for heading in (
            "Mode-sensitive capability gate",
            "Candidate lifecycle",
            "Workflow",
        ):
            with self.subTest(heading=heading):
                self.assertIn(f"## {heading}", self.skill)

    def test_checker_uses_the_pinned_manifest_and_keeps_binary_overrides(self) -> None:
        manifest = self.require_surface_manifest()
        self.assertEqual("hylo-operator-surface-manifest/v1", manifest["schema"])
        self.assertTrue(manifest["commands"])
        self.assertTrue(manifest["required_capabilities"])
        self.assertNotIn(
            "hctp-sealed-role-driver",
            "\n".join(
                command["documented_command"] for command in manifest["commands"]
            ),
        )

        checker_source = read(SURFACE_CHECKER)
        self.assertIn("--surface-manifest", checker_source)
        self.assertIn("HYLO_OPERATOR_SURFACE_MANIFEST", checker_source)
        for binary_flag in ("--seq", "--ledger", "--cas"):
            with self.subTest(binary_flag=binary_flag):
                self.assertIn(binary_flag, checker_source)
        for retired_inventory in (
            "SEQ_FEATURES =",
            "LEDGER_FEATURES =",
            "CAS_FEATURES =",
            "LEDGER_TRIAL_COMMANDS =",
            "LEDGER_VALIDATE_CONTRACTS =",
            "CAS_OPERATOR_TRIAL_COMMANDS =",
        ):
            with self.subTest(retired_inventory=retired_inventory):
                self.assertNotIn(retired_inventory, checker_source)

    def test_native_surface_lock_is_an_exact_immutable_source_address(self) -> None:
        lock = json.loads(read(NATIVE_SURFACE_LOCK))
        self.assertEqual(
            {"schema", "repository", "commit"},
            set(lock),
        )
        self.assertEqual(NATIVE_SURFACE_LOCK_SCHEMA, lock["schema"])
        self.assertEqual("tkersey/skills-zig", lock["repository"])
        self.assertRegex(lock["commit"], r"\A[0-9a-f]{40}\Z")

    def test_documentation_projects_the_exact_pinned_native_recipe(self) -> None:
        manifest = self.require_surface_manifest()
        expected = self.require_expected_route()
        expected_path = Path(str(manifest["path"])).with_name("expected-route.json")
        self.assertEqual(expected_path.resolve(strict=True), Path(expected["path"]))

        bindings = native_recipe_bindings(self.orchestration)
        self.assertTrue(bindings)
        validate_native_recipe_binding(expected["payload"], bindings, manifest)
        semantic_binding = native_recipe_semantic_binding(self.orchestration)
        validate_native_semantic_binding(expected["payload"], semantic_binding)

    def test_native_recipe_binding_rejects_sequence_and_owner_drift(self) -> None:
        manifest = self.require_surface_manifest()
        expected = self.require_expected_route()["payload"]
        bindings = native_recipe_bindings(self.orchestration)
        sequence = list(expected["portable_sequence"])

        sequence_variants = {
            "missing": sequence[:-1],
            "added": sequence + ["unreleased_step"],
            "reordered": [sequence[1], sequence[0], *sequence[2:]],
        }
        for label, variant in sequence_variants.items():
            changed = dict(expected)
            changed["portable_sequence"] = variant
            with self.subTest(label=label), self.assertRaisesRegex(
                ValueError, "do not exactly match"
            ):
                validate_native_recipe_binding(changed, bindings, manifest)

        unmanifested = list(bindings)
        unmanifested[0] = (unmanifested[0][0], "seq unreleased-command")
        with self.assertRaisesRegex(ValueError, "unmanifested owner command"):
            validate_native_recipe_binding(expected, tuple(unmanifested), manifest)

    def test_native_semantic_binding_rejects_each_object_drift(self) -> None:
        expected = self.require_expected_route()["payload"]
        documented = native_recipe_semantic_binding(self.orchestration)
        flattened = flatten_json(documented)
        self.assertGreater(len(flattened), len(EXPECTED_ROUTE_SEMANTIC_KEYS))

        for semantic_key in EXPECTED_ROUTE_SEMANTIC_KEYS:
            changed = copy.deepcopy(expected)
            changed[semantic_key] = {"deliberate_drift": True}
            with self.subTest(semantic_key=semantic_key), self.assertRaisesRegex(
                ValueError, "does not exactly match"
            ):
                validate_native_semantic_binding(changed, documented)

        diagnostic = documented["routes"]["diagnostic_only"]
        self.assertFalse(diagnostic["registration_allowed"])
        self.assertIn(
            "trial compilation, registration, and comparison execution forbidden",
            self.documentation,
        )

    def test_operator_contract_actions_are_immutable_full_sha_pins(self) -> None:
        workflow = read(OPERATOR_CONTRACT_WORKFLOW)
        action_refs = re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", workflow)
        self.assertTrue(action_refs)
        for action_ref in action_refs:
            with self.subTest(action_ref=action_ref):
                self.assertRegex(action_ref, r"\A[^@\s]+@[0-9a-f]{40}\Z")

    def test_operator_contract_executes_the_pinned_native_recipe_lanes(self) -> None:
        workflow = read(OPERATOR_CONTRACT_WORKFLOW)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertGreaterEqual(workflow.count("persist-credentials: false"), 2)
        portable = "test-hylo-operator-recipe"
        executable = "test-hylo-operator-recipe-executable"
        self.assertIn(portable, workflow)
        self.assertIn(executable, workflow)
        recipe_step = workflow.index("Execute pinned native operator recipe")
        self.assertLess(recipe_step, workflow.index("Verify documentation contract"))

    def test_registration_order_matches_the_native_transition_graph(self) -> None:
        section = markdown_section(self.orchestration, "Registration order")
        ordered_markers = (
            "campaign_created",
            "target_bundle_admitted",
            "scenario_admitted",
            "owner-applied change",
            "doctor and inspect admission state",
            "compile trial",
            "validate trial",
            "source-validate completed trial",
            "register trial",
        )
        positions = []
        for marker in ordered_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, section)
            positions.append(section.index(marker))
        self.assertEqual(sorted(positions), positions)

        self.assertIn("A trial is additive to an admitted campaign", self.documentation)

    def test_lane_source_materialization_precedes_start_and_private_treatment(self) -> None:
        for heading in ("Direct lane", "Historical lane"):
            section = markdown_section(self.orchestration, heading)
            with self.subTest(heading=heading):
                self.assertLess(
                    section.index("materialize the exact visible input"),
                    section.index("start-lane or commit-lane-start"),
                )
                self.assertLess(
                    section.index("start-lane or commit-lane-start"),
                    section.index("materialize the selected treatment"),
                )
                self.assertLess(
                    section.index("materialize the selected treatment"),
                    section.index("cas trial run"),
                )

    def test_direct_and_historical_routes_are_distinct(self) -> None:
        route_table = markdown_section(self.orchestration, "Source route table")
        direct_lane = markdown_section(self.orchestration, "Direct lane")
        historical_lane = markdown_section(self.orchestration, "Historical lane")
        for marker in (
            'source_profile.kind == "direct"',
            'source_profile.kind == "historical_decision"',
            "replay_eligible:false",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, route_table)

        normalized_direct = " ".join(direct_lane.split()).lower()
        self.assertRegex(
            normalized_direct,
            r"compile-replay.{0,100}(?:skip|forbid|must not|forbidden)",
        )
        normalized_historical = " ".join(historical_lane.split()).lower()
        self.assertRegex(
            normalized_historical,
            r"cas.{0,180}(?:dcp/rip|replay).{0,120}(?:internal|internally)",
        )
        normalized_route = " ".join(route_table.split()).lower()
        self.assertRegex(
            normalized_route,
            r"replay_eligible:false.{0,300}diagnostic_only.{0,120}(?:forbid|forbidden)",
        )
        self.assertIn("never upgraded by changing its label", normalized_route)

    def test_preflight_projection_uses_canonical_field_names(self) -> None:
        checker = runpy.run_path(str(SURFACE_CHECKER))
        expected = {
            "source_profile_kind",
            "compile_replay_required",
            "replay_preparation_mode",
            "source_profile_body_delivery",
            "execution_route",
            "required_lineage",
        }
        self.assertEqual(expected, checker["CAS_PREFLIGHT_FIELDS"])
        cas_skill = read(ROOT.parent / "cas" / "SKILL.md")
        for field in expected:
            with self.subTest(field=field):
                self.assertIn(field, self.documentation)
                self.assertIn(field, cas_skill)
        for retired in ("source_kind", "historical_replay_required"):
            with self.subTest(retired=retired):
                self.assertNotIn(retired, self.documentation)
                self.assertNotIn(retired, cas_skill)

    def test_replay_preparation_is_integrated_and_not_an_operator_step(self) -> None:
        manifest = self.require_surface_manifest()
        closure, _ = self.checker["project_mode"]("open-direct-trial", None)
        operator_commands = self.checker["command_tokens"](
            manifest, "cas", closure
        ) - {"capabilities", "trial"}
        self.assertNotIn("compile-replay", operator_commands)
        self.assertEqual(
            {"preflight", "run", "status", "cleanup"}, operator_commands
        )

        cas_skill = read(ROOT.parent / "cas" / "SKILL.md")
        supporting = "\n".join(
            (
                self.documentation,
                cas_skill,
                read(ROOT.parent / "seq" / "SKILL.md"),
                read(ROOT.parent / "ledger" / "SKILL.md"),
                read(ROOT.parent / "retrace" / "SKILL.md"),
            )
        )
        normalized = " ".join(supporting.split())
        for marker in (
            'compile_replay_required:false',
            'replay_preparation_mode:"none"',
            'replay_preparation_mode:"integrated_run"',
            "execution_authority:false",
            "--source-profile-fd",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)
        self.assertNotIn("compile_replay_required:true", normalized)
        self.assertRegex(
            normalized,
            r"run.{0,100}(?:consumes neither|does not consume).{0,120}(?:receipt|dcp/rip)",
        )
        self.assertRegex(
            normalized,
            r"protected.{0,120}directly.{0,80}cas trial run --source-profile-fd",
        )

    def test_source_receipt_validation_follows_trial_construction(self) -> None:
        section = markdown_section(
            self.orchestration, "Phase 6 — Compile and register the trial"
        )
        self.assertIn("--custody-output-fd", section)
        self.assertIn("hylo-trial-build-receipt/v2", section)
        self.assertIn("custody_material_delivered:true", section)
        self.assertLess(section.index("compile-trial"), section.index("validate-trial"))
        self.assertLess(
            section.index("validate-trial"), section.index("hctp-source validate")
        )
        self.assertLess(
            section.index("hctp-source validate"), section.index("register-trial")
        )
        self.assertIn("--custody-input-fd", section)

    def test_private_v2_lane_materialization_precedes_cas_run(self) -> None:
        section = markdown_section(self.orchestration, "Lane execution")
        bridge = markdown_section(self.orchestration, "Private treatment bridge")
        for marker in (
            "hylo-trial/v2",
            "lane-materialization",
            "--custody-input-fd",
            "--lease-input-fd",
            "--materialization-output-fd",
            "--materialization-fd",
            "hylo-lane-materialization-receipt/v2",
            "hylo-run-receipt/v2",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, bridge)
        self.assertLess(bridge.index("lane-materialization"), bridge.index("cas trial run"))
        self.assertIn("treatment_commitment", bridge)
        self.assertIn("commitment-only", bridge)
        self.assertIn("--materialization-fd", section)

    def test_private_v2_start_and_case_materialization_use_exact_openings(self) -> None:
        lane_execution = markdown_section(self.orchestration, "Lane execution")
        private_bridge = markdown_section(
            self.orchestration, "Private treatment bridge"
        )
        for marker in (
            "start-lane",
            "--custody-input-fd",
            "hylo-source-selection-opening/v1",
            "--source-selection-opening-fd",
            "hylo-target-common-projection-opening/v1",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, lane_execution + private_bridge)

        seq_skill = read(ROOT.parent / "seq" / "SKILL.md")
        self.assertIn("--source-selection-opening-fd", seq_skill)
        self.assertIn("hylo-source-selection-opening/v1", seq_skill)
        ledger_skill = read(ROOT.parent / "ledger" / "SKILL.md")
        self.assertIn("start-lane", ledger_skill)
        self.assertIn("--custody-input-fd", ledger_skill)
        cas_skill = read(ROOT.parent / "cas" / "SKILL.md")
        self.assertIn("hylo-target-common-projection-opening/v1", cas_skill)

    def test_private_v2_public_and_custody_carriers_are_explicit(self) -> None:
        compiler = markdown_section(
            self.orchestration, "Phase 6 — Compile and register the trial"
        )
        reveal = markdown_section(
            self.orchestration, "Phase 8 — Grade, reveal, and prove"
        )
        for marker in (
            "hylo-trial/v2",
            "hylo-trial-custody/v1",
            "artifact:sha256:<64 lowercase hex>",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, compiler)
        self.assertNotIn("hylo-trial-reveal-material/v1", compiler)
        for marker in (
            "hylo-trial-reveal/v2",
            "full source-selection receipt remains custody-only",
            "excludes private custody",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, reveal)

        blinding = markdown_section(self.grading, "Blinding and commitments")
        for marker in (
            "full source-selection receipt",
            "raw before/after target fingerprints",
            "target common projection",
            "intervention witness",
            "treatment opening or materialization body",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, blinding)

    def test_reveal_result_close_and_proof_follow_native_lifecycle(self) -> None:
        phase = markdown_section(
            self.orchestration, "Phase 8 — Grade, reveal, and prove"
        )
        ordered_commands = (
            "ledger --source hylo reveal-trial",
            "ledger --source hylo trial-result --repo <repo> "
            "--trial-id <trial-id> --format json",
            "ledger --source hylo close-trial --repo <repo> --trial-id <trial-id>",
            "ledger --source hylo proof-artifact-set",
        )
        positions = []
        for command in ordered_commands:
            with self.subTest(command=command):
                self.assertIn(command, phase)
            positions.append(phase.index(command))
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Observe the derived result before closing the trial", phase)
        self.assertIn("Proof occurs only after `close-trial`", phase)

    def test_v2_source_profile_and_fir_are_safe_public_projections(self) -> None:
        supporting = "\n".join(
            read(ROOT.parent / name / "SKILL.md")
            for name in ("cas", "seq", "ledger", "retrace")
        )
        normalized_documentation = " ".join(self.documentation.split())
        normalized_supporting = " ".join(supporting.split())
        for marker in (
            "units[*].source_profile",
            "exact native safe projection",
            "hylo-fir-public-projection/v1",
            "full FIR",
            "v1",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized_documentation)
                self.assertIn(marker, normalized_supporting)
        self.assertRegex(
            " ".join((self.documentation + supporting).split()),
            r"v1.{0,160}(?:compatible|established).{0,80}full-FIR carrier",
        )

    def test_documented_native_command_inventory_is_complete(self) -> None:
        manifest = self.require_surface_manifest()
        operator_closure, _ = self.checker["project_mode"]("operator", None)
        manifest_commands = [
            command
            for command in manifest["commands"]
            if operator_closure.intersection(command["modes"])
        ]
        self.assertTrue(manifest_commands)
        for command in manifest_commands:
            documented = command["documented_command"]
            help_token = command["help_token"]
            with self.subTest(command=documented):
                self.assertTrue(
                    documented in self.documentation
                    or help_token in self.documentation,
                    f"manifest command is not documented: {documented}",
                )

        examples = shell_blocks(self.documentation)
        self.assertNotRegex(examples, r"(?m)^\s*cas\s+trial\s+compile-replay\b")

    def test_documented_operator_commands_are_owned_by_the_native_manifest(self) -> None:
        manifest = self.require_surface_manifest()
        manifest_by_component: dict[str, set[str]] = {}
        for command in manifest["commands"]:
            manifest_by_component.setdefault(command["component"], set()).add(
                command["documented_command"]
            )

        documented_by_component, probes = documented_owner_command_inventory(
            (self.documentation, *self.supporting_owner_documentation)
        )
        for _, identity in native_recipe_bindings(self.orchestration):
            component = command_component(identity)
            self.assertIsNotNone(component)
            documented_by_component.setdefault(component, set()).add(identity)

        self.assertEqual(ALLOWED_OWNER_SURFACE_PROBES, probes)
        for component, documented_commands in sorted(
            documented_by_component.items()
        ):
            missing = sorted(
                documented_commands - manifest_by_component.get(component, set())
            )
            with self.subTest(component=component):
                self.assertFalse(
                    missing,
                    "documented owner commands are absent from the native manifest: "
                    + ", ".join(missing),
                )

    def test_reverse_inventory_exposes_an_unmanifested_command(self) -> None:
        manifest = self.require_surface_manifest()
        manifest_commands = {
            command["documented_command"]
            for command in manifest["commands"]
            if command["component"] == "ledger-hylo"
        }
        documented_by_component, probes = documented_owner_command_inventory(
            (
                "```bash\nledger --source hylo unmanifested-command --repo REPO\n```\n",
            )
        )
        self.assertEqual(set(), probes)
        self.assertEqual(
            {"ledger --source hylo unmanifested-command"},
            documented_by_component["ledger-hylo"] - manifest_commands,
        )

    def test_balanced_allocation_is_not_compatibility_chronology(self) -> None:
        section = markdown_section(self.orchestration, "Allocation and chronology")
        normalized = " ".join(section.split()).lower()
        for marker in ("a/b", "b/a", "either semantic arm", "compatibility"):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)
        self.assertRegex(
            normalized,
            r"compatibility.{0,500}baseline.{0,180}(?:predate|before).{0,120}candidate",
        )

    def test_sealed_route_requires_an_admitted_external_broker(self) -> None:
        section = markdown_section(self.orchestration, "Sealed assurance")
        normalized = " ".join(section.split()).lower()
        for marker in (
            "admitted broker",
            "hctp-sealed-role-driver",
            "conformance",
            "not installed product capability",
            "os_confinement:false",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

        # Mentioning the fixture is allowed; presenting it as an executable
        # command in a shell block is not.
        driver_invocation = re.compile(r"(?m)^\s*(?:\S*/)?hctp-sealed-role-driver\b")
        self.assertIsNone(driver_invocation.search(shell_blocks(self.documentation)))

    def test_matching_broker_commitments_do_not_establish_admission(self) -> None:
        check_sealed_broker = self.checker["check_sealed_broker"]
        require_admission = self.checker["require_sealed_broker_admission"]
        sha256_file = self.checker["sha256_file"]
        check_failure = self.checker["CheckFailure"]

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            broker = root / "broker"
            broker.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            broker.chmod(0o700)
            contract = root / "broker-contract.json"
            contract.write_text('{"schema":"test-only"}\n', encoding="utf-8")
            args = SimpleNamespace(
                sealed_broker=str(broker),
                sealed_broker_sha256=sha256_file(broker),
                sealed_broker_contract=str(contract),
                sealed_broker_contract_sha256=sha256_file(contract),
            )

            evidence = check_sealed_broker(args)
            self.assertTrue(evidence["configured"])
            self.assertTrue(evidence["commitments_verified"])
            self.assertFalse(evidence["admitted"])
            with self.assertRaisesRegex(
                check_failure,
                "matching caller-provided broker commitments do not establish",
            ):
                require_admission(evidence)

    def test_candidate_evaluation_and_derivation_are_separate_lifecycles(self) -> None:
        section = markdown_section(self.orchestration, "Candidate lifecycle")
        normalized = " ".join(section.split()).lower()
        for marker in (
            "evaluate existing candidate",
            "derive next candidate",
            "owner",
            "run",
            "new evaluation trial",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)
        self.assertIn("authority_granted:false", self.documentation)

    def test_protected_fd_examples_do_not_use_named_file_redirection(self) -> None:
        unsafe = re.compile(r"(?m)(?:^|\s)(?:[3-9]|[1-9][0-9]+)(?:>|<)(?![&])")
        self.assertIsNone(unsafe.search(shell_blocks(self.documentation)))

    def test_live_probe_keeps_case_blinding_orthogonal_to_source_route(self) -> None:
        manifest = self.require_surface_manifest()
        project_mode = self.checker["project_mode"]
        required_features = self.checker["required_features"]
        requires_historical_profile_fd = self.checker[
            "requires_historical_profile_fd"
        ]
        cas_features = self.checker["feature_requirements_by_mode"](
            manifest, "cas"
        )
        seq_features = self.checker["feature_requirements_by_mode"](
            manifest, "seq"
        )

        direct, direct_route = project_mode("case-blind-trial", None)
        historical, historical_route = project_mode(
            "case-blind-trial", "historical_decision"
        )
        operator, operator_route = project_mode("operator", None)
        sealed_direct, sealed_direct_route = project_mode("sealed-trial", None)
        sealed_historical, sealed_historical_route = project_mode(
            "sealed-trial", "historical_decision"
        )
        plain_historical, plain_historical_route = project_mode(
            "historical-trial", None
        )

        self.assertEqual("direct", direct_route)
        self.assertNotIn("historical-trial", direct)
        self.assertNotIn("historical-case-blind-trial", direct)
        self.assertEqual("historical_decision", historical_route)
        self.assertIn("historical-trial", historical)
        self.assertIn("historical-case-blind-trial", historical)
        self.assertEqual("direct+historical_decision", operator_route)
        self.assertIn("historical-trial", operator)
        self.assertIn("historical-case-blind-trial", operator)
        self.assertEqual("direct", sealed_direct_route)
        self.assertNotIn("historical-trial", sealed_direct)
        self.assertNotIn("historical-case-blind-trial", sealed_direct)
        self.assertEqual("historical_decision", sealed_historical_route)
        self.assertIn("historical-trial", sealed_historical)
        self.assertIn("historical-case-blind-trial", sealed_historical)
        self.assertEqual("historical_decision", plain_historical_route)
        self.assertIn("historical-trial", plain_historical)
        self.assertNotIn("historical-case-blind-trial", plain_historical)

        direct_caps = required_features(direct, cas_features)
        historical_caps = required_features(historical, cas_features)
        self.assertNotIn("hylo_internal_historical_replay_v1", direct_caps)
        self.assertNotIn("dcp_v2", direct_caps)
        self.assertIn("hylo_internal_historical_replay_v1", historical_caps)
        self.assertIn("dcp_v2", historical_caps)

        direct_seq_caps = required_features(direct, seq_features)
        historical_seq_caps = required_features(historical, seq_features)
        plain_historical_seq_caps = required_features(
            plain_historical, seq_features
        )
        self.assertIn("hctp_source_selection_opening_fd_v1", direct_seq_caps)
        self.assertNotIn("hctp_historical_profile_v1", direct_seq_caps)
        self.assertNotIn("hctp_case_blind_source_profile_fd_v1", direct_seq_caps)
        self.assertIn("hctp_historical_profile_v1", historical_seq_caps)
        self.assertIn(
            "hctp_case_blind_source_profile_fd_v1", historical_seq_caps
        )
        self.assertIn(
            "hctp_historical_profile_v1", plain_historical_seq_caps
        )
        self.assertNotIn(
            "hctp_case_blind_source_profile_fd_v1",
            plain_historical_seq_caps,
        )
        self.assertFalse(requires_historical_profile_fd(direct))
        self.assertTrue(requires_historical_profile_fd(historical))
        self.assertFalse(requires_historical_profile_fd(plain_historical))

    def test_proof_export_requires_v2_trial_custody_and_proof_capabilities(self) -> None:
        manifest = self.require_surface_manifest()
        project_mode = self.checker["project_mode"]
        required_features = self.checker["required_features"]
        ledger_requirements = self.checker["feature_requirements_by_mode"](
            manifest, "ledger-hylo"
        )

        closure, selected_route = project_mode("proof-export", None)
        self.assertIsNone(selected_route)
        self.assertNotIn("open-direct-trial", closure)
        self.assertIn("ledger-v2-proof-prerequisites", closure)
        self.assertIn("proof-export", closure)
        self.assertNotIn("historical-trial", closure)
        required = required_features(closure, ledger_requirements)
        for capability in (
            "hylo_trial_v2",
            "hylo_private_trial_custody_v1",
            "hylo_trial_custody_fd_v1",
            "hylo_private_lane_start_custody_fd_v1",
            "hylo_reveal_material_fd_v1",
            "hylo_proof_bundle_v1",
            "hylo_external_proof_anchor_v1",
        ):
            with self.subTest(capability=capability):
                self.assertIn(capability, required)

        cas_requirements = self.checker["feature_requirements_by_mode"](
            manifest, "cas"
        )
        self.assertEqual(set(), required_features(closure, cas_requirements))

    def test_proof_export_needs_v2_ledger_but_does_not_resolve_cas(self) -> None:
        manifest = self.require_surface_manifest()
        closure, _ = self.checker["project_mode"]("proof-export", None)
        ledger_requirements = self.checker["feature_requirements_by_mode"](
            manifest, "ledger-hylo"
        )
        required = self.checker["required_features"](closure, ledger_requirements)

        def write_fake_ledger(path: Path, features: set[str]) -> None:
            capabilities = json.dumps(
                {"schema": "hylo-capabilities/v1", "features": sorted(features)},
                separators=(",", ":"),
            )
            path.write_text(
                "#!/bin/sh\n"
                'case "$*" in\n'
                '  "--version") printf \'ledger 0.10.6\\n\' ;;\n'
                '  "--source hylo capabilities") '
                f"printf '%s\\n' '{capabilities}' ;;\n"
                '  "--source hylo --help") '
                "printf '%s\\n' capabilities proof-artifact-set export-proof "
                "verify-proof ;;\n"
                "  *) exit 64 ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            path.chmod(0o700)

        def run_checker(ledger: Path) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    sys.executable,
                    str(SURFACE_CHECKER),
                    "--mode",
                    "proof-export",
                    "--surface-manifest",
                    str(manifest["path"]),
                    "--ledger",
                    str(ledger),
                    "--cas",
                    "/definitely/not/an/installed/cas",
                    "--json",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            current = root / "ledger-current"
            write_fake_ledger(current, required)
            current_result = run_checker(current)
            self.assertEqual(0, current_result.returncode, current_result.stderr)
            current_report = json.loads(current_result.stdout)
            self.assertTrue(current_report["ready"])
            self.assertEqual(["ledger-hylo"], current_report["checked_components"])
            self.assertNotIn("cas", current_report["components"])

            legacy = root / "ledger-v1-only"
            write_fake_ledger(
                legacy,
                {
                    "hylo_trial_v1",
                    "hylo_proof_bundle_v1",
                    "hylo_external_proof_anchor_v1",
                },
            )
            legacy_result = run_checker(legacy)
            self.assertEqual(2, legacy_result.returncode)
            legacy_report = json.loads(legacy_result.stdout)
            self.assertFalse(legacy_report["ready"])
            self.assertIn("hylo_trial_v2", legacy_report["error"])

    def test_documented_capability_keys_are_the_live_probe_keys(self) -> None:
        manifest = self.require_surface_manifest()
        for component in ("seq", "ledger-hylo", "cas"):
            requirements = self.checker["feature_requirements_by_mode"](
                manifest, component
            )
            configured = set().union(*requirements.values())
            with self.subTest(component=component):
                self.assertTrue(configured)
            keys = configured
            for key in keys:
                with self.subTest(key=key):
                    self.assertIn(key, self.skill)

        seq_requirements = self.checker["feature_requirements_by_mode"](
            manifest, "seq"
        )
        route_sensitive_keys = set().union(
            seq_requirements["case-blind-trial"],
            seq_requirements["historical-trial"],
            seq_requirements["historical-case-blind-trial"],
        )
        for key in route_sensitive_keys:
            with self.subTest(key=key):
                self.assertIn(key, self.documentation)

    def test_supporting_skills_name_every_component_capability(self) -> None:
        manifest = self.require_surface_manifest()
        supporting_skills = {
            "seq": read(ROOT.parent / "seq" / "SKILL.md"),
            "ledger-hylo": read(ROOT.parent / "ledger" / "SKILL.md"),
            "cas": read(ROOT.parent / "cas" / "SKILL.md"),
        }
        for component, skill in supporting_skills.items():
            requirements = self.checker["feature_requirements_by_mode"](
                manifest, component
            )
            for key in set().union(*requirements.values()):
                with self.subTest(component=component, key=key):
                    self.assertIn(key, skill)


if __name__ == "__main__":
    unittest.main()
