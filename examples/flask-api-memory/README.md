# flask-api-memory

Todo JSON API built with Flask and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (no generator).

## Run

From the repo root:

```sh
uv run --project examples/flask-api-memory flask --app app.main run
```

Then `GET http://localhost:5000/todos`.
