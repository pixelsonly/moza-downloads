"""Build and serialize Moza Pit House .mzdash documents.

Knows the file format, nothing about any particular layout.
"""
import copy
import json
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent / "templates"
_cache = {}


def _template(name):
    if name not in _cache:
        _cache[name] = json.loads((TEMPLATES / f"{name}.json").read_text(encoding="utf-8"))
    return copy.deepcopy(_cache[name])


def argb(rgb):
    """'#RRGGBB' -> opaque Pit House colour '#FFRRGGBB'."""
    return "#FF" + rgb.lstrip("#").upper()


def solid(color):
    return {"color": color, "type": "SOLID"}


def telemetry(key, fallback=None):
    expr = f'Telemetry.get("v1/gameData/{key}").value'
    return expr if fallback is None else f"{expr} || {json.dumps(fallback)}"


def chain(expr, formatter="_result"):
    return {"methods": [expr, formatter], "type": "METHOD_CHAINING"}


class Ids:
    """Sequential widget ids. The Window is always 0, so allocation starts at 1."""

    def __init__(self, start=1):
        self._next = start

    def take(self):
        n = self._next
        self._next += 1
        return n


def _place(node, ids, name, x, y, w, h, visible, shown=True):
    node["id"] = ids.take()
    node["name"] = name
    node["general"].update(x=x, y=y, width=w, height=h)
    if visible is not None:
        node["binding"]["general.visible"] = chain(f"({visible}) ? 1 : 0")
        node["general"]["visible"] = shown
    return node


def rect(ids, name, x, y, w, h, fill, visible=None, shown=True):
    node = _template("rect")
    _place(node, ids, name, x, y, w, h, visible, shown)
    node["general"]["backgroundColor"] = solid(argb(fill))
    return node


def text(ids, name, x, y, w, h, sample, *, font, size, color,
         weight=500, key=None, fallback=None, formatter="_result", visible=None, shown=True):
    node = _template("text")
    _place(node, ids, name, x, y, w, h, visible, shown)
    node["text"].update(
        text=sample,
        fontFamily=font,
        fontSize=size,
        fontWeight=weight,
        fontColor=solid(argb(color)),
        horizontalAlignment="AlignCenter",
        verticalAlignment="AlignCenter",
    )
    if key is not None:
        node["binding"]["text.text"] = chain(telemetry(key, fallback), formatter)
    return node


def screen(ids, name, background, children, radius=6):
    node = _template("screen")
    node["id"] = ids.take()
    node["name"] = name
    node["general"]["backgroundColor"] = solid(argb(background))
    node["general"]["borderRadius"] = radius
    node["children"] = children
    return node


def window(name, guid, screens, devices, background, last_modified, radius=6):
    node = _template("window")
    node["id"] = 0
    node["name"] = name
    node["window"]["GUID"] = guid
    node["window"]["defaultScreenId"] = 0  # index into children, not a widget id
    node["window"]["idealDeviceInfos"] = copy.deepcopy(devices)
    node["general"]["backgroundColor"] = solid(argb(background))
    node["general"]["borderRadius"] = radius
    node["lastModified"] = last_modified
    node["children"] = screens
    return node


def walk(node):
    """Yield node and all descendants, depth-first."""
    yield node
    for child in node.get("children", []):
        yield from walk(child)


# --- serializer: Qt QJsonDocument::Indented layout, as Pit House and the Moza editor write it ---

def _dump(value, depth):
    pad = "    " * depth
    if isinstance(value, dict):
        if not value:
            return "{\n" + pad + "}"
        items = [f"{pad}    {json.dumps(k, ensure_ascii=False)}: {_dump(value[k], depth + 1)}"
                 for k in sorted(value)]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(value, list):
        if not value:
            return "[\n" + pad + "]"
        items = [f"{pad}    {_dump(v, depth + 1)}" for v in value]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return json.dumps(value, ensure_ascii=False)


def dumps(doc, newline="\n"):
    """Serialize to on-disk text: sorted keys, 4-space indent.

    LF matches exports via Axom; Pit House itself wrote CRLF (newline="\\r\\n").
    """
    return (_dump(doc, 0) + "\n").replace("\n", newline)


def write(doc, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(dumps(doc).encode("utf-8"))
