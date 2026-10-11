# python-web-todo

A follow up of <https://github.com/hasansezertasan/hello-world-python-web>.

While `hello-world-python-web` compares 30+ Python web frameworks with the same minimal "Hello, World!" app, this project compares them with the same small **Todo app**: a slightly richer app that exposes routing, request handling, rendering, and storage differences.

## What we compare

We compare the **shape of the code, project structure, and selected capabilities** — not every capability.

Frameworks are compared **within the capabilities they are suited to**:

- Some frameworks are strong on the server-rendered side (e.g. Django).
- Some are strong on the JSON API side (e.g. FastAPI).
- Some are malleable (e.g. Litestar) or micro (e.g. Flask) enough to do both, as separate applications.

Putting Django and Flask in the same bucket for everything would not be just. So Django SSR is compared with Flask SSR, and FastAPI API with Litestar/Flask API — never full-stack against micro directly.

## Structure

Examples are flat: one folder per example, prefixed with the framework name (`examples/<framework>-<interface>-<storage>[-<engine-or-extension>]/`). Each example is self-contained with its own dependencies and framework-native entry point. The `interface` segment decides the contract: `*-api-*` follows the JSON API spec, `*-ssr-*` the server-rendered spec.

`examples/MATRIX.md` is the catalog of examples with a run command for each. A new framework starts with the variant that fits it best; full coverage is never required. Authoring rules live in `skills/new-example/SKILL.md`.

## Repo layout

- `specs/` — the behavior contracts.
- `examples/` — one folder per example, cataloged in `examples/MATRIX.md`.
- `tests/` — shared contract suites plus per-framework runners.
- `skills/new-example/` — authoring rules for new examples.
- `deferred/` — frameworks with no example, each with a reason.

## Conventions

- **Behavior comparable, implementations idiomatic:** keep behavior comparable, not implementations identical. Stick to framework idioms. Page output should look the same across SSR examples, and OpenAPI output should be as similar as possible where both frameworks generate it, but implementations stay idiomatic.
- **Specs:** behavior contracts live in `specs/`; `tests/` checks each example against them.

## Growth

We aim to support as many frameworks as possible from the `hello-world-python-web` list. Which example to build first per framework is documented in `skills/new-example/SKILL.md`.

Fairness comes from the contracts: Django SSR is compared with Flask SSR, FastAPI API with Litestar/Flask API, SQLite variants with each other — never Django full-stack against a micro framework directly.

## What won't be there

- No forced full matrix: frameworks only implement examples that fit them.
- No cross-contract comparisons: SSR examples are compared with SSR, API with API.
- Special UI / data-app frameworks (`dash`, `streamlit`, `nicegui`, `reflex`, `gradio`, `flet`, `pywebio`) do not fit the `api`/`ssr` contracts and are deferred to a separate track or marked out of scope.
- Low-level stdlib (`socket`, `http`) has no routing/templating idiom to compare and is deferred.
- Blocked on this toolchain (Python 3.14): `hug` — pinned to `falcon==2.0.0`, which imports the long-removed `cgi` stdlib module — and `eve` — needs external MongoDB while its mongo layer is broken with PyMongo 4. Recorded under `deferred/` instead of worked around.
- Each deferred framework has a folder under `deferred/` with a README giving the reason — see `deferred/README.md` for the index.
