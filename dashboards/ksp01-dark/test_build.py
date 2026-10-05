import hashlib
import json
import unittest
from pathlib import Path

import build
import mzdash as mz

# SHA-256 of the built .mzdash (last_modified=0). release-please only releases this dashboard
# for commits under dashboards/ksp01-dark/, so a change to the KSP01 design or the generator that
# alters the output must update this hash in the same PR — that edit is what cuts the release.
OUTPUT_SHA256 = "3498aeeb1e1cbe819b60e0ebfd1c92d484238384f1e6c896fb689b62734d488d"

KSP01_GUID = "ZDeNozqZZemMJvQVUDy0bh0CjoE1APz5"


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = build.build_document(last_modified=0)

    def test_serializes_to_valid_json(self):
        self.assertEqual(json.loads(mz.dumps(self.doc)), self.doc)

    def test_window_identity(self):
        self.assertEqual(self.doc["name"], "Pixelsonly Racing KSP01 Dark")
        self.assertEqual(self.doc["window"]["GUID"], "hWHyuGOTGFmcTyfXzaPY0psjfO2b065i")
        self.assertEqual(self.doc["version"], "1.1.1")
        self.assertEqual([s["name"] for s in self.doc["children"]], ["Dark"])

    def test_guid_differs_from_ksp01_so_imports_do_not_replace_it(self):
        self.assertNotEqual(self.doc["window"]["GUID"], KSP01_GUID)

    def test_screen_matches_ksp01_dark_screen(self):
        # Same design as the switchable ksp01, minus the other screen.
        dynamic = build.design.document("x", "x" * 32, ("Dark", "Light"), last_modified=0)
        expected = next(s for s in dynamic["children"] if s["name"] == "Dark")
        strip = lambda nodes: [{**n, "id": None} for n in nodes]  # noqa: E731
        self.assertEqual(strip(self.doc["children"][0]["children"]), strip(expected["children"]))

    def test_output_hash_is_pinned(self):
        digest = hashlib.sha256(mz.dumps(self.doc).encode("utf-8")).hexdigest()
        self.assertEqual(digest, OUTPUT_SHA256, "output changed: update OUTPUT_SHA256 so this dashboard releases")


class LayoutTest(unittest.TestCase):
    def test_name_comes_from_dashboard_json(self):
        meta = json.loads((Path(build.__file__).parent / "dashboard.json").read_text())
        self.assertEqual(build.NAME, meta["name"])

    def test_out_dir_is_repo_dist_regardless_of_cwd(self):
        repo = Path(build.__file__).resolve().parents[2]
        self.assertEqual(build.OUT_DIR, repo / "dist" / "Pixelsonly Racing KSP01 Dark")


if __name__ == "__main__":
    unittest.main()
