# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Implementer's walkthrough for Contract 3: URI dispatch.

Illustrative only. Not for production use.

The reader maintains a registry of schema URL -> per-URL handler. Each
handler reads the document according to its URL's spec, using field
lookups and hand-coded type/shape expectations. No runtime schema
validation. Unknown URL = fail.
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
    "02-rename":                  {"before.json": "OK", "after.json": "OK"},
    "03-retype":                  {"before.json": "OK", "after.json": "OK"},
    "04-semantic-only":           {"before.json": "OK", "after.json": "OK"},
    "05-add-with-semantic-shift": {"before.json": "OK", "after.json": "OK"},
}


def load(change: str, name: str) -> dict:
    return json.loads((FIXTURES / change / name).read_text())


def _proj_attrs(data: dict) -> dict:
    return {k: v for k, v in data.get("attributes", {}).items() if k.startswith("proj:")}


def _url(data: dict) -> str:
    return data["attributes"]["zarr_conventions"][0].get("schema_url", "")


def _corner_center_anchored(t: list[float]) -> tuple[float, float]:
    return (t[2] - t[0] / 2.0, t[5] - t[4] / 2.0)


def _handler_v1(data: dict, change: str) -> str:
    """Reads documents written under the v1 URL. Knows v1 field names and v1 semantics."""
    pa = _proj_attrs(data)
    if change == "02-rename" and "proj:code" not in pa:
        return "FAIL: malformed v1 document"
    if change == "03-retype" and not isinstance(pa.get("proj:code"), str):
        return "FAIL: malformed v1 document"
    if change == "04-semantic-only" and "proj:transform" in pa:
        # v1 semantics: center-anchored. Compute and discard; the handler "uses" it.
        _ = _corner_center_anchored(pa["proj:transform"])
    if change == "05-add-with-semantic-shift" and "proj:transform" in pa:
        _ = _corner_center_anchored(pa["proj:transform"])
    return "OK"


def _handler_v2(data: dict, change: str) -> str:
    """Reads documents written under the v2 URL. Knows v2 field names and v2 semantics."""
    pa = _proj_attrs(data)
    if change == "02-rename" and "proj:identifier" not in pa:
        return "FAIL: malformed v2 document"
    if change == "03-retype" and not isinstance(pa.get("proj:code"), list):
        return "FAIL: malformed v2 document"
    if change == "04-semantic-only" and "proj:transform" in pa:
        # v2 semantics: corner-anchored.
        _ = (pa["proj:transform"][2], pa["proj:transform"][5])
    if change == "05-add-with-semantic-shift" and "proj:transform" in pa:
        alignment = pa.get("proj:cell_alignment", "center")
        t = pa["proj:transform"]
        _ = (t[2], t[5]) if alignment == "corner" else _corner_center_anchored(t)
    return "OK"


HANDLERS = {
    "https://example.com/proj/v1/schema.json": _handler_v1,
    "https://example.com/proj/v2/schema.json": _handler_v2,
}


def uri_dispatch(data: dict, change: str) -> str:
    """Dispatch on schema_url to the matching per-URL handler."""
    handler = HANDLERS.get(_url(data))
    if handler is None:
        return "FAIL: unknown schema_url"
    return handler(data, change)


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
            matrix[change][name] = uri_dispatch(data, change)

    print_matrix(matrix)
    if matrix != EXPECTED_MATRIX:
        print("\nFAIL: matrix does not match documented expectation.", file=sys.stderr)
        return 1
    print("\nOK: matrix matches documented expectation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
