---
title: Walkthroughs
description: Implementer's guides for the five contracts, each exercised against the catalogued change types with failure modes when the author breaks the covenant.
---

# Walkthroughs

One walkthrough per contract. Each shows a focused reader implementation, exercises it against the five catalogued change types (per the [2026 spec-evolution survey](/posts/2026-survey)), and lays out what happens when the convention author breaks their side of the covenant.

::: tip A note on validation
None of the reader implementations in these walkthroughs include runtime JSON Schema validation, because the vast majority of real consumers of geospatial JSON-metadata conventions do not validate at read time. They do field-lookup-and-use. The walkthroughs reflect that: each reader extracts the fields it cares about, applies its understanding of them, and ships the value downstream. The failure modes shown are the ones unvalidated readers actually experience.

If your application can afford schema validation as an extra defence (one-shot at ingest, or periodically against a stored corpus), it is a useful belt-and-suspenders mitigation against silent failures, especially under [Stable additive covenant](/walkthroughs/01-stable-additive-covenant). Each contract page's "When the author breaks the covenant" section notes which violations validation can catch.
:::

## The contracts

- [01. Stable additive covenant](/walkthroughs/01-stable-additive-covenant): one schema, no version awareness. Trusts the author.
- [02. Structural inspection](/walkthroughs/02-structural-inspection): recognizes by JSON shape, baked-in interpretation.
- [03. URI dispatch](/walkthroughs/03-uri-dispatch): per-URL handler registry. Unknown URL fails.
- [04. Integer-major with structural pass-through](/walkthroughs/04-integer-major-pass-through): per-major handler; additive evolution within a major.
- [05. Semver with declared migrators](/walkthroughs/05-semver-with-migrators): full semver, range-check, in-spec migrators.

## Synthesis matrix

Each cell is the reader's outcome on `before.json` (v1-shaped data) and `after.json` (v2-shaped data) for that change type. `OK` = correct output; `FAIL` = loud refusal; `SILENT-WRONG` = the reader proceeds and produces wrong output without raising; `MIGRATED` = the reader applied an in-spec migrator and then produced correct output.

| Change type | [1. Stable additive covenant](/walkthroughs/01-stable-additive-covenant) | [2. Structural inspection](/walkthroughs/02-structural-inspection) | [3. URI dispatch](/walkthroughs/03-uri-dispatch) | [4. Integer-major](/walkthroughs/04-integer-major-pass-through) | [5. Semver with migrators](/walkthroughs/05-semver-with-migrators) |
|---|---|---|---|---|---|
| 01-add-optional | OK / OK | OK / OK | OK / OK | OK / OK | OK / OK |
| 02-rename | **SILENT** / OK | OK / **FAIL** | OK / OK | OK / OK | MIGRATED / OK |
| 03-retype | **SILENT** / OK | OK / **FAIL** | OK / OK | OK / OK | MIGRATED / OK |
| 04-semantic-only | **SILENT** / OK | OK / **SILENT** | OK / OK | OK / OK | MIGRATED / OK |
| 05-add-with-semantic-shift | OK / **SILENT** | OK / **SILENT** | OK / OK | OK / OK | MIGRATED / OK |

Reading the matrix:

- **All-OK cells**: the contract handles that change type cleanly on the happy path.
- **FAIL cells**: the contract detects the change and refuses the data. Loud, safe failure; the reader cannot process old or new data but at least signals the mismatch.
- **SILENT cells**: the reader proceeds and produces wrong output without raising. The most dangerous failure mode, since downstream tooling cannot distinguish wrong output from right output.
- **MIGRATED cells**: the contract applied an in-spec migration rule to normalize the data, then processed it correctly. Requires the convention's spec to ship the migrator.

The matrix shows that contracts 3 and 4 produce no SILENT or FAIL cells on the happy path; both rely on the convention author maintaining their side. Their failure modes appear only when the author breaks the covenant (see each contract's "When the author breaks the covenant" section).

## Caveat: happy-path versus broken-covenant

The matrix above depicts every change type as a clean version transition (v1 → v2) where the author honors their covenant. When the author *breaks* their covenant (ships a rename under the additive-covenant contract, or a within-major semantic shift under integer-major, or new content at an existing URL under URI dispatch), the outcome can degrade silently. Each contract walkthrough has a "When the author breaks the covenant" section that walks through those failure modes.

## Change types covered

The five change types are drawn from the [2026 spec-evolution survey](/posts/2026-survey):

| # | Change type | Exercised because |
|---|---|---|
| 01-add-optional | new optional field added; absence preserves prior behavior | baseline: every contract should handle this |
| 02-rename | field renamed (semantically equivalent, syntactically different) | exposes which contracts fail loud vs. silent on shape changes |
| 03-retype | same field name, new type | the cleanest schema-detectable break |
| 04-semantic-only | identical JSON, different meaning | the case JSON-structure inspection cannot detect |
| 05-add-with-semantic-shift | new optional field whose presence changes interpretation of an existing field | the cell-type case from [zarr-conventions-spec#7](https://github.com/zarr-conventions/zarr-conventions-spec/issues/7) |

## Running locally

Each walkthrough is a single PEP 723 script that loads shared fixtures and asserts its outcome matrix:

```bash
uv run walkthroughs/01-stable-additive-covenant/run.py
```

Shared fixtures (JSON inputs and schemas) live under `walkthroughs/fixtures/0X-<change>/`. Each contract's `run.py` imports from there.

See [`walkthroughs/README.md`](https://github.com/zarr-conventions/zarr-conventions-guidance/blob/main/walkthroughs/README.md) for the full repo layout.
