---
title: Zarr Conventions Guidance
description: Non-normative guidance, worked examples, and supporting evidence for the Zarr Conventions framework.
---

# Zarr Conventions Guidance

Non-normative guidance for the [Zarr Conventions framework](https://github.com/zarr-conventions/zarr-conventions-spec). This site collects recommended patterns, worked examples, and the empirical evidence behind them. Nothing here is binding; the normative specification lives elsewhere.

## What is on this site

- **[Implementation Contracts](/implementation-contracts)** — A menu of five well-formed pairings between author-side compatibility promises and reader-side consumption modes. Start here if you are designing a convention or writing a reader for one.
- **[Walkthroughs](/walkthroughs/)** — One implementer's guide per contract, showing a focused reader, the change types it can and cannot handle, and what failure modes look like when the author breaks their side of the covenant.
- **[2026 spec-evolution survey](/posts/2026-survey)** — The empirical evidence underneath the guidance: approximately 46 catalogued changes across six JSON-metadata conventions, classified by the kind of break each one produces. A one-time snapshot from May 2026, not actively maintained.

## How this site relates to the normative spec

The [normative Zarr Conventions specification](https://github.com/zarr-conventions/zarr-conventions-spec) tells convention authors how to identify and version their conventions. It does not say what an implementation should do when it encounters one. This site addresses that gap, naming patterns the broader JSON-metadata ecosystem has proven workable, and documenting their trade-offs honestly. The Implementation Contracts page is the central artifact; everything else exists to support it.

Items in the menu may eventually be promoted into the normative spec if community consensus forms around any of them. Until then, the content here is opinionated guidance grounded in evidence, not a list of requirements.

## Audience

The site has two intended readers:

- **Convention authors** designing a new convention, choosing how to version it, and writing the rules implementers should follow. The [Implementation Contracts](/implementation-contracts) page and the "decision aid" within it are the main entry point.
- **Implementers** writing a reader, validator, or downstream library that consumes one of these conventions. The [walkthroughs](/walkthroughs/) are organised by contract so an implementer who has chosen one can see the reader code, the failure modes, and the consequences of the spec author honoring or breaking the covenant.

## Status

The site is in its initial release. The Implementation Contracts page, the walkthroughs, and the 2026 survey are all considered the first published versions; revisions will be tracked in the Git history of the [source repository](https://github.com/zarr-conventions/zarr-conventions-guidance).
