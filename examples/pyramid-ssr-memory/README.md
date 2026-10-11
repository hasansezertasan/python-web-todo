# pyramid-ssr-memory

Server-rendered todo app built with Pyramid, Chameleon templates, and in-memory storage.
Implements the [server-rendered contract](../../specs/server-rendered.md) and
[shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/pyramid-ssr-memory pyramid-ssr-memory
```

Then open `http://localhost:8000/`.

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
It returns the Pyramid router (a plain WSGI app), so the harness can drive it
with `webtest.TestApp(create_app())`.

## Notes

- Templates use Chameleon (`.pt`), the Pyramid-native template engine, rendered
  via `PageTemplateFile` with an absolute path derived from `__file__` so they
  resolve both from source and from the installed wheel (verified: `uv build`
  ships `app/templates/index.pt` via `packages = ["src/app"]` alone, so no
  `force-include` is needed — and adding one breaks the wheel build with a
  duplicate-path error). `pyramid_jinja2` was deliberately not used: it would
  add a dependency for zero contract benefit.
- Redirects are `302` as per the contract, but the `Location` header is absolute
  (`http://<host>/`) rather than `/`: WebOb absolutizes relative locations at
  response time. This is Pyramid/WebOb idiom; following the redirect lands on
  `/` exactly as the contract requires.
