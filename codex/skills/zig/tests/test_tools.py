"""Behavioral regressions. All writes/deletions stay in disposable fixtures."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="zig-skill-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.global_cache = self.base / "shared-cache"
        self.global_cache.mkdir()
        self.env = {**os.environ, "HOME": str(self.home), "LC_ALL": "C",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                    "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                    "TEST_GLOBAL_CACHE": str(self.global_cache)}
        self.stub("zig", "import json, os\nprint(json.dumps({'global_cache_dir': os.environ['TEST_GLOBAL_CACHE']}))")
        self.stub("pgrep", "raise SystemExit(1)")

    def stub(self, name, body):
        path = self.bin / name
        path.write_text(f"#!{sys.executable}\n{body}\n")
        path.chmod(0o755)

    def file(self, name, contents="sentinel", root=None):
        path = (root or self.root) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path

    def git(self, *args, root=None):
        return subprocess.run(["git", "-C", str(root or self.root), *args], env=self.env,
                              check=True, capture_output=True, text=True).stdout.strip()

    def repo(self):
        self.git("init", "-q")
        self.file("build.zig", "// fixture")
        return self.commit()

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def tool(self, name, *args, root=None):
        return subprocess.run([sys.executable, str(SCRIPTS / name), "--root", str(root or self.root), *args],
                              env=self.env, capture_output=True, text=True, timeout=30)


class CacheTests(Fixture):
    def drain(self, *args):
        return self.tool("zig_cache_drain.py", *args)

    def test_default_dry_run_preserves_contents(self):
        sentinel = self.file(".zig-cache/o/item")
        result = self.drain()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(sentinel.exists())
        self.assertIn("CACHE_DRY_RUN_ONLY", result.stdout)
        self.assertNotIn("DRAINED", result.stdout)

    def test_local_deletion_reports_success_and_exits_zero(self):
        sentinel = self.file(".zig-cache/o/item")
        result = self.drain("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(sentinel.exists())
        self.assertIn("CACHE_LOCAL_DRAINED", result.stdout)

    def test_empty_selection_does_not_claim_deletion(self):
        result = self.drain("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CACHE_NO_CHANGES", result.stdout)
        self.assertNotIn("DRAINED", result.stdout)

    def test_arbitrary_global_path_refuses_before_local_deletion(self):
        sentinel = self.file("source.zig")
        local = self.file(".zig-cache/o/item")
        result = self.drain("--yes", "--include-global", "--global-path", str(self.root))
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sentinel.exists() and local.exists())
        self.assertNotIn("DRAINED", result.stdout)

    def test_global_discovery_does_not_authorize_source_tree(self):
        sentinel = self.file("source.zig", root=self.global_cache)
        result = self.drain("--yes", "--include-global")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sentinel.exists())
        self.assertIn("CACHE_LAYOUT_REFUSED", result.stderr)

    def test_missing_global_cache_never_reports_drained(self):
        self.env["TEST_GLOBAL_CACHE"] = str(self.base / "missing")
        result = self.drain("--yes", "--include-global")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("DRAINED", result.stdout)

    def test_global_object_deletion_preserves_packages(self):
        object_file = self.file("o/hash/object", root=self.global_cache)
        dependency = self.file("p/pkg/source.zig", root=self.global_cache)
        result = self.drain("--yes", "--include-global")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(object_file.exists())
        self.assertTrue(dependency.exists())
        self.assertIn("CACHE_GLOBAL_DRAINED", result.stdout)
        self.assertNotIn("CACHE_LOCAL_DRAINED", result.stdout)

    def test_zon_global_discovery(self):
        self.stub("zig", "import json, os\nprint('.global_cache_dir = ' + json.dumps(os.environ['TEST_GLOBAL_CACHE']) + ',')")
        self.file("o/hash/object", root=self.global_cache)
        result = self.drain("--include-global")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would delete", result.stdout)

    def test_dependency_deletion_is_retired_even_without_git_metadata(self):
        source = self.file("zig-pkg/dependency/source.zig")
        local = self.file(".zig-cache/o/item")
        result = self.drain("--yes", "--include-zig-pkg")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(source.exists() and local.exists())

    def test_dirty_dependency_worktree_is_preserved(self):
        self.repo()
        dep = self.root / "zig-pkg" / "dep"
        self.git("worktree", "add", "--detach", str(dep), "HEAD")
        source = self.file("build.zig", "// modified", root=dep)
        result = self.drain("--yes", "--include-zig-pkg")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(source.read_text(), "// modified")
        self.assertTrue((dep / ".git").is_file())

    def test_worktree_gitfile_inside_cache_is_preserved(self):
        source = self.file(".zig-cache/work/.git", "gitdir: elsewhere")
        result = self.drain("--yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(source.exists())

    def test_tracked_files_are_preserved(self):
        self.repo()
        sentinel = self.file(".zig-cache/source.zig")
        self.commit()
        result = self.drain("--yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sentinel.exists())

    def test_symlink_cache_cannot_redirect_deletion(self):
        source = self.file("source.zig", root=self.global_cache)
        (self.root / ".zig-cache").symlink_to(self.global_cache, target_is_directory=True)
        result = self.drain("--yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(source.exists())

    def test_nested_projects_and_outputs_are_not_implicitly_deleted(self):
        self.file(".zig-cache/item")
        nested = self.file("nested/.zig-cache/item")
        output = self.file("zig-out/app")
        result = self.drain("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(nested.exists() and output.exists())

    def test_output_is_deleted_only_when_selected(self):
        output = self.file("zig-out/app")
        result = self.drain("--yes", "--include-zig-out")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(output.exists())
        self.assertIn("CACHE_OUTPUT_DRAINED", result.stdout)

    def test_recent_descendant_prevents_age_based_deletion(self):
        sentinel = self.file(".zig-cache/o/item")
        old = time.time() - 10 * 86400
        os.utime(sentinel.parent, (old, old))
        os.utime(sentinel.parent.parent, (old, old))
        result = self.drain("--yes", "--older-than", "7")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(sentinel.exists())
        self.assertIn("CACHE_SKIPPED_RECENT", result.stdout)

    def test_active_or_unavailable_process_check_refuses_deletion(self):
        sentinel = self.file(".zig-cache/o/item")
        for status in (0, 3):
            with self.subTest(status=status):
                self.stub("pgrep", f"raise SystemExit({status})")
                result = self.drain("--yes")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(sentinel.exists())
                self.assertNotIn("DRAINED", result.stdout)

    def test_dry_run_does_not_require_quiescence(self):
        self.file(".zig-cache/item")
        self.stub("pgrep", "raise SystemExit(0)")
        self.assertEqual(self.drain().returncode, 0)

    def test_invalid_arguments_do_not_delete(self):
        sentinel = self.file(".zig-cache/item")
        for args in (("--root",), ("--older-than", "-1"), ("--older-than", "bad")):
            with self.subTest(args=args):
                self.assertNotEqual(self.drain("--yes", *args).returncode, 0)
                self.assertTrue(sentinel.exists())


class ClosureTests(Fixture):
    def scan(self, *args, root=None):
        result = self.tool("zig_repo_closure_scan.py", *args, root=root)
        return result, json.loads(result.stdout)["zig_repo_closure_scan"]

    def test_non_ascii_and_control_characters_are_preserved(self):
        self.repo()
        names = ["café.zig", "space name.zig", "tab\tname.zig", "line\nbreak.zig", 'quote"name.zig']
        for name in names:
            self.file(name)
        result, body = self.scan()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({c["path"] for c in body["changes"]}, set(names))
        self.commit()
        for name in names:
            self.file(name, "changed")
        _, body = self.scan()
        self.assertEqual({c["path"] for c in body["changes"]}, set(names))

    def test_staged_change_is_not_duplicated(self):
        self.repo()
        self.file("build.zig", "changed")
        self.git("add", "build.zig")
        _, body = self.scan()
        self.assertEqual(len(body["changes"]), 1)

    def test_clean_branch_requires_explicit_review_range(self):
        base = self.repo()
        self.file("new.zig")
        self.commit()
        _, working = self.scan()
        self.assertEqual(working["scope"]["kind"], "working-tree")
        self.assertEqual(working["changes"], [])
        result, review = self.scan("--base", base)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(review["scope"]["kind"], "review")
        self.assertEqual(review["changes"][0]["path"], "new.zig")

    def test_review_rejects_mixed_or_wrong_snapshot(self):
        base = self.repo()
        self.file("new.zig")
        head = self.commit()
        self.file("new.zig", "dirty")
        result, body = self.scan("--base", base)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(body["verdict"], "error")
        self.git("restore", "new.zig")
        result, _ = self.scan("--base", head, "--head", base)
        self.assertNotEqual(result.returncode, 0)

    def test_head_without_base_is_rejected(self):
        self.repo()
        result, _ = self.scan("--head", "HEAD")
        self.assertNotEqual(result.returncode, 0)

    def test_rename_from_zig_to_unrecognized_suffix_remains_relevant(self):
        self.repo()
        self.file("old.zig")
        self.commit()
        self.git("mv", "old.zig", "new.data")
        _, body = self.scan()
        row = body["changes"][0]
        self.assertEqual((row["old_path"], row["path"]), ("old.zig", "new.data"))

    def test_unborn_repository(self):
        self.git("init", "-q")
        self.file("first.zig")
        self.git("add", "first.zig")
        result, body = self.scan()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(body["changes"][0]["path"], "first.zig")

    def test_oversized_contract_is_reported_and_strict_fails(self):
        self.repo()
        self.file("registry.json", "x" * 100)
        result, body = self.scan("--max-file-bytes", "20", "--strict")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(body["coverage"], "partial")
        self.assertEqual(body["skipped"][0]["path"], "registry.json")
        self.assertEqual(body["verdict"], "incomplete")

    def test_symlink_contract_is_not_silently_omitted(self):
        self.repo()
        (self.root / "registry.json").symlink_to(self.root / "build.zig")
        result, body = self.scan("--strict")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(body["skipped"])

    def test_strict_gap_and_registered_positive_control(self):
        self.repo()
        self.file("registry.json", "[]")
        self.file("extra.zig")
        result, body = self.scan("--strict")
        self.assertEqual(result.returncode, 2)
        self.assertIn("extra.zig", body["likely_unregistered_paths"])
        self.file("registry.json", '["extra.zig"]')
        _, body = self.scan()
        extra = next(c for c in body["changes"] if c["path"] == "extra.zig")
        self.assertEqual(extra["contract_references"][0]["contract_path"], "registry.json")

    def test_git_worktree_scope(self):
        self.repo()
        worktree = self.base / "worktree"
        self.git("worktree", "add", "--detach", str(worktree), "HEAD")
        self.file("new.zig", root=worktree)
        result, body = self.scan(root=worktree)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(body["changes"][0]["path"], "new.zig")

    def test_invalid_ref_is_an_error_not_no_changes(self):
        self.repo()
        result, body = self.scan("--base", "missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(body["verdict"], "error")


if __name__ == "__main__":
    unittest.main()
