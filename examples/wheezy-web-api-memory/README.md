# wheezy-web-api-memory

Todo JSON API built with wheezy.web and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (wheezy.web generates no OpenAPI).

Handlers are `wheezy.web.handlers.MethodHandler` subclasses served through a `wheezy.routing` URL table; `MethodHandler` only dispatches GET/POST/HEAD, so the item handler extends dispatch to PATCH and DELETE. The per-app repository is carried in the WSGI `options` dict (`options["todo_repo"]`), so `create_app()` yields a fresh in-memory store per call.

## Run

From the repo root:

```sh
uv run --project examples/wheezy-web-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. The `PORT` env var overrides the port (default `8000`):

```sh
PORT=8123 uv run --project examples/wheezy-web-api-memory python -m app.main
```
