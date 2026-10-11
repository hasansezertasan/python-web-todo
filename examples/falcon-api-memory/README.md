# falcon-api-memory

Todo JSON API built with Falcon (WSGI) and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Falcon generates no OpenAPI).

## Run

From the repo root:

```sh
uv run --project examples/falcon-api-memory gunicorn app.main:app
```

Then `GET http://localhost:8000/todos`.
