import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import release_tag  # noqa: E402


class ParseTagTest(unittest.TestCase):
    def test_plain_release(self):
        self.assertEqual(release_tag.parse_tag("ksp01-v0.1.0"), ("ksp01", "0.1.0"))

    def test_prerelease_and_build_metadata(self):
        self.assertEqual(release_tag.parse_tag("ksp01-v1.0.0-rc.1"), ("ksp01", "1.0.0-rc.1"))
        self.assertEqual(release_tag.parse_tag("ksp01-v1.0.0+build.5"), ("ksp01", "1.0.0+build.5"))

    def test_hyphenated_id(self):
        self.assertEqual(release_tag.parse_tag("gt-wheel-v2.3.4"), ("gt-wheel", "2.3.4"))

    def test_rejects_malformed_tags(self):
        for tag in ("v0.1.0", "ksp01-0.1.0", "ksp01-v0.1", "ksp01-v0.1.0/x", "ksp01-v0.1.0-", "KSP01-v0.1.0",
                    "../x-v0.1.0", "ksp01-v0.1.0 extra"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release_tag.parse_tag(tag)

    def test_cli_prints_github_outputs(self):
        done = subprocess.run([sys.executable, str(HERE / "release_tag.py"), "ksp01-v0.1.0"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout, "tag=ksp01-v0.1.0\nid=ksp01\nversion=0.1.0\n")

    def test_cli_rejects_bad_tag(self):
        done = subprocess.run([sys.executable, str(HERE / "release_tag.py"), "ksp01-v0.1.0/x"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 1)
        self.assertIn("ksp01-v0.1.0/x", done.stderr)


if __name__ == "__main__":
    unittest.main()
