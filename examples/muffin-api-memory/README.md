# muffin-api-memory

Todo JSON API built with Muffin and in-memory storage. Plain-JSON example for the [JSON API contract](../../specs/json-api.md) and [shared todo behavior](../../specs/todo-behavior.md). Exempt from OpenAPI expectations (no generator in plain Muffin core; OpenAPI only exists via the separate `muffin-rest` plugin, out of scope here).

## Run

From the repo root:

```sh
uv run --project examples/muffin-api-memory uvicorn app.main:app
```

Then `GET http://localhost:8000/todos`.

## Notes

- In-memory store starts empty; data is lost on restart. `create_app()` takes an optional repository/store and returns a fresh app per call.
- Handlers are `async def` (Muffin is ASGI); plain `dict`/`list` returns serialize to JSON automatically, and `(status, content)` tuples set the status (`201` on create).
- Empty or missing `title` returns `422` with a JSON body. Muffin's `request.json()` raises on an empty body, so the app catches that and treats it as `{}` (missing title).
- Unknown ids return `404` with a JSON body via `ResponseJSON`. Raising `ResponseError.NOT_FOUND` instead would render a plain-text body, which does not satisfy the contract's JSON-body requirement.
- Test client: Muffin's own `TestClient` (`muffin.TestClient`, an `asgi_tools` client) is **async-only** (`await client.get(...)`, `await response.json()`). The sync shared suite can instead drive the app with Starlette's (FastAPI's) sync `TestClient(app)`, which works unmodified since the app is plain ASGI.
