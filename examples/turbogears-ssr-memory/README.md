# turbogears-ssr-memory

Server-rendered todo app built with TurboGears, Genshi templates, and in-memory storage.
Implements the [server-rendered contract](../../specs/server-rendered.md) and
[shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/turbogears-ssr-memory turbogears-ssr-memory
```

Then open `http://localhost:8000/`.

The server honors the `PORT` environment variable (default `8000`):

```sh
PORT=8123 uv run --project examples/turbogears-ssr-memory turbogears-ssr-memory
```

## Flows

- `GET /` renders the todo list page (titles, done/not-done state, add form,
  per-item toggle and delete controls).
- `POST /todos` with a `title` field adds an item, then redirects to `/`.
- `POST /todos/{id}/toggle` flips the item's done state, then redirects to `/`.
- `POST /todos/{id}/delete` removes the item, then redirects to `/`.
- Empty (or whitespace-only) titles re-render the list with status `400` and the
  error `Title must not be empty`; nothing is created.
- Unknown ids answer `404`.

Titles are stripped of leading/trailing whitespace before storage.

## Testability

`src/app/main.py` exposes `create_app(repo=None)`, which takes an optional
`InMemoryTodoRepository` so contract tests get a fresh, empty store per test.
It returns the TurboGears WSGI app, so the harness can drive it with
`webtest.TestApp(create_app())` (import path `app.main`, `sys.path` including
`src/`; `webtest` must be installed in the driving environment).

## Notes

- `AppConfig(minimal=True, ...)` disables TurboGears' full-stack defaults
  (SQLAlchemy, Ming, transactions, sessions, auth), so no database is
  configured at all — no dummy DB was needed. Storage is a plain process-local
  `InMemoryTodoRepository` starting empty.
- Routing is TurboGears object dispatch: `RootController.index` serves `GET /`,
  `TodosController.index` handles `POST /todos`, and dynamic `/todos/{id}/*`
  segments dispatch via an `@expose()`-decorated `_lookup` (crank, the TG
  dispatcher, only consults `_lookup` when it is exposed) returning a
  per-item `TodoItemController` with `toggle`/`delete` actions. Successful
  POSTs use `tg.redirect("/")` (a `302`; the `Location` header is absolute,
  `http://<host>/`, per WebOb idiom — following it lands on `/` exactly as
  the contract requires). Unknown ids use `tg.abort(404)`.
- Templates use Genshi (`.html`), the TurboGears-native template engine,
  referenced by dotted name (`app.templates.index`, so `templates/` ships an
  `__init__.py`) and resolved from `__file__`, working both from source and
  from the installed wheel (verified: `uv build` ships
  `app/templates/index.html` via `packages = ["src/app"]` alone, so no
  `force-include` is needed — and adding one breaks the wheel build with a
  duplicate-path error).
