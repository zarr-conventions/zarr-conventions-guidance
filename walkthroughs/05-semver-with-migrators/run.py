# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Implementer's walkthrough for Contract 5: Semver with declared migrators.

Illustrative only. Not for production use.

The reader implements v2 (the latest known version). For documents
declaring an older version inside the compatibility range, it applies
an in-spec migrator that transforms the v1 shape into v2 shape in
memory, then processes through the v2 path. Out-of-range = fail.
No runtime schema validation.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"

CHANGE_TYPES = [
    "01-add-optional",
    "02-rename",
    "03-retype",
    "04-semantic-only",
    "05-add-with-semantic-shift",
]
INPUTS = ["before.json", "after.json"]

EXPECTED_MATRIX = {
    "01-add-optional":            {"before.json": "OK",       "after.json": "OK"},
    "02-rename":                  {"before.json": "MIGRATED", "after.json": "OK"},
    "03-retype":                  {"before.json": "MIGRATED", "after.json": "OK"},
    "04-semantic-only":           {"before.json": "MIGRATED", "after.json": "OK"},
    "05-add-with-semantic-shift": {"before.json": "MIGRATED", "after.json": "OK"},
}


def load(change: str, name: str) -> dict:
    return json.loads((FIXTURES / change / name).read_text())


def _proj_attrs(data: dict) -> dict:
    return {k: v for k, v in data.get("attributes", {}).items() if k.startswith("proj:")}


def _parse_major(data: dict) -> int | None:
    url = data["attributes"]["zarr_conventions"][0].get("schema_url", "")
    m = re.search(r"/v(\d+)/", url)
    return int(m.group(1)) if m else None


def _migrate_v1_to_v2(pa: dict, change: str) -> tuple[dict, bool]:
    """Per-change migrator shipped by the convention's spec. The reader applies
    it in memory to normalize v1 data to v2 shape before processing.
    Returns the (possibly transformed) attrs plus a flag indicating whether
    any actual transformation was applied.
    """
    pa = dict(pa)
    if change == "02-rename":
        if "proj:code" in pa:
            pa["proj:identifier"] = pa.pop("proj:code")
            return pa, True
    elif change == "03-retype":
        code = pa.get("proj:code")
        if isinstance(code, str):
            m = re.match(r"EPSG:(\d+)", code)
            if m:
                pa["proj:code"] = [int(m.group(1))]
                return pa, True
    elif change == "04-semantic-only":
        t = pa["proj:transform"]
        pa["proj:transform"] = [t[0], t[1], t[2] - t[0] / 2.0, t[3], t[4], t[5] - t[4] / 2.0]
        return pa, True
    elif change == "05-add-with-semantic-shift":
        pa.setdefault("proj:cell_alignment", "center")
        return pa, True
    return pa, False


def _read_v2(pa: dict, change: str) -> None:
    """v2 reader path. Looks up fields by their v2 names and applies v2 semantics."""
    if change == "02-rename":
        _ = pa.get("proj:identifier")
    elif change == "03-retype":
        _ = pa.get("proj:code", [None])[0]
    elif change == "04-semantic-only":
        t = pa["proj:transform"]
        _ = (t[2], t[5])  # corner-anchored
    elif change == "05-add-with-semantic-shift":
        t = pa["proj:transform"]
        if pa.get("proj:cell_alignment", "center") == "corner":
            _ = (t[2], t[5])
        else:
            _ = (t[2] - t[0] / 2.0, t[5] - t[4] / 2.0)


def semver_with_migrators(data: dict, change: str) -> str:
    """Range-check the version. In-range v1 data is migrated to v2 in memory
    via the spec-shipped migrator before processing. The reader implements
    v2 only.
    """
    major = _parse_major(data)
    if major not in {1, 2}:
        return "FAIL: out of compatibility range"

    pa = _proj_attrs(data)
    transformed = False
    if major == 1:
        pa, transformed = _migrate_v1_to_v2(pa, change)

    _read_v2(pa, change)
    return "MIGRATED" if transformed else "OK"


def print_matrix(matrix: dict[str, dict[str, str]]) -> None:
    col_w = max(len(c) for c in CHANGE_TYPES) + 2
    val_w = max(max(len(v) for v in row.values()) for row in matrix.values()) + 2
    header = " " * col_w + "  ".join(f"{i:<{val_w}}" for i in INPUTS)
    print(header)
    for c in CHANGE_TYPES:
        row = f"{c:<{col_w}}" + "  ".join(f"{matrix[c][i]:<{val_w}}" for i in INPUTS)
        print(row)


def main() -> int:
    matrix: dict[str, dict[str, str]] = {}
    for change in CHANGE_TYPES:
        matrix[change] = {}
        for name in INPUTS:
            data = load(change, name)
            matrix[change][name] = semver_with_migrators(data, change)

    print_matrix(matrix)
    if matrix != EXPECTED_MATRIX:
        print("\nFAIL: matrix does not match documented expectation.", file=sys.stderr)
        return 1
    print("\nOK: matrix matches documented expectation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
