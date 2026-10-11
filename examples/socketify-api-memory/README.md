# socketify-api-memory

Todo JSON API built with socketify.py and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (socketify.py generates no OpenAPI).

Validation is manual (socketify.py has no request-body validation): missing/empty `title` returns `422` with a JSON body, unknown ids return `404` with a JSON body. A non-boolean `done` on update returns `422` with a JSON body.

## Run

From the repo root:

```sh
uv run --project examples/socketify-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. `PORT` env var overrides the port (default `8000`):

```sh
PORT=8001 uv run --project examples/socketify-api-memory python -m app.main
```
