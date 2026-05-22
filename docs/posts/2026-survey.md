---
title: A snapshot of how six JSON-metadata conventions actually change
description: One-time survey of approximately 46 substantive changes across six Zarr-adjacent conventions, classified by the kind of break they produce. The empirical basis for the Implementation Contracts page.
---

# A snapshot of how six JSON-metadata conventions actually change

::: warning One-time snapshot, not a maintained reference
This is a survey done in May 2026 and is not actively updated. It is the empirical evidence underneath the [Implementation Contracts](/implementation-contracts) page and its [walkthroughs](/walkthroughs/). If you have corrections or want to extend the catalog with additional specs or more recent changes, open an issue or PR rather than treating this page as living documentation.
:::

Posted **2026-05-22**.

## Why this exists

The [Implementation Contracts](/implementation-contracts) page asks convention authors to pick a compatibility-promise / consumption-mode pairing. Each contract's "Evidence" callout cites a count or a row ID from a catalog of real spec changes. This post is that catalog's external face: where the numbers come from, what the classification means, which findings drove which contract.

## What we did

For each of six JSON-metadata conventions in the Zarr orbit, we walked the public version history and tagged every substantive change with one or more labels from a fixed taxonomy. Documentation-only edits ("clarify wording that didn't affect any conformant implementation") were filtered out. The result is approximately 46 catalogued rows.

The six conventions:

| Spec | Status | Window | Source |
|---|---|---|---|
| [`raster`](https://github.com/stac-extensions/raster) (STAC raster extension) | stable | v1.0.0 (2021-05) -> v2.0.0 (2024-09) | [CHANGELOG](https://github.com/stac-extensions/raster/blob/main/CHANGELOG.md) + JSON Schema diffs |
| [`ngff`](https://github.com/ome/ngff) (OME-NGFF) | stable | 0.1.0 (2020-04) -> 0.5.2 (2024-11) | [Version history](https://ngff.openmicroscopy.org/0.5/#history) + Bikeshed source diff |
| [`stac-spec`](https://github.com/radiantearth/stac-spec) (STAC core) | stable | 1.0.0-rc.x (2020) -> 1.1.0 (2023) | [Release notes](https://github.com/radiantearth/stac-spec/blob/main/CHANGELOG.md) |
| [`multiscales`](https://github.com/zarr-conventions/multiscales) (Zarr Conventions: multiscales) | pre-release | PR history | per-PR review |
| [`spatial`](https://github.com/zarr-conventions/spatial) (Zarr Conventions: spatial) | pre-release | PRs #1-#28 (2025-12 -> 2026-05) | per-PR review |
| [`proj`](https://github.com/zarr-conventions/proj) (Zarr Conventions: geo-proj) | pre-release | PRs #1-#18 (2025-10 -> 2026-04) | per-PR review |

## The classification

Each change gets one or more tags. Tags are intrinsic properties of the change, not opinions about what version bump it deserves.

| Tag | Definition | Example from catalog |
|---|---|---|
| `add-optional` | New field added; absence preserves prior behavior; existing fields keep their meaning. | [NGFF 0.1.2](https://ngff.openmicroscopy.org/0.5/#history) added the `omero` rendering-metadata block. |
| `add-with-semantic-shift` | New field added, *and* its absence vs. presence changes how an existing field is interpreted. | [Spatial PR#4](https://github.com/zarr-conventions/spatial/pull/4): optional `spatial:registration` field with `"pixel"` (default) vs. `"node"` rewrites how `spatial:transform` coefficients are interpreted. |
| `add-required` | New required field. Old documents become invalid; old writers produce invalid documents. | [NGFF 0.3.0](https://ngff.openmicroscopy.org/0.5/#history) added the required `axes` field. |
| `remove` | Field deleted. | [Raster PR#45](https://github.com/stac-extensions/raster/pull/45): `raster:bands` removed in favor of STAC common `bands`. |
| `rename` | Field renamed (semantically equivalent, syntactically different). | [Raster PR#45](https://github.com/stac-extensions/raster/pull/45): six fields renamed from unprefixed forms to `raster:*`. |
| `retype` | Same field name, new type or shape. | [NGFF 0.4.0](https://ngff.openmicroscopy.org/0.5/#history): `axes` restructured from list of strings to list of objects. |
| `tighten` | Constraint narrowed (optional -> required, broader enum -> narrower, value range shrunk). | [NGFF 0.3.0](https://ngff.openmicroscopy.org/0.5/#history) added type and ordering constraints on axes. |
| `loosen` | Constraint broadened. | [Raster #18](https://github.com/stac-extensions/raster/issues/18): `nodata` widened from `number` to `oneOf: [number, enum]`. |
| `semantic-only` | Same shape, same types, *new meaning*. Identical JSON now means something different. | [Spatial PR#9](https://github.com/zarr-conventions/spatial/pull/9): affine transform formula notation changed from `(i, j)` to `(col_index, row_index)`. No JSON change; semantics inverted. |
| `clarify` | Wording change with no behavior consequence for any conformant implementation. | Editorial wording cleanup. |
| `bundled` | Multiple of the above in one release or PR. Applied alongside the specific tags. | Most major-version releases. |

Decision rule for the high-stakes cases:

- **`add-with-semantic-shift` vs `add-optional`:** ask "does an old reader that ignores the new field still produce the right answer for all documents?" If yes -> `add-optional`. If no -> `add-with-semantic-shift`.
- **`clarify` is a high bar:** if two implementations could legitimately disagree on the meaning before the change but not after, it is `semantic-only`, not `clarify`.

## Headline distribution

```
tag                        raster  ngff  stac-spec  multiscales  spatial  proj   total
add-optional                    3     4         11            0        0     1      19
add-with-semantic-shift         0     0          0            0        1     0       1
add-required                    0     3          1            0        0     0       4
remove                          1     0          5            2        1     3      12
rename                          1     0          3            1        1     1       7
retype                          1     4          0            3        0     2      10
tighten                         0     5          7            1        3     1      17
loosen                          2     0         11            0        0     1      14
semantic-only                   0     0          4            0        2     1       7
clarify                         1     2         10            2        4     4      23
bundled                         3     4          6            4        1     4      22
```

A change tagged with multiple labels is counted under each, so column totals exceed 46 (`bundled` and `clarify` in particular co-occur with substantive tags). The substantive-change total of ~46 excludes `clarify`-only rows.

## The eight cases where structural inspection alone cannot help

The most consequential finding for the [Implementation Contracts](/implementation-contracts) page is which rows are *silent-misinterpretation candidates*: same JSON shape before and after, but a reader that ignores version and looks only at structure produces wrong output. These are the rows tagged `semantic-only` or `add-with-semantic-shift`.

| # | spec | id | description | tag |
|---|---|---|---|---|
| 1 | spatial | [Spatial PR#4](https://github.com/zarr-conventions/spatial/pull/4) | New optional `spatial:registration` field; default `"pixel"` preserves prior behavior, value `"node"` re-anchors `spatial:transform` coefficients (corner-of-pixel vs. cell-center). | `add-with-semantic-shift` |
| 2 | spatial | [Spatial PR#7](https://github.com/zarr-conventions/spatial/pull/7) | When composing with multiscales, the multiscales `translation` should be `[0,0]` for standard geospatial overviews; pixel origin comes from `spatial:transform`. Pre-PR a different composition rule was equally defensible. | `semantic-only` |
| 3 | spatial | [Spatial PR#9](https://github.com/zarr-conventions/spatial/pull/9) | Affine transform formula notation `(i, j)` replaced with `(col_index, row_index)`. No JSON change. The conventional array-programming reading of `(i, j)` is `(row, col)`, opposite of the spec's intent. | `semantic-only` |
| 4 | proj | [Proj PR#14](https://github.com/zarr-conventions/proj/pull/14) | `proj:transform` declared authoritative over multiscales `scale`/`translation` for geospatial coordinates. Pre-PR ambiguity allowed two compositions; same JSON now means one specific thing. | `semantic-only` |
| 5 | stac-spec | [STAC #1064](https://github.com/radiantearth/stac-spec/issues/1064) | First entry of Collection `extent` arrays redefined as the overall extent; subsequent entries are sub-extents. Positional meaning added to a previously-unordered array. | `semantic-only` |
| 6 | stac-spec | [STAC PR#1111](https://github.com/radiantearth/stac-spec/pull/1111) | Field-absent is no longer equivalent to field-set-to-null. Implementations conflating them now diverge silently. | `semantic-only` |
| 7 | stac-spec | [STAC discussion #1212](https://github.com/radiantearth/stac-spec/discussions/1212) | URL trailing-slash significance codified per RFC 3986. Relative-link resolution changes for implementations that previously normalized. | `semantic-only` |
| 8 | stac-spec | [STAC #1280](https://github.com/radiantearth/stac-spec/issues/1280) | `start_datetime`/`end_datetime` clarified as inclusive bounds. Exclusive-bound implementations produce different boundary results. | `semantic-only` |

Eight rows across three specs (spatial, proj, stac-spec). Zero in raster, ngff, and multiscales. The strongest case is [Spatial PR#9](https://github.com/zarr-conventions/spatial/pull/9): a pure prose change, no JSON difference, where the conventional reading of the pre-clarification formula was demonstrably wrong. [Spatial PR#4](https://github.com/zarr-conventions/spatial/pull/4) is the case the cell-type example in [zarr-conventions-spec#7](https://github.com/zarr-conventions/zarr-conventions-spec/issues/7) imagines, made real.

## The patch slot is unused

Of the catalogued specs, only NGFF has shipped patch releases. stac-spec went 1.0.0 -> 1.1.0 with no 1.0.x; raster went 1.0.0 -> 1.1.0 -> 2.0.0 with no patches; the three pre-release specs have never tagged a release at all.

NGFF's patches (0.1.1 through 0.4.1, all listed in the [version history](https://ngff.openmicroscopy.org/0.5/#history)) all carry additive metadata, not backward-compatible bug fixes:

- 0.1.1 documented multiresolution ordering (`clarify`)
- 0.1.2 added `omero` rendering metadata (`add-optional`)
- 0.1.3 added the `labels` sub-spec (`add-optional`)
- 0.1.4 added HCS plate metadata (`add-optional`)
- 0.4.1 added `bioformats2raw.layout` transitional metadata (`add-optional`)

Selected non-Zarr precedents reinforce this. [OpenAPI 3.0](https://github.com/OAI/OpenAPI-Specification/releases) has shipped four patch releases (3.0.1-3.0.4); each adds features. [CloudEvents](https://github.com/cloudevents/spec/releases) 1.0.1 added protobuf format support, a WebSockets binding, and permission to use null JSON values; 1.0.2 added C# namespace options and SDK clarifications. Both are additions, not bug fixes.

**Implication:** semver's three-slot discipline (patch = bugfix, minor = additive, major = breaking) is not maintained in practice. The slots are used more like *small / medium / large* than *bugfix / additive / breaking*. This finding is what makes the [Integer-major with structural pass-through](/implementation-contracts#_4-integer-major-with-structural-pass-through) contract workable: if patch is misused for additions and minor sometimes carries tightening, the only slot that reliably means what semver claims is MAJOR.

## Beyond the six: precedents outside the per-row catalog

The catalog above is row-level evidence: every substantive change in each of the six conventions, classified one row at a time. Stepping back, what choices have specs *outside* the six made? This section is the broader-but-shallower companion: pattern-level rather than row-level, but covering a wider field.

### Three patterns in the JSON-metadata ecosystem

Most JSON-based metadata formats fall into three groups by how they handle versioning:

| Pattern | Mechanism | Examples |
|---|---|---|
| **No version** | Document carries no version identifier. Identity is purely structural (e.g., a `type` member). | [GeoJSON (RFC 7946)](https://datatracker.ietf.org/doc/html/rfc7946), [TopoJSON](https://github.com/topojson/topojson-specification), most config files (`tsconfig.json`, `.eslintrc.json`). |
| **URI-as-version** | Document references a context or dialect URI. Changing semantics means publishing a new URI. | [JSON-LD `@context`](https://www.w3.org/TR/json-ld11/), [JSON Schema `$schema`](https://json-schema.org/draft/2020-12/json-schema-core), [Schema.org](https://schema.org/docs/datamodel.html). |
| **Versioned field** | Document carries an explicit version field (number, semver string, or date). | [OpenAPI `openapi`](https://github.com/OAI/OpenAPI-Specification), [AsyncAPI `asyncapi`](https://www.asyncapi.com/), [CloudEvents `specversion`](https://github.com/cloudevents/spec), [glTF `asset.version`](https://github.com/KhronosGroup/glTF), [SARIF `version`](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html), [CycloneDX `specVersion`](https://cyclonedx.org/), [SPDX `spdxVersion`](https://spdx.dev/). STAC and NGFF (catalogued above) also belong here. |

The split is not arbitrary. Document-interchange formats (descriptions of resources, events, artifacts, models) overwhelmingly chose to version. Config files and a handful of geospatial formats chose not to. Vocabulary-style formats (JSON-LD, Schema.org) chose URI-as-version, which gives most of the benefits of explicit versioning without putting a number in every document.

### The GeoJSON case: a no-version covenant in real life

[GeoJSON RFC 7946 (2016)](https://datatracker.ietf.org/doc/html/rfc7946) is the most directly relevant precedent for the no-version stance. From §8: "The GeoJSON format can be extended as defined here, but no explicit versioning scheme is defined." The 2008 GeoJSON spec allowed a `crs` member naming an arbitrary CRS. RFC 7946 removed it ([Appendix B](https://datatracker.ietf.org/doc/html/rfc7946#appendix-B): "Specification of coordinate reference systems has been removed [...] the `crs` member of [GJ2008] is no longer used"), defaulted to WGS84, and provided **no migration guidance** for what an implementation should do when it encounters a `crs` member in a legacy document.

A 2008 FeatureCollection with `"crs": "urn:ogc:def:crs:EPSG::3857"` is structurally indistinguishable from a 2016 FeatureCollection that omits `crs`, except for the extra member. A strict fail-on-unknown reader rejects (safe); a lenient ignore-unknown reader silently misinterprets the coordinates (unsafe). There is no signal in the document itself for a reader to tell which spec version it was written against. This is the same shape as the `semantic-only` cases catalogued in the six, demonstrated in production over a real spec transition.

[TopoJSON](https://github.com/topojson/topojson-specification) extends GeoJSON's no-version stance and has been effectively frozen since 2014, which is a weaker but still-informative precedent: "no version" is viable for a spec that does not change, not necessarily for one that does. Config files like `tsconfig.json` work without versioning because the consumer is a single dominant tool and misinterpretation is bounded (a wrong tsconfig field fails to compile; it does not silently produce wrong output). Neither condition holds for zarr conventions.

### Why URI-as-version is on the contract menu

The [URI dispatch](/implementation-contracts#_3-uri-dispatch) contract on the implementation-contracts page rests on this pattern. [JSON Schema dialect URIs](https://json-schema.org/draft/2020-12/json-schema-core) are the cleanest implementation of "fail-on-unknown" in this survey: validators that don't recognize the URI (`draft-07`, `2019-09`, `2020-12`) fail fast, without needing an integer or semver in the document. [JSON-LD `@context`](https://www.w3.org/TR/json-ld11/) uses the same idea in vocabulary form (and additionally allows a `@version` entry inside the context to select processing mode, so the spec hedges by having both mechanisms). [Schema.org's](https://schema.org/docs/datamodel.html) URL has been stable enough that most documents reference `https://schema.org` without specifying a version; the vocabulary expands additively.

The conventions framework's `schema_url` field is structurally identical to `$schema`. Every consequence the JSON Schema community learned from years of dialect dispatch transfers directly: URLs must be stable, the URL identifies the semantics, unrecognized URLs fail safely.

## What this evidence says about the four positions in the issue thread

The catalog was built to weigh four positions surfaced in [zarr-conventions-spec#7](https://github.com/zarr-conventions/zarr-conventions-spec/issues/7). Brief summary; full reasoning lives in the [Implementation Contracts](/implementation-contracts) page.

**"JSON structure plus fail-on-unknown is sufficient; versions are redundant."** *Partially falsified.* Eight rows across three specs show silent-misinterpretation potential where structural inspection cannot help. The strongest case ([Spatial PR#9](https://github.com/zarr-conventions/spatial/pull/9)) is pure prose change with no JSON difference. But five of the eight are *clarifications of pre-existing ambiguity* rather than the spec changing its mind, a subtler attack than the cell-type-style additive-semantic-shift case the issue thread frames.

**"Semver minor gives a graceful-degradation contract integers cannot."** *Mixed.* The empirically minor-bumped specs ([STAC 1.0 -> 1.1](https://github.com/radiantearth/stac-spec/blob/main/CHANGELOG.md#v110---2024-09-10), [NGFF 0.4 -> 0.5](https://ngff.openmicroscopy.org/0.5/#history), [Raster v1.0 -> v1.1](https://github.com/stac-extensions/raster/blob/main/CHANGELOG.md)) made changes that include both purely additive cases and tightening cases that invalidated old documents. STAC's 1.0 -> 1.1 had three `tighten` rows ([STAC v1.1.0-beta.1 changelog](https://github.com/radiantearth/stac-spec/blob/main/CHANGELOG.md#v110-beta1---2024-08-08), [STAC #1243](https://github.com/radiantearth/stac-spec/issues/1243), [STAC #1281](https://github.com/radiantearth/stac-spec/issues/1281)) that produce documents invalid against v1.0 schemas. A strict semver reading would call those breaking. Semver in practice (as actually used by STAC's maintainers) is looser than semver in theory.

**"Semver minor burdens writers with version choice."** *Partially tested.* Per-document writer behavior isn't visible in spec diffs, but maintainer behavior across the three semver slots is, and the catalogued specs plus surveyed precedents show that maintainers don't operate the fine-grained patch / minor / major distinction this position presupposes.

**"Only MAJOR is useful in practice."** *Partial support.* Of the changes in this catalog, `retype` (10) + `add-required` (4) + `remove` (12) + `rename` (7) = 33 are arguably breaking. Versus `add-optional` (19) and `loosen` (14) which are additive and reader-safe. Plus 7-8 semantic-only cases that don't fit cleanly into either bucket. The "MAJOR-only is workable" instinct is consistent with the data.

## What is not in this evidence

- **Reader behavior.** The catalog classifies spec changes, not what real implementations did when meeting them. The silent-misinterpretation rows are *opportunities*; whether any real reader was hit depends on the reader.
- **Writer choice frequency.** How often a real writer would face the "what minimum version do I declare?" decision is not captured.
- **A counterfactual for the disciplined specs.** Raster, ngff, and multiscales have zero silent-misinterpretation rows. This could mean their maintainers were disciplined, or that they had fewer opportunities (smaller surface area, structural-reboot pattern). The catalog cannot distinguish these.

## How to cite

This page is the citable source for the numbers and findings used elsewhere in the guidance site. If you want to refer to it externally, use the date stamp at the top and link to this page directly. Per-spec catalogs and per-row notes are not reproduced here; they live in the working folder that produced this summary and may be opened as a follow-up artifact if the community wants them.
