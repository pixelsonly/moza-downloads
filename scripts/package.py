"""Stage and zip one built dashboard for a release.

Run from the repo root after building:  python3 scripts/package.py <id> <version> [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REQUIRED = ("name", "slug", "wheel", "previews")
SLUG = re.compile(r"^[A-Za-z0-9-]+$")


def load_meta(dashboard_dir: Path) -> dict:
    """Parse and validate dashboard_dir/dashboard.json."""
    path = Path(dashboard_dir) / "dashboard.json"
    meta = json.loads(path.read_text(encoding="utf-8"))
    for key in REQUIRED:
        if key not in meta:
            raise ValueError(f"{path}: missing key '{key}'")
    if not SLUG.match(meta["slug"]):
        raise ValueError(f"{path}: slug {meta['slug']!r} must match {SLUG.pattern}")
    seen = {}
    for preview in meta["previews"]:
        if not (Path(dashboard_dir) / preview).is_file():
            raise ValueError(f"{path}: preview not found: {preview}")
        base = Path(preview).name
        if base in seen:
            raise ValueError(f"{path}: previews {seen[base]} and {preview} share the file name {base}")
        seen[base] = preview
    return meta


def zip_name(slug: str, version: str) -> str:
    return f"pixelsonly-racing-{slug}-v{version}.zip"


def package(dashboard_dir: Path, dist_dir: Path, version: str, out_dir: Path) -> Path:
    """Zip the built .mzdash, Resource/ dirs and listed previews under <name>/."""
    dashboard_dir = Path(dashboard_dir)
    meta = load_meta(dashboard_dir)
    name = meta["name"]
    mzdash = Path(dist_dir) / name / f"{name}.mzdash"
    if not mzdash.is_file():
        raise FileNotFoundError(f"build output not found: {mzdash} (run the dashboard's build.py first)")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / zip_name(meta["slug"], version)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in (f"{name}/", f"{name}/Resource/", f"{name}/Resource/MD5/"):
            info = zipfile.ZipInfo(d)
            info.external_attr = (0o40755 << 16) | 0x10  # unix drwxr-xr-x + MS-DOS directory flag
            zf.writestr(info, "")
        zf.write(mzdash, f"{name}/{mzdash.name}")
        for preview in meta["previews"]:
            zf.write(dashboard_dir / preview, f"{name}/{Path(preview).name}")
    return path


def all_dashboards(repo: Path) -> list[Path]:
    return sorted(p.parent for p in (Path(repo) / "dashboards").glob("*/dashboard.json"))


def release_config_problems(repo: Path) -> list[str]:
    """Mismatches between dashboards/*/ and the release-please config and manifest."""
    repo = Path(repo)
    packages = json.loads((repo / "release-please-config.json").read_text(encoding="utf-8"))["packages"]
    manifest = json.loads((repo / ".release-please-manifest.json").read_text(encoding="utf-8"))
    problems = []
    for d in all_dashboards(repo):
        key = f"dashboards/{d.name}"
        if key not in packages:
            problems.append(f"{key} is missing from release-please-config.json packages")
        elif packages[key].get("component") != d.name:
            problems.append(f"{key} component {packages[key].get('component')!r} must equal {d.name!r}")
        if key not in manifest:
            problems.append(f"{key} is missing from .release-please-manifest.json")
    for key in sorted(set(packages) | set(manifest)):
        if not (repo / key / "dashboard.json").is_file():
            problems.append(f"{key} is configured for release but has no dashboard.json")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("id")
    parser.add_argument("version")
    parser.add_argument("--out", type=Path, default=REPO / "dist")
    args = parser.parse_args(argv)
    dashboard_dir = REPO / "dashboards" / args.id
    try:
        if not (dashboard_dir / "dashboard.json").is_file():
            raise ValueError(f"unknown dashboard: {args.id}")
        print(package(dashboard_dir, REPO / "dist", args.version, args.out))
    except (ValueError, FileNotFoundError) as err:
        print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
