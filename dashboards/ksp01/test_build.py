import hashlib
import json
import unittest
from pathlib import Path

import build
import mzdash as mz

# SHA-256 of the built .mzdash (last_modified=0). release-please only releases this dashboard
# for commits under dashboards/ksp01/, so a design or generator change that alters the output
# must update this hash in the same PR — that edit is what cuts the release.
OUTPUT_SHA256 = "d96f8e6804f1366fe958d6b61502ca24f20c8b5ccf70b384033a7b77cb52b208"


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = build.build_document(last_modified=0)

    def test_serializes_to_valid_json(self):
        self.assertEqual(json.loads(mz.dumps(self.doc)), self.doc)

    def test_window_identity(self):
        self.assertEqual(self.doc["name"], "Pixelsonly Racing KSP01")
        self.assertEqual(self.doc["window"]["GUID"], "ZDeNozqZZemMJvQVUDy0bh0CjoE1APz5")
        self.assertEqual(self.doc["version"], "1.1.1")
        self.assertEqual([s["name"] for s in self.doc["children"]], ["Dark", "Light"])

    def test_output_hash_is_pinned(self):
        digest = hashlib.sha256(mz.dumps(self.doc).encode("utf-8")).hexdigest()
        self.assertEqual(digest, OUTPUT_SHA256, "output changed: update OUTPUT_SHA256 so this dashboard releases")


class LayoutTest(unittest.TestCase):
    def test_name_comes_from_dashboard_json(self):
        meta = json.loads((Path(build.__file__).parent / "dashboard.json").read_text())
        self.assertEqual(build.NAME, meta["name"])
        self.assertEqual(build.NAME, "Pixelsonly Racing KSP01")

    def test_out_dir_is_repo_dist_regardless_of_cwd(self):
        repo = Path(build.__file__).resolve().parents[2]
        self.assertEqual(build.OUT_DIR, repo / "dist" / "Pixelsonly Racing KSP01")


if __name__ == "__main__":
    unittest.main()
