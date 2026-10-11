# morepath-api-memory

Todo JSON API built with Morepath (model-driven `@path` models + `@json`/`@view` views, manual validation) and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Morepath generates no OpenAPI).

## Run

From the repo root:

```sh
uv run --project examples/morepath-api-memory python -m app.main
```

Then `GET http://localhost:5000/todos`. `PORT` env var overrides the port.

## Test isolation

`create_app(repo=None)` builds a fresh Morepath `App` subclass per call, registers the collection/item models and views against it, and commits it with `morepath.commit` — Morepath binds configuration to the app class, so a new subclass per call is what gives each test its own empty `InMemoryTodoRepository`. Module-level `app` is the runnable instance. The shared harness drives it with `webtest.TestApp(create_app())`.
