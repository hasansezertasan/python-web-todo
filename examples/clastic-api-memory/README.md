# clastic-api-memory

Todo JSON API built with Clastic and in-memory storage. JSON API contract in [specs/json-api.md](../../specs/json-api.md), shared behavior in [specs/todo-behavior.md](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Clastic generates no OpenAPI).

## Run

From the repo root:

```sh
uv run --project examples/clastic-api-memory python -m app.main
```

Then `GET http://localhost:5000/todos`.
