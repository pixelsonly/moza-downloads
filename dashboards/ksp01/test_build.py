import json
import unittest
from pathlib import Path

import build
import jseval
import mzdash as mz

COLOR_KEYS = ("backgroundColor", "fontColor")


def strip_colors(node):
    """Copy of a widget tree with every colour value removed."""
    if isinstance(node, dict):
        return {k: strip_colors(v) for k, v in node.items() if k not in COLOR_KEYS}
    if isinstance(node, list):
        return [strip_colors(v) for v in node]
    return node


def by_name(screen):
    return {n["name"]: n for n in screen["children"]}


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = build.build_document(last_modified=0)
        cls.dark, cls.light = cls.doc["children"]

    def test_serializes_to_valid_json(self):
        self.assertEqual(json.loads(mz.dumps(self.doc)), self.doc)

    def test_window_identity(self):
        self.assertEqual(self.doc["name"], "Pixelsonly Racing KSP01")
        self.assertEqual(len(self.doc["window"]["GUID"]), 32)
        self.assertEqual(self.doc["version"], "1.1.1")
        self.assertEqual([s["name"] for s in self.doc["children"]], ["Dark", "Light"])

    def test_ids_unique(self):
        ids = [n["id"] for n in mz.walk(self.doc)]
        self.assertEqual(len(ids), len(set(ids)))

    def test_everything_inside_canvas(self):
        for n in mz.walk(self.doc):
            g = n["general"]
            with self.subTest(n["name"]):
                self.assertGreaterEqual(g["x"], 0)
                self.assertGreaterEqual(g["y"], 0)
                self.assertLessEqual(g["x"] + g["width"], 780)
                self.assertLessEqual(g["y"] + g["height"], 248)

    def test_ten_grid_cells_leave_2px_lines(self):
        cells = [n for n in self.dark["children"] if n["name"] == "Cell"]
        self.assertEqual(len(cells), 10)
        area = sum(c["general"]["width"] * c["general"]["height"] for c in cells)
        self.assertEqual(area, 250 * 64 + 250 * 118 + 250 * 58 + 242 * 64 + 242 * 118 + 242 * 58 + 4 * 139 * 121)

    def test_screens_differ_only_in_colour(self):
        dark = [strip_colors(n) | {"id": None} for n in self.dark["children"]]
        light = [strip_colors(n) | {"id": None} for n in self.light["children"]]
        self.assertEqual(dark, light)

    def test_each_telemetry_key_bound_to_expected_widget(self):
        expected = {"Gear": "Gear", "POS": "CurrentPos", "LAP": "CurrentLap", "EST LAP": "EstimatedLapTime",
                    "Driver": "PlayerName", "B-BIAS": "BrakeBias", "ABS": "ABSLevel", "TC-1": "TCLevel",
                    "TC-2": "TCCut", "RPM": "Rpm", "KM/H": "SpeedKmh", "DELTA (ahead)": "GAP",
                    "DELTA (behind)": "GAP", "DELTA (neutral)": "GAP"}
        widgets = by_name(self.dark)
        for name, key in expected.items():
            with self.subTest(name):
                self.assertTrue(widgets[name]["binding"]["text.text"]["methods"][0].startswith(mz.telemetry(key)))

    def test_label_colours_follow_palette_roles(self):
        for screen, pal in ((self.dark, build.PALETTES["Dark"]), (self.light, build.PALETTES["Light"])):
            widgets = by_name(screen)
            for name, role in (("B-BIAS label", "red"), ("ABS label", "amber"), ("TC-1 label", "blue"),
                               ("TC-2 label", "blue"), ("POS label", "label"), ("DELTA label (ahead)", "green"),
                               ("DELTA label (behind)", "red")):
                with self.subTest(screen["name"], name=name):
                    self.assertEqual(widgets[name]["text"]["fontColor"]["color"], mz.argb(pal[role]))

    def test_exactly_one_delta_state_visible(self):
        widgets = by_name(self.dark)
        states = ["ahead", "behind", "neutral"]
        conds = {s: widgets[f"DELTA ({s})"]["binding"]["general.visible"]["methods"][0] for s in states}
        inputs = ["-1.5", "-0.001", "0", "0.001", "2", "NaN"]
        results = jseval.run([(conds[s], i) for i in inputs for s in states])
        for n, inp in enumerate(inputs):
            row = results[n * 3:(n + 1) * 3]
            with self.subTest(gap=inp):
                self.assertEqual(sorted(row), [0, 0, 1])
        ahead_at = {inp: results[n * 3] for n, inp in enumerate(inputs)}
        self.assertEqual(ahead_at["-1.5"], 1 if build.DELTA_AHEAD_IS_NEGATIVE else 0)

    def test_tints_share_visibility_with_their_text(self):
        widgets = by_name(self.dark)
        for s in ("ahead", "behind"):
            self.assertEqual(widgets[f"Delta tint {s}"]["binding"]["general.visible"],
                             widgets[f"DELTA ({s})"]["binding"]["general.visible"])

    def test_delta_widgets_default_hidden_except_neutral(self):
        # Before the first telemetry update (e.g. in the Pit House editor preview, or
        # with no game running), only the neutral cell should render.
        hidden = ["Delta tint ahead", "Delta tint behind",
                  "DELTA label (ahead)", "DELTA (ahead)",
                  "DELTA label (behind)", "DELTA (behind)"]
        shown = ["DELTA label (neutral)", "DELTA (neutral)"]
        for screen in (self.dark, self.light):
            widgets = by_name(screen)
            for name in hidden:
                with self.subTest(screen["name"], name=name):
                    self.assertFalse(widgets[name]["general"]["visible"])
            for name in shown:
                with self.subTest(screen["name"], name=name):
                    self.assertTrue(widgets[name]["general"]["visible"])

    def test_driver_falls_back_to_uppercased_placeholder(self):
        driver = by_name(self.dark)["Driver"]
        expr, formatter = driver["binding"]["text.text"]["methods"]
        self.assertEqual(driver["text"]["text"], "F.LAST")
        self.assertEqual((driver["text"]["fontFamily"], driver["text"]["fontWeight"]), (build.LABEL_FONT, 700))
        results = jseval.run([(f"(_result => {formatter})({expr})", v) for v in ("''", "null", "'r.lindsey'")])
        self.assertEqual(results, ["F.LAST", "F.LAST", "R.LINDSEY"])

    def test_screen_border_radius_matches_window(self):
        for screen in (self.dark, self.light):
            with self.subTest(screen["name"]):
                self.assertEqual(screen["general"]["borderRadius"], self.doc["general"]["borderRadius"])

    def test_label_height_matches_tightest_real_export_ratio(self):
        self.assertEqual(build.LABEL_H, 16)


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
