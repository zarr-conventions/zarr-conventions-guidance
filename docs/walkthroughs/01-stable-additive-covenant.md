---
title: Implementing Stable additive covenant
description: A reader for the Stable additive covenant contract, exercised against the five catalogued change types, with failure modes when the author breaks the covenant.
---

# Implementing: [Stable additive covenant](/implementation-contracts#_1-stable-additive-covenant)

The contract: the convention author publicly commits that all future changes will be purely additive, no renames or retypes or semantic shifts. The reader trusts this and writes a single code path against the latest known schema.

## Reader skeleton

```python
def stable_additive_covenant(data):
    pa = proj_attrs(data)
    code = pa.get("proj:identifier")    # latest known name
    if code is None:
        return None
    # ... use the value
```

That is the entire contract. No version field, no URL dispatch, no migrators, no runtime schema validation. The reader looks up fields by their current (latest-known) names and uses them. It trusts the author's covenant that the names and types and meanings will not move.

## How change types hit this reader

For each of the five catalogued change types, the v1-shaped input and v2-shaped input arrive at the reader:

|  | before.json (v1) | after.json (v2) | What happens |
|---|---|---|---|
| add-optional | OK | OK | The reader's current understanding of every field still matches both shapes. New optional field is harmless. |
| rename | **SILENT-WRONG** | OK | v1 carries the old name `proj:code`. The reader looks up `proj:identifier` (its current understanding), finds nothing, and silently returns `None`. |
| retype | **SILENT-WRONG** | OK | v1 carries `proj:code` as a string. The reader assumes the v2 shape (array of integer) and pulls element `[0]`, which on a string gives the character `'E'`. The reader proceeds with the wrong value. |
| semantic-only | **SILENT-WRONG** | OK | The JSON is structurally identical to v2 data. The reader applies its current (v2) interpretation. v1 data is interpreted as v2 and produces wrong coordinates. |
| add-with-semantic-shift | OK | **SILENT-WRONG** | v1 has no signal of the new field; reader's baked-in semantics match v1 reality. v2 carries `proj:cell_alignment: "corner"` which the reader does not know to look up; it applies the same baked-in semantics, which is wrong for v2 data. |

**Four of five rows** produce a silent failure. The reader returns a value that looks plausible but is wrong. There is no detection signal in the document or in the reader code: that is the cost of trusting the covenant.

## When the author breaks the covenant

The covenant says: *no renames, no retypes, no removes, no semantic shifts; only additive changes.* What does each violation look like from the reader's side?

- **Author renames a field** (e.g., `proj:code` → `proj:identifier`). The reader looks up the new name and gets nothing. Silently missing data. No signal.
- **Author retypes a field** (e.g., `proj:code` from string to array). The reader assumes the new shape and uses old data as the new shape: indexing a string where an array was expected pulls a character; arithmetic on the wrong type may crash deep in downstream code or silently produce garbage. No signal at the reader level.
- **Author semantically shifts an existing field** (e.g., re-anchors transform coefficients). JSON is unchanged. The reader applies its current understanding to old data, producing wrong output with no signal.
- **Author adds a field whose presence changes interpretation of an existing field** (the "cell-type" case). Old documents lack the field, default interpretation matches old reality, so old documents are fine. New documents carry the new field; the reader ignores it under the safely-ignorable principle and applies the wrong (default) interpretation.

All four violations are silent. The covenant only works if the author honors it; the reader has no machinery to detect breaches.

::: tip If you do add JSON Schema validation
A reader that validates incoming documents against a frozen JSON Schema can catch some violations loudly: a `retype` becomes `FAIL: schema mismatch` instead of garbage downstream. Validation is opt-in and most JSON-metadata consumers do not include it (see the [survey](/posts/2026-survey) on real-world implementer practice); adding it is a useful belt-and-suspenders mitigation when the cost of silent failure is high.
:::

## Run it

```bash
uv run walkthroughs/01-stable-additive-covenant/run.py
```

## Outcome matrix

```
                            before.json                                   after.json
01-add-optional             OK                                            OK
02-rename                   SILENT-WRONG: identifier=None                 OK
03-retype                   SILENT-WRONG: epsg='E'                        OK
04-semantic-only            SILENT-WRONG: corner=(500000.0, 5000000.0)    OK
05-add-with-semantic-shift  OK                                            SILENT-WRONG: corner=(499995.0, 5000005.0)
```

The `SILENT-WRONG` rows print the value the reader actually produced. `epsg='E'` on the retype row is the single character pulled when the reader treated the legacy string `"EPSG:4326"` as the array shape v2 expected: `code[0]` returned the literal letter `'E'`, and the reader passed it downstream with no signal that anything was wrong.

## Reader code

<<< @/../walkthroughs/01-stable-additive-covenant/run.py{python}

## Commentary

The Stable additive covenant is the simplest contract to implement and the most exposed if the author breaks it. Four of five change types produce silent failures: the reader returns plausible-looking output with no signal that the underlying assumption was violated. The contract is a forcing function on the author: it gives the reader no machinery to detect a misstep, which is why the [survey](/posts/2026-survey) found GeoJSON's no-version covenant broke when the `crs` member was removed in 2016.

If you are choosing this contract: be confident the author will hold the covenant for the lifetime of the data, and reach for a stronger contract ([URI dispatch](/walkthroughs/03-uri-dispatch) or [Integer-major](/walkthroughs/04-integer-major-pass-through)) if you cannot.
