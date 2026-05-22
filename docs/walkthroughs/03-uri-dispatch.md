---
title: Implementing URI dispatch
description: A reader for the URI dispatch contract, exercised against the five catalogued change types, with failure modes when the author breaks the covenant.
---

# Implementing: [URI dispatch](/implementation-contracts#_3-uri-dispatch)

The contract: the `schema_url` is the version. Every breaking or semantic change gets a new URL; the old URL keeps its old meaning forever. The reader maintains a registry mapping known URLs to handlers; unknown URLs fail.

## Reader skeleton

```python
HANDLERS = {
    "https://example.com/proj/v1/schema.json": handler_v1,
    "https://example.com/proj/v2/schema.json": handler_v2,
}

def uri_dispatch(data):
    url = data["attributes"]["zarr_conventions"][0]["schema_url"]
    handler = HANDLERS.get(url)
    if handler is None:
        return "FAIL: unknown schema_url"
    return handler(data)
```

The registry pattern is the entire contract. New URL = the implementer writes a new handler; until then, unknown URLs fail loudly (safe). The author's commitment is "new URL for new semantics, never the same URL with new semantics." Each handler does its own field lookup against the shape it was coded for. No runtime schema validation.

## How change types hit this reader

|  | before.json (v1) | after.json (v2) | What happens |
|---|---|---|---|
| add-optional | OK | OK | Both URLs are known; v1 handler reads v1 schema, v2 handler reads v2 schema. |
| rename | OK | OK | v1 handler knows `proj:code`; v2 handler knows `proj:identifier`. |
| retype | OK | OK | Each handler validates against its own schema; the type difference is per-version. |
| semantic-only | OK | OK | The JSON is identical across the transition, but the URL is not. Each handler applies the appropriate semantics. |
| add-with-semantic-shift | OK | OK | v2 handler knows to read `proj:cell_alignment`; v1 handler does not need to. |

The matrix is all OK. That is the point: URI dispatch handles every catalogued change type, *as long as the convention author honored the covenant*.

## When the author breaks the covenant

The covenant is simple: **new URL for every breaking or semantic change**. Two violations matter:

- **Author ships a breaking change at the same URL.** The reader has already cached a handler for that URL with the old understanding. v1-era documents (still valid against that old understanding) still read correctly. New documents written against the new (silently changed) meaning of that URL produce silent wrong output: the reader applies the old handler's logic to data that now means something different. There is no detection signal in the JSON.
- **Author publishes a new URL but the URL pattern shifts in a way the reader does not expect.** Reader gets an unknown URL and fails loudly. Safe, but the new documents are unreadable until the implementer ships an update.

The first failure mode is the one that matters. URI dispatch trades "verify the author's promise" for "verify the URL changed." That tradeoff is excellent if the author has URL discipline and catastrophic if they do not.

A practical mitigation: implementers and validators can pin the URL's expected schema content (e.g., compute a hash on first fetch and reject mismatches). That makes "author silently changed the URL's content" a loud failure rather than a silent one, at the cost of more work for both sides.

## Run it

```bash
uv run walkthroughs/03-uri-dispatch/run.py
```

## Outcome matrix

```
                            before.json  after.json
01-add-optional             OK           OK
02-rename                   OK           OK
03-retype                   OK           OK
04-semantic-only            OK           OK
05-add-with-semantic-shift  OK           OK
```

## Reader code

<<< @/../walkthroughs/03-uri-dispatch/run.py{python}

## Commentary

URI dispatch handles every catalogued change type because the author's covenant carries every detection signal the reader needs: the URL itself. The reader does not have to reason about version numbers, range checks, migrators, or semver semantics; it only has to ask "do I know this URL?" The [survey](/posts/2026-survey) found this is the cleanest implementation of "fail-on-unknown" in the broader JSON-metadata ecosystem (JSON Schema dialect URIs, JSON-LD `@context`, Frictionless `profile`).

The cost is that the implementer must ship a code update for every new URL the author publishes. The reader cannot cross-version share code: each handler is independent. For a convention that ships frequent additive changes, this is more friction than [Integer-major with structural pass-through](/walkthroughs/04-integer-major-pass-through), which lets a single handler tolerate additive evolution within a major.
