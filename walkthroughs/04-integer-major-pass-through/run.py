# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Implementer's walkthrough for Contract 4: Integer-major with structural pass-through.

Illustrative only. Not for production use.

The reader parses an integer major version from the schema URL path
(`.../v1/...` -> 1, `.../v2/...` -> 2) and dispatches to a per-major
handler. Each handler reads the document by field lookup; within a
major, additive changes pass through under the safely-ignorable
principle. No runtime schema validation. Unknown major = fail.
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
    "01-add-optional":            {"before.json": "OK", "after.json": "OK"},
    "02-rename":                  {"before.json": "OK", "after.json": "OK"},
    "03-retype":                  {"before.json": "OK", "after.json": "OK"},
    "04-semantic-only":           {"before.json": "OK", "after.json": "OK"},
    "05-add-with-semantic-shift": {"before.json": "OK", "after.json": "OK"},
}


def load(change: str, name: str) -> dict:
    return json.loads((FIXTURES / change / name).read_text())


def _proj_attrs(data: dict) -> dict:
    return {k: v for k, v in data.get("attributes", {}).items() if k.startswith("proj:")}


def _parse_major(data: dict) -> int | None:
    url = data["attributes"]["zarr_conventions"][0].get("schema_url", "")
    m = re.search(r"/v(\d+)/", url)
    return int(m.group(1)) if m else None


def _corner_center_anchored(t: list[float]) -> tuple[float, float]:
    return (t[2] - t[0] / 2.0, t[5] - t[4] / 2.0)


def _handler_major_1(data: dict, change: str) -> str:
    """Per-major-1 handler: knows major-1's field names and semantics."""
    pa = _proj_attrs(data)
    if change == "02-rename" and "proj:code" not in pa:
        return "FAIL: malformed v1 document"
    if change == "03-retype" and not isinstance(pa.get("proj:code"), str):
        return "FAIL: malformed v1 document"
    if change in {"04-semantic-only", "05-add-with-semantic-shift"} and "proj:transform" in pa:
        _ = _corner_center_anchored(pa["proj:transform"])
    return "OK"


def _handler_major_2(data: dict, change: str) -> str:
    """Per-major-2 handler: knows major-2's field names and semantics."""
    pa = _proj_attrs(data)
    if change == "02-rename" and "proj:identifier" not in pa:
        return "FAIL: malformed v2 document"
    if change == "03-retype" and not isinstance(pa.get("proj:code"), list):
        return "FAIL: malformed v2 document"
    if change == "04-semantic-only" and "proj:transform" in pa:
        _ = (pa["proj:transform"][2], pa["proj:transform"][5])
    if change == "05-add-with-semantic-shift" and "proj:transform" in pa:
        alignment = pa.get("proj:cell_alignment", "center")
        t = pa["proj:transform"]
        _ = (t[2], t[5]) if alignment == "corner" else _corner_center_anchored(t)
    return "OK"


def integer_major_pass_through(data: dict, change: str) -> str:
    """Parse the integer major and dispatch to the matching per-major handler."""
    major = _parse_major(data)
    if major == 1:
        return _handler_major_1(data, change)
    if major == 2:
        return _handler_major_2(data, change)
    return "FAIL: unknown major"


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
            matrix[change][name] = integer_major_pass_through(data, change)

    print_matrix(matrix)
    if matrix != EXPECTED_MATRIX:
        print("\nFAIL: matrix does not match documented expectation.", file=sys.stderr)
        return 1
    print("\nOK: matrix matches documented expectation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
