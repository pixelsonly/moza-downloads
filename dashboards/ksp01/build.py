"""Pixelsonly Racing KSP01: the KSP01 design with Dark and Light screens, switched on the wheel.

Run from the repo root:  python3 dashboards/ksp01/build.py
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "generator"))

import design  # noqa: E402
import mzdash as mz  # noqa: E402

META = json.loads((Path(__file__).resolve().parent / "dashboard.json").read_text(encoding="utf-8"))
NAME = META["name"]
GUID = "ZDeNozqZZemMJvQVUDy0bh0CjoE1APz5"  # fixed: re-imports replace, not duplicate
OUT_DIR = REPO / "dist" / NAME
SCREENS = ("Dark", "Light")


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
