"""Pixelsonly Racing KSP01 Dark: the KSP01 design with a single Dark screen.

Run from the repo root:  python3 dashboards/ksp01-dark/build.py
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "generator"))
sys.path.insert(0, str(REPO / "dashboards" / "ksp01"))

import design  # noqa: E402
import mzdash as mz  # noqa: E402

META = json.loads((Path(__file__).resolve().parent / "dashboard.json").read_text(encoding="utf-8"))
NAME = META["name"]
GUID = "hWHyuGOTGFmcTyfXzaPY0psjfO2b065i"  # fixed: re-imports replace, not duplicate
OUT_DIR = REPO / "dist" / NAME
SCREENS = ("Dark",)


def build_document(last_modified):
    return design.document(NAME, GUID, SCREENS, last_modified)


def main():
    doc = build_document(int(time.time()))
    path = OUT_DIR / f"{NAME}.mzdash"
    mz.write(doc, path)
    (OUT_DIR / "Resource").mkdir(exist_ok=True)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
