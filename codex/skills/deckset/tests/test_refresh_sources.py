"""Exercise cache publication failures with isolated files and mocked HTTP."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/refresh_sources.py"
SPEC = importlib.util.spec_from_file_location("deckset_refresh", SCRIPT)
R = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = R
SPEC.loader.exec_module(R)


class RefreshTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.examples = self.root / "examples"
        self.prior = {"gist_etag": "old", "gist_last_modified": "old-date"}
        self.errors = []

    def seed(self, files=None, gist_id="fixture"):
        files = files or {"a.md": "old A", "b.md": "old B"}
        self.examples.mkdir()
        for name, content in files.items():
            (self.examples / name).write_text(content)
        (self.examples / "_gist-index.json").write_text(json.dumps({
            "gist_id": gist_id, "refreshed_at": "old-time", "files": sorted(files),
            "source": "https://api.github.com/gists/fixture",
        }, indent=2))

    def snapshot(self):
        if not self.examples.exists():
            return {}
        return {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.examples.iterdir() if p.is_file()}

    def response(self, files):
        return 200, json.dumps({"files": files}).encode(), {"ETag": "new", "Last-Modified": "new-date"}

    def fetch(self, max_age=0):
        return R.fetch_gist_examples("fixture", self.examples, 1, self.errors,
                                     self.prior, max_age, None)

    def partial_response(self):
        return self.response({
            "a": {"filename": "a.md", "content": "new A"},
            "b": {"filename": "b.md", "truncated": True, "raw_url": "https://fixture/b"},
        })

    def test_failed_second_download_preserves_complete_cache_and_validators(self):
        self.seed()
        before = self.snapshot()
        with patch.object(R, "http_get", side_effect=[self.partial_response(), TimeoutError("fixture")]):
            result, meta = self.fetch()
        self.assertEqual(result.source, "cache_fallback")
        self.assertTrue(result.ok)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((meta["etag"], meta["last_modified"]), ("old", "old-date"))
        self.assertEqual([p.name for p in self.root.iterdir()], ["examples"])

    def test_failed_download_without_cache_never_publishes_partial_bundle(self):
        with patch.object(R, "http_get", side_effect=[self.partial_response(), TimeoutError("fixture")]):
            result, meta = self.fetch()
        self.assertFalse(result.ok)
        self.assertEqual(result.source, "none")
        self.assertIsNone(meta["etag"])
        self.assertFalse(self.examples.exists())

    def test_failed_directory_install_restores_previous_bundle(self):
        self.seed()
        before = self.snapshot()
        replace = R.os.replace
        def fail_install(source, destination):
            if ".stage-" in Path(source).name and Path(destination) == self.examples:
                raise OSError("fixture install failure")
            return replace(source, destination)
        with patch.object(R, "http_get", return_value=self.response({
            "new": {"filename": "new.md", "content": "new"},
        })), patch.object(R.os, "replace", side_effect=fail_install):
            result, meta = self.fetch()
        self.assertEqual(result.source, "cache_fallback")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(meta["etag"], "old")
        self.assertEqual([p.name for p in self.root.iterdir()], ["examples"])

    def test_success_publishes_complete_bundle_and_removes_stale_files(self):
        self.seed()
        with patch.object(R, "http_get", return_value=self.response({
            "new": {"filename": "new.md", "content": ""},
        })):
            result, meta = self.fetch()
        self.assertEqual(result.source, "network")
        self.assertEqual(meta["etag"], "new")
        self.assertEqual(set(self.snapshot()), {"new.md", "_gist-index.json"})
        self.assertTrue(R.has_examples_cache(self.examples, "fixture"))

    def test_identical_refresh_leaves_bytes_and_mtimes_unchanged(self):
        self.seed()
        before = self.snapshot()
        with patch.object(R, "http_get", return_value=self.response({
            "a": {"filename": "a.md", "content": "old A"},
            "b": {"filename": "b.md", "content": "old B"},
        })):
            result, meta = self.fetch()
        self.assertTrue(result.ok)
        self.assertEqual(meta["etag"], "new")
        self.assertEqual(self.snapshot(), before)

    def test_invalid_cache_cannot_qualify_for_ttl_304_or_fallback(self):
        for defect in ("missing-file", "wrong-gist", "missing-index"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory(dir=self.root) as parent:
                self.examples = Path(parent) / "examples"
                self.seed(gist_id="wrong" if defect == "wrong-gist" else "fixture")
                if defect == "missing-file":
                    (self.examples / "b.md").unlink()
                if defect == "missing-index":
                    (self.examples / "_gist-index.json").unlink()
                self.prior["refreshed_at"] = R.now_utc()
                for response in ((304, b"", {}), TimeoutError("fixture")):
                    with patch.object(R, "http_get", side_effect=[response]) as http:
                        result, meta = self.fetch(max_age=3600)
                    self.assertFalse(result.ok)
                    self.assertNotIn("If-None-Match", http.call_args.args[2])
                    self.assertIsNone(meta["etag"])

    def test_malformed_or_colliding_entries_preserve_cache(self):
        self.seed()
        before = self.snapshot()
        for files in (
            {"a": None}, {"a": {"filename": "a.md"}},
            {"a": {"filename": 42, "content": "bad"}},
            {"a": {"filename": "  ", "content": "bad"}},
            {"a": {"filename": "_gist-index.json", "content": "bad"}},
            {"a": {"filename": "a?.md", "content": "a"},
             "b": {"filename": "a!.md", "content": "b"}},
        ):
            with self.subTest(files=files), patch.object(R, "http_get", return_value=self.response(files)):
                result, meta = self.fetch()
            self.assertEqual(result.source, "cache_fallback")
            self.assertEqual(meta["etag"], "old")
            self.assertEqual(self.snapshot(), before)

    def test_unmanaged_directory_is_preserved(self):
        self.seed()
        (self.examples / "private").mkdir()
        with patch.object(R, "http_get", return_value=self.response({
            "a": {"filename": "a.md", "content": "new"},
        })):
            result, _ = self.fetch()
        self.assertEqual(result.source, "cache_fallback")
        self.assertTrue((self.examples / "private").is_dir())
        self.assertEqual((self.examples / "a.md").read_text(), "old A")

    def test_docs_publication_failure_retains_prior_validator(self):
        docs = self.root / "docs.html"
        docs.write_bytes(b"old docs")
        with patch.object(R, "http_get", return_value=(200, b"new docs", {"ETag": "new"})), \
             patch.object(R, "atomic_write_if_changed", side_effect=OSError("fixture disk error")):
            result, meta = R.fetch_docs("https://fixture/docs", docs, 1, self.errors,
                                       {"docs_etag": "old"}, 0)
        self.assertEqual(result.source, "cache_fallback")
        self.assertEqual(meta["etag"], "old")
        self.assertEqual(docs.read_bytes(), b"old docs")

    def test_replacement_without_validators_clears_old_conditionals(self):
        self.seed()
        docs = self.root / "docs.html"
        docs.write_bytes(b"old docs")
        for source in ("docs", "gist"):
            with self.subTest(source=source):
                prior = {f"{source}_etag": "old", f"{source}_last_modified": "old-date"}
                body = b"new docs" if source == "docs" else self.response({
                    "a": {"filename": "a.md", "content": "new A"},
                })[1]

                def fetch(current_prior):
                    if source == "docs":
                        return R.fetch_docs("https://fixture/docs", docs, 1, self.errors, current_prior, 0)
                    return R.fetch_gist_examples("fixture", self.examples, 1, self.errors, current_prior, 0, None)

                with patch.object(R, "http_get", return_value=(200, body, {})):
                    result, meta = fetch(prior)
                self.assertEqual(result.source, "network")
                self.assertIsNone(meta["etag"])
                self.assertIsNone(meta["last_modified"])
                next_prior = {f"{source}_etag": meta["etag"],
                              f"{source}_last_modified": meta["last_modified"]}
                with patch.object(R, "http_get", return_value=(200, body, {})) as http:
                    fetch(next_prior)
                self.assertNotIn("If-None-Match", http.call_args.args[2])
                self.assertNotIn("If-Modified-Since", http.call_args.args[2])

    def test_304_without_validators_retains_current_conditionals(self):
        self.seed()
        docs = self.root / "docs.html"
        docs.write_bytes(b"old docs")
        with patch.object(R, "http_get", return_value=(304, b"", {})):
            gist_result, gist_meta = self.fetch()
            docs_result, docs_meta = R.fetch_docs("https://fixture/docs", docs, 1, self.errors,
                {"docs_etag": "old", "docs_last_modified": "old-date"}, 0)
        for result, meta in ((gist_result, gist_meta), (docs_result, docs_meta)):
            self.assertEqual(result.source, "cache_not_modified")
            self.assertEqual((meta["etag"], meta["last_modified"]), ("old", "old-date"))


if __name__ == "__main__":
    unittest.main()
