---
title: Implementing Structural inspection
description: A reader for the Structural inspection contract, exercised against the five catalogued change types, with failure modes when the author breaks the covenant.
---

# Implementing: [Structural inspection](/implementation-contracts#_2-structural-inspection)

The contract: the convention has no version field. Identity is the JSON shape itself. The reader recognizes the convention's data by a structural signature (here, the presence of `proj:code` as a string) and applies its baked-in interpretation. No schema, no URL dispatch, no version awareness.

## Reader skeleton

```python
def structural_inspection(data):
    pa = proj_attrs(data)
    if "proj:code" not in pa:
        return "FAIL: unrecognized structure"
    if not isinstance(pa["proj:code"], str):
        return "FAIL: unrecognized type"
    code = pa["proj:code"]
    # ... apply baked-in interpretation
```

The "signature" is hand-written: a couple of `isinstance` checks the implementer added because they know what shape they expect. This is not JSON Schema validation; it is the same code the implementer would write if the spec had no schema at all. The signature is frozen once the reader ships; the implementer has to go edit it to extend it.

## How change types hit this reader

|  | before.json (v1) | after.json (v2) | What happens |
|---|---|---|---|
| add-optional | OK | OK | Signature still matches both versions; additive fields are tolerated under the safely-ignorable principle. |
| rename | OK | **FAIL** | v2 dropped `proj:code` for `proj:identifier`. Signature no longer recognizes v2 data. Loud failure. |
| retype | OK | **FAIL** | v2 changed `proj:code` to an integer array. Signature requires a string; the type check fails. Loud failure. |
| semantic-only | OK | **SILENT-WRONG** | The JSON shape is unchanged across the version transition. The reader recognizes the structure and applies its v1-knowledge interpretation; v2 data carries v2 semantics that the reader does not implement. |
| add-with-semantic-shift | OK | **SILENT-WRONG** | Same shape recognized. v2 carries `proj:cell_alignment: "corner"` which the reader does not know to inspect. It applies its v1 (center) interpretation. |

Structural inspection turns a JSON-shape break into a loud failure (rename and retype catch loudly). Semantic-only shifts are invisible to it: the signature cannot distinguish v1 data from v2 data when only the *meaning* changed.

## When the author breaks the covenant

The Structural inspection contract has a stricter version of the additive covenant: the author promises both *no semantic shifts* and *no signature-breaking changes*. Each violation has a predictable shape:

- **Author renames a field** (signature-breaking). Reader fails loudly on documents written under the new name. Old data still reads fine. Loud failure on one side of the transition.
- **Author retypes a field** (signature-breaking). Same as above; the type check rejects new-shaped data.
- **Author removes a field that was part of the signature**. Reader fails to recognize new documents at all. Loud.
- **Author semantically shifts an existing field** (signature-preserving). No detection mechanism. Silent misread on whichever side of the shift the reader was not coded against.
- **Author adds a field whose presence changes interpretation of an existing field** (signature-preserving). Same: the new field is unknown to the reader, which ignores it under the safely-ignorable principle and applies the original interpretation regardless of the new field's value.

Structural inspection is sturdier than [Stable additive covenant](/walkthroughs/01-stable-additive-covenant) for JSON-shape breaks (it catches them loudly), but no better for semantic shifts. The two contracts have the same Achilles heel: the [survey](/posts/2026-survey) lists 8 catalogued cases of semantic-only or add-with-semantic-shift that this contract cannot detect.

## Run it

```bash
uv run walkthroughs/02-structural-inspection/run.py
```

## Outcome matrix

```
                            before.json    after.json
01-add-optional             OK             OK
02-rename                   OK             FAIL: unrecognized structure
03-retype                   OK             FAIL: unrecognized type
04-semantic-only            OK             SILENT-WRONG: corner=(499995.0, 5000005.0)
05-add-with-semantic-shift  OK             SILENT-WRONG: corner=(499995.0, 5000005.0)
```

## Reader code

<<< @/../walkthroughs/02-structural-inspection/run.py{python}

## Commentary

Structural inspection is the "JSON structure plus fail-on-unknown is sufficient" position from [zarr-conventions-spec#7](https://github.com/zarr-conventions/zarr-conventions-spec/issues/7). For specs that never change semantics (only their shape), it is workable. For specs that do shift semantics, it has no signal to dispatch on. The [survey](/posts/2026-survey)'s eight semantic-only / add-with-semantic-shift cases are the documented falsifiers.

If you choose this contract, your reader will be sturdy against rename and retype but blind to the very change-types that motivate strong versioning. Reach for [URI dispatch](/walkthroughs/03-uri-dispatch) or stronger if your domain admits any chance of meaning drift.
