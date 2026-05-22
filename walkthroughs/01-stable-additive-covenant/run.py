# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Implementer's walkthrough for Contract 1: Stable additive covenant.

Illustrative only. Not for production use.

A single reader is implemented against the latest known understanding of
the convention. The reader trusts the convention author's promise of
purely additive evolution: it looks up fields by their current names,
uses the values directly, and ships no runtime schema validation. This
mirrors how most consumers of JSON metadata conventions actually work.
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
    "02-rename":                  {"before.json": "SILENT-WRONG: identifier=None", "after.json": "OK"},
    "03-retype":                  {"before.json": "SILENT-WRONG: epsg='E'", "after.json": "OK"},
    "04-semantic-only":           {"before.json": "SILENT-WRONG: corner=(500000.0, 5000000.0)", "after.json": "OK"},
    "05-add-with-semantic-shift": {"before.json": "OK", "after.json": "SILENT-WRONG: corner=(499995.0, 5000005.0)"},
}


def load(change: str, name: str) -> dict:
    return json.loads((FIXTURES / change / name).read_text())


def _proj_attrs(data: dict) -> dict:
    return {k: v for k, v in data.get("attributes", {}).items() if k.startswith("proj:")}


def _corner_center_anchored(t: list[float]) -> tuple[float, float]:
    return (t[2] - t[0] / 2.0, t[5] - t[4] / 2.0)


def _corner_corner_anchored(t: list[float]) -> tuple[float, float]:
    return (t[2], t[5])


def _correct_corner(data: dict, change: str) -> tuple[float, float]:
    """Ground truth: what the document was written to mean, by version."""
    pa = _proj_attrs(data)
    t = pa.get("proj:transform")
    if t is None:
        return (0.0, 0.0)
    url = data["attributes"]["zarr_conventions"][0].get("schema_url", "")
    if change == "05-add-with-semantic-shift":
        return _corner_corner_anchored(t) if pa.get("proj:cell_alignment", "center") == "corner" else _corner_center_anchored(t)
    if change == "04-semantic-only":
        return _corner_center_anchored(t) if "/v1/" in url else _corner_corner_anchored(t)
    return (0.0, 0.0)


def stable_additive_covenant(data: dict, change: str) -> str:
    """Latest-understanding reader. No runtime validation, no version dispatch.
    Looks up fields by their current names and applies the current interpretation.
    """
    pa = _proj_attrs(data)

    # 02-rename: look up the field by its current (v2) name.
    if change == "02-rename":
        identifier = pa.get("proj:identifier")
        if identifier is None:
            return f"SILENT-WRONG: identifier={identifier}"
        return "OK"

    # 03-retype: assume proj:code is the v2 shape (array of integer).
    # A naive reader pulls element [0] without type-checking.
    if change == "03-retype":
        code = pa.get("proj:code")
        epsg = code[0]
        if not isinstance(epsg, int):
            return f"SILENT-WRONG: epsg={epsg!r}"
        return "OK"

    # 04, 05: extract proj:transform and compute the corner using the reader's
    # current (v2) interpretation. v1 data interpreted with v2 semantics
    # silently produces the wrong corner.
    if change == "04-semantic-only":
        got = _corner_corner_anchored(pa["proj:transform"])
        if got != _correct_corner(data, change):
            return f"SILENT-WRONG: corner={got}"
        return "OK"

    if change == "05-add-with-semantic-shift":
        # Reader is at v1-knowledge: doesn't look up the new proj:cell_alignment
        # field, so it always applies center-anchor semantics.
        got = _corner_center_anchored(pa["proj:transform"])
        if got != _correct_corner(data, change):
            return f"SILENT-WRONG: corner={got}"
        return "OK"

    # 01-add-optional: just use proj:code.
    code = pa.get("proj:code")
    if code is None:
        return "SILENT-WRONG: code missing"
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
            matrix[change][name] = stable_additive_covenant(data, change)

    print_matrix(matrix)
    if matrix != EXPECTED_MATRIX:
        print("\nFAIL: matrix does not match documented expectation.", file=sys.stderr)
        return 1
    print("\nOK: matrix matches documented expectation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
