---
title: Implementation Contracts for Zarr Conventions
description: Non-normative menu of well-formed pairings between author-side compatibility promises and reader-side consumption modes.
---

# Implementation Contracts for Zarr Conventions

::: warning Non-normative guidance
This document does not add requirements beyond those in the [normative Zarr Conventions specification](https://github.com/zarr-conventions/zarr-conventions-spec). It describes well-known patterns that conventions can opt into.
:::

## Why this exists

The normative spec tells convention *authors* how to version their conventions but says nothing about what *implementations* should do when they encounter one. As long as that gap is unspecified, every library invents its own rule, and the [survey](/posts/2026-survey) of six conventions shows enough silent-misinterpretation risk in real spec histories that the gap is worth closing with concrete guidance.

This page names contracts that have proven to work in practice across the JSON-metadata ecosystem. It is opinionated guidance, not RFC2119 requirements. The community can pick items off this menu, ignore them, or push to promote them into the normative spec once consensus forms.

## Vocabulary

- **Compatibility promise.** What the convention author publicly commits to about their version numbers (or about the absence of versioning).
- **Consumption mode.** What a reader's code does when it encounters a convention.
- **Contract.** A well-formed pairing of a compatibility promise with a consumption mode.

A *cross-cutting safety mechanism* worth knowing about but not promoted to its own menu item: the `must_understand` flag pattern (the Protocol Buffers "ignore unknown" idea in its explicit-opt-in form). Any contract below can adopt it as an additional safeguard.

## The contract menu

The five contracts below are ordered taxonomically by increasing version-system formality, from no-version-system to full semver. The order is not a ranking; pick whichever contract fits the convention's likely change profile.

### 1. Stable additive covenant

**Summary.** No version, no schema-URL version pin. The convention author publicly commits that all future changes will be purely additive.

**Author commits to.** Never renaming, retyping, removing, or semantically shifting existing fields. New optional fields and broadened ranges only. The convention's own spec records the covenant explicitly. The `zarr_conventions` entry carries identity (UUID, `spec_url`) but no version key in attributes.

**Reader does.** Detect the convention by identity, validate against the single (never-versioned) schema, ignore any version metadata, tolerate unknown additional fields per the conventions framework's safely-ignorable principle.

**Fit.** Good for small-surface, semantically stable vocabularies: a tiny discovery-metadata field set, or a domain vocabulary that has settled. Bad for conventions whose semantics may legitimately evolve as domain understanding evolves, since the covenant offers no escape hatch when a clarification or restriction has to ship.

**Precedents.** Dublin Core (15 elements, stable since 1995). TopoJSON (effectively frozen since 2014). GeoJSON RFC 7946 tried this and the covenant broke when `crs` was removed in 2016, see evidence below.

::: details Evidence
Source: [2026 spec-evolution survey](/posts/2026-survey).

The GeoJSON 2008 to RFC 7946 (2016) transition is the canonical no-version-covenant failure. RFC 7946 removed the `crs` member without providing migration guidance; a 2008 document with `"crs": "urn:ogc:def:crs:EPSG::3857"` is structurally indistinguishable from a 2016 document apart from the extra member, and a reader that silently ignores `crs` produces wrong coordinates. This is a real-world `semantic-only` failure (per the classification in the [survey](/posts/2026-survey)) of the additive-covenant approach. Beyond GeoJSON, the survey found 8 catalogued changes across other specs that would have produced silent misinterpretation under a no-version contract.
:::

**Example.** A minimal `zarr_conventions` entry with just UUID and `spec_url`, and no version key in attributes:

```json
{
    "zarr_format": 3,
    "node_type": "array",
    "attributes": {
        "zarr_conventions": [
            {
                "uuid": "f17cb550-5864-4468-aeb7-f3180cfb622f",
                "spec_url": "https://example.com/proj/README.md",
                "name": "proj:",
                "description": "Coordinate reference system information for geospatial data."
            }
        ],
        "proj:code": "EPSG:4326"
    }
}
```

### 2. Structural inspection

**Summary.** No version field. Identity carried by JSON shape. Readers act on what they recognize and refuse what they don't.

**Author commits to.** The absence of versioning machinery. The convention's spec defines the structural signature that distinguishes its data (which top-level keys, which nested shapes, which type constraints).

**Reader does.** Inspect the JSON structure, identify the convention by shape, parse what is structurally recognized, fail or warn on structurally unfamiliar fields. There is no version to dispatch on; recognition is purely structural.

**Fit.** Works for highly-structured formats where shape unambiguously communicates intent and the format truly never makes breaking changes. Bad when semantic-only changes are possible, because the reader has no signal that meaning has shifted while the JSON stayed put.

**Precedents.** GeoTIFF GeoKeys (recognized by tag presence). PROJ WKT autodetection. Apache Parquet's footer.

::: details Evidence
Source: [2026 spec-evolution survey](/posts/2026-survey).

This is the position, surfaced in zarr-conventions-spec issue #7, that "JSON structure plus fail-on-unknown is sufficient, versions are redundant." The [survey](/posts/2026-survey) found 8 of approximately 46 catalogued changes across 6 specs are `semantic-only` or `add-with-semantic-shift`. The sharpest case is a multiscales-adjacent spec where the affine-transform formula notation was clarified from `(i, j)` to `(col_index, row_index)`: no JSON change at all, but the conventional array-programming reading of `(i, j)` is `(row, col)`, opposite of the spec's intent. A structural-inspection reader of pre-clarification data silently produces transposed coordinates. Another case: STAC clarified that field-absent is not equivalent to field-set-to-null; implementations that conflated the two diverged silently. Structural inspection alone cannot help with either.
:::

**Example.** The JSON looks the same as it does for [Stable additive covenant](#_1-stable-additive-covenant), and that is the point of the contract: there is no version field to look at, no schema URL to dispatch on. The convention is recognized by the structural signature (here, the presence of the `proj:` prefix and the shape of `proj:code`):

```json
{
    "zarr_format": 3,
    "node_type": "array",
    "attributes": {
        "zarr_conventions": [
            {
                "uuid": "f17cb550-5864-4468-aeb7-f3180cfb622f",
                "spec_url": "https://example.com/proj/README.md",
                "name": "proj:",
                "description": "Coordinate reference system information for geospatial data."
            }
        ],
        "proj:code": "EPSG:4326"
    }
}
```

### 3. URI dispatch

**Summary.** The `schema_url` is the version. New URL means new semantics. Old URL keeps the old meaning forever.

**Author commits to.** Publishing a new `schema_url` for every breaking or semantic change. Old URLs continue to resolve to documents that mean what they used to mean. No version-number parsing required; the URL itself is the identity.

**Reader does.** Dispatch on `schema_url` (per the normative spec's Convention Identity precedence). Known URL, process. Unknown URL, fail or warn. No semver semantics; there is no implied compatibility between URLs that happen to look similar.

**Fit.** Good for conventions hosted at stable URLs with mature URL discipline. Good when the author wants strict reader behavior without committing to semver. Bad if URLs are not stable, or if the author wants library writers to share code across versions, since URL dispatch implies one code path per URL.

**Precedents.** JSON Schema `$schema`. JSON-LD `@context`. Frictionless Data Package `profile`. schema.org context URL.

::: details Evidence
Source: [2026 spec-evolution survey](/posts/2026-survey) (precedents from the broader JSON-metadata ecosystem; this contract is not represented in the catalogued Zarr-adjacent specs).

URI dispatch is the closest implementation of clean "fail-on-unknown" in the broader JSON-metadata ecosystem. JSON Schema dialect URIs (`draft-07`, `2019-09`, `2020-12`) are dispatched on directly by validators; unrecognized URIs cause fail-fast. Frictionless `profile` is consumed by readers that resolve-and-validate, with explicit divergence for unrecognized URLs. The pattern requires URL stability; the conventions framework's UUID provides a fallback identity if the URL eventually moves, but the URL is still the semantics-carrier under this contract.
:::

**Example.** A `zarr_conventions` entry with a versioned `schema_url`; reader dispatches on the exact URL:

```json
{
    "zarr_format": 3,
    "node_type": "array",
    "attributes": {
        "zarr_conventions": [
            {
                "uuid": "f17cb550-5864-4468-aeb7-f3180cfb622f",
                "schema_url": "https://raw.githubusercontent.com/zarr-experimental/geo-proj/refs/tags/v2/schema.json",
                "spec_url": "https://github.com/zarr-experimental/geo-proj/blob/v2/README.md",
                "name": "proj:",
                "description": "Coordinate reference system information for geospatial data."
            }
        ],
        "proj:code": "EPSG:4326"
    }
}
```

### 4. Integer-major with structural pass-through

**Summary.** Single integer version (v1, v2, ...). Additive within a major. Only major bumps are breaking.

**Author commits to.** A single integer in the version field, carried both in `schema_url` (e.g., `/v2/schema.json`) and optionally in a `<prefix>:version` attribute. All changes within a major are additive. Breaking changes increment the major; the previous major remains valid for existing data and gets its own preserved spec.

**Reader does.** Parse the integer major from `schema_url` or the in-attributes version key. Recognized major, process, tolerating additive changes within the major per the safely-ignorable principle. Unrecognized major, fail or warn.

**Fit.** Good for conventions willing to accept that minor evolution equals breaking change (no `loosen`-only or `clarify`-only intermediate states; if you change at all, it is a new major or a no-op). Matches the "only MAJOR is useful in practice" position, which the catalog partially supports. Bad if the author needs to ship clarifications or restrictions that the strict-semver community would call minor, and bad for semantic-only changes within a major, since those are invisible to an integer-major reader.

**Precedents.** CloudEvents `specversion` (string version, used as major). The raster convention (v1.0 to v1.1 to v2.0 with no patches). GeoParquet `version` (semver string but used loosely). The [Cargo / Rust-style pre-1.0 variant](/walkthroughs/04-integer-major-pass-through#addendum-the-cargo-rust-style-pre-1-0-variant), where `0.x` minor bumps are treated as breaking and `1.0+` minor bumps are additive, fits young specs like NGFF that need an iteration phase before committing to a stable major boundary.

::: details Evidence
Source: [2026 spec-evolution survey](/posts/2026-survey).

Of the catalogued specs, raster went v1.0 to v1.1 to v2.0 with no patch releases; stac-spec went 1.0.0 to 1.1.0 with no patches; multiscales, spatial, and proj are pre-release and have not exercised the patch slot. The empirical pattern is consistent with "patch is unused": the patch slot is never load-bearing in this corpus. The "MAJOR-only is workable" instinct is consistent with the data. Still vulnerable to semantic-only changes within a major: the survey includes cases like [Proj PR#14](https://github.com/zarr-conventions/proj/pull/14), where a `proj:transform` interpretation was tightened without a JSON shape change, which an integer-major reader cannot detect.
:::

**Example.** Convention metadata with `schema_url` ending in `/v2/schema.json` and a `proj:version: 2` attribute; reader checks the major before processing:

```json
{
    "zarr_format": 3,
    "node_type": "array",
    "attributes": {
        "zarr_conventions": [
            {
                "uuid": "f17cb550-5864-4468-aeb7-f3180cfb622f",
                "schema_url": "https://raw.githubusercontent.com/zarr-experimental/geo-proj/refs/tags/v2/schema.json",
                "spec_url": "https://github.com/zarr-experimental/geo-proj/blob/v2/README.md",
                "name": "proj:",
                "description": "Coordinate reference system information for geospatial data."
            }
        ],
        "proj:version": 2,
        "proj:code": "EPSG:4326"
    }
}
```

### 5. Semver with declared migrators

**Summary.** Full MAJOR.MINOR.PATCH. The convention's spec ships explicit migration rules from prior minors and an Arrow-style compatibility-range promise. Readers may migrate in memory.

**Author commits to.** Full semver semantics; an Arrow-style explicit compatibility promise (e.g., "readers of v1.2 can safely process v1.0 and v1.1 data"); and, for each release, an in-spec migration rule from prior minors so readers can normalize old data in memory before processing.

**Reader does.** Parse the semver. Range-check the version against the convention's declared compatibility promise. If the data is in-range, process directly. If out-of-range but a migrator is documented, apply the migrator in memory and then process. If out-of-range and no migrator exists, fail.

**Fit.** Good for conventions with frequent additive evolution and an engaged maintainer community willing to write migrators (STAC and pystac are the model). Bad for conventions with thin maintenance, because the migration burden falls on libraries if the spec does not ship the rules itself.

**Precedents.** STAC plus pystac (the catalogued reference case). OpenAPI 3.0 vs 3.1 (where the version split caused a known tooling divide).

::: details Evidence
Source: [2026 spec-evolution survey](/posts/2026-survey).

stac-spec's catalogued 1.0.0 to 1.1.0 was promoted as a minor but included three `tighten` rows that produced documents invalid against v1.0 schemas. Semver-in-theory would call those breaking. Semver-as-actually-practiced by STAC's maintainers treats minor as "medium-sized change including some incompatibilities," which the migrators absorb. So adopting this contract means committing to writing migrators, not assuming pure semver discipline will hold. Also catalogued: of approximately 46 changes across 6 specs, 19 are `add-optional` (safely additive, deserve minor under semver) and 14 are `loosen` (also additive). Combined, those represent the volume of evolution that semver minor is good for.
:::

**Example.** Convention metadata with a semver string in `schema_url` and a `proj:version` attribute; reader range-checks and migrates as needed:

```json
{
    "zarr_format": 3,
    "node_type": "array",
    "attributes": {
        "zarr_conventions": [
            {
                "uuid": "f17cb550-5864-4468-aeb7-f3180cfb622f",
                "schema_url": "https://raw.githubusercontent.com/zarr-experimental/geo-proj/refs/tags/v1.2.0/schema.json",
                "spec_url": "https://github.com/zarr-experimental/geo-proj/blob/v1.2.0/README.md",
                "name": "proj:",
                "description": "Coordinate reference system information for geospatial data."
            }
        ],
        "proj:version": "1.2.0",
        "proj:code": "EPSG:4326"
    }
}
```

## Choosing a contract

| Contract | Version field? | Schema URL version? | Reader cost | Handles semantic-only? |
|---|---|---|---|---|
| [1. Stable additive covenant](#_1-stable-additive-covenant) | none | none | lowest (one schema) | no |
| [2. Structural inspection](#_2-structural-inspection) | none | none | low (shape check) | no |
| [3. URI dispatch](#_3-uri-dispatch) | none (URL is identity) | yes (URL per version) | medium (per-URL handler) | yes (new URL signals new semantics) |
| [4. Integer-major with structural pass-through](#_4-integer-major-with-structural-pass-through) | integer | yes (path segment) | medium (per-major handler) | no within a major |
| [5. Semver with declared migrators](#_5-semver-with-declared-migrators) | full semver | yes (semver string) | highest (range + migrators) | yes (if migrator is shipped) |

If you are in the following situation, start with the following contract:

- If your vocabulary is small and you can credibly commit to never breaking it: start with **1. Stable additive covenant**.
- If your data is recognizable purely from its shape and you accept that semantic-only changes are not in scope: start with **2. Structural inspection**.
- If you publish your convention at stable URLs and want strict reader behavior without committing to a version number system: start with **3. URI dispatch**.
- If you expect occasional breaking changes but never want to ship migrators or distinguish minor from major: start with **4. Integer-major with structural pass-through**.
- If you expect frequent additive evolution and have the maintainer capacity to ship migration rules with each release: start with **5. Semver with declared migrators**.

A convention may evolve from one contract to another over its lifetime. The covenant in 1 sometimes has to be revised; when it does, the convention typically moves to 3 (assign a versioned schema URL) or 4 (pick an integer major). Moving from 4 to 5 means writing migrators and committing to the Arrow-style compatibility range. The migration path is always upward in formality; once a versioning system is published, removing it tends to break consumers.

## Worked walkthroughs

For runnable demonstrations of how each contract handles concrete change types (`add-optional`, `rename`, `retype`, `semantic-only`, `add-with-semantic-shift`), see the [walkthroughs index](/walkthroughs/).
