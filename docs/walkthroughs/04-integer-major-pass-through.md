---
title: Implementing Integer-major with structural pass-through
description: A reader for the Integer-major contract, exercised against the five catalogued change types, with failure modes when the author breaks the covenant.
---

# Implementing: [Integer-major with structural pass-through](/implementation-contracts#_4-integer-major-with-structural-pass-through)

The contract: the convention is versioned by a single integer (v1, v2, ...). All changes within a major are additive; only major bumps are breaking. The reader parses the major and dispatches to a per-major handler. Within a recognized major, additive changes pass through under the safely-ignorable principle.

## Reader skeleton

```python
def integer_major_pass_through(data):
    url = data["attributes"]["zarr_conventions"][0]["schema_url"]
    major = parse_major(url)                          # e.g. /v2/ -> 2
    if major == 1:
        return handler_major_1(data)
    if major == 2:
        return handler_major_2(data)
    return "FAIL: unknown major"
```

The dispatch is the same shape as URI dispatch, but on a parsed integer instead of an opaque URL. Each per-major handler does its own field lookups for the shape it was coded for; no runtime schema validation. The key consequence is that the reader is robust to any *additive* change within a major: a v2 handler will accept any v2.x document because the major did not change.

## How change types hit this reader

|  | before.json (v1) | after.json (v2) | What happens |
|---|---|---|---|
| add-optional | OK | OK | The change here happens to bump the major; in real life the author would not bump for a purely additive change. Either way, both majors are known. |
| rename | OK | OK | Author bumped major. Each major has its own handler, each handler knows its own field names. |
| retype | OK | OK | Same: per-major schema validation, per-major type handling. |
| semantic-only | OK | OK | Author bumped major. Each handler applies its own semantics. |
| add-with-semantic-shift | OK | OK | v2 handler knows the new field's meaning; v1 handler does not need to. |

The matrix is all OK. As with URI dispatch, this is the happy path: the author is honoring the covenant (bump major for every breaking change). Where Integer-major is *weaker* than URI dispatch shows up in the violations.

## When the author breaks the covenant

Integer-major's covenant has two pieces: **bump the major for every breaking change**, and **stay additive within a major**. Violations:

- **Author ships a within-major rename or retype.** The reader's per-major schema validates documents against the major's known shape. A rename or retype within the major produces documents that fail validation loudly. Safe failure mode, but old code can no longer read new data without an update.
- **Author ships a within-major semantic-only shift.** No detection signal. The major did not change; the schema may still validate (if shapes are unchanged); the reader applies its frozen per-major semantics. Silent wrong output. This is the same failure mode as [Stable additive covenant](/walkthroughs/01-stable-additive-covenant) on the same change type: integer-major cannot detect semantic drift any better than the no-version contracts.
- **Author ships a within-major add-with-semantic-shift.** Same as above. The new field is unknown to the v2 handler; the safely-ignorable principle says to ignore it; the resulting interpretation is wrong.
- **Author bumps the major for a breaking change** (the happy path). Reader either has a handler for the new major (OK) or fails loudly on `FAIL: unknown major` (safe).

The integer-major contract's central tradeoff: it makes per-major dispatch cheap (one integer parse) and is robust against any change that respects the additive-within-a-major rule, but it has no signal for within-major semantic drift. For specs whose authors are disciplined about major bumps, this is an excellent contract. For specs whose authors slip a semantic shift into a minor or patch release, it produces the same silent wrong output as [Stable additive covenant](/walkthroughs/01-stable-additive-covenant).

## Run it

```bash
uv run walkthroughs/04-integer-major-pass-through/run.py
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

<<< @/../walkthroughs/04-integer-major-pass-through/run.py{python}

## Commentary

Integer-major matches the empirical pattern the [survey](/posts/2026-survey) found: of the catalogued specs, the patch slot is never load-bearing, and minor bumps carry tightening changes that strict semver would call breaking. Treating only the major as load-bearing matches how maintainers actually operate. The contract is robust against the additive-within-a-major rule, which lines up with how the data actually moves through release cycles in the field.

The contract's gap is semantic-only and add-with-semantic-shift changes *within* a major. If your convention can rule those out by policy ("no semantic shifts, ever, in any release"), this contract is excellent. If not, prefer [Semver with declared migrators](/walkthroughs/05-semver-with-migrators), which explicitly ships migrators for those cases.

## Addendum: the Cargo / Rust-style pre-1.0 variant

A useful variant of this contract follows the [Cargo SemVer convention](https://doc.rust-lang.org/cargo/reference/semver.html) that the Rust ecosystem standardised: while a crate is at `0.x.y`, each new `0.x` minor bump is treated as breaking; patches on `0.x.y` are additive; once a stable `1.0.0` ships, minor versions become non-breaking and the conventional integer-major rule applies. The contract is otherwise unchanged: the reader dispatches on a "compatibility key" parsed from the version, and unknown keys fail loudly.

The compatibility-key rule for a parsed semver:

```python
def compat_key(major: int, minor: int) -> str:
    return f"0.{minor}" if major == 0 else str(major)
```

Under this rule:

- `0.1.x` documents share a compatibility key; the reader implements a `0.1` handler.
- `0.2.0` is treated as breaking; the reader needs a separate `0.2` handler.
- `1.0.0` shares its key with `1.5.0` (both `"1"`); minor evolution is additive after stable.
- `2.0.0` is a new key.

The handler dispatch is otherwise identical to the integer-major reader above; only `_parse_major` is replaced by the Cargo-style `compat_key`.

### Why this variant exists

[NGFF](https://ngff.openmicroscopy.org/0.5/#history) is the cleanest example from the [survey](/posts/2026-survey): it spent its first five years iterating from `0.1.0` to `0.5.2` with breaking changes at each minor (`0.2.0` changed chunk-separator encoding, `0.3.0` added required `axes`, `0.4.0` restructured `axes` to objects, `0.5.0` moved metadata under `attributes.ome`). Patches (`0.1.1`-`0.1.4`, `0.4.1`) were used for additive sub-spec releases. A strict integer-major reader of NGFF that dispatched only on the leading integer would see every version as `0` and break repeatedly; a Cargo-style reader dispatching on `0.1` / `0.2` / `0.3` / `0.4` / `0.5` is what every NGFF library actually does.

The variant is also a hedge for *new* conventions: it lets a spec iterate freely under `0.x` without committing to "this is what `1.0` looks like" until the design is settled. Once `1.0` ships, the rules tighten and minor evolution becomes additive. This is what the Rust ecosystem and a sizable chunk of the JSON-metadata ecosystem do in practice (npm, RubyGems, and Cargo all encode this rule into their dependency resolvers).

### Trade-offs vs. plain integer-major

- **Plus:** the spec gets a real iteration phase before committing to a stable major boundary. Convention authors can ship breaking changes during `0.x` without "wasting" major numbers.
- **Plus:** the reader's dispatch shape is identical; only the key extraction differs.
- **Minus:** the contract is more nuanced to explain ("minor is breaking, but only until 1.0"). The author has to communicate the rule, and the reader has to encode it.
- **Minus:** the same within-major silent-shift gap applies to *both* pre-1.0 and post-1.0 phases. The variant does not buy any extra safety for semantic-only changes; it just adds a phase where breaking changes are cheaper to ship.

If your spec is established and unlikely to ship breaking changes after release, plain integer-major is simpler. If your spec is young and you expect to iterate on the design through several breaking releases before reaching a stable surface, the Cargo-style variant matches that lifecycle better.
