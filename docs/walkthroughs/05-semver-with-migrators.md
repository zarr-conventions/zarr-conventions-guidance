---
title: Implementing Semver with declared migrators
description: A reader for the Semver with declared migrators contract, exercised against the five catalogued change types, with failure modes when the author breaks the covenant.
---

# Implementing: [Semver with declared migrators](/implementation-contracts#_5-semver-with-declared-migrators)

The contract: full MAJOR.MINOR.PATCH versioning, with an Arrow-style compatibility-range promise and a declared migrator for each release. The reader implements the latest known version, range-checks every incoming document, and applies the documented migrator to normalize older data into the latest shape before processing.

Where the migrator lives is a separate architectural choice: it may live in the convention's spec text (as algorithmic guidance), or in a designated reference library (the way [pystac](https://github.com/stac-utils/pystac) carries STAC's migrators while the [stac-spec](https://github.com/radiantearth/stac-spec) repo only ships changelogs). Other implementations either depend on the reference library or port its migrators. The contract works the same either way; the burden distribution differs.

## Reader skeleton

```python
def semver_with_migrators(data):
    version = parse_semver(url(data))
    if not in_compat_range(version):
        return "FAIL: out of compatibility range"

    pa = proj_attrs(data)
    if version < latest_known:
        pa, transformed = MIGRATORS[version](pa)        # spec-shipped rule

    return read_latest(pa)                              # the v2 path
```

The migrator is the contract's distinctive piece. The convention (or its reference library) must declare one for every release that changed shape or semantics, so any in-range document can be normalized into the latest representation in memory before the reader's v2 path consumes it. After migration the reader does the same field-lookup-and-use it would do natively; no runtime schema validation is needed.

## How change types hit this reader

|  | before.json (v1) | after.json (v2) | What happens |
|---|---|---|---|
| add-optional | OK | OK | v1 data validates against the v2 schema (the new field is optional). No migration needed; reader proceeds via the v2 path. |
| rename | MIGRATED | OK | The spec's migrator renames `proj:code` to `proj:identifier`. After migration, the v2 reader sees v2 shape. |
| retype | MIGRATED | OK | The migrator parses the string EPSG code into the integer array. v2 reader proceeds. |
| semantic-only | MIGRATED | OK | The migrator shifts transform coefficients by half a pixel to convert center-anchored to corner-anchored. After migration, the v2 reader applies v2 semantics and produces the right answer. |
| add-with-semantic-shift | MIGRATED | OK | The migrator inserts `proj:cell_alignment: "center"` (matching v1's implicit default). v2 reader then dispatches on the field correctly. |

All MIGRATED-or-OK. The contract handles every catalogued change type *if the author ships the migrator*. The matrix's strength is that the v2 reader has one code path; only the migrators differ per release.

## When the author breaks the covenant

Semver with migrators has the strictest covenant of the five: the author commits to **shipping a working migrator for every release**, **declaring an honest compatibility range**, and **maintaining semver discipline** across releases. Three violations:

- **Author bumps a minor or patch without shipping a migrator.** The reader has no migration path for the older shape; it either falls back to fail-loudly (refuse the data) or processes naively (and silently misreads, depending on how the implementer wrote the no-migrator path). Reader correctness now depends on the implementer's fallback choice.
- **Author claims a compatibility range that is too wide.** v1 data falls in-range; the migrator does not actually fit the case (e.g., the rename migrator doesn't know about a third intermediate name from a deprecated 0.x release). After migration, the data is wrong-shaped, and v2 schema validation either fails loudly or — if the migrator's bug produced a coincidentally-valid shape — passes with silently wrong values.
- **Author ships a major bump.** Reader fails loudly with `FAIL: out of compatibility range`. Safe; the reader knows it cannot handle this data and refuses cleanly.

The major failure mode is **migration debt**: the contract works only as long as the author ships migrators every release, and the implementer keeps up. STAC plus pystac is the catalogued reference case where this discipline is maintained over years; the [survey](/posts/2026-survey) notes that stac-spec's 1.0 → 1.1 transition included three `tighten` rows that produced documents invalid against v1.0 schemas, which the migrators absorb. The contract is excellent when the maintainers operate it consciously.

## Run it

```bash
uv run walkthroughs/05-semver-with-migrators/run.py
```

## Outcome matrix

```
                            before.json  after.json
01-add-optional             OK           OK
02-rename                   MIGRATED     OK
03-retype                   MIGRATED     OK
04-semantic-only            MIGRATED     OK
05-add-with-semantic-shift  MIGRATED     OK
```

## Reader code

<<< @/../walkthroughs/05-semver-with-migrators/run.py{python}

## Commentary

Semver with migrators is the most robust contract on the menu and the most expensive to operate. It is the only contract that handles `semantic-only` and `add-with-semantic-shift` cleanly across the version transition: the migrator normalizes old data into new shape before processing, so the v2 reader's single code path serves every supported release. The cost is that the author or reference-library maintainers must write the migrators, the convention community must point implementers at them, and every reader must apply them. If any link breaks, the contract degrades to the same failure modes as [Integer-major with structural pass-through](/walkthroughs/04-integer-major-pass-through) or worse. STAC has held this together for years by concentrating migration work in pystac and letting other consumers ride that maintenance, which is the lowest-burden version of the contract that still actually works.

Choose this contract when (a) your maintainer community is engaged enough to write migrators with every release, and (b) your domain demands the ability to read older data after semantic shifts. If either condition is uncertain, prefer the lower-cost contracts and accept their failure modes.
