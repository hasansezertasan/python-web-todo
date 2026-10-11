---
name: new-example
description: Scaffolding new todo-app examples and validating existing ones against the repo rules. Use this skill whenever adding an example under examples/, checking an example for rule compliance, or when the user mentions scaffolding, a new framework example, example structure, or MATRIX registration — even if they don't explicitly ask for the skill.
---

# New Example

Every example is one flat folder implementing exactly what its folder name says.

## Rules

1. **Flat location.** Each example is a direct child of `examples/`, never nested. Name it `<framework>-<interface>-<storage>[-<engine-or-extension>]`, e.g. `fastapi-api-memory`, `django-ssr-memory-native`.
2. **src layout.** All code lives under `src/<package>/` (typically `src/app/`). The example root holds only config (`pyproject.toml`), `README.md`, and framework-mandated files. No flat modules next to the config.
3. **Scope discipline.** Implement exactly what the folder name says, no more:
   - `*-memory` examples: no database, ORM, or migration files/dependencies.
   - `*-sqlite-*` examples: persistence only via the framework-idiomatic integration named in the folder. In-memory and SQLite variants must preserve the same observable behavior; compare setup and project shape without pretending a built-in database (Django) equals an extension.
   - `*-api-*` examples: JSON endpoints only, no templates or HTML forms.
   - `*-ssr-*` examples: server-rendered pages and forms only, no JSON API surface beyond the contract.
4. **Self-contained project.** Each example has its own `pyproject.toml` with its own dependencies. No imports from sibling examples or the repo root.
5. **Testable entry point.** Expose an app factory (e.g. `create_app()` taking an optional repository/store) so contract tests get a fresh state per test. If the framework has no factory idiom, document the equivalent in the example README.
6. **Contract compliance.** `*-api-*` follows `specs/json-api.md`, `*-ssr-*` follows `specs/server-rendered.md`; both follow `specs/todo-behavior.md`. The contract is derived from the `interface` segment of the folder name. The JSON API contract covers common operations, status codes, error behavior, and representative OpenAPI expectations; the server-rendered contract covers user-visible flows, page content, and form behavior.
7. **Registration.** Add a row to `examples/MATRIX.md` (interface, rendering, storage, status, working run command) and ship a per-example `README.md` with run instructions and links to the relevant specs.

Behavior stays comparable across examples; implementations stay idiomatic to the framework. When a rule conflicts with a strong framework idiom, follow the idiom and note the deviation in the example README — do not silently break the rule.

## Scaffolding a new example

1. Derive the folder name from the rule 1 pattern and confirm which contract applies (rule 6).
2. Create `examples/<name>/` with `pyproject.toml`, `README.md`, and `src/<package>/` code. Since the package name won't match the project name, declare it explicitly so the hatchling build finds it:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/<package>"]
```
Typical interior (frameworks keep their native layout — a Django example has `manage.py` plus project/app packages instead):
```text
examples/<name>/
├── pyproject.toml
├── README.md
└── src/
    └── app/
        ├── main.py
        ├── models.py
        ├── schemas.py
        └── repository.py
```
3. Implement the contract endpoints/flows against an in-memory store first (or the idiomatic SQLite integration for `*-sqlite-*`).
4. Add the example to `API_EXAMPLES` / `SMOKE_TARGETS` (or their SSR counterparts) in `tests/` so the shared contract suite covers it.
5. Run `uv run pytest -q` from the repo root, then boot the example with its documented run command and exercise list/create/toggle/delete once.
6. Register the row in `examples/MATRIX.md` with status Done.

## Which example to build first

Use these capability groups to pick the first example for a framework. A framework only ever implements examples that fit it — full coverage is never required:

- SSR-first full-stack (`django`, `pyramid`, `turbogears`): start with `<framework>-ssr-*`.
- API-first ASGI (`fastapi`, `starlette`, `blacksheep`, `sanic`, `connexion`, `falcon`): start with `<framework>-api-memory`.
- Flexible micro (`flask`, `litestar`, `quart`): can do both, as separate examples.
- Minimal WSGI (`bottle`, `klein`, `hug`, `pycnic`, `clastic`, `muffin`, `morepath`): start with `<framework>-api-memory`, add `<framework>-ssr-*` only if templating is idiomatic.
- Standalone / event-driven (`aiohttp`, `tornado`, `twisted`, `robyn`, `tremolo`, `circuits`, `socketify`, `rsgi`): start with `<framework>-api-memory` only.

## Framework notes (learned from the first 12 examples)

- **Django** has no factory idiom: keep `manage.py` at the example root (it only wires `src/` onto `sys.path`), put project/app packages under `src/`, use a dummy `DATABASES` for memory examples, and expose a reset hook (e.g. `reset_store()`) plus a DB-path override (e.g. `TODO_DB_PATH` / `create_app(db_path=...)`) for SQLite. The shared pytest suite cannot host multiple Django settings modules in one process — Django examples are exercised via `tests/django_check.py`, one example per process.
- **Templates must ship in the wheel.** Verify with `uv build` (check the wheel contains the templates) plus a boot via the documented run command. Current hatchling auto-includes template files under `packages = ["src/<package>"]` — do NOT add a `force-include` for them, a duplicate entry breaks the wheel build.
- **Status-code mapping is the example's job.** If the framework's idiomatic error status differs from the contract (e.g. Litestar validation defaults to 400, DRF serializer errors default to 400), remap to the contract's status (422) in the example and document it — do not weaken the shared contract.
- **SQLite defaults must not depend on cwd.** Resolve the default DB file from `__file__` (the run command executes from the repo root) and accept an override (`db_url` param or env var) for test isolation.
- **Not every framework fits the shared root venv.** When the framework can't live there (hostile dependency pins like `werkzeug==1.0.1`, or an async-only test client), the example is exercised via `tests/venv_check.py`, which runs the shared checks inside the example's own venv (`uv run --project`); client adapters live in `tests/_in_venv.py`. Report the exact client construction so the adapter can be written.
- **Compatibility gate.** Old frameworks may not run on this toolchain at all (`hug` is blocked: its `falcon==2.0.0` pin imports the removed `cgi` module). If it doesn't install/import cleanly, stop and report — don't pin ancient versions or monkeypatch. Blocked frameworks are recorded in the README's "What won't be there".
- **Standalone servers need `PORT` + the live runner.** Frameworks with no usable in-process test client are exercised via `tests/live_check.py`, which boots the documented run command as a subprocess on an ephemeral port. Every such example must honor the `PORT` env var (default documented in its README).

## Validating an existing example

Check each rule in order and report violations with file paths:

1. `ls examples/` — the example is one direct child, correctly named.
2. No `.py` files or packages at the example root outside `src/` (config and docs excepted).
3. Dependencies and files match the folder-name scope (rule 3) — flag ORMs in memory examples, templates in API examples, JSON routes in SSR examples.
4. Imports resolve within the example; `create_app()` (or documented equivalent) yields fresh state.
5. `uv run pytest -q` passes and the documented run command boots a working app.
