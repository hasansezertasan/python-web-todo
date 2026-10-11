# bottle-api-memory

Todo JSON API built with Bottle and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Bottle generates no OpenAPI).

## Run

From the repo root:

```sh
uv run --project examples/bottle-api-memory python -m app.main
```

Then `GET http://localhost:5000/todos`. `PORT` env var overrides the port.
