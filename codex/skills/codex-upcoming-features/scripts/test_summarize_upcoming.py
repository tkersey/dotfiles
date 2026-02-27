import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).with_name("summarize_upcoming.py")
SPEC = importlib.util.spec_from_file_location("summarize_upcoming", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load summarize_upcoming.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

FEATURES_RS = textwrap.dedent(
    """
    pub enum Feature { JsRepl, Collab }

    pub enum Stage {
        Experimental {
            name: &'static str,
            menu_description: &'static str,
            announcement: &'static str,
        },
        UnderDevelopment,
        Stable,
        Deprecated,
        Removed,
    }

    pub struct FeatureSpec {
        pub id: Feature,
        pub key: &'static str,
        pub default_enabled: bool,
        pub stage: Stage,
    }

    pub const FEATURES: &[FeatureSpec] = &[
        FeatureSpec {
            id: Feature::JsRepl,
            key: "js_repl",
            default_enabled: true,
            stage: Stage::Experimental {
                name: "JavaScript REPL",
                menu_description: "Enable node REPL.",
                announcement: "NEW: JS REPL",
            },
        },
        FeatureSpec {
            id: Feature::Collab,
            key: "collab",
            default_enabled: false,
            stage: Stage::UnderDevelopment,
        },
    ];
    """
).strip() + "\n"

CHATWIDGET_RS = textwrap.dedent(
    """
    pub(crate) fn open_experimental_popup(&mut self) {
        let _features = FEATURES
            .iter()
            .filter_map(|spec| {
                let _name = spec.stage.experimental_menu_name()?;
                let _description = spec.stage.experimental_menu_description()?;
                Some(ExperimentalFeatureItem {
                    feature: spec.id,
                    name: "n".to_string(),
                    description: "d".to_string(),
                    enabled: self.config.features.enabled(spec.id),
                })
            })
            .collect::<Vec<_>>();
    }
    """
).strip() + "\n"

CODEX_RS = textwrap.dedent(
    """
    impl Session {
        /// Builds the `x-codex-beta-features` header value for this session.
        fn build_model_client_beta_features_header(config: &Config) -> Option<String> {
            let beta_features_header = FEATURES
                .iter()
                .filter_map(|spec| {
                    if spec.stage.experimental_menu_description().is_some()
                        && config.features.enabled(spec.id)
                    {
                        Some(spec.key)
                    } else {
                        None
                    }
                })
                .collect::<Vec<_>>()
                .join(",");
            Some(beta_features_header)
        }
    }
    """
).strip() + "\n"

PROCESSOR_RS = textwrap.dedent(
    """
    async fn experimental_feature_list(&self) {
        let _data = FEATURES
            .iter()
            .map(|spec| {
                let (stage, display_name, description, announcement) = match spec.stage {
                    Stage::Experimental {
                        name,
                        menu_description,
                        announcement,
                    } => (
                        ApiExperimentalFeatureStage::Beta,
                        Some(name.to_string()),
                        Some(menu_description.to_string()),
                        Some(announcement.to_string()),
                    ),
                    Stage::UnderDevelopment => (
                        ApiExperimentalFeatureStage::UnderDevelopment,
                        None,
                        None,
                        None,
                    ),
                    Stage::Stable => (ApiExperimentalFeatureStage::Stable, None, None, None),
                    Stage::Deprecated => (ApiExperimentalFeatureStage::Deprecated, None, None, None),
                    Stage::Removed => (ApiExperimentalFeatureStage::Removed, None, None, None),
                };

                ApiExperimentalFeature {
                    name: spec.key.to_string(),
                    stage,
                    display_name,
                    description,
                    announcement,
                    enabled: true,
                    default_enabled: false,
                }
            })
            .collect::<Vec<_>>();
    }
    """
).strip() + "\n"

V2_RS = textwrap.dedent(
    """
    pub enum ExperimentalFeatureStage {
        Beta,
        UnderDevelopment,
        Stable,
        Deprecated,
        Removed,
    }

    pub struct ExperimentalFeature {
        pub name: String,
        pub stage: ExperimentalFeatureStage,
        pub display_name: Option<String>,
        pub description: Option<String>,
        pub announcement: Option<String>,
        pub enabled: bool,
        pub default_enabled: bool,
    }
    """
).strip() + "\n"

SCHEMA_JSON = textwrap.dedent(
    """
    {
      "definitions": {
        "ExperimentalFeature": {
          "required": ["defaultEnabled", "enabled", "name", "stage"]
        },
        "ExperimentalFeatureStage": {
          "oneOf": [
            {"enum": ["beta"]},
            {"enum": ["underDevelopment"]},
            {"enum": ["stable"]},
            {"enum": ["deprecated"]},
            {"enum": ["removed"]}
          ]
        }
      },
      "required": ["data"]
    }
    """
).strip() + "\n"

README_MD = "- `experimentalFeature/list` — list feature flags with stage metadata.\n"

TOOLTIPS_RS = textwrap.dedent(
    """
    const ANNOUNCEMENT_TIP_URL: &str = "https://raw.githubusercontent.com/openai/codex/main/announcement_tip.toml";

    fn experimental_tooltips() -> Vec<&'static str> {
        FEATURES
            .iter()
            .filter_map(|spec| spec.stage.experimental_announcement())
            .collect()
    }

    fn get_tooltip() -> Option<String> {
        if let Some(announcement) = announcement::fetch_announcement_tip() {
            return Some(announcement);
        }
        None
    }
    """
).strip() + "\n"

ANNOUNCEMENT_TIP = textwrap.dedent(
    """
    [[announcements]]
    content = "Welcome"
    from_date = "2024-10-01"
    to_date = "2027-10-15"
    target_app = "cli"

    [[announcements]]
    content = "This is a test announcement"
    version_regex = '^0\\.0\\.0$'
    to_date = "2026-05-10"
    """
).strip() + "\n"

FIXTURES = {
    "codex-rs/core/src/features.rs": FEATURES_RS,
    "codex-rs/tui/src/chatwidget.rs": CHATWIDGET_RS,
    "codex-rs/core/src/codex.rs": CODEX_RS,
    "codex-rs/app-server/src/codex_message_processor.rs": PROCESSOR_RS,
    "codex-rs/app-server-protocol/src/protocol/v2.rs": V2_RS,
    "codex-rs/app-server-protocol/schema/json/v2/ExperimentalFeatureListResponse.json": SCHEMA_JSON,
    "codex-rs/app-server/README.md": README_MD,
    "codex-rs/tui/src/tooltips.rs": TOOLTIPS_RS,
    "announcement_tip.toml": ANNOUNCEMENT_TIP,
}


def write_fixture_repo(base: Path) -> None:
    for rel, content in FIXTURES.items():
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


class SummarizeUpcomingRegressionTests(unittest.TestCase):
    def test_required_files_and_markers_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            write_fixture_repo(repo)
            mined = MODULE.ensure_required_source_files(repo)
            self.assertEqual(mined, MODULE.REQUIRED_SOURCE_FILES)

    def test_required_markers_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            write_fixture_repo(repo)
            target = repo / "codex-rs/core/src/codex.rs"
            target.write_text("fn nope() {}\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                MODULE.ensure_required_source_files(repo)

    def test_supporting_evidence_covers_all_required_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            write_fixture_repo(repo)

            features = MODULE.parse_features_registry(repo / "codex-rs/core/src/features.rs")
            self.assertEqual(len(features), 2)

            beta, under_dev = MODULE.select_primary_features(features)
            self.assertEqual(len(beta), 1)
            self.assertEqual(len(under_dev), 1)

            evidence = MODULE.mine_source_supporting_evidence(repo, features)
            self.assertIn("features_registry", evidence)
            self.assertIn("chatwidget_experimental_popup", evidence)
            self.assertIn("beta_header", evidence)
            self.assertIn("app_server_feature_mapping", evidence)
            self.assertIn("protocol_v2", evidence)
            self.assertIn("protocol_schema_v2", evidence)
            self.assertIn("app_server_readme", evidence)
            self.assertIn("tooltips_announcement_pipeline", evidence)
            self.assertIn("announcement_tip_file", evidence)

            stage_values = evidence["protocol_schema_v2"]["stage_values"]
            self.assertEqual(
                stage_values,
                ["beta", "underDevelopment", "stable", "deprecated", "removed"],
            )
            self.assertEqual(evidence["announcement_tip_file"]["entry_count"], 2)


if __name__ == "__main__":
    unittest.main()
