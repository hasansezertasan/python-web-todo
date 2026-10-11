# quart-api-memory

Todo JSON API built with Quart (async Flask-like) and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (Quart generates no OpenAPI).

Validation is manual (Quart has no request-body validation by default): missing/empty `title` returns `422` with a JSON body, unknown ids return `404` with a JSON body.

## Run

From the repo root:

```sh
uv run --project examples/quart-api-memory hypercorn app.main:app --bind 0.0.0.0:5000
```

Then `GET http://localhost:5000/todos`.
