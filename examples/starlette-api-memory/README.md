# starlette-api-memory

Todo JSON API built with Starlette (routes + `JSONResponse`, manual validation) and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/starlette-api-memory uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`.

## Test isolation

`create_app(repo=None)` builds a fresh `Starlette` app with its own empty `InMemoryTodoRepository`;
module-level `app` is the runnable instance. The app has no lifespan dependencies, so the shared
harness can drive it directly with `starlette.testclient.TestClient(app)`.

## Notes

- Starlette generates no OpenAPI, so this example is **exempt** from OpenAPI expectations
  (like other plain-JSON examples).
- `httpx` is a runtime dependency so `starlette.testclient.TestClient` works out of the box.
