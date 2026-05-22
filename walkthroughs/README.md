# walkthroughs/

Runnable artifacts behind the [walkthroughs section of the guidance site](https://zarr-conventions.github.io/zarr-conventions-guidance/walkthroughs/). The prose for each walkthrough lives in `docs/walkthroughs/0X-<contract>.md`; this tree holds the JSON fixtures and the Python that produces the matrix the docs quote.

## Layout

- `fixtures/0X-<change>/` — shared JSON inputs and schemas, one folder per catalogued change type (`add-optional`, `rename`, `retype`, `semantic-only`, `add-with-semantic-shift`).
- `0X-<contract>/run.py` — one script per contract. Each script implements a single reader for that contract and exercises it against all five fixture sets. Asserts its outcome matrix matches the documentation.

## Running

Each `run.py` is a PEP 723 script. `uv` resolves its dependencies inline; no project-level virtualenv is needed.

```bash
uv run walkthroughs/01-stable-additive-covenant/run.py
uv run walkthroughs/02-structural-inspection/run.py
uv run walkthroughs/03-uri-dispatch/run.py
uv run walkthroughs/04-integer-major-pass-through/run.py
uv run walkthroughs/05-semver-with-migrators/run.py
```

The code here is illustrative, non-normative, and not intended for production use. Each script focuses on showing what an implementation following one contract looks like, and what happens when the convention author honors or violates their side of the covenant.
