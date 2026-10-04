"""Pixelsonly Racing KSP01 — layout, palettes, and the build entry point.

Run from the repo root:  python3 dashboards/ksp01/build.py
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "generator"))

import formatters as fmt  # noqa: E402
import mzdash as mz  # noqa: E402

META = json.loads((Path(__file__).resolve().parent / "dashboard.json").read_text(encoding="utf-8"))
NAME = META["name"]
GUID = "ZDeNozqZZemMJvQVUDy0bh0CjoE1APz5"  # fixed: re-imports replace, not duplicate
OUT_DIR = REPO / "dist" / NAME

# Set False if on-track testing shows positive GAP means ahead.
DELTA_AHEAD_IS_NEGATIVE = True

DEVICES = [
    {"deviceId": 17, "hardwareVersion": "RS21-W08-HW SM-DU-V14", "networkId": 1, "productType": "W17 Display"},
    {"deviceId": 8, "hardwareVersion": "RS21-W17-HW RGB-DU-V11", "networkId": 1, "productType": "W17 Display"},
    {"deviceId": 16, "hardwareVersion": "RS21-W17-HW RGB-DU-V11", "networkId": 1, "productType": "W18 Display"},
    {"deviceId": 17, "hardwareVersion": "RS21-W08-HW SM-DU-V14", "networkId": 1, "productType": "W20 Display"},
]

PALETTES = {
    "Dark": {
        "line": "#1C1F26", "cell": "#0B0D12", "value": "#E4EAF5", "label": "#6A707A",
        "green": "#73F264", "green_tint": "#132E13", "red": "#D8304A", "red_tint": "#35131A",
        "amber": "#E1B549", "blue": "#4A9DD8",
    },
    "Light": {
        "line": "#C8CDD6", "cell": "#EEF1F6", "value": "#0B0D12", "label": "#5E6572",
        "green": "#1B8A2E", "green_tint": "#D5F0D2", "red": "#B8213A", "red_tint": "#F6D5DA",
        "amber": "#9A6B0C", "blue": "#1D66A8",
    },
}

# Grid tracks as (start, size), 2 px lines and margin.
COLS = [(2, 250), (254, 242), (498, 280)]
ROWS = [(2, 64), (68, 118), (188, 58)]
SET_COLS = [(498, 139), (639, 139)]
SET_ROWS = [(2, 121), (125, 121)]

VALUE_FONT = "Furore"
LABEL_FONT = "Roboto"
LABEL_SIZE = 12
LABEL_H = 16
LABEL_GAP = 4


def box(col, row):
    (x, w), (y, h) = col, row
    return x, y, w, h


def halves(b):
    x, y, w, h = b
    left = w // 2
    return (x, y, left, h), (x + left, y, w - left, h)


# Readouts: (cell box, label, sample, telemetry key, formatter, value size, label colour role, label below?)
READOUTS = [
    (halves(box(COLS[0], ROWS[0]))[0], "POS", "00", "CurrentPos", fmt.PAD2, 28, "label", False),
    (halves(box(COLS[0], ROWS[0]))[1], "LAP", "00", "CurrentLap", fmt.PAD2, 28, "label", False),
    (box(COLS[0], ROWS[1]), "EST LAP", "0:00.000", "EstimatedLapTime", fmt.LAPTIME, 28, "label", False),
    (halves(box(COLS[1], ROWS[2]))[0], "RPM", "0", "Rpm", fmt.INT, 18, "label", True),
    (halves(box(COLS[1], ROWS[2]))[1], "KM/H", "0", "SpeedKmh", fmt.INT, 18, "label", True),
    (box(SET_COLS[0], SET_ROWS[0]), "B-BIAS", "0.0", "BrakeBias", fmt.BIAS, 36, "red", False),
    (box(SET_COLS[1], SET_ROWS[0]), "ABS", "0", "ABSLevel", fmt.INT, 36, "amber", False),
    (box(SET_COLS[0], SET_ROWS[1]), "TC-1", "0", "TCLevel", fmt.INT, 36, "blue", False),
    (box(SET_COLS[1], SET_ROWS[1]), "TC-2", "0", "TCCut", fmt.INT, 36, "blue", False),
]
DELTA_BOX = box(COLS[1], ROWS[0])
DELTA_SIZE = 24
GEAR_BOX = box(COLS[1], ROWS[1])
GEAR_SIZE = 104
DRIVER_BOX = box(COLS[0], ROWS[2])
DRIVER_SIZE = 16
DRIVER_FALLBACK = "F.Last"  # shown when PlayerName is empty; NAME uppercases it


def delta_conditions():
    """JS conditions for the three delta states; exactly one is true for any GAP."""
    g = f"Number({mz.telemetry('GAP')})"
    ahead, behind = ("<", ">") if DELTA_AHEAD_IS_NEGATIVE else (">", "<")
    return {
        "ahead": f"(({g}) {ahead} 0)",
        "behind": f"(({g}) {behind} 0)",
        "neutral": f"!(({g}) < 0 || ({g}) > 0)",
    }


def cells(ids, pal):
    """Background rectangles; the 2 px gaps between them are the grid lines."""
    out = [mz.rect(ids, "Cell", *box(c, r), pal["cell"]) for c in COLS[:2] for r in ROWS]
    out += [mz.rect(ids, "Cell", *box(c, r), pal["cell"]) for r in SET_ROWS for c in SET_COLS]
    return out


def readout(ids, b, label, sample, key, formatter, size, label_color, value_color,
            label_below=False, visible=None, shown=True):
    """Label + value text pair, vertically centred as a group inside box b."""
    x, y, w, h = b
    value_h = round(size * 1.2)
    top = y + (h - (LABEL_H + LABEL_GAP + value_h)) // 2
    if label_below:
        value_y, label_y = top, top + value_h + LABEL_GAP
    else:
        label_y, value_y = top, top + LABEL_H + LABEL_GAP
    return [
        mz.text(ids, f"{label} label", x, label_y, w, LABEL_H, label,
                font=LABEL_FONT, size=LABEL_SIZE, weight=700, color=label_color, visible=visible, shown=shown),
        mz.text(ids, label, x, value_y, w, value_h, sample,
                font=VALUE_FONT, size=size, color=value_color, key=key, formatter=formatter,
                visible=visible, shown=shown),
    ]


def delta(ids, pal):
    cond = delta_conditions()
    out = [
        mz.rect(ids, "Delta tint ahead", *DELTA_BOX, pal["green_tint"], visible=cond["ahead"], shown=False),
        mz.rect(ids, "Delta tint behind", *DELTA_BOX, pal["red_tint"], visible=cond["behind"], shown=False),
    ]
    states = (("ahead", pal["green"], pal["green"], "-0.156", False),
              ("behind", pal["red"], pal["red"], "+0.156", False),
              ("neutral", pal["label"], pal["value"], "0.000", True))
    for state, label_color, value_color, sample, shown in states:
        for node in readout(ids, DELTA_BOX, "DELTA", sample, "GAP", fmt.DELTA, DELTA_SIZE,
                            label_color, value_color, visible=cond[state], shown=shown):
            node["name"] += f" ({state})"
            out.append(node)
    return out


def build_screen(ids, name, pal):
    kids = cells(ids, pal)
    kids += delta(ids, pal)
    for b, label, sample, key, formatter, size, role, below in READOUTS:
        kids += readout(ids, b, label, sample, key, formatter, size, pal[role], pal["value"], below)
    kids.append(mz.text(ids, "Gear", *GEAR_BOX, "N", font=VALUE_FONT, size=GEAR_SIZE,
                        color=pal["value"], key="Gear", formatter=fmt.GEAR))
    kids.append(mz.text(ids, "Driver", *DRIVER_BOX, DRIVER_FALLBACK.upper(), font=LABEL_FONT, size=DRIVER_SIZE,
                        weight=700, color=pal["value"], key="PlayerName", fallback=DRIVER_FALLBACK,
                        formatter=fmt.NAME))
    return mz.screen(ids, name, pal["line"], kids)


def build_document(last_modified):
    ids = mz.Ids()
    screens = [build_screen(ids, name, pal) for name, pal in PALETTES.items()]
    return mz.window(NAME, GUID, screens, DEVICES, PALETTES["Dark"]["line"], last_modified)


def main():
    doc = build_document(int(time.time()))
    path = OUT_DIR / f"{NAME}.mzdash"
    mz.write(doc, path)
    (OUT_DIR / "Resource").mkdir(exist_ok=True)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
