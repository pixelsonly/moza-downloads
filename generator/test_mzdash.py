import json
import unittest
from pathlib import Path

import mzdash as mz

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "source" / "base-template" / "base-template.mzdash"


class SerializerTest(unittest.TestCase):
    @unittest.skipUnless(BASE.exists(), "Pit House export fixture not in repo")
    def test_round_trips_pit_house_export_byte_for_byte(self):
        raw = BASE.read_bytes()
        self.assertEqual(mz.dumps(json.loads(raw.decode("utf-8")), newline="\r\n").encode("utf-8"), raw)

    def test_empty_containers_and_lf_by_default(self):
        self.assertEqual(mz.dumps({"a": {}, "b": []}), '{\n    "a": {\n    },\n    "b": [\n    ]\n}\n')

    def test_crlf_on_request(self):
        self.assertEqual(mz.dumps({"a": 1}, newline="\r\n"), '{\r\n    "a": 1\r\n}\r\n')

    def test_integral_floats_written_as_ints(self):
        self.assertEqual(mz.dumps({"x": 2.0, "y": 2.5}), '{\n    "x": 2,\n    "y": 2.5\n}\n')


class FactoryTest(unittest.TestCase):
    def test_ids_start_at_one_and_increase(self):
        ids = mz.Ids()
        self.assertEqual([ids.take(), ids.take()], [1, 2])

    def test_rect_sets_geometry_fill_and_border_style(self):
        r = mz.rect(mz.Ids(), "Cell", 2, 3, 40, 50, "#0B0D12")
        self.assertEqual(r["type"], "Rectangle.qml")
        self.assertEqual((r["id"], r["name"]), (1, "Cell"))
        self.assertEqual({k: r["general"][k] for k in ("x", "y", "width", "height")},
                         {"x": 2, "y": 3, "width": 40, "height": 50})
        self.assertEqual(r["general"]["backgroundColor"], {"color": "#FF0B0D12", "type": "SOLID"})
        self.assertIn("borderStyle", r)
        self.assertEqual(r["binding"], {})

    def test_visible_condition_becomes_binding(self):
        r = mz.rect(mz.Ids(), "Tint", 0, 0, 1, 1, "#000000", visible="x < 0")
        self.assertEqual(r["binding"]["general.visible"],
                         {"methods": ["(x < 0) ? 1 : 0", "_result"], "type": "METHOD_CHAINING"})

    def test_visible_condition_defaults_to_shown(self):
        r = mz.rect(mz.Ids(), "Tint", 0, 0, 1, 1, "#000000", visible="x < 0")
        self.assertTrue(r["general"]["visible"])

    def test_visible_condition_can_default_to_hidden(self):
        r = mz.rect(mz.Ids(), "Tint", 0, 0, 1, 1, "#000000", visible="x < 0", shown=False)
        self.assertFalse(r["general"]["visible"])
        self.assertEqual(r["binding"]["general.visible"],
                         {"methods": ["(x < 0) ? 1 : 0", "_result"], "type": "METHOD_CHAINING"})

    def test_text_visible_condition_can_default_to_hidden(self):
        t = mz.text(mz.Ids(), "ABS", 0, 0, 10, 10, "4", font="Furore", size=36,
                    color="#E4EAF5", visible="x < 0", shown=False)
        self.assertFalse(t["general"]["visible"])

    def test_no_visible_condition_leaves_general_visible_untouched(self):
        r = mz.rect(mz.Ids(), "Cell", 0, 0, 1, 1, "#000000")
        self.assertTrue(r["general"]["visible"])

    def test_text_sets_font_alignment_and_telemetry_binding(self):
        t = mz.text(mz.Ids(), "ABS", 0, 0, 10, 10, "4", font="Furore", size=36,
                    color="#E4EAF5", key="ABSLevel", formatter="_result")
        self.assertEqual(t["type"], "Text.qml")
        self.assertEqual(t["text"]["text"], "4")
        self.assertEqual((t["text"]["fontFamily"], t["text"]["fontSize"], t["text"]["fontWeight"]), ("Furore", 36, 500))
        self.assertEqual(t["text"]["fontColor"]["color"], "#FFE4EAF5")
        self.assertEqual((t["text"]["horizontalAlignment"], t["text"]["verticalAlignment"]), ("AlignCenter", "AlignCenter"))
        self.assertEqual(t["binding"]["text.text"]["methods"],
                         ['Telemetry.get("v1/gameData/ABSLevel").value', "_result"])

    def test_text_binding_fallback(self):
        t = mz.text(mz.Ids(), "Driver", 0, 0, 10, 10, "F.LAST", font="Roboto", size=16,
                    color="#E4EAF5", key="PlayerName", fallback="F.Last")
        self.assertEqual(t["binding"]["text.text"]["methods"][0],
                         'Telemetry.get("v1/gameData/PlayerName").value || "F.Last"')

    def test_templates_are_not_shared_between_widgets(self):
        ids = mz.Ids()
        a = mz.text(ids, "a", 0, 0, 1, 1, "a", font="Roboto", size=12, color="#000000")
        b = mz.text(ids, "b", 0, 0, 1, 1, "b", font="Roboto", size=12, color="#000000")
        self.assertIsNot(a["general"], b["general"])

    def test_window_wraps_screens(self):
        ids = mz.Ids()
        s = mz.screen(ids, "Dark", "#1C1F26", [])
        w = mz.window("Name", "G" * 32, [s], [{"productType": "W17 Display"}], "#1C1F26", 123)
        self.assertEqual((w["type"], w["id"], w["name"], w["lastModified"]), ("Window.qml", 0, "Name", 123))
        self.assertEqual(w["window"]["GUID"], "G" * 32)
        self.assertEqual(w["window"]["defaultScreenId"], 0)
        self.assertEqual(w["children"], [s])
        self.assertEqual(s["general"]["backgroundColor"]["color"], "#FF1C1F26")
        self.assertEqual([n["type"] for n in mz.walk(w)], ["Window.qml", "Screen.qml"])

    def test_screen_default_border_radius_matches_window(self):
        s = mz.screen(mz.Ids(), "Dark", "#1C1F26", [])
        self.assertEqual(s["general"]["borderRadius"], 6)

    def test_screen_border_radius_is_overridable(self):
        s = mz.screen(mz.Ids(), "Dark", "#1C1F26", [], radius=0)
        self.assertEqual(s["general"]["borderRadius"], 0)


if __name__ == "__main__":
    unittest.main()
