"""Custom 0.17 package locations must survive cache cleanup."""
from test_tools import Fixture


class PackagePathTests(Fixture):
    def test_env_package_inside_cache_refuses_before_any_deletion(self):
        package = self.file(".zig-cache/vendor/source.zig")
        other = self.file("zig-cache/o/object")
        self.env["ZIG_LOCAL_PKG_DIR"] = ".zig-cache/vendor"
        result = self.tool("zig_cache_drain.py", "--yes")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("CACHE_PACKAGE_PATH_UNTOUCHED", result.stderr)
        self.assertTrue(package.exists())
        self.assertTrue(other.exists())

    def test_cli_package_path_is_resolved_against_project_not_cwd(self):
        package = self.file(".zig-cache/vendor/source.zig")
        result = self.tool("zig_cache_drain.py", "--yes", "--pkg-path", ".zig-cache/vendor")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("CACHE_PACKAGE_PATH_UNTOUCHED", result.stderr)
        self.assertTrue(package.exists())

    def test_default_package_symlink_into_cache_is_preserved(self):
        package = self.file(".zig-cache/vendor/source.zig")
        (self.root / "zig-pkg").symlink_to(package.parent, target_is_directory=True)
        result = self.tool("zig_cache_drain.py", "--yes")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(package.exists())

    def test_separate_package_path_does_not_disable_legitimate_cleanup(self):
        package = self.file("custom-packages/source.zig")
        cached = self.file(".zig-cache/o/object")
        result = self.tool("zig_cache_drain.py", "--yes", "--pkg-path", "custom-packages")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(cached.exists())
        self.assertTrue(package.exists())
