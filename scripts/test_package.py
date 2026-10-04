import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))

import package  # noqa: E402

META = {"name": "Test Dash", "slug": "Test-Slug", "wheel": "Test Wheel", "previews": ["previews/a.png"]}


class PackageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.dash = root / "dashboards" / "test"
        (self.dash / "previews").mkdir(parents=True)
        (self.dash / "previews" / "a.png").write_bytes(b"png")
        self.write_meta(META)
        self.dist = root / "dist"
        self.built = self.dist / "Test Dash"
        (self.built / "Resource").mkdir(parents=True)
        (self.built / "Test Dash.mzdash").write_text("{}")
        self.out = root / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def write_meta(self, meta):
        (self.dash / "dashboard.json").write_text(json.dumps(meta))

    def test_zip_name(self):
        self.assertEqual(package.zip_name("Moza-KS-PRO", "0.1.0"), "pixelsonly-racing-Moza-KS-PRO-v0.1.0.zip")

    def test_package_handles_names_with_spaces(self):
        z = package.package(self.dash, self.dist, "1.2.3", self.out)
        self.assertEqual(z.name, "pixelsonly-racing-Test-Slug-v1.2.3.zip")
        with zipfile.ZipFile(z) as zf:
            self.assertEqual(sorted(zf.namelist()), [
                "Test Dash/", "Test Dash/Resource/", "Test Dash/Resource/MD5/",
                "Test Dash/Test Dash.mzdash", "Test Dash/a.png"])

    def test_directory_entries_are_marked_as_directories(self):
        with zipfile.ZipFile(package.package(self.dash, self.dist, "1.0.0", self.out)) as zf:
            for info in zf.infolist():
                if info.filename.endswith("/"):
                    self.assertTrue(info.external_attr & 0x10, info.filename)
                    self.assertEqual((info.external_attr >> 16) & 0o777, 0o755, info.filename)

    def test_ignores_unlisted_files_in_build_dir(self):
        (self.built / ".DS_Store").write_bytes(b"x")
        (self.built / "stray.png").write_bytes(b"x")
        (self.built / "Resource" / "MD5").mkdir()
        (self.built / "Resource" / "MD5" / "old.png").write_bytes(b"x")
        with zipfile.ZipFile(package.package(self.dash, self.dist, "1.0.0", self.out)) as zf:
            names = zf.namelist()
        self.assertFalse(any(n.endswith((".DS_Store", "stray.png", "old.png")) or "__MACOSX" in n for n in names))

    def test_missing_mzdash_fails(self):
        (self.built / "Test Dash.mzdash").unlink()
        with self.assertRaises(FileNotFoundError) as cm:
            package.package(self.dash, self.dist, "1.0.0", self.out)
        self.assertIn("Test Dash.mzdash", str(cm.exception))

    def test_missing_preview_fails(self):
        (self.dash / "previews" / "a.png").unlink()
        with self.assertRaises(ValueError) as cm:
            package.load_meta(self.dash)
        self.assertIn("previews/a.png", str(cm.exception))

    def test_bad_slug_fails(self):
        self.write_meta(dict(META, slug="bad slug!"))
        with self.assertRaises(ValueError) as cm:
            package.load_meta(self.dash)
        self.assertIn("slug", str(cm.exception))

    def test_missing_key_fails(self):
        self.write_meta({k: v for k, v in META.items() if k != "wheel"})
        with self.assertRaises(ValueError) as cm:
            package.load_meta(self.dash)
        self.assertIn("wheel", str(cm.exception))

    def test_rejects_unknown_dashboard(self):
        done = subprocess.run([sys.executable, str(REPO / "scripts" / "package.py"), "nope", "1.0.0"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 1)
        self.assertIn("unknown dashboard: nope", done.stderr)


class ReleaseConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        for d in ("ksp01", "ksp02"):
            (self.repo / "dashboards" / d).mkdir(parents=True)
            (self.repo / "dashboards" / d / "dashboard.json").write_text("{}")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, packages, manifest):
        (self.repo / "release-please-config.json").write_text(json.dumps({"packages": packages}))
        (self.repo / ".release-please-manifest.json").write_text(json.dumps(manifest))

    def test_consistent_config_has_no_problems(self):
        self.write({"dashboards/ksp01": {"component": "ksp01"}, "dashboards/ksp02": {"component": "ksp02"}},
                   {"dashboards/ksp01": "0.1.0", "dashboards/ksp02": "0.0.0"})
        self.assertEqual(package.release_config_problems(self.repo), [])

    def test_dashboard_missing_from_config_is_reported(self):
        self.write({"dashboards/ksp01": {"component": "ksp01"}}, {"dashboards/ksp01": "0.1.0"})
        problems = package.release_config_problems(self.repo)
        self.assertTrue(any("dashboards/ksp02" in p and "release-please-config.json" in p for p in problems), problems)
        self.assertTrue(any("dashboards/ksp02" in p and ".release-please-manifest.json" in p for p in problems), problems)

    def test_component_must_equal_folder_name(self):
        self.write({"dashboards/ksp01": {"component": "ksp01"}, "dashboards/ksp02": {"component": "ksp-02"}},
                   {"dashboards/ksp01": "0.1.0", "dashboards/ksp02": "0.0.0"})
        problems = package.release_config_problems(self.repo)
        self.assertTrue(any("ksp-02" in p for p in problems), problems)


class RepoDashboardsTest(unittest.TestCase):
    def test_repo_release_config_matches_dashboards(self):
        self.assertEqual(package.release_config_problems(REPO), [])

    def test_repo_dashboards_valid_and_slugs_unique(self):
        metas = [package.load_meta(d) for d in package.all_dashboards(REPO)]
        self.assertGreaterEqual(len(metas), 1)
        slugs = [m["slug"] for m in metas]
        self.assertEqual(len(slugs), len(set(slugs)), f"duplicate slugs: {slugs}")


if __name__ == "__main__":
    unittest.main()
