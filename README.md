# zarr-conventions-guidance

Non-normative guidance for the [Zarr Conventions framework](https://github.com/zarr-conventions/zarr-conventions-spec).

This repository publishes opinionated patterns, recommendations, and worked examples that the community can opt into. Nothing here is binding; the normative spec lives in `zarr-conventions-spec`.

Rendered site:
- Current: https://zarr-conventions.github.io/zarr-conventions-guidance/
- Aspirational: https://conventions.zarr.dev/guidance/

## What is here

- `docs/implementation-contracts.md`: the first guidance page, describing five well-formed contracts (pairings of author-side compatibility promises with reader-side consumption modes) that conventions can adopt.
- `docs/walkthroughs/`: VitePress pages walking through how each contract handles representative change types (`add-optional`, `rename`, `retype`, `semantic-only`, `add-with-semantic-shift`).
- `walkthroughs/`: runnable Python (`uv run walkthroughs/0X-<change>/run.py`) plus JSON fixtures behind each walkthrough.

## Running the walkthroughs

Each walkthrough is a single PEP 723 script with inline dependencies. Requires `uv`:

```bash
uv run walkthroughs/01-add-optional/run.py
```

## Running the docs site locally

Requires Node.js:

```bash
npm install
npm run docs:dev
```

## Contributing

See the [zarr-conventions](https://github.com/zarr-conventions) organization.
