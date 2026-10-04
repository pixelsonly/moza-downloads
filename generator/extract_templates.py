"""One-off: extract widget templates from Pit House exports into generator/templates/.

Run from the project root:  python3 generator/extract_templates.py
Requires Pit House exports under source/ supplied locally; they are not committed.
"""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "templates"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def find(node, type_):
    if node["type"] == type_:
        return node
    for child in node.get("children", []):
        hit = find(child, type_)
        if hit:
            return hit
    return None


def neutral(node):
    node = copy.deepcopy(node)
    node["id"] = 0
    node["binding"] = {}
    node["general"]["locked"] = False
    if "children" in node:
        node["children"] = []
    return node


def main():
    base = load("source/base-template/base-template.mzdash")
    rally = load("source/Rally V4/Rally V4.mzdash")

    window = neutral(base)
    window["name"] = ""
    window["window"]["GUID"] = ""
    window["window"]["idealDeviceInfos"] = []

    screen = neutral(find(base, "Screen.qml"))
    text = neutral(find(base, "Text.qml"))

    # base-template has no Rectangle; take Rally V4's and give it the 1.1.1 borderStyle block.
    rect = neutral(find(rally, "Rectangle.qml"))
    rect["borderStyle"] = copy.deepcopy(text["borderStyle"])
    rect["general"]["borderWidth"] = 0
    rect["general"]["borderColor"] = {"color": "#00000000", "type": "SOLID"}

    OUT.mkdir(exist_ok=True)
    for name, node in (("window", window), ("screen", screen), ("text", text), ("rect", rect)):
        (OUT / f"{name}.json").write_text(json.dumps(node, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote", OUT / f"{name}.json")


if __name__ == "__main__":
    main()
