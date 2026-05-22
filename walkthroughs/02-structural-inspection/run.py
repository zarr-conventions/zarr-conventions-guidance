# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Implementer's walkthrough for Contract 2: Structural inspection.

Illustrative only. Not for production use.

The reader recognizes the convention by inline type-aware shape checks
(here, `isinstance(pa["proj:code"], str)`). This is not JSON Schema
validation: the implementer hand-wrote the shape expectation in the
recognition path. No version field, no URL dispatch. The recognized
shape is whatever the implementer coded against, here v1.
"""

import json
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
    "01-add-optional":            {"before.json": "OK", "after.json": "OK"},
    "02-rename":                  {"before.json": "OK", "after.json": "FAIL: unrecognized structure"},
    "03-retype":                  {"before.json": "OK", "after.json": "FAIL: unrecognized type"},
    "04-semantic-only":           {"before.json": "OK", "after.json": "SILENT-WRONG: corner=(499995.0, 5000005.0)"},
    "05-add-with-semantic-shift": {"before.json": "OK", "after.json": "SILENT-WRONG: corner=(499995.0, 5000005.0)"},
}


def load(change: str, name: str) -> dict:
    return json.loads((FIXTURES / change / name).read_text())


def _proj_attrs(data: dict) -> dict:
    return {k: v for k, v in data.get("attributes", {}).items() if k.startswith("proj:")}


def _corner_center_anchored(t: list[float]) -> tuple[float, float]:
    return (t[2] - t[0] / 2.0, t[5] - t[4] / 2.0)


def _correct_corner(data: dict, change: str) -> tuple[float, float]:
    pa = _proj_attrs(data)
    t = pa.get("proj:transform")
    if t is None:
        return (0.0, 0.0)
    url = data["attributes"]["zarr_conventions"][0].get("schema_url", "")
    if change == "05-add-with-semantic-shift":
        return (t[2], t[5]) if pa.get("proj:cell_alignment", "center") == "corner" else _corner_center_anchored(t)
    if change == "04-semantic-only":
        return _corner_center_anchored(t) if "/v1/" in url else (t[2], t[5])
    return (0.0, 0.0)


def structural_inspection(data: dict, change: str) -> str:
    """Recognize the convention by hand-written shape checks
    (isinstance on proj:code), then apply v1-knowledge interpretation.
    """
    pa = _proj_attrs(data)

    # Hand-written signature check: presence and string type of proj:code.
    if "proj:code" not in pa:
        return "FAIL: unrecognized structure"
    if not isinstance(pa["proj:code"], str):
        return "FAIL: unrecognized type"

    # Recognition passed. Apply baked-in (v1-knowledge) interpretation.
    if change in {"04-semantic-only", "05-add-with-semantic-shift"}:
        got = _corner_center_anchored(pa["proj:transform"])
        expected = _correct_corner(data, change)
        if got != expected:
            return f"SILENT-WRONG: corner={got}"

    return "OK"


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
            matrix[change][name] = structural_inspection(data, change)

    print_matrix(matrix)
    if matrix != EXPECTED_MATRIX:
        print("\nFAIL: matrix does not match documented expectation.", file=sys.stderr)
        return 1
    print("\nOK: matrix matches documented expectation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
