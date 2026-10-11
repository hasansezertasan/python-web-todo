# flama-api-memory

Todo JSON API built with Flama (function endpoints, pydantic schemas via
`types.Schema`/`SchemaMetadata`, `JSONResponse`) and in-memory storage.
Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From the repo root:

```sh
uv run --project examples/flama-api-memory python -m app.main
```

Then `GET http://localhost:8000/todos`. `PORT` env var overrides the port (default `8000`):

```sh
PORT=8001 uv run --project examples/flama-api-memory python -m app.main
```

(`main()` reads `PORT` and passes it to `uvicorn.run`. An equivalent
uvicorn form is `uv run --project examples/flama-api-memory uvicorn app.main:app
--host 0.0.0.0 --port ${PORT:-8000}`.)

## Test isolation

`create_app(repo=None)` builds a fresh `Flama` app with its own empty
`InMemoryTodoRepository`; module-level `app` is the runnable instance.
The app has no lifespan dependencies, so the shared harness can drive it
in-process with the async `flama.client.Client`:

```py
from flama.client import Client

from app.main import create_app

async with Client(app=create_app()) as client:
    response = await client.get("/todos")
```

(`starlette.testclient.TestClient` does not fit here: Flama 2.x ships its own
ASGI/HTTP stack, so `starlette` is not installed in this example's venv.)

## Notes

- Flama serves schema-driven OpenAPI: the schema document is at `/schema/`
  (`application/vnd.oai.openapi+json`) and interactive docs at `/docs/`.
  The document exposes all five operations with item schemas containing
  `id`, `title`, and `done`.
- Flama reports request-validation failures as `400` by default; this example
  remaps `flama.exceptions.ValidationError` to the contract's `422` via
  `app.add_exception_handler(...)` (same approach as `litestar-api-memory`).
  Unknown ids raise `flama.exceptions.HTTPException(404)`, rendered as a
  JSON body by Flama's default error handler.
- `httpx` is a runtime dependency; the async `flama.client.Client` is used
  for in-process testing.
