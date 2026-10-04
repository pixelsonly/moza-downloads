"""Split a release tag like ksp01-v0.1.0 into dashboard id and version.

Usage:  python3 scripts/release_tag.py <tag>  — prints tag=, id=, version= lines for $GITHUB_OUTPUT.
"""
from __future__ import annotations

import re
import sys

# <id>-v<semver>: id is lower-case words joined by hyphens; version is SemVer 2.0 with
# optional pre-release and build metadata.
TAG = re.compile(
    r"^(?P<id>[a-z0-9]+(?:-[a-z0-9]+)*)"
    r"-v(?P<version>(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?)$"
)


def parse_tag(tag: str) -> tuple[str, str]:
    match = TAG.match(tag)
    if not match:
        raise ValueError(f"tag {tag!r} is not <id>-v<semver> (e.g. ksp01-v0.1.0)")
    return match["id"], match["version"]


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        dashboard, version = parse_tag(args[0])
    except ValueError as err:
        print(err, file=sys.stderr)
        return 1
    print(f"tag={args[0]}\nid={dashboard}\nversion={version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
