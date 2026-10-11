# flask-ssr-memory-jinja

Server-rendered todo app built with Flask, Jinja templates, and in-memory storage.
Implements the [server-rendered contract](../../specs/server-rendered.md) and
[shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/flask-ssr-memory-jinja flask --app app.main run
```

Then open `http://localhost:5000/`.

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
`InMemoryTodoRepository` so contract tests (or a Flask test client via
`app.test_client()`) get a fresh, empty store per test.
