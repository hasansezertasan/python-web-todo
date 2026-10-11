# baize-api-memory

Todo JSON API built with Baize (ASGI `Router` + `JSONResponse`, manual method dispatch and validation) and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/baize-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. `PORT` env var overrides the port (default `8000`):

```sh
PORT=8001 uv run --project examples/baize-api-memory python -m app.main
```

## Test isolation

`create_app(repo=None)` builds a fresh `Router` with its own empty `InMemoryTodoRepository`;
module-level `app` is the runnable instance. The app has no lifespan dependencies, so the
shared harness can drive it directly with `starlette.testclient.TestClient(app)` used
synchronously without a lifespan context (verified: full list/create/get/update/delete
flow plus JSON `404`/`422` cases pass; `Router` only raises on `lifespan` messages, which
a bare `TestClient(app)` never sends).

## Notes

- Baize generates no OpenAPI, so this example is **exempt** from OpenAPI expectations
  (like other plain-JSON examples).
- Baize's `Router` routes by path only (no per-method routes), so each route handler
  dispatches on `request.method` and answers anything else with `405` + a JSON body.
- `Router` raises `RuntimeError` on the ASGI `lifespan` protocol; uvicorn tolerates this
  in its default `auto` lifespan mode (startup logs a warning) and serves normally.
