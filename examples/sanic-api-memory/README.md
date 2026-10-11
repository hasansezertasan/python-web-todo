# sanic-api-memory

Todo JSON API built with Sanic and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Sanic generates no OpenAPI by default).

Validation is manual (Sanic has no request-body validation by default): missing/empty `title` returns `422` with a JSON body, unknown ids return `404` with a JSON body.

## Run

From the repo root:

```sh
uv run --project examples/sanic-api-memory sanic app.main:app --host=0.0.0.0 --port=8000
```

Then `GET http://localhost:8000/todos`.
