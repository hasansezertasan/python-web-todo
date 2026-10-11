# klein-api-memory

Todo JSON API built with Klein (Twisted micro-framework) and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Klein generates no OpenAPI).

## Run

From the repo root:

```sh
uv run --project examples/klein-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. `PORT` env var overrides the port (default `8000`):

```sh
PORT=8123 uv run --project examples/klein-api-memory python -m app.main
```
