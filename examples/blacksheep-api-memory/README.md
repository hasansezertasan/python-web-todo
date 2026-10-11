# blacksheep-api-memory

Todo JSON API built with BlackSheep 2.x and in-memory storage. Implements the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md).

## Run

From this directory:

```sh
uv run uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`. Interactive docs at `http://localhost:8000/docs`, OpenAPI JSON at `http://localhost:8000/openapi.json`.

## Test harness

```python
from blacksheep.testing import TestClient
from app.main import create_app

app = create_app()  # fresh in-memory store per call
await app.start()
client = TestClient(app)
response = await client.get("/todos")
await app.stop()
```

`create_app(repo=None)` accepts an optional `InMemoryTodoRepository` for seeded state. `TestClient` is used after `await app.start()` (no context manager required); call `await app.stop()` when done. Each `create_app()` builds its own `Router` — `Application()` would otherwise share BlackSheep's global default router, so a second factory call in the same process would re-register (and collide on) every route.

## Notes

- **422 remap:** BlackSheep's model binders report invalid request bodies as `400` by default, while the shared contract expects `422`. This example parses the JSON body manually and returns `422` with a JSON body for missing/empty/invalid `title`, mirroring the Litestar examples' remap approach.
- **Non-integer ids** (e.g. `/todos/abc`) are reported as `404` with a JSON body, per "unknown ids are not found".
