"""Derived report boundaries only; no model dispatch or review-credit simulation."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[2] / "elenctic" / "scripts" / "report.py"
SPEC = importlib.util.spec_from_file_location("ergasterion_shared_report", MODULE)
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)

# A small trusted-template fixture isolates server-side rendering/file mechanics.
# The shared browser UI is not changed or simulated by these tests.
TEMPLATE = ('<title>__REPORT_TITLE__ · Elenctic</title><b>ELENCTIC</b>'
            '<pre>__REPORT_TEXT__</pre>'
            '<script id="report-data" type="application/json">__REPORT_DATA__</script>')


def fixture(*, composed=True, blocked=False):
    identity = dict(schema="elenctic-review-identity/v1", mode="campaign", repo="example/project", pr=7,
                    campaign_id="test-round-a", base="a" * 40, candidate="b" * 40, view="pr-head",
                    coverage="complete", selected_scope_coverage="complete", whole_pr_coverage="complete",
                    verdict="BLOCKED" if blocked else "APPROVE")
    if composed:
        identity.update(schema="ergasterion-review-identity/v1", strategy="combined", base_tip="c" * 40)
        identity["assessments"] = {}
        for owner in ("architectonic", "elenctic"):
            source = {k: identity[k] for k in ("repo", "pr", "base", "base_tip", "candidate")}
            source.update(source_ref=f"fixture-{owner}-output", scope="Synthetic fixture scope", coverage="complete")
            if owner == "elenctic":
                source["whole_pr_coverage"] = "complete"
            identity["assessments"][owner] = source
    else:
        identity.update(campaign_context_id="test-context", campaign_seed_thread_id="test-seed", campaign_policy_id="test-policy")
    findings = []
    if blocked:
        f = dict(id="f-alpha", number=1, disposition="merge-blocker", title="Fixture violation",
                 location="src/example.ts:4", detail="Synthetic authority and witness.",
                 required_outcome="Preserve the fixture obligation.")
        if composed:
            f["origins"] = [dict(owner="architectonic", reference="fixture-A1", disposition="defect"),
                            dict(owner="elenctic", reference="fixture-E1", disposition="merge-blocker")]
        findings.append(f)
    return dict(schema="ergasterion-report/v1" if composed else "elenctic-report/v1", identity=identity,
                workflow="comments", title="Synthetic report fixture", pr_url="https://example.org/project/pull/7",
                generated_at="2026-10-08T00:00:00Z", summary="Synthetic result, not a real review.",
                coverage_note="Synthetic scope; no model has reviewed a program.",
                report_text="Complete synthetic report and source provenance.", findings=findings)


def analysis_fixture(*, composed=True):
    raw = fixture(composed=composed)
    i = raw["identity"]
    for k in ("campaign_id", "coverage", "selected_scope_coverage", "whole_pr_coverage", "verdict",
              "assessments", "campaign_context_id", "campaign_seed_thread_id", "campaign_policy_id"):
        i.pop(k, None)
    i.update(schema=("ergasterion" if composed else "elenctic") + "-construction-identity/v1",
             mode="analysis", analysis_id="fixture-analysis")
    if composed:
        i["evidence_refs"] = ["fixture-feedback-source"]
    raw["workflow"] = "construction"
    raw["construction"] = dict(status="complete", groups=[], adjudications=[], compatibility="No retained proposals.")
    return raw


class CompositionReportTests(unittest.TestCase):
    def test_composition_policy_is_in_native_snapshot_inventory(self):
        path = MODULE.with_name("freeze_policy.py")
        spec = importlib.util.spec_from_file_location("ergasterion_policy_inventory", path)
        policy = importlib.util.module_from_spec(spec); spec.loader.exec_module(policy)
        paths = policy.runtime_paths(MODULE.parents[2])
        self.assertIn("elenctic/references/ergasterion-composition.md", paths)
        self.assertIn("elenctic/scripts/report.py", paths)

    def test_native_identity_and_namespace_unchanged(self):
        r = report.prepare(fixture(composed=False))
        self.assertEqual(r["schema"], "elenctic-report/v1")
        self.assertTrue(r["report_key"].startswith("elenctic:"))
        self.assertEqual(r["identity"]["campaign_seed_thread_id"], "test-seed")

    def test_native_analysis_remains_analysis(self):
        r = report.prepare(analysis_fixture(composed=False))
        self.assertTrue(r["report_key"].startswith("elenctic-analysis:"))
        self.assertNotIn("verdict", r["identity"])

    def test_complete_combined_sources(self):
        r = report.prepare(fixture())
        self.assertTrue(r["report_key"].startswith("ergasterion:"))
        self.assertEqual(set(r["identity"]["assessments"]), {"architectonic", "elenctic"})

    def test_missing_source_cannot_claim_complete(self):
        for owner in ("architectonic", "elenctic"):
            with self.subTest(owner=owner):
                raw = fixture(); del raw["identity"]["assessments"][owner]
                with self.assertRaises(ValueError): report.prepare(raw)

    def test_partial_evidence_keeps_blocker(self):
        raw = fixture(blocked=True)
        raw["identity"].update(coverage="partial", selected_scope_coverage="partial", whole_pr_coverage="partial")
        raw["identity"]["assessments"]["elenctic"]["coverage"] = "partial"
        r = report.prepare(raw)
        self.assertEqual(r["identity"]["verdict"], "BLOCKED")
        self.assertEqual(len(r["findings"][0]["origins"]), 2)

    def test_unrun_sources_can_report_incomplete(self):
        raw = fixture()
        raw["identity"].update(assessments={}, verdict="INCOMPLETE", coverage="partial",
                               selected_scope_coverage="partial", whole_pr_coverage="not-established")
        self.assertEqual(report.prepare(raw)["findings"], [])

    def test_mixed_subjects_rejected(self):
        for field, value in (("repo", "other/project"), ("pr", 8), ("base", "d" * 40),
                             ("base_tip", "d" * 40), ("candidate", "d" * 40)):
            with self.subTest(field=field):
                raw = fixture(); raw["identity"]["assessments"]["architectonic"][field] = value
                with self.assertRaises(ValueError): report.prepare(raw)

    def test_boolean_source_pr_rejected(self):
        raw = fixture(); raw["identity"]["pr"] = 1
        for source in raw["identity"]["assessments"].values(): source["pr"] = 1
        raw["identity"]["assessments"]["elenctic"]["pr"] = True
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_complete_selected_cannot_hide_partial_whole_pr(self):
        raw = fixture(); raw["identity"]["assessments"]["elenctic"]["whole_pr_coverage"] = "partial"
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_native_provenance_cannot_be_forged_on_aggregate(self):
        for field in ("campaign_context_id", "campaign_seed_thread_id", "campaign_policy_id"):
            with self.subTest(field=field):
                raw = fixture(); raw["identity"][field] = None
                with self.assertRaises(ValueError): report.prepare(raw)

    def test_schema_cannot_relabel_aggregate_as_elenctic(self):
        raw = fixture(); raw["identity"]["schema"] = "elenctic-review-identity/v1"
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_non_native_strategy_only(self):
        for strategy in ("actuating", "unknown", [], None):
            with self.subTest(strategy=strategy):
                raw = fixture(); raw["identity"]["strategy"] = strategy
                with self.assertRaises(ValueError): report.prepare(raw)

    def test_architectural_scope_does_not_claim_whole_pr(self):
        raw = fixture(); i = raw["identity"]
        i.update(strategy="architectonic", whole_pr_coverage="not-established", coverage="partial")
        del i["assessments"]["elenctic"]
        self.assertEqual(report.prepare(raw)["identity"]["verdict"], "APPROVE")
        i.update(whole_pr_coverage="complete", coverage="complete")
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_single_elenctic_scope_is_explicit(self):
        raw = fixture(); raw["identity"]["strategy"] = "elenctic"
        del raw["identity"]["assessments"]["architectonic"]
        self.assertEqual(report.prepare(raw)["identity"]["strategy"], "elenctic")

    def test_origins_are_lossless_and_order_independent(self):
        raw = fixture(blocked=True); first = report.prepare(raw)
        raw["findings"][0]["origins"].reverse(); second = report.prepare(raw)
        self.assertEqual(first["findings"][0]["fingerprint"], second["findings"][0]["fingerprint"])
        self.assertEqual(len(first["findings"][0]["origins"]), 2)

    def test_origin_change_reopens_evidence(self):
        raw = fixture(blocked=True); old = report.prepare(raw)
        raw["findings"][0]["origins"][0]["disposition"] = "risk"
        self.assertNotEqual(old["findings"][0]["fingerprint"], report.prepare(raw)["findings"][0]["fingerprint"])

    def test_missing_duplicate_and_unknown_origins_rejected(self):
        for origins in ([], None, [dict(owner="unknown", reference="A", disposition="defect")]):
            with self.subTest(origins=origins):
                raw = fixture(blocked=True); raw["findings"][0]["origins"] = origins
                with self.assertRaises(ValueError): report.prepare(raw)
        raw = fixture(blocked=True); raw["findings"][0]["origins"] *= 2
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_architectural_nonblocking_draft_is_preserved(self):
        raw = fixture(blocked=True); raw["identity"]["verdict"] = "APPROVE"
        raw["findings"][0].update(disposition="concern", draft="A verified optional architectural proposal.",
                                  draft_owner="architectonic")
        r = report.prepare(raw)
        self.assertEqual(r["findings"][0]["disposition"], "concern")
        self.assertEqual(r["findings"][0]["draft_owner"], "architectonic")

    def test_elenctic_draft_policy_not_broadened(self):
        for composed in (False, True):
            with self.subTest(composed=composed):
                raw = fixture(composed=composed, blocked=True); raw["identity"]["verdict"] = "APPROVE"
                raw["findings"][0].update(disposition="concern", draft="Not an eligible Elenctic draft.", draft_owner="elenctic")
                with self.assertRaises(ValueError): report.prepare(raw)

    def test_aggregate_coordinator_can_draft_joint_blocker(self):
        raw = fixture(blocked=True); raw["findings"][0].update(draft="Joint verified blocker.", draft_owner="ergasterion")
        self.assertEqual(report.prepare(raw)["findings"][0]["draft_owner"], "ergasterion")

    def test_stable_numbers_required_and_not_part_of_evidence(self):
        raw = fixture(blocked=True); old = report.prepare(raw)
        raw["findings"][0]["number"] = 4
        self.assertEqual(old["findings"][0]["fingerprint"], report.prepare(raw)["findings"][0]["fingerprint"])
        del raw["findings"][0]["number"]
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_feedback_analysis_has_no_review_credit(self):
        raw = analysis_fixture(); r = report.prepare(raw)
        self.assertTrue(r["report_key"].startswith("ergasterion-analysis:"))
        for field, value in (("verdict", "APPROVE"), ("assessments", {}), ("coverage", "complete")):
            with self.subTest(field=field):
                changed = deepcopy(raw); changed["identity"][field] = value
                with self.assertRaises(ValueError): report.prepare(changed)

    def test_empty_feedback_provenance_rejected(self):
        raw = analysis_fixture(); raw["identity"]["evidence_refs"] = []
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_no_native_credit_fields_in_aggregate_identity(self):
        raw = fixture(); raw["identity"]["native_standard_cleans"] = 5
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_missing_elenctic_cannot_claim_partial_file_coverage(self):
        raw = fixture(); i = raw["identity"]
        i.update(strategy="architectonic", whole_pr_coverage="partial", coverage="partial")
        del i["assessments"]["elenctic"]
        with self.assertRaises(ValueError): report.prepare(raw)

    def test_groups_remain_lossless(self):
        raw = fixture(blocked=True); raw["workflow"] = "resolution"
        raw["resolution"] = dict(status="complete", groups=[])
        with self.assertRaises(ValueError): report.prepare(raw)
        raw["resolution"]["groups"] = [dict(id="R1", title="Unit", rationale="One obligation", objective="Preserve it",
                                              finding_ids=["f-alpha"], completion_checks=[dict(finding_id="f-alpha", evidence="Independent check")],
                                              depends_on=[])]
        self.assertEqual(len(report.prepare(raw)["resolution"]["groups"]), 1)

    def test_unsafe_links_remain_rejected(self):
        for url in ("javascript:alert(1)", "https://user:password@example.org", "file:///tmp/a"):
            with self.subTest(url=url):
                raw = fixture(); raw["pr_url"] = url
                with self.assertRaises(ValueError): report.prepare(raw)

    def test_strategy_base_tip_and_round_have_distinct_namespaces(self):
        raw = fixture(); key = report.prepare(raw)["report_key"]
        raw["identity"]["campaign_id"] = "test-round-b"
        self.assertNotEqual(key, report.prepare(raw)["report_key"])
        raw = fixture(); raw["identity"]["base_tip"] = "e" * 40
        for a in raw["identity"]["assessments"].values(): a["base_tip"] = "e" * 40
        self.assertNotEqual(key, report.prepare(raw)["report_key"])

    def test_render_brands_template_without_rewriting_evidence(self):
        raw = fixture(); raw["title"] = "Elenctic evidence <script>"
        raw["report_text"] = "Elenctic source </script><script>alert(1)</script>"
        with patch.object(Path, "read_text", return_value=TEMPLATE):
            document, prepared = report.render(raw)
        self.assertIn("ERGASTERION", document)
        self.assertIn("Elenctic evidence &lt;script&gt;", document)
        self.assertNotIn("</script><script>alert", document)
        self.assertIn("Elenctic source", prepared["report_text"])

    def test_private_atomic_output_and_namespace_guard(self):
        original_read = Path.read_text
        def read(path, *args, **kwargs):
            if path.name == "report.html" and path.parent.name == "assets": return TEMPLATE
            return original_read(path, *args, **kwargs)
        with tempfile.TemporaryDirectory() as temp, patch.object(Path, "read_text", autospec=True, side_effect=read):
            folder = Path(temp); folder.chmod(0o700)
            output = folder / "report.html"
            raw = fixture(blocked=True)
            self.assertEqual(report.write_report(raw, output), output)
            if os.name == "posix": self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            report.write_report(raw, output)
            changed = deepcopy(raw); changed["identity"]["campaign_id"] = "other-round"
            with self.assertRaises(ValueError): report.write_report(changed, output)
            changed = deepcopy(raw); changed["findings"][0]["number"] = 9
            with self.assertRaises(ValueError): report.write_report(changed, output)


if __name__ == "__main__":
    unittest.main()
